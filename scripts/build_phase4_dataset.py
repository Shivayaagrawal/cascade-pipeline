"""Build synthetic-independent-challenge-v1 and freeze oracle labels."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cascadeguard_phase4 import CONSTRUCTION_VERSION, DATASET_ID, ORACLE_VERSION, SEED
from cascadeguard_phase4.dataset_builder import build_all
from cascadeguard_phase4.independent_oracle import judge


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    destination = ROOT / "data" / "phase4"
    destination.mkdir(parents=True, exist_ok=True)
    built = build_all(ROOT / "data" / "synthetic" / "annotations" / "annotations.jsonl")
    cases = built["cases"]
    inventory = built["inventory"]
    bundles = []
    labels = []
    referents = []
    for case in cases:
        bundles.append(
            {
                "case_id": case["case_id"],
                "parent_id": case["parent_id"],
                "case_category": case["case_category"],
                "split": case["split"],
                "transformation": case["transformation"],
                "construction_version": case["construction_version"],
                "candidate_source": case["candidate_source"],
                "generation_method": case["generation_method"],
                "candidates": case["candidates"],
            }
        )
        label = judge(case["candidates"], case["referent"], inventory)
        label["case_id"] = case["case_id"]
        label["parent_id"] = case["parent_id"]
        label["case_category"] = case["case_category"]
        label["split"] = case["split"]
        labels.append(label)
        referents.append(
            {
                "case_id": case["case_id"],
                "parent_id": case["parent_id"],
                "intent": case["referent"]["intent"],
                "slots": case["referent"]["slots"],
            }
        )
    bundle_path = destination / "candidate_bundles.jsonl"
    label_path = destination / "oracle_labels.jsonl"
    referent_path = destination / "scenario_referents.jsonl"
    for path, rows in (
        (bundle_path, bundles),
        (label_path, labels),
        (referent_path, referents),
    ):
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
    challenge = destination / "challenge_cases.csv"
    with challenge.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "parent_id",
                "case_category",
                "split",
                "transformation",
                "candidate_ids",
                "transcripts",
                "candidate_provenance",
                "construction_version",
            ],
        )
        writer.writeheader()
        for case in cases:
            writer.writerow(
                {
                    "case_id": case["case_id"],
                    "parent_id": case["parent_id"],
                    "case_category": case["case_category"],
                    "split": case["split"],
                    "transformation": case["transformation"],
                    "candidate_ids": "|".join(item["candidate_id"] for item in case["candidates"]),
                    "transcripts": " || ".join(item["text"] for item in case["candidates"]),
                    "candidate_provenance": "|".join(item["provenance"] for item in case["candidates"]),
                    "construction_version": CONSTRUCTION_VERSION,
                }
            )
    splits = {
        "seed": SEED,
        "parent_ids": built["split_parents"],
        "case_ids": {
            split: [case["case_id"] for case in cases if case["split"] == split]
            for split in ("development", "validation", "test")
        },
        "category_counts": {
            split: dict(Counter(case["case_category"] for case in cases if case["split"] == split))
            for split in ("development", "validation", "test")
        },
    }
    (destination / "splits.json").write_text(json.dumps(splits, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    counts = Counter((case["split"], case["case_category"]) for case in cases)
    parents_by_split = built["split_parents"]
    leaked = []
    seen: dict[str, str] = {}
    for split, parent_ids in parents_by_split.items():
        for parent_id in parent_ids:
            if parent_id in seen:
                leaked.append(parent_id)
            seen[parent_id] = split
    manifest = destination / "manifest.csv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["field", "value"])
        writer.writeheader()
        for field, value in (
            ("dataset_id", DATASET_ID),
            ("seed", SEED),
            ("oracle_version", ORACLE_VERSION),
            ("construction_version", CONSTRUCTION_VERSION),
            ("cases", len(cases)),
            ("eligible_parents", built["eligible_parents"]),
            ("excluded_parents", " ".join(built["excluded_parents"])),
            ("shortfalls", json.dumps(built["shortfalls"], sort_keys=True)),
            ("bundles_sha256", _sha(bundle_path)),
            ("oracle_sha256", _sha(label_path)),
            ("parent_leakage", str(bool(leaked))),
        ):
            writer.writerow({"field": field, "value": value})
    lines = [
        "# synthetic-independent-challenge-v1",
        "",
        f"Cases: {len(cases)}. Seed: {SEED}. Eligible parents: {built['eligible_parents']}.",
        f"Excluded parents, because a required slot is absent: {', '.join(built['excluded_parents']) or 'none'}.",
        f"Shortfalls: {built['shortfalls'] or 'none'}.",
        "",
        "Expected labels are only in `oracle_labels.jsonl`. Candidate bundles do not contain them.",
        "",
        "| Split | Category | Cases |",
        "| --- | --- | ---: |",
    ]
    for (split, category), count in sorted(counts.items()):
        lines.append(f"| {split} | {category} | {count} |")
    lines.extend(
        [
            "",
            "Parent ids are not shared across splits. Variants of one parent stay in that parent's split.",
            "This is a synthetic text set. It is not speech and not ASR N-best output.",
            "",
        ]
    )
    (destination / "dataset_card.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "cases": len(cases),
        "counts": built["category_counts"],
        "shortfalls": built["shortfalls"],
        "split_parents": built["split_parent_counts"],
        "leakage": leaked,
    }, indent=2))


if __name__ == "__main__":
    main()
