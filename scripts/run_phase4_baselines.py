"""Baseline outputs are produced by scripts/run_phase4_evaluation.py.

Re-running this file does not overwrite experiments/phase4.
"""

from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1] / "experiments" / "phase4" / "baseline"
    missing = [f"E{index}" for index in range(8) if not (root / f"E{index}" / "report.json").exists()]
    if missing:
        raise SystemExit(f"baseline reports missing: {missing}. Run scripts/run_phase4_evaluation.py.")
    print("baseline reports present for E0-E7")


if __name__ == "__main__":
    main()
