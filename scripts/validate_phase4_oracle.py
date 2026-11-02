"""Recompute frozen oracle labels and compare them to oracle_labels.jsonl."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cascadeguard_phase4.independent_oracle import judge, load_inventory


def main() -> None:
    data = ROOT / "data" / "phase4"
    inventory = load_inventory(ROOT / "data" / "synthetic" / "annotations" / "annotations.jsonl")
    bundles = [json.loads(line) for line in (data / "candidate_bundles.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    referents = {json.loads(line)["case_id"]: json.loads(line) for line in (data / "scenario_referents.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    frozen = {json.loads(line)["case_id"]: json.loads(line) for line in (data / "oracle_labels.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    mismatches = []
    for bundle in bundles:
        referent = {"intent": referents[bundle["case_id"]]["intent"], "slots": referents[bundle["case_id"]]["slots"]}
        fresh = judge(bundle["candidates"], referent, inventory)
        stored = frozen[bundle["case_id"]]
        for key, value in fresh.items():
            if stored.get(key) != value:
                mismatches.append(bundle["case_id"])
                break
    if mismatches:
        raise SystemExit(f"{len(mismatches)} oracle rows differ from a fresh judgment")
    print(f"oracle rows checked: {len(bundles)}")


if __name__ == "__main__":
    main()
