"""Score the frozen Phase 5 policy once.

Validation is scored before the policy file is written. Test labels are parsed
only after that file exists. The switches are not changed after either split.
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
from pathlib import Path

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard_phase5 import DATASET_ID, SEED, STRATEGY
from cascadeguard_phase5.baselines import run_baseline, v5_decision
from cascadeguard_phase5.commit_policy_v5 import GateSwitches
from cascadeguard_phase5.phase5_metrics import judge, summarize
from cascadeguard_phase5.semantic_controller_v5 import run_semantic_v5

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase5"
RUN = ROOT / "experiments" / "phase5" / "run-20261102-stage4-scored"
LEXICON = lexicon_from_utterances()
EXPERIMENTS = (
    ("E0", "b0_prefix"),
    ("E1", "b1_prefix"),
    ("E2", "b2_prefix_controller"),
    ("E3", "b1_forced_lexical"),
    ("E4", "b2_lexical_v3"),
    ("E5", "b2_semantic_v4"),
    ("E6", STRATEGY),
)
ABLATIONS = {
    "A0": GateSwitches(),
    "A1": GateSwitches(modality=False),
    "A2": GateSwitches(polarity=False),
    "A3": GateSwitches(critical_slots=False),
    "A4": GateSwitches(provenance=False),
    "A5": GateSwitches(conditionality=False),
    "A6": GateSwitches(gate=False),
    "A7": GateSwitches(recovery=False),
    "A8": GateSwitches(risk=False),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_challenge(split: str) -> list[dict[str, object]]:
    rows = []
    for line in (DATA / "challenge_cases.jsonl").read_text(encoding="utf-8").splitlines():
        if f'"split": "{split}"' not in line:
            continue
        row = json.loads(line)
        if row["split"] == split:
            rows.append(row)
    return rows


def _load_labels(split: str) -> dict[str, dict[str, object]]:
    rows = {}
    for line in (DATA / "oracle_labels.jsonl").read_text(encoding="utf-8").splitlines():
        if f'"split": "{split}"' not in line:
            continue
        row = json.loads(line)
        if row["split"] == split:
            rows[str(row["case_id"])] = row
    return rows


def _check_isolation(cases: list[dict[str, object]], split: str) -> None:
    parents = json.loads((DATA / "splits.json").read_text(encoding="utf-8"))
    allowed = set(parents[split])
    forbidden = {"referent", "expected_action", "expected_commit", "expected_safe_candidates", "intended_referent"}
    for case in cases:
        if case["parent_utterance_id"] not in allowed:
            raise SystemExit(f"{case['case_id']} leaks into {split}")
        if forbidden & set(case):
            raise SystemExit(f"{case['case_id']} carries a label into the controller input")


def _score_v5(cases, labels, switches: GateSwitches) -> list[dict[str, object]]:
    judged = []
    for case in cases:
        result = run_semantic_v5(
            {"bundle_id": case["candidate_bundle_id"], "candidates": case["candidates"]},
            LEXICON,
            switches,
        )
        decision = v5_decision(case, result)
        row = judge(labels[str(case["case_id"])], decision)
        row["raw_action"] = result["raw"]["action"]
        row["normalized_action"] = result["normalized"]["action"]
        row["execution_time_ms"] = result["execution_time_ms"]
        judged.append(row)
    return judged


def _score_baseline(name: str, cases, labels) -> list[dict[str, object]]:
    judged = []
    for case in cases:
        decision = run_baseline(name, case, LEXICON)
        judged.append(judge(labels[str(case["case_id"])], decision))
    return judged


def _bootstrap(left: list[dict[str, object]], right: list[dict[str, object]], field: str, seed: int) -> dict[str, object]:
    grouped_left: dict[str, list[int]] = defaultdict(list)
    grouped_right: dict[str, list[int]] = defaultdict(list)
    for row in left:
        grouped_left[str(row["parent_utterance_id"])].append(int(bool(row[field])))
    for row in right:
        grouped_right[str(row["parent_utterance_id"])].append(int(bool(row[field])))
    parents = sorted(set(grouped_left) & set(grouped_right))

    def estimate(sample: list[str]) -> float:
        diffs = []
        for parent in sample:
            diffs.append(
                sum(grouped_left[parent]) / len(grouped_left[parent])
                - sum(grouped_right[parent]) / len(grouped_right[parent])
            )
        return sum(diffs) / len(diffs)

    rng = random.Random(seed)
    draws = sorted(estimate([parents[rng.randrange(len(parents))] for _ in parents]) for _ in range(1000))
    return {
        "estimate": estimate(parents),
        "ci95_low": draws[24],
        "ci95_high": draws[974],
        "clusters": len(parents),
        "seed": seed,
        "field": field,
        "contrast": "E6 minus comparison",
    }


def _write(directory: Path, rows: list[dict[str, object]]) -> None:
    directory.mkdir(parents=True)
    (directory / "evaluation.jsonl").write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    (directory / "report.json").write_text(json.dumps(summarize(rows), indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if RUN.exists():
        raise SystemExit(f"{RUN} already exists. Choose a new run id. This run is not overwritten.")
    validation_cases = _load_challenge("validation")
    _check_isolation(validation_cases, "validation")
    validation_labels = _load_labels("validation")
    validation_rows = _score_v5(validation_cases, validation_labels, GateSwitches())
    policy = {
        "policy_id": "phase5-gates-v1",
        "strategy": STRATEGY,
        "dataset_id": DATASET_ID,
        "seed": SEED,
        "switches": asdict(GateSwitches()),
        "weight_search": None,
        "test_cases_read": False,
        "note": "Gates are predeclared. A low risk score cannot override a failed gate. No threshold was selected from data.",
    }
    RUN.mkdir(parents=True)
    policy_path = RUN / "validation" / "frozen_policy.json"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    _write(RUN / "validation" / "E6", validation_rows)
    test_cases = _load_challenge("test")
    _check_isolation(test_cases, "test")
    test_labels = _load_labels("test")
    reports = {}
    stored = {}
    for experiment, name in EXPERIMENTS:
        if name == STRATEGY:
            rows = _score_v5(test_cases, test_labels, GateSwitches())
        else:
            rows = _score_baseline(name, test_cases, test_labels)
        stored[experiment] = rows
        reports[experiment] = summarize(rows)
        _write(RUN / "final_test" / experiment, rows)
    ablations = {}
    for name, switches in ABLATIONS.items():
        rows = _score_v5(test_cases, test_labels, switches)
        ablations[name] = summarize(rows)
        _write(RUN / "ablations" / name, rows)
    contrasts = {
        other: {
            "unsafe_commit": _bootstrap(stored["E6"], stored[other], "unsafe_commit", SEED),
            "committed": _bootstrap(stored["E6"], stored[other], "committed", SEED + 1),
        }
        for other in ("E0", "E1", "E2", "E4", "E5")
    }
    manifest = {
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "seed": SEED,
        "dataset_id": DATASET_ID,
        "dataset_hashes": {
            "challenge_cases.jsonl": _sha(DATA / "challenge_cases.jsonl"),
            "oracle_labels.jsonl": _sha(DATA / "oracle_labels.jsonl"),
            "splits.json": _sha(DATA / "splits.json"),
        },
        "policy_sha256": _sha(policy_path),
        "test_cases": len(test_cases),
        "validation_cases": len(validation_cases),
        "supersedes": "experiments/phase5/run-20261102-stage4 counted an adapter-traced safe candidate as an unsafe path. Controller outputs were not retuned. This directory is the scoring correction.",
        "validation": summarize(validation_rows),
        "test": reports,
        "ablations": ablations,
        "parent_cluster_bootstrap": contrasts,
        "experiment_names": {
            "E0": "b0_prefix",
            "E1": "b1_prefix",
            "E2": "b2_prefix_controller",
            "E3": "b1_forced_lexical",
            "E4": "b2_lexical_v3",
            "E5": "b2_semantic_v4",
            "E6": "b2_semantic_v5",
            "phase4_warning": "Phase 4 E5 was the lexical ablation and Phase 4 E7 was b2_semantic_v4. Those names are not reused here.",
        },
    }
    (RUN / "reports" / "phase5_summary.json").parent.mkdir(parents=True)
    (RUN / "reports" / "phase5_summary.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"validation": manifest["validation"], "test": {key: reports[key] for key in reports}}, indent=2))


if __name__ == "__main__":
    sys.exit(main())
