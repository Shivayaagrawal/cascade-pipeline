"""Write the Phase 5 challenge files. Labels stay in oracle_labels.jsonl."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from cascadeguard_phase5.dataset_builder import build_dataset
from cascadeguard_phase5.phase5_oracle import label_case

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "synthetic" / "annotations" / "annotations.jsonl"
OUT = ROOT / "data" / "phase5"


def main() -> None:
    if (OUT / "oracle_labels.jsonl").exists():
        raise SystemExit(f"{OUT} already exists. Phase 5 data is not overwritten.")
    built = build_dataset(SOURCE)
    OUT.mkdir(parents=True)
    challenge_path = OUT / "challenge_cases.jsonl"
    bundle_path = OUT / "candidate_bundles.jsonl"
    oracle_path = OUT / "oracle_labels.jsonl"
    with challenge_path.open("w", encoding="utf-8") as challenge, bundle_path.open("w", encoding="utf-8") as bundles, oracle_path.open("w", encoding="utf-8") as oracle:
        for case in built["cases"]:
            public = {key: value for key, value in case.items() if key != "referent"}
            challenge.write(json.dumps(public, sort_keys=True) + "\n")
            bundles.write(json.dumps({"case_id": case["case_id"], "candidate_bundle_id": case["candidate_bundle_id"], "candidates": case["candidates"]}, sort_keys=True) + "\n")
            oracle.write(json.dumps(label_case(case), sort_keys=True) + "\n")
    (OUT / "splits.json").write_text(json.dumps(built["split_parents"], indent=2) + "\n", encoding="utf-8")
    with (OUT / "manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, ["case_id", "split", "corruption_category", "parent_utterance_id", "transformation"])
        writer.writeheader()
        for case in built["cases"]:
            writer.writerow({key: case[key] for key in writer.fieldnames})
    card = {
        "dataset_id": built["dataset_id"],
        "seed": built["seed"],
        "eligible_parents": built["eligible_parents"],
        "excluded_parents": built["excluded_parents"],
        "cases": len(built["cases"]),
        "category_counts": built["category_counts"],
        "shortfalls": built["shortfalls"],
        "label_location": "oracle_labels.jsonl",
        "same_session_limitation": "The specification table and the controller were written in the same session. The labels are not human gold.",
    }
    (OUT / "dataset_card.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(card, indent=2))


if __name__ == "__main__":
    main()
