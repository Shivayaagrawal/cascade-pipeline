"""Write Phase 6 files. Labels stay in the oracle. References stay in their own file."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from cascadeguard_phase6.dataset_builder import build_dataset
from cascadeguard_phase6.phase6_oracle import label_case
from cascadeguard_phase6.reference_signal import critical_slot_reference, full_referent_reference

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "synthetic" / "annotations" / "annotations.jsonl"
OUT = ROOT / "data" / "phase6"


def main() -> None:
    if (OUT / "oracle_labels.jsonl").exists():
        raise SystemExit(f"{OUT} already exists. Phase 6 data is not overwritten.")
    built = build_dataset(SOURCE)
    OUT.mkdir(parents=True)
    public_fields = ("case_id", "parent_utterance_id", "candidate_bundle_id", "corruption_category", "transformation", "split", "candidates")
    with (OUT / "challenge_cases.jsonl").open("w", encoding="utf-8") as challenge, (OUT / "reference_signals.jsonl").open("w", encoding="utf-8") as references, (OUT / "oracle_labels.jsonl").open("w", encoding="utf-8") as oracle:
        for case in built["cases"]:
            challenge.write(json.dumps({key: case[key] for key in public_fields}, sort_keys=True) + "\n")
            referent = case["referent"]
            mode1 = critical_slot_reference(str(case["case_id"]), str(referent["intent"]), dict(referent["slots"]))
            mode2 = full_referent_reference(str(case["case_id"]), str(referent["intent"]), dict(referent["slots"]), str(case["full_referent_transcript"]))
            references.write(json.dumps({"case_id": case["case_id"], "split": case["split"], "critical_slots": mode1, "full_referent": mode2}, sort_keys=True) + "\n")
            oracle.write(json.dumps(label_case(case), sort_keys=True) + "\n")
    manifest = {
        "dataset_id": built["dataset_id"],
        "seed": built["seed"],
        "preassigned_test": built["preassigned_test"],
        "split_parents": built["split_parents"],
    }
    (OUT / "splits.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    with (OUT / "manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, ["case_id", "split", "corruption_category", "transformation", "parent_utterance_id"])
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
        "preassigned_test": built["preassigned_test"],
        "multiple_slot_category": built["multiple_slot_category"],
        "same_session_limitation": "The specification table and the reference check were written in the same session. The labels are not human gold.",
    }
    (OUT / "dataset_card.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(card, indent=2))


if __name__ == "__main__":
    main()
