"""Validation, frozen policy, one test pass, ablations, and paired intervals.

Test bundles are loaded only after frozen_policy.json is written.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cascadeguard_facade.commit_policy_v4 import PolicySwitches
from cascadeguard_phase4.execute import (
    PHASE3_THRESHOLD,
    PHASE3_WEIGHTS,
    evaluate_rows,
    search_validation,
    write_json,
    write_jsonl,
)
from cascadeguard_phase4.independent_evaluator import frames_equal
from cascadeguard_phase4.phase4_metrics import summarize
from cascadeguard_phase4.statistical_analysis import paired_cluster_difference

DATA = ROOT / "data" / "phase4"
OUT = ROOT / "experiments" / "phase4"
CODES = ("E0", "E1", "E2", "E3", "E4", "E5", "E6", "E7")


def _load(split: str) -> tuple[list[dict], dict[str, dict]]:
    bundles = [
        json.loads(line)
        for line in (DATA / "candidate_bundles.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    labels = [
        json.loads(line)
        for line in (DATA / "oracle_labels.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    chosen = [row for row in bundles if row["split"] == split]
    label_map = {row["case_id"]: row for row in labels if row["split"] == split}
    if set(label_map) != {row["case_id"] for row in chosen}:
        raise RuntimeError(f"{split} bundles and oracle labels do not match")
    return chosen, label_map


def _store(directory: Path, code: str, decisions, judged) -> None:
    write_jsonl(directory / code / "decision_log.jsonl", decisions)
    write_jsonl(directory / code / "evaluation.jsonl", judged)
    summary = summarize(judged)
    summary["by_category"] = {
        category: summarize(judged, category=category)
        for category in sorted({row["category"] for row in judged})
    }
    if code == "E3":
        summary["forced_exact_frame_accuracy"] = _forced(decisions, judged)
        summary["coverage_note"] = "Forced selection is not coverage."
    write_json(directory / code / "report.json", summary)


def _forced(decisions, judged) -> dict[str, object]:
    from cascadeguard_phase4.phase4_metrics import proportion

    by_id = {row["case_id"]: row for row in judged}
    correct = 0
    for decision in decisions:
        frame = decision["answered_frame"] or {"intent": None, "slots": {}}
        row = by_id[decision["case_id"]]
        correct += int(
            frames_equal(
                None if row.get("expected_intent") is None else str(row["expected_intent"]),
                dict(row.get("expected_slots") or {}),
                frame.get("intent"),
                dict(frame.get("slots") or {}),
            )
        )
    return proportion(correct, len(decisions), "no cases")


def _attach_expected_intent(judged, labels):
    for row in judged:
        row["expected_intent"] = labels[row["case_id"]]["expected_intent"]


def _contrasts(by_code: dict[str, list[dict]]) -> dict[str, object]:
    contrasts = {}
    for other in ("E0", "E1", "E2", "E4"):
        contrasts[f"E7_minus_{other}"] = {
            "unsafe_commit_per_case": paired_cluster_difference(
                by_code["E7"], by_code[other], "unsafe_commit", seed=20261104
            ),
            "coverage_per_case": paired_cluster_difference(
                by_code["E7"], by_code[other], "committed", seed=20261105
            ),
            "candidate_safe_per_case": paired_cluster_difference(
                by_code["E7"], by_code[other], "candidate_safe", seed=20261106
            ),
        }
    return contrasts


def _hypothesis(by_code: dict[str, list[dict]], contrasts) -> dict[str, object]:
    def verdict(diff: dict, direction: str) -> str:
        estimate = diff["estimate"]
        interval = diff["ci95"]
        if estimate is None or interval is None:
            return "inconclusive"
        if direction == "lower":
            if interval["high"] < 0:
                return "supported"
            if interval["low"] > 0:
                return "contradicted"
        if direction == "higher":
            if interval["low"] > 0:
                return "supported"
            if interval["high"] < 0:
                return "contradicted"
        return "inconclusive"

    def category_rate(code: str, category: str, key: str) -> dict:
        rows = [row for row in by_code[code] if row["category"] == category]
        commits = [row for row in rows if row["committed"]]
        from cascadeguard_phase4.phase4_metrics import proportion

        per_commit = proportion(
            sum(bool(row[key]) for row in commits),
            len(commits),
            "no commits in this category",
        )
        per_case = proportion(sum(bool(row[key]) for row in rows), len(rows), "no cases")
        return {"per_commit": per_commit, "per_case": per_case, "cases": len(rows)}

    clean = [row for row in by_code["E7"] if row["category"] == "clean_control"]
    from cascadeguard_phase4.phase4_metrics import proportion

    return {
        "H1_unsafe_lower_than_prefix": {
            "E0": verdict(contrasts["E7_minus_E0"]["unsafe_commit_per_case"], "lower"),
            "E1": verdict(contrasts["E7_minus_E1"]["unsafe_commit_per_case"], "lower"),
            "E2": verdict(contrasts["E7_minus_E2"]["unsafe_commit_per_case"], "lower"),
        },
        "H2_path_safety_indicator": {
            "E0": verdict(contrasts["E7_minus_E0"]["candidate_safe_per_case"], "higher"),
            "E4": verdict(contrasts["E7_minus_E4"]["candidate_safe_per_case"], "higher"),
        },
        "H3_negation": {
            "E7": category_rate("E7", "negation_polarity", "unsafe_commit"),
            "E0": category_rate("E0", "negation_polarity", "unsafe_commit"),
            "E4": category_rate("E4", "negation_polarity", "unsafe_commit"),
        },
        "H4_slot_mutation": {
            "E7": category_rate("E7", "critical_slot_mutation", "unsafe_commit"),
            "E0": category_rate("E0", "critical_slot_mutation", "unsafe_commit"),
            "E4": category_rate("E4", "critical_slot_mutation", "unsafe_commit"),
        },
        "H5_provenance_retries": _retry_check(by_code["E7"]),
        "H6_coverage_difference": {
            "E0": contrasts["E7_minus_E0"]["coverage_per_case"],
            "E4": contrasts["E7_minus_E4"]["coverage_per_case"],
        },
        "H7_clean_controls": {
            "coverage": proportion(sum(row["committed"] for row in clean), len(clean), "no clean controls"),
            "unnecessary_abstention": proportion(
                sum(row["outcome"] == "UNNECESSARY_ABSTENTION" for row in clean),
                len(clean),
                "no clean controls",
            ),
            "safe_commit": proportion(
                sum(row["outcome"] == "SAFE_COMMIT" for row in clean),
                len(clean),
                "no clean controls",
            ),
        },
    }


def _retry_check(rows: list[dict]) -> dict[str, object]:
    provenance = [row for row in rows if row["category"] == "candidate_provenance"]
    retries = [row for row in provenance if row["outcome"] == "SAFE_COMMIT"]
    invalid = [row for row in provenance if row["outcome"] == "INVALID_ACTION_PATH"]
    return {
        "cases": len(provenance),
        "safe_commits": len(retries),
        "invalid_paths": len(invalid),
        "unsafe_commits": sum(bool(row["unsafe_commit"]) for row in provenance),
    }


def _ablation(records, labels, name: str):
    if name == "A8":
        return evaluate_rows(
            records, labels, "E5", weights=PHASE3_WEIGHTS, threshold=PHASE3_THRESHOLD
        )
    switches = PolicySwitches(
        polarity=name != "A1",
        modality=name != "A2",
        critical_slots=name != "A3",
        completeness=name != "A5",
        contradiction=name != "A6",
        ambiguity=name != "A7",
    )
    return evaluate_rows(
        records,
        labels,
        "E7",
        weights=PHASE3_WEIGHTS,
        threshold=PHASE3_THRESHOLD,
        switches=switches,
    )


def main() -> None:
    validation_records, validation_labels = _load("validation")
    baseline = OUT / "baseline"
    by_validation = {}
    for code in CODES:
        decisions, judged = evaluate_rows(
            validation_records,
            validation_labels,
            code,
            weights=PHASE3_WEIGHTS,
            threshold=PHASE3_THRESHOLD,
        )
        _attach_expected_intent(judged, validation_labels)
        _store(baseline, code, decisions, judged)
        by_validation[code] = judged
    search = search_validation(validation_records, validation_labels)
    policy = {
        "policy_version": "phase4-policy-v1",
        "primary_configuration": "phase3-policy-v1",
        "primary_weights": PHASE3_WEIGHTS,
        "primary_threshold": PHASE3_THRESHOLD,
        "selection_split": "validation",
        "test_cases_read": False,
        "grid_size": search["grid_size"],
        "tie_count_on_scientific_criteria": search["tie_count"],
        "phase3_config_in_optimal_set": search["phase3_in_tie_set"],
        "selection_rule_weights": search["chosen_weights"],
        "selection_rule_threshold": search["chosen_threshold"],
        "selection_rule": [
            "fewest unsafe candidate commitments",
            "fewest invalid action paths",
            "highest safe commitment accuracy",
            "lowest selective risk",
            "highest coverage",
            "lowest unnecessary abstention",
            "if the Phase 3 configuration ties, keep it",
            "otherwise lexicographic weights then lowest threshold",
        ],
        "hypothesis_configuration": "primary_configuration",
        "note": "Hypotheses are scored on the unmodified Phase 3 configuration. The selection-rule cell is a sensitivity run frozen before the test split is read.",
    }
    policy_path = OUT / "validation" / "frozen_policy.json"
    write_json(policy_path, policy)
    write_json(OUT / "validation" / "search.json", {"grid_size": search["grid_size"], "tie_count": search["tie_count"], "rows": search["rows"]})
    write_json(OUT / "risk_coverage" / "validation_curve.json", {"points": search["curve"], "illustrative": False})
    policy_hash = hashlib.sha256(policy_path.read_bytes()).hexdigest()

    test_records, test_labels = _load("test")
    final = OUT / "final_test" / "phase3_config"
    by_test = {}
    for code in CODES:
        decisions, judged = evaluate_rows(
            test_records,
            test_labels,
            code,
            weights=PHASE3_WEIGHTS,
            threshold=PHASE3_THRESHOLD,
        )
        _attach_expected_intent(judged, test_labels)
        _store(final, code, decisions, judged)
        by_test[code] = judged
    sensitivity = None
    if (search["chosen_weights"], search["chosen_threshold"]) != (PHASE3_WEIGHTS, PHASE3_THRESHOLD):
        decisions, judged = evaluate_rows(
            test_records,
            test_labels,
            "E7",
            weights=search["chosen_weights"],
            threshold=search["chosen_threshold"],
        )
        _attach_expected_intent(judged, test_labels)
        _store(OUT / "final_test" / "selection_rule", "E7", decisions, judged)
        sensitivity = summarize(judged)
    contrasts = _contrasts(by_test)
    hypotheses = _hypothesis(by_test, contrasts)
    ablation_dir = OUT / "ablations"
    ablation_summaries = {}
    e7_outcomes = [(row["case_id"], row["outcome"], row["action"]) for row in by_test["E7"]]
    for name in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"):
        decisions, judged = _ablation(test_records, test_labels, name)
        _attach_expected_intent(judged, test_labels)
        _store(ablation_dir, name, decisions, judged)
        changed = sum(
            (row["case_id"], row["outcome"], row["action"]) != previous
            for row, previous in zip(judged, e7_outcomes, strict=True)
        )
        ablation_summaries[name] = {
            "changed_cases": changed,
            "component_absent": name == "A4" and changed == 0,
            "summary": summarize(judged),
        }
    report = {
        "policy_sha256": policy_hash,
        "test_cases": len(test_records),
        "validation_cases": len(validation_records),
        "hypotheses": hypotheses,
        "contrasts": contrasts,
        "selection_rule_test": sensitivity,
        "ablations": {
            name: {"changed_cases": item["changed_cases"], "component_absent": item["component_absent"]}
            for name, item in ablation_summaries.items()
        },
    }
    write_json(OUT / "reports" / "phase4_summary.json", report)
    print(json.dumps({"policy_sha256": policy_hash, "test_cases": len(test_records), "tie_count": search["tie_count"], "chosen_threshold": search["chosen_threshold"]}, indent=2))


if __name__ == "__main__":
    main()
