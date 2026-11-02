"""Ablation outputs are produced by scripts/run_phase4_evaluation.py.

Re-running this file does not overwrite experiments/phase4.
"""

from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1] / "experiments" / "phase4" / "ablations"
    missing = [f"A{index}" for index in range(1, 9) if not (root / f"A{index}" / "report.json").exists()]
    if missing:
        raise SystemExit(f"ablation reports missing: {missing}. Run scripts/run_phase4_evaluation.py.")
    print("ablation reports present for A1-A8")


if __name__ == "__main__":
    main()
