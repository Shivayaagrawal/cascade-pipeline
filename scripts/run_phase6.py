"""Score the predeclared Phase 6 policy once.

The policy file is written before any oracle line is parsed. Switches are not
changed after validation or test results are known.
"""

from __future__ import annotations

import hashlib
import json
import platform
import random
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard_phase5.baselines import run_baseline
from cascadeguard_phase5.modality_analyzer_v5 import analyze_modality
from cascadeguard_phase6 import DATASET_ID, SEED
from cascadeguard_phase6.candidate_only_adapter import run_candidate_only
from cascadeguard_phase6.phase6_metrics import judge, summarize
from cascadeguard_phase6.reference_aware_controller import ReferenceSwitches, run_reference_aware
from cascadeguard_phase6.reference_signal import partial_reference

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase6"
RUN = ROOT / "experiments" / "phase6" / "run-20261102-phase6"
LEXICON = lexicon_from_utterances()
CONDITIONS = {
    "E0": "candidate_only",
    "E1": "candidate_only",
    "E2": "candidate_only",
    "E3": "candidate_only",
    "E4": "critical_slot_reference",
    "E5": "full_referent",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows(path: Path, split: str) -> list[dict[str, object]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if f'"split": "{split}"' not in line:
            continue
        row = json.loads(line)
        if row["split"] == split:
            rows.append(row)
    return rows


def _labels(split: str) -> dict[str, dict[str, object]]:
    return {str(row["case_id"]): row for row in _rows(DATA / "oracle_labels.jsonl", split)}


def _references(split: str) -> dict[str, dict[str, object]]:
    return {str(row["case_id"]): row for row in _rows(DATA / "reference_signals.jsonl", split)}


def _check(cases: list[dict[str, object]], split: str) -> None:
    parents = json.loads((DATA / "splits.json").read_text(encoding="utf-8"))["split_parents"]
    allowed = set(parents[split])
    for case in cases:
        if case["parent_utterance_id"] not in allowed:
            raise SystemExit(f"{case['case_id']} leaks into {split}")
        if {"referent", "expected_action", "expected_commit", "intended_referent"} & set(case):
            raise SystemExit(f"{case['case_id']} carries an oracle field")


def _modality(case: dict[str, object], candidate_id: str | None) -> dict[str, str]:
    text = str(case["candidates"][0]["text"])
    if candidate_id is not None:
        for item in case["candidates"]:
            if item["candidate_id"] == candidate_id:
                text = str(item["text"])
    reading = analyze_modality(text)
    return {"modality_label": reading.modality, "polarity": reading.polarity, "conditionality": reading.conditionality}


def _from_controller(case: dict[str, object], result: dict[str, object]) -> dict[str, object]:
    normalized = result["normalized"]
    decision = {
        "case_id": case["case_id"],
        "actual_commit": bool(normalized["committed"]),
        "committed_frame": normalized.get("committed_frame"),
        "committed_candidate_id": normalized.get("committed_candidate_id"),
        "provenance_status": "CONTROLLER_EMITTED" if normalized["committed"] else "NO_COMMIT",
        "normalized_action": normalized["action"],
    }
    decision.update(_modality(case, None if not normalized["committed"] else normalized.get("committed_candidate_id")))
    return decision


def _score(name: str, cases, labels, references, switches: ReferenceSwitches | None = None, signal: str = "critical_slots") -> list[dict[str, object]]:
    condition = CONDITIONS.get(name, "critical_slot_reference")
    judged = []
    for case in cases:
        if name == "E0":
            decision = run_baseline("b0_prefix", case, LEXICON)
        elif name == "E1":
            decision = run_baseline("b2_lexical_v3", case, LEXICON)
        elif name == "E2":
            decision = run_baseline("b2_semantic_v4", case, LEXICON)
        elif name == "E3":
            decision = _from_controller(case, run_candidate_only(case, LEXICON))
        else:
            reference = None
            if signal == "partial":
                reference = partial_reference(references[str(case["case_id"])]["critical_slots"])
            elif signal == "absent":
                reference = None
            elif signal == "full_referent":
                reference = references[str(case["case_id"])]["full_referent"]
            else:
                reference = references[str(case["case_id"])]["critical_slots"]
            decision = _from_controller(case, run_reference_aware(case, reference, LEXICON, switches))
        judged.append(judge(labels[str(case["case_id"])], decision, condition))
    return judged


def _bootstrap(left, right, field: str, seed: int) -> dict[str, object]:
    grouped_left = defaultdict(list)
    grouped_right = defaultdict(list)
    for row in left:
        grouped_left[str(row["parent_utterance_id"])].append(int(bool(row[field])))
    for row in right:
        grouped_right[str(row["parent_utterance_id"])].append(int(bool(row[field])))
    parents = sorted(set(grouped_left) & set(grouped_right))

    def estimate(sample: list[str]) -> float:
        diffs = []
        for parent in sample:
            diffs.append(sum(grouped_left[parent]) / len(grouped_left[parent]) - sum(grouped_right[parent]) / len(grouped_right[parent]))
        return sum(diffs) / len(diffs)

    rng = random.Random(seed)
    draws = sorted(estimate([parents[rng.randrange(len(parents))] for _ in parents]) for _ in range(1000))
    return {"estimate": estimate(parents), "ci95_low": draws[24], "ci95_high": draws[974], "clusters": len(parents), "seed": seed, "field": field, "contrast": "E4 minus E3"}


def _write(directory: Path, rows: list[dict[str, object]]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "evaluation.jsonl").write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    (directory / "report.json").write_text(json.dumps(summarize(rows), indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if RUN.exists():
        raise SystemExit(f"{RUN} already exists. This run is not overwritten.")
    validation_cases = _rows(DATA / "challenge_cases.jsonl", "validation")
    test_cases = _rows(DATA / "challenge_cases.jsonl", "test")
    _check(validation_cases, "validation")
    _check(test_cases, "test")
    policy = {
        "policy_id": "phase6-reference-v1",
        "dataset_id": DATASET_ID,
        "seed": SEED,
        "primary_comparison": "E3 candidate-only versus E4 critical-slot reference",
        "switches": asdict(ReferenceSwitches()),
        "weight_search": None,
        "validation_used_for_selection": False,
        "test_cases_read": False,
        "note": "The reference check is predeclared. No threshold or weight was selected from scores.",
    }
    RUN.mkdir(parents=True)
    policy_path = RUN / "validation" / "frozen_policy.json"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    validation_labels = _labels("validation")
    validation_refs = _references("validation")
    validation_rows = {
        "E3": _score("E3", validation_cases, validation_labels, validation_refs),
        "E4": _score("E4", validation_cases, validation_labels, validation_refs),
    }
    for name, rows in validation_rows.items():
        _write(RUN / "validation" / name, rows)
    test_access = datetime.now(timezone.utc).isoformat()
    test_labels = _labels("test")
    test_refs = _references("test")
    stored = {}
    reports = {}
    for name in ("E0", "E1", "E2", "E3", "E4", "E5"):
        signal = "full_referent" if name == "E5" else "critical_slots"
        rows = _score(name, test_cases, test_labels, test_refs, signal=signal)
        stored[name] = rows
        reports[name] = summarize(rows)
        _write(RUN / "final_test" / name, rows)
    ablations = {
        "A0": ("critical_slots", ReferenceSwitches()),
        "A1": ("critical_slots", ReferenceSwitches(reference=False)),
        "A2": ("critical_slots", ReferenceSwitches(modality=False)),
        "A3": ("critical_slots", ReferenceSwitches(polarity=False)),
        "A4": ("critical_slots", ReferenceSwitches(conditionality=False)),
        "A5": ("critical_slots", ReferenceSwitches(provenance=False)),
        "A6": ("critical_slots", ReferenceSwitches(gate=False)),
        "A7": ("partial", ReferenceSwitches()),
        "A8": ("absent", ReferenceSwitches()),
    }
    ablation_reports = {}
    for name, (signal, switches) in ablations.items():
        rows = _score("E4", test_cases, test_labels, test_refs, switches, signal)
        ablation_reports[name] = summarize(rows)
        _write(RUN / "ablations" / name, rows)
    boundary = []
    by_id = {row["case_id"]: row for row in stored["E3"]}
    full = {row["case_id"]: row for row in stored["E5"]}
    for row in stored["E4"]:
        if row["category"] not in {"date_substitution", "time_substitution", "amount_substitution", "candidate_provenance_conflict", "parent_transcript_cue", "clean_affirmative", "clean_polite_instruction"}:
            continue
        boundary.append(
            {
                "case_id": row["case_id"],
                "category": row["category"],
                "transformation": row["transformation"],
                "candidate_only": by_id[row["case_id"]]["outcome"],
                "critical_slot_reference": row["outcome"],
                "full_referent": full[row["case_id"]]["outcome"],
            }
        )
    (RUN / "reports").mkdir(parents=True)
    (RUN / "reports" / "information_boundary.jsonl").write_text("".join(json.dumps(row) + "\n" for row in boundary), encoding="utf-8")
    summary = {
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "seed": SEED,
        "dataset_id": DATASET_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "test_labels_parsed_at": test_access,
        "policy_sha256": _sha(policy_path),
        "dataset_hashes": {
            "challenge_cases.jsonl": _sha(DATA / "challenge_cases.jsonl"),
            "oracle_labels.jsonl": _sha(DATA / "oracle_labels.jsonl"),
            "reference_signals.jsonl": _sha(DATA / "reference_signals.jsonl"),
            "splits.json": _sha(DATA / "splits.json"),
            "phase5_controller": _sha(ROOT / "src" / "cascadeguard_phase5" / "semantic_controller_v5.py"),
        },
        "test_cases": len(test_cases),
        "validation_cases": len(validation_cases),
        "test_parent_clusters": len({case["parent_utterance_id"] for case in test_cases}),
        "timing_note": "Measured durations are controller time. They are not ASR latency.",
        "validation": {name: summarize(rows) for name, rows in validation_rows.items()},
        "test": reports,
        "ablations": ablation_reports,
        "bootstrap_e4_minus_e3": {
            "unsafe_commit": _bootstrap(stored["E4"], stored["E3"], "unsafe_commit", SEED),
            "committed": _bootstrap(stored["E4"], stored["E3"], "committed", SEED + 1),
        },
        "experiment_names": {
            "E0": "b0_prefix",
            "E1": "b2_lexical_v3",
            "E2": "b2_semantic_v4",
            "E3": "b2_semantic_v5 candidate-only",
            "E4": "b2_reference_aware_v1 critical-slot reference",
            "E5": "b2_reference_aware_v1 full parent transcript",
            "phase5_warning": "Phase 5 E3 was forced lexical and Phase 5 E6 was b2_semantic_v5. Those ids are not reused here.",
        },
    }
    (RUN / "reports" / "phase6_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"validation": summary["validation"], "test": {key: {"coverage": reports[key]["coverage"], "unsafe": reports[key]["unsafe_commit_rate"], "critical": reports[key]["critical_slot_safety"], "detection": reports[key]["critical_substitution_detection"], "false_rejection": reports[key]["false_rejection_on_clean"], "outcomes": reports[key]["outcomes"]} for key in reports}}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
