#!/usr/bin/env python3
"""Audit extension for sim-eval-v3. Writes only experiments/sim-eval-v3b/."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances  # noqa: E402
from cascadeguard.evaluation.v3_metrics import b0_exact_count, selective_report  # noqa: E402
from cascadeguard.evaluation.v3b_audit import (  # noqa: E402
    assert_audit_destination,
    assemble_audit_report,
    decision_log,
    lexical_timing,
    log_mismatches,
    mismatches_against_frozen,
)
from cascadeguard.simulation.candidate_diversity import gold_is_not_exact, v1_candidate_texts  # noqa: E402
from cascadeguard.simulation.utterance_generator import generate_utterances  # noqa: E402

PRESERVED = (
    ROOT / "experiments" / "B0" / "summary.json",
    ROOT / "experiments" / "B1" / "summary.json",
    ROOT / "experiments" / "B2" / "summary.json",
    ROOT / "artifacts" / "reports" / "simulation_report.json",
    ROOT / "experiments" / "sim-eval-v2" / "report.json",
    ROOT / "experiments" / "sim-eval-v3" / "report.json",
    ROOT / "configs" / "evaluation_v3.yaml",
    ROOT / "data" / "librispeech" / "annotations" / "phase_1c_pilot_30.csv",
)
OPTIONAL_PRESERVED = (ROOT / "artifacts" / "reports" / "simulation_v3" / "report.json",)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _preserved_paths() -> list[Path]:
    paths = [path for path in PRESERVED if path.is_file()]
    missing = [path for path in PRESERVED if not path.is_file()]
    if missing:
        raise SystemExit("Missing preserved file: " + ", ".join(str(path) for path in missing))
    for path in OPTIONAL_PRESERVED:
        if path.is_file():
            paths.append(path)
    return paths


def main() -> None:
    destination = ROOT / "experiments" / "sim-eval-v3b"
    assert_audit_destination(destination)
    frozen_path = ROOT / "experiments" / "sim-eval-v3" / "report.json"
    if destination.resolve() == frozen_path.parent.resolve():
        raise SystemExit("Refusing to write into sim-eval-v3")
    preserved = _preserved_paths()
    before = {str(path.relative_to(ROOT)): _sha256(path) for path in preserved}
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    if frozen.get("experiment_id") != "sim-eval-v3":
        raise SystemExit("Frozen report is not sim-eval-v3")

    seed = 17
    utterances = generate_utterances()
    expected_ids = [f"utt-{index:03d}" for index in range(200)]
    if [row.utterance_id for row in utterances] != expected_ids:
        raise SystemExit("Utterance ids are not utt-000 through utt-199")
    lexicon = lexicon_from_utterances(utterances)
    grouped = v1_candidate_texts(utterances, seed)
    for row in utterances:
        if not gold_is_not_exact(row.text, grouped[row.utterance_id]):
            raise SystemExit(f"Gold transcript entered the v1 list for {row.utterance_id}")

    selective = selective_report(
        utterances,
        grouped,
        lexicon,
        b0_exact=b0_exact_count(utterances, grouped),
    )
    disagreements = mismatches_against_frozen(selective, frozen["selector_comparison"]["v1_injector"])
    if disagreements:
        raise SystemExit(
            "Recomputed v1 section does not match the frozen sim-eval-v3 report:\n"
            + "\n".join(disagreements)
        )
    rows = decision_log(utterances, grouped, lexicon)
    log_errors = log_mismatches(rows, selective)
    if log_errors:
        raise SystemExit("Decision log does not match the aggregate:\n" + "\n".join(log_errors))
    timing = lexical_timing(utterances, grouped, lexicon)
    report = assemble_audit_report(
        selective,
        rows,
        timing,
        frozen.get("recovery_with_simulated_retry"),
        seed=seed,
        utterance_ids=expected_ids,
    )
    report["started_at"] = datetime.now(timezone.utc).isoformat()
    report["frozen_v3_report_sha256"] = before["experiments/sim-eval-v3/report.json"]
    report["preserved_sha256_before"] = before
    report["config"] = "configs/evaluation_v3b.yaml"

    destination.mkdir(parents=True, exist_ok=True)
    log_payload = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    log_path = destination / "decision_log.jsonl"
    log_path.write_text(log_payload, encoding="utf-8")
    report["decision_log"]["sha256"] = hashlib.sha256(log_payload.encode("utf-8")).hexdigest()
    report["decision_log"]["rows"] = len(rows)

    after = {str(path.relative_to(ROOT)): _sha256(path) for path in preserved}
    if after != before:
        raise SystemExit("Preserved experiment files changed")
    report["preserved_sha256_after"] = after
    payload = json.dumps(report, indent=2) + "\n"
    (destination / "report.json").write_text(payload, encoding="utf-8")
    if {str(path.relative_to(ROOT)): _sha256(path) for path in preserved} != before:
        raise SystemExit("Preserved experiment files changed")
    print(json.dumps({
        "experiment_id": report["experiment_id"],
        "rows": len(rows),
        "matches_frozen_v3": True,
        "negation_evidence_available": False,
        "uncertainty_evidence_available": False,
        "asr_latency": False,
        "preserved": True,
    }, indent=2))


if __name__ == "__main__":
    main()
