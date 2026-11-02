"""Integrity checks for the automated annotation audit. They do not score labels."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / "data/manual_audit/annotations.csv"
PROVISIONAL = ROOT / "data/manual_audit/llm_provisional_annotations.csv"
COMPARISON = ROOT / "data/manual_audit/llm_comparison_report.json"
HUMAN_COMPARISON = ROOT / "data/manual_audit/comparison_report.json"

JUDGEMENT_FIELDS = (
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
)


def test_human_sheet_remains_pending() -> None:
    with SHEET.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 120
    assert all(row["annotation_status"] == "pending" for row in rows)
    assert all(row[field] == "" for row in rows for field in JUDGEMENT_FIELDS)
    assert "gold_intent" not in rows[0]


def test_provisional_file_is_separate_and_complete() -> None:
    with SHEET.open(newline="", encoding="utf-8") as handle:
        sheet = list(csv.DictReader(handle))
    with PROVISIONAL.open(newline="", encoding="utf-8") as handle:
        labels = list(csv.DictReader(handle))
    assert len(labels) == 120
    assert [row["candidate_id"] for row in labels] == [row["candidate_id"] for row in sheet]
    assert all(row["transcript"] == source["transcript"] for row, source in zip(labels, sheet))
    assert all(row["label_status"] == "llm_provisional" for row in labels)
    assert all(row["model_name"] == "Cursor Auto" for row in labels)
    assert all(row["prompt_version"] == "llm-audit-v1" for row in labels)
    assert all(row["annotation_order_seed"] == "20261102" for row in labels)
    assert "gold_intent" not in labels[0]
    assert "human_intent" not in labels[0]


def test_comparison_does_not_claim_human_validation() -> None:
    report = json.loads(COMPARISON.read_text(encoding="utf-8"))
    human = json.loads(HUMAN_COMPARISON.read_text(encoding="utf-8"))
    assert report["status"] == "llm_provisional_comparison_complete"
    assert report["inter_annotator_agreement"] == "not_claimed"
    assert report["rows"] == 120
    assert human["comparison_performed"] is False
    assert "not human annotations" in report["claim_boundary"]
