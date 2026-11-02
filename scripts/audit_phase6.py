"""Recompute the cited Phase 6 report and check that Phase 5 stayed frozen."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from cascadeguard_phase6.phase6_metrics import summarize

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "experiments" / "phase6" / "run-20261102-phase6"
sys.path.insert(0, str(ROOT))
from tests.phase4.test_regression import PROTECTED


def main() -> int:
    policy = json.loads((RUN / "validation" / "frozen_policy.json").read_text(encoding="utf-8"))
    if policy["test_cases_read"] is not False or policy["validation_used_for_selection"] is not False:
        raise SystemExit("policy was marked as tuned or as having read the test split")
    stored = json.loads((RUN / "final_test" / "E4" / "report.json").read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in (RUN / "final_test" / "E4" / "evaluation.jsonl").read_text(encoding="utf-8").splitlines()]
    recomputed = summarize(rows)
    for key in ("coverage", "unsafe_commit_rate", "critical_substitution_detection", "false_rejection_on_clean"):
        if stored[key]["numerator"] != recomputed[key]["numerator"] or stored[key]["denominator"] != recomputed[key]["denominator"]:
            raise SystemExit(f"{key} does not match the log")
    if stored["critical_slot_safety"]["value"] is not None:
        raise SystemExit("E4 critical-slot safety should be null when no substitution was committed")
    summary = json.loads((RUN / "reports" / "phase6_summary.json").read_text(encoding="utf-8"))
    controller = ROOT / "src" / "cascadeguard_phase5" / "semantic_controller_v5.py"
    if hashlib.sha256(controller.read_bytes()).hexdigest() != summary["dataset_hashes"]["phase5_controller"]:
        raise SystemExit("b2_semantic_v5 changed after the Phase 6 run")
    if "cascadeguard_phase6" in controller.read_text(encoding="utf-8"):
        raise SystemExit("Phase 5 controller imports Phase 6")
    for relative, digest in PROTECTED.items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"protected hash changed: {relative}")
    completed = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT)
    print(json.dumps({"e4_coverage": stored["coverage"], "e4_unsafe": stored["unsafe_commit_rate"], "e4_detection": stored["critical_substitution_detection"], "pytest_exit": completed.returncode}))
    return completed.returncode


if __name__ == "__main__":
    main()
