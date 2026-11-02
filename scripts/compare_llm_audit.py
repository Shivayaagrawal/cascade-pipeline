"""Compare stored LLM provisional labels with existing gold. Does not relabel.

Gold is read only here, after llm_provisional_annotations.csv already exists.
The pending human sheet is not modified.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = ROOT / "data/manual_audit/llm_provisional_annotations.csv"
SEALED = ROOT / "data/manual_audit/sealed_gold.json"
VARIANTS = ROOT / "data/synthetic/transcripts/variants.csv"
COMPARISON = ROOT / "data/manual_audit/llm_comparison_report.json"
EXAMPLES = ROOT / "data/manual_audit/llm_disagreement_examples.json"


def parse_slots(text: str) -> dict[str, str] | str:
    if text in {"uncertain", "not_applicable"}:
        return text
    if text == "":
        return {}
    parsed: dict[str, str] = {}
    for part in text.split("|"):
        name, value = part.split("=", 1)
        parsed[name] = value
    return parsed


def slots_agree(predicted: dict[str, str] | str, gold: dict[str, str]) -> bool:
    if predicted == "not_applicable":
        return gold == {}
    if not isinstance(predicted, dict):
        return False
    return predicted == gold


def rate(numerator: int, denominator: int) -> dict[str, float | int | None]:
    if denominator == 0:
        return {"numerator": numerator, "denominator": 0, "value": None}
    return {"numerator": numerator, "denominator": denominator, "value": numerator / denominator}


def main() -> None:
    with LABELS.open(newline="", encoding="utf-8") as handle:
        labels = list(csv.DictReader(handle))
    sealed = json.loads(SEALED.read_text(encoding="utf-8"))
    gold = {row["utterance_id"]: row for row in sealed["rows"]}
    categories: dict[str, str] = {}
    with VARIANTS.open(newline="", encoding="utf-8") as handle:
        for item in csv.DictReader(handle):
            categories[item["variant_id"]] = item["category"]

    records = []
    for label in labels:
        gold_row = gold[label["utterance_id"]]
        gold_slots = parse_slots(gold_row["gold_slots"])
        if not isinstance(gold_slots, dict):
            gold_slots = {}
        predicted_slots = parse_slots(label["llm_slots"])
        kind = "gold" if label["candidate_id"].endswith("-gold") else "variant"
        category = None if kind == "gold" else categories[label["candidate_id"]]
        intent_match = label["llm_intent"] == gold_row["gold_intent"]
        slot_match = slots_agree(predicted_slots, gold_slots)
        temporal_match = None
        gold_temporal = gold_slots.get("date") or gold_slots.get("time")
        if gold_temporal:
            temporal_match = gold_temporal in label["temporal_expression"]
        amount = gold_slots.get("amount")
        numerical_match = None if amount is None else label["numerical_expression"] == amount
        records.append(
            {
                "candidate_id": label["candidate_id"],
                "utterance_id": label["utterance_id"],
                "row_kind": kind,
                "variant_category": category,
                "transcript": label["transcript"],
                "llm_intent": label["llm_intent"],
                "gold_intent": gold_row["gold_intent"],
                "intent_agreement": intent_match,
                "llm_slots": label["llm_slots"],
                "gold_slots": gold_row["gold_slots"],
                "slot_agreement": slot_match,
                "frame_agreement": intent_match and slot_match,
                "negation_present": label["negation_present"],
                "uncertainty_present": label["uncertainty_present"],
                "temporal_expression": label["temporal_expression"],
                "temporal_agreement_with_gold_date_or_time": temporal_match,
                "numerical_expression": label["numerical_expression"],
                "numerical_agreement_with_gold_amount": numerical_match,
                "semantic_completeness": label["semantic_completeness"],
                "semantic_ambiguity": label["semantic_ambiguity"],
                "coreference_dependency": label["coreference_dependency"],
                "commit_safety": label["commit_safety"],
                "annotation_confidence": label["annotation_confidence"],
                "explanation": label["explanation"],
            }
        )

    def subset(name: str, rows: list[dict[str, object]]) -> dict[str, object]:
        comparable_temporal = [row for row in rows if row["temporal_agreement_with_gold_date_or_time"] is not None]
        comparable_amount = [row for row in rows if row["numerical_agreement_with_gold_amount"] is not None]
        return {
            "rows": len(rows),
            "intent_agreement": rate(sum(row["intent_agreement"] is True for row in rows), len(rows)),
            "slot_agreement": rate(sum(row["slot_agreement"] is True for row in rows), len(rows)),
            "frame_agreement": rate(sum(row["frame_agreement"] is True for row in rows), len(rows)),
            "temporal_agreement_where_gold_has_date_or_time": rate(
                sum(row["temporal_agreement_with_gold_date_or_time"] is True for row in comparable_temporal),
                len(comparable_temporal),
            ),
            "numerical_agreement_where_gold_has_amount": rate(
                sum(row["numerical_agreement_with_gold_amount"] is True for row in comparable_amount),
                len(comparable_amount),
            ),
            "group": name,
        }

    gold_rows = [row for row in records if row["row_kind"] == "gold"]
    variant_rows = [row for row in records if row["row_kind"] == "variant"]
    by_category = {}
    for category in sorted({row["variant_category"] for row in variant_rows}):
        chosen = [row for row in variant_rows if row["variant_category"] == category]
        by_category[str(category)] = subset(str(category), chosen)

    negation_on_negation_edits = [
        row for row in variant_rows
        if row["variant_category"] == "negation_corruption"
    ]
    negation_elsewhere = [
        row for row in records
        if row["negation_present"] == "yes" and row["variant_category"] != "negation_corruption"
    ]
    ambiguity_rows = [row for row in records if row["semantic_ambiguity"] == "yes"]
    uncertain_commit = [row for row in records if row["commit_safety"] == "uncertain"]
    unsafe_commit = [row for row in records if row["commit_safety"] == "unsafe"]
    gold_disagreement = [row for row in gold_rows if row["frame_agreement"] is not True]
    medium_or_low = [row for row in records if row["annotation_confidence"] in {"medium", "low"}]

    def brief(row: dict[str, object]) -> dict[str, object]:
        return {
            "candidate_id": row["candidate_id"],
            "row_kind": row["row_kind"],
            "variant_category": row["variant_category"],
            "transcript": row["transcript"],
            "llm_intent": row["llm_intent"],
            "gold_intent": row["gold_intent"],
            "intent_agreement": row["intent_agreement"],
            "llm_slots": row["llm_slots"],
            "gold_slots": row["gold_slots"],
            "slot_agreement": row["slot_agreement"],
            "negation_present": row["negation_present"],
            "semantic_ambiguity": row["semantic_ambiguity"],
            "commit_safety": row["commit_safety"],
            "annotation_confidence": row["annotation_confidence"],
            "explanation": row["explanation"],
        }

    report = {
        "status": "llm_provisional_comparison_complete",
        "claim_boundary": (
            "These labels are LLM-generated provisional annotations. "
            "They are not human annotations and not independently validated ground truth. "
            "Agreement with synthetic gold is a consistency check, not a benchmark."
        ),
        "model_name": labels[0]["model_name"],
        "prompt_version": labels[0]["prompt_version"],
        "annotation_order_seed": labels[0]["annotation_order_seed"],
        "generated_at": labels[0]["generated_at"],
        "rows": len(records),
        "human_sheet_modified": False,
        "inter_annotator_agreement": "not_claimed",
        "audio_reviewed": "not_applicable_text_audit",
        "overall": subset("all_rows", records),
        "gold_rows": subset("gold_transcripts", gold_rows),
        "variant_rows": subset("edited_variants", variant_rows),
        "by_variant_category": by_category,
        "label_counts": {
            "negation_present": dict(Counter(row["negation_present"] for row in records)),
            "uncertainty_present": dict(Counter(row["uncertainty_present"] for row in records)),
            "semantic_ambiguity": dict(Counter(row["semantic_ambiguity"] for row in records)),
            "semantic_completeness": dict(Counter(row["semantic_completeness"] for row in records)),
            "coreference_dependency": dict(Counter(row["coreference_dependency"] for row in records)),
            "commit_safety": dict(Counter(row["commit_safety"] for row in records)),
            "annotation_confidence": dict(Counter(row["annotation_confidence"] for row in records)),
            "llm_intent": dict(Counter(row["llm_intent"] for row in records)),
        },
        "negation_against_edit_category": {
            "note": "negation_corruption is an edit tag, not a gold semantic label.",
            "negation_corruption_rows": len(negation_on_negation_edits),
            "marked_negation_yes": sum(row["negation_present"] == "yes" for row in negation_on_negation_edits),
            "negation_yes_outside_that_category": [row["candidate_id"] for row in negation_elsewhere],
        },
        "uncertainty": {
            "note": "The synthetic gold tables have no uncertainty label. 'please' was not coded as uncertainty. No row contained 'maybe'.",
            "uncertainty_yes": sum(row["uncertainty_present"] == "yes" for row in records),
        },
        "review_counts": {
            "gold_frame_disagreements": len(gold_disagreement),
            "semantic_ambiguity_yes": len(ambiguity_rows),
            "commit_uncertain": len(uncertain_commit),
            "commit_unsafe": len(unsafe_commit),
            "confidence_medium_or_low": len(medium_or_low),
        },
    }
    examples = {
        "claim_boundary": report["claim_boundary"],
        "gold_frame_disagreements": [brief(row) for row in gold_disagreement],
        "negation_yes_outside_negation_corruption": [brief(row) for row in negation_elsewhere],
        "ambiguous_rows": [brief(row) for row in ambiguity_rows],
        "uncertain_commit_rows": [brief(row) for row in uncertain_commit],
        "medium_or_low_confidence_rows": [brief(row) for row in medium_or_low],
        "unsafe_gold_rows": [brief(row) for row in gold_rows if row["commit_safety"] == "unsafe"],
        "variant_frame_disagreement_ids": [
            row["candidate_id"] for row in variant_rows if row["frame_agreement"] is not True
        ],
    }
    COMPARISON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    EXAMPLES.write_text(json.dumps(examples, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["overall"], indent=2))
    print("gold", json.dumps(report["gold_rows"], indent=2))
    print("review", report["review_counts"])
    print("negation", report["negation_against_edit_category"])
    print("categories", {key: value["frame_agreement"] for key, value in by_category.items()})


if __name__ == "__main__":
    main()
