"""Print the saved Phase 4 summary. This does not rescore the test split."""

import json
from pathlib import Path


def main() -> None:
    path = Path(__file__).resolve().parents[1] / "experiments" / "phase4" / "reports" / "phase4_summary.json"
    if not path.exists():
        raise SystemExit("summary missing. Run scripts/run_phase4_evaluation.py.")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
