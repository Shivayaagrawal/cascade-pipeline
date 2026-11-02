"""Recompute the cited Phase 5 report from its logs and check protected files."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from cascadeguard_phase5.phase5_metrics import summarize

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.phase4.test_regression import PROTECTED
RUN = ROOT / "experiments" / "phase5" / "run-20261102-stage4-scored"


def _rows(relative: str) -> list[dict[str, object]]:
    return [json.loads(line) for line in (RUN / relative).read_text(encoding="utf-8").splitlines()]


def main() -> int:
    policy = json.loads((RUN / "validation" / "frozen_policy.json").read_text(encoding="utf-8"))
    if policy["test_cases_read"] is not False:
        raise SystemExit("frozen policy was marked as having read the test split")
    stored = json.loads((RUN / "final_test" / "E6" / "report.json").read_text(encoding="utf-8"))
    recomputed = summarize(_rows("final_test/E6/evaluation.jsonl"))
    for key in ("coverage", "unsafe_commit_rate", "path_safety", "selective_risk"):
        if stored[key]["numerator"] != recomputed[key]["numerator"] or stored[key]["denominator"] != recomputed[key]["denominator"]:
            raise SystemExit(f"{key} does not match the log")
    for row in _rows("final_test/E6/evaluation.jsonl"):
        if row["outcome"] in {"SAFE_ABSTENTION", "UNNECESSARY_ABSTENTION"} and row["committed"]:
            raise SystemExit(f"{row['case_id']} abstained and committed")
        if row["committed"] and row["provenance_status"] != "CONTROLLER_EMITTED":
            raise SystemExit(f"{row['case_id']} committed without an emitted id")
    splits = json.loads((ROOT / "data" / "phase5" / "splits.json").read_text(encoding="utf-8"))
    if set(splits["test"]) & set(splits["validation"]) or set(splits["test"]) & set(splits["development"]):
        raise SystemExit("parent lists overlap")
    for relative, digest in PROTECTED.items():
        found = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if found != digest:
            raise SystemExit(f"protected hash changed: {relative}")
    completed = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT)
    print(json.dumps({"policy_test_cases_read": policy["test_cases_read"], "e6_coverage": stored["coverage"], "e6_unsafe": stored["unsafe_commit_rate"], "pytest_exit": completed.returncode}))
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
