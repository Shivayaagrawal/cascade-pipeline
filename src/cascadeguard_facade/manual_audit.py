"""Draw a text-audit sample from the frozen synthetic files. Does not edit them."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

from cascadeguard.simulation.utterance_generator import INTENTS

SAMPLING_SEED = 20261102
ANNOTATION_FIELDS = (
    "utterance_id",
    "candidate_id",
    "transcript",
    "human_intent",
    "human_slots",
    "negation_present",
    "uncertainty_present",
    "temporal_expression",
    "numerical_expression",
    "semantic_completeness",
    "semantic_ambiguity",
    "coreference_dependency",
    "commit_safety",
    "annotation_confidence",
    "annotator_id",
    "annotation_notes",
    "annotation_status",
)


def parse_slots(text: str) -> dict[str, str]:
    if not text.strip():
        return {}
    slots: dict[str, str] = {}
    for part in text.split("|"):
        name, value = part.split("=", 1)
        slots[name] = value
    return slots


def load_tables(manifest_path: Path, variants_path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    with manifest_path.open(newline="") as handle:
        gold = list(csv.DictReader(handle))
    with variants_path.open(newline="") as handle:
        variants = list(csv.DictReader(handle))
    return gold, variants


def select_ids(
    gold: list[dict[str, str]],
    seed: int = SAMPLING_SEED,
    per_intent: int = 3,
) -> dict[str, list[str]]:
    """Three ids per intent. Ids are sorted before sampling so the seed is stable."""

    strata, _rng = draw_sample(gold, seed, per_intent)
    return strata


def draw_sample(
    gold: list[dict[str, str]],
    seed: int = SAMPLING_SEED,
    per_intent: int = 3,
) -> tuple[dict[str, list[str]], random.Random]:
    """Draw strata and return the same generator so later shuffles continue it."""

    rng = random.Random(seed)
    chosen: dict[str, list[str]] = {}
    by_intent: dict[str, list[str]] = {intent: [] for intent in INTENTS}
    for row in gold:
        by_intent[row["intent"]].append(row["utterance_id"])
    for intent in INTENTS:
        pool = sorted(by_intent[intent])
        if len(pool) < per_intent:
            raise ValueError(f"{intent} has {len(pool)} utterances, need {per_intent}.")
        chosen[intent] = rng.sample(pool, per_intent)
    return chosen, rng


def build_rows(
    gold: list[dict[str, str]],
    variants: list[dict[str, str]],
    strata: dict[str, list[str]],
    rng: random.Random,
) -> tuple[list[dict[str, str]], list[str]]:
    """Gold text plus every variants.csv row for the selected ids.

    `rng` must be the generator returned by `draw_sample` after the strata draws.
    """

    selected = [utterance_id for intent in INTENTS for utterance_id in strata[intent]]
    gold_by_id = {row["utterance_id"]: row for row in gold}
    grouped: dict[str, list[dict[str, str]]] = {utterance_id: [] for utterance_id in selected}
    for row in variants:
        if row["utterance_id"] in grouped:
            grouped[row["utterance_id"]].append(row)
    items: list[dict[str, str]] = []
    for utterance_id in selected:
        source = gold_by_id[utterance_id]
        items.append(
            {
                "utterance_id": utterance_id,
                "candidate_id": f"{utterance_id}-gold",
                "transcript": source["text"],
                "row_kind": "gold",
            }
        )
        for variant in grouped[utterance_id]:
            items.append(
                {
                    "utterance_id": utterance_id,
                    "candidate_id": variant["variant_id"],
                    "transcript": variant["text"],
                    "row_kind": "variant",
                }
            )
    order = list(range(len(items)))
    rng.shuffle(order)
    presented = [items[index] for index in order]
    return presented, selected


def annotation_row(item: dict[str, str]) -> dict[str, str]:
    row = {field: "" for field in ANNOTATION_FIELDS}
    row["utterance_id"] = item["utterance_id"]
    row["candidate_id"] = item["candidate_id"]
    row["transcript"] = item["transcript"]
    row["annotation_status"] = "pending"
    return row


def write_audit(
    destination: Path,
    manifest_path: Path,
    variants_path: Path,
    seed: int = SAMPLING_SEED,
) -> dict[str, object]:
    """Write derived audit files. The source paths are opened read-only."""

    gold, variants = load_tables(manifest_path, variants_path)
    strata, rng = draw_sample(gold, seed)
    presented, selected = build_rows(gold, variants, strata, rng)
    destination.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for row in variants:
        if row["utterance_id"] in set(selected):
            counts[row["utterance_id"]] = counts.get(row["utterance_id"], 0) + 1
    manifest = {
        "dataset": "synthetic-seed17-v1",
        "seed": seed,
        "method": (
            "One random.Random(seed). For each intent in utterance_generator.INTENTS "
            "order, sort utterance ids and draw 3 with sample. The same generator "
            "then shuffles annotation presentation order."
        ),
        "per_intent": 3,
        "intent_order": list(INTENTS),
        "strata": strata,
        "utterance_ids": selected,
        "variant_counts": counts,
        "gold_rows": len(selected),
        "variant_rows": sum(counts.values()),
        "annotation_rows": len(presented),
        "source_files": [str(manifest_path), str(variants_path)],
        "gold_hidden_from_annotation_sheet": True,
        "audio": "not_used",
    }
    (destination / "sampling_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    with (destination / "annotations.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ANNOTATION_FIELDS)
        writer.writeheader()
        for item in presented:
            writer.writerow(annotation_row(item))
    gold_by_id = {row["utterance_id"]: row for row in gold}
    sealed = {
        "warning": "Do not open this file while annotating. It holds gold labels for a later comparison.",
        "rows": [
            {
                "utterance_id": utterance_id,
                "gold_intent": gold_by_id[utterance_id]["intent"],
                "gold_slots": gold_by_id[utterance_id]["slots"],
                "gold_text": gold_by_id[utterance_id]["text"],
            }
            for utterance_id in selected
        ],
    }
    (destination / "sealed_gold.json").write_text(
        json.dumps(sealed, indent=2) + "\n",
        encoding="utf-8",
    )
    comparison = {
        "status": "pending_human_annotation",
        "comparison_performed": False,
        "reason": (
            "Annotation fields are pending. Gold labels were not compared and were "
            "not written into annotations.csv."
        ),
        "single_annotator": True,
        "inter_annotator_agreement": "not_claimed",
        "audio_reviewed": "not_applicable_text_audit",
        "selected_utterances": len(selected),
        "annotation_rows": len(presented),
        "seed": seed,
        "disagreements": None,
    }
    (destination / "comparison_report.json").write_text(
        json.dumps(comparison, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest
