"""Run Phase 3 experiments. Validation selects the policy. Test runs after that file exists."""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import replace
from pathlib import Path

from cascadeguard.asr.base import Hypothesis
from cascadeguard.evaluation.intent_metrics import frames_equal
from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard.evaluation.selective import forced_selection, recovery_action
from cascadeguard.pipeline import run_b0, run_b1, run_b2
from cascadeguard_facade.commit_policy_v4 import PolicySwitches
from cascadeguard_facade.contracts import CandidateBundle, CandidateRecord
from cascadeguard_facade.phase3_metrics import summarize
from cascadeguard_facade.phase3_registry import route_phase3
from cascadeguard_facade.risk_assessment_v4 import thresholds, weight_grid

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data" / "phase3" / "challenge_cases.csv"
OUT = ROOT / "experiments" / "phase3"
POLICY = OUT / "frozen_policy.json"


def load_cases() -> list[dict[str, str]]:
    with CASES.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _slots(text: str) -> dict[str, str]:
    if not str(text).strip():
        return {}
    parsed = {}
    for part in str(text).split("|"):
        name, value = part.split("=", 1)
        parsed[name] = value
    return parsed


def bundle_for(case: dict[str, str]) -> CandidateBundle:
    records = [
        CandidateRecord(
            f"{case['case_id']}-a",
            case["transformed_text"],
            "synthetic_edit",
            0,
            "SYNTHETIC_PROXY",
        )
    ]
    if case["alternate_text"]:
        records.append(
            CandidateRecord(
                f"{case['case_id']}-b",
                case["alternate_text"],
                "synthetic_edit",
                1,
                "SYNTHETIC_PROXY",
            )
        )
    return CandidateBundle(case["case_id"], tuple(records), "phase3_transform", "SYNTHETIC_PROXY")


def _judge(case: dict[str, str], action: str | None, reason: str, intent: str | None, slots: dict[str, str], polarity: str, labels: set[str]) -> dict[str, object]:
    gold_slots = _slots(case["expected_slots"])
    committed = intent is not None
    frame_ok = committed and frames_equal(case["expected_intent"], gold_slots, intent, slots)
    allowed = case["expected_commit_safety"] == "true"
    return {
        "case_id": case["case_id"],
        "category": case["category"],
        "split": case["split"],
        "action": action,
        "reason": reason,
        "committed": committed,
        "committed_slots": "|".join(f"{key}={value}" for key, value in sorted(slots.items())),
        "expected_slots": case["expected_slots"],
        "expected_action": case["expected_action"],
        "expected_ambiguity": case["expected_ambiguity"],
        "expected_contradiction": case["expected_contradiction"],
        "intent_correct": committed and intent == case["expected_intent"],
        "exact_frame": frame_ok,
        "unsafe": committed and not allowed,
        "selective_error": committed and not frame_ok,
        "safe_commit": committed and allowed and frame_ok,
        "action_correct": action == case["expected_action"],
        "retry_success": action == "RETRY" and case["expected_action"] == "RETRY" and frame_ok,
        "polarity_correct": polarity == case["expected_polarity"],
        "predicted_ambiguity": "SEMANTIC_AMBIGUITY" in labels or reason == "AMBIGUOUS_INTENT",
        "predicted_contradiction": "CONTRADICTORY_EVIDENCE" in labels or reason in {
            "CONTRADICTORY_EVIDENCE",
            "CRITICAL_SLOT_CONFLICT",
        },
        "critical_slot_case": case["category"] in {"SLOT_VALUE_CORRUPTION", "CONTRADICTORY_EVIDENCE"},
        "critical_slot_error": case["category"] in {"SLOT_VALUE_CORRUPTION", "CONTRADICTORY_EVIDENCE"}
        and committed
        and not frame_ok,
    }


def _prefix_slots(intent: str | None, slots: dict[str, str]) -> dict[str, str]:
    return dict(slots)


def run_frozen(name: str, case: dict[str, str], lexicon) -> dict[str, object]:
    bundle = bundle_for(case)
    ordered = bundle.ordered()
    hypotheses = tuple(Hypothesis(item.text, item.provenance, item.rank) for item in ordered)
    if name == "E0":
        output = run_b0(case["case_id"], hypotheses[0])
        return _judge(case, None, "prefix_parse", output.intent, _prefix_slots(output.intent, output.slots), "unknown", set())
    if name == "E1":
        output = run_b1(case["case_id"], hypotheses)
        return _judge(case, None, "prefix_confidence_then_rank", output.intent, output.slots, "unknown", set())
    if name == "E2":
        output, decision = run_b2(case["case_id"], hypotheses[0], hypotheses[1:])
        commit = decision.action.value in {"CONTINUE", "RETRY"}
        return _judge(
            case,
            decision.action.value,
            decision.failure.value,
            output.intent if commit else None,
            output.slots if commit else {},
            "unknown",
            set(),
        )
    texts = [item.text for item in ordered]
    if name == "E3":
        intent, slots = forced_selection(texts, lexicon)
        row = _judge(case, None, "forced_selection", None, {}, "unknown", set())
        row["forced_exact"] = frames_equal(case["expected_intent"], _slots(case["expected_slots"]), intent, slots)
        return row
    action, decision, _mechanism = recovery_action(texts, lexicon)
    commit = action.value in {"CONTINUE", "RETRY"}
    return _judge(
        case,
        action.value,
        decision.reason,
        decision.intent if commit else None,
        decision.slots if commit else {},
        "unknown",
        set(),
    )


def run_v4(case, lexicon, weights, threshold, switches, frozen_recovery) -> dict[str, object]:
    result = route_phase3(
        "b2_semantic_v4",
        bundle_for(case),
        lexicon,
        weights=weights,
        threshold=threshold,
        switches=switches,
        frozen_recovery=frozen_recovery,
    )
    labels = set(result.raw.get("diagnosis_labels") or [])
    slots = dict(result.committed_slots)
    return _judge(case, result.action, result.reason, result.committed_intent, slots, result.polarity, labels)


def evaluate(cases, name, lexicon, weights, threshold, switches=None, frozen=False) -> list[dict[str, object]]:
    rows = []
    for case in cases:
        if name in {"E0", "E1", "E2", "E3", "E4"}:
            rows.append(run_frozen(name, case, lexicon))
        else:
            rows.append(run_v4(case, lexicon, weights, threshold, switches or PolicySwitches(), frozen))
    return rows


def selection_key(summary: dict[str, object], weights: dict[str, float], threshold: float) -> tuple:
    unsafe = int(summary["unsafe_count"])
    safe = summary["safe_commitment_accuracy"]["value"]
    risk = summary["selective_risk"]["value"]
    coverage = summary["coverage"]["value"]
    safe_sort = -(safe if isinstance(safe, float) else -1.0)
    risk_sort = risk if isinstance(risk, float) else 1.0
    coverage_sort = -(coverage if isinstance(coverage, float) else 0.0)
    weight_tuple = tuple(weights[name] for name in ("intent", "slot", "polarity", "ambiguity", "contradiction"))
    return (unsafe, safe_sort, risk_sort, coverage_sort, weight_tuple, threshold)


def select_policy(validation: list[dict[str, str]], lexicon) -> dict[str, object]:
    ranked = []
    for weights in weight_grid():
        for threshold in thresholds():
            rows = evaluate(validation, "E7", lexicon, weights, threshold, PolicySwitches(), False)
            summary = summarize(rows, polarity_available=True)
            ranked.append((selection_key(summary, weights, threshold), weights, threshold, summary))
    ranked.sort(key=lambda item: item[0])
    _key, weights, threshold, summary = ranked[0]
    payload = {
        "policy_version": "phase3-policy-v1",
        "selection_split": "validation",
        "test_cases_read": False,
        "weights": weights,
        "threshold": threshold,
        "grid_size": len(ranked),
        "selection_rule": [
            "fewest unsafe commits",
            "highest safe commitment accuracy",
            "lowest selective risk",
            "highest coverage",
            "lexicographic weights then lowest threshold",
        ],
        "validation_summary": summary,
        "rationale": (
            "The published selective risk stays null when nothing is committed. "
            "The tuner uses 1.0 only as a sort sentinel for that missing rate so a null risk is not treated as a perfect zero."
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    POLICY.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (OUT / "validation_search.json").write_text(
        json.dumps(
            [
                {
                    "weights": item[1],
                    "threshold": item[2],
                    "unsafe_count": item[3]["unsafe_count"],
                    "coverage": item[3]["coverage"],
                    "selective_risk": item[3]["selective_risk"],
                    "safe_commitment_accuracy": item[3]["safe_commitment_accuracy"],
                }
                for item in ranked
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def write_report(directory: Path, summary: dict[str, object], rows: list[dict[str, object]]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "report.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (directory / "decision_log.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--select-only"
    cases = load_cases()
    lexicon = lexicon_from_utterances()
    validation = [case for case in cases if case["split"] == "validation"]
    if mode == "--select-only":
        payload = select_policy(validation, lexicon)
        print(json.dumps({"weights": payload["weights"], "threshold": payload["threshold"], "unsafe": payload["validation_summary"]["unsafe_count"], "coverage": payload["validation_summary"]["coverage"]}, indent=2))
        return
    if not POLICY.exists():
        raise SystemExit("frozen_policy.json is missing. Run --select-only first.")
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    test = [case for case in cases if case["split"] == "test"]
    weights = policy["weights"]
    threshold = policy["threshold"]
    conditions = {
        "E0_b0": ("E0", None, False),
        "E1_b1_prefix": ("E1", None, False),
        "E2_b2_prefix": ("E2", None, False),
        "E3_forced_lexical": ("E3", None, False),
        "E4_lexical_v3": ("E4", None, False),
        "E5_semantic_diagnosis": ("E5", PolicySwitches(), True),
        "E6_safe_commit": ("E6", replace(PolicySwitches(), allow_retry=False), False),
        "E7_semantic_controller_v4": ("E7", PolicySwitches(), False),
    }
    overview = {}
    for folder, (name, switches, frozen) in conditions.items():
        rows = evaluate(test, name, lexicon, weights, threshold, switches, frozen)
        polarity = name in {"E5", "E6", "E7"}
        summary = summarize(rows, polarity_available=polarity)
        summary["split"] = "test"
        summary["policy_version"] = policy["policy_version"]
        write_report(OUT / folder, summary, rows)
        overview[folder] = {
            "coverage": summary["coverage"],
            "selective_risk": summary["selective_risk"],
            "unsafe_commit_rate": summary["unsafe_commit_rate"],
            "exact_frame_accuracy": summary["exact_frame_accuracy"],
            "action_accuracy": summary["action_accuracy"],
        }
    ablations = {
        "A1": replace(PolicySwitches(), polarity=False),
        "A2": replace(PolicySwitches(), ambiguity=False),
        "A3": replace(PolicySwitches(), critical_slots=False),
        "A4": replace(PolicySwitches(), contradiction=False),
        "A5": replace(PolicySwitches(), completeness=False),
        "A6": replace(PolicySwitches(), modality=False),
        "A7": replace(PolicySwitches(), risk_score=False),
    }
    for name, switches in ablations.items():
        rows = evaluate(test, "E7", lexicon, weights, threshold, switches, False)
        summary = summarize(rows, polarity_available=True)
        summary["split"] = "test"
        summary["ablation"] = name
        write_report(OUT / "ablations" / name, summary, rows)
        overview[name] = {
            "coverage": summary["coverage"],
            "selective_risk": summary["selective_risk"],
            "unsafe_commit_rate": summary["unsafe_commit_rate"],
            "exact_frame_accuracy": summary["exact_frame_accuracy"],
        }
    rows = evaluate(test, "E5", lexicon, weights, threshold, PolicySwitches(), True)
    summary = summarize(rows, polarity_available=True)
    summary["split"] = "test"
    summary["ablation"] = "A8"
    summary["note"] = "Recovery policy removed. Action comes from frozen recovery_action."
    write_report(OUT / "ablations" / "A8", summary, rows)
    overview["A8"] = {
        "coverage": summary["coverage"],
        "selective_risk": summary["selective_risk"],
        "unsafe_commit_rate": summary["unsafe_commit_rate"],
        "exact_frame_accuracy": summary["exact_frame_accuracy"],
    }
    (OUT / "test_overview.json").write_text(json.dumps(overview, indent=2) + "\n", encoding="utf-8")
    print("wrote test overview")


if __name__ == "__main__":
    main()
