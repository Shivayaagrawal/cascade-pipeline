"""Phase 1C annotation contracts. Fixtures are not LibriSpeech labels."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pytest

from annotation.validate_annotations import load_rows, validate_rows
from cascadeguard.dataset.sampling import order_utterances

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data" / "librispeech" / "annotations" / "phase_1c_pilot_30.csv"
DEV_SAMPLE = ROOT / "data" / "librispeech" / "processed" / "dev-clean" / "sample-200.csv"
TEST_SAMPLE = ROOT / "data" / "librispeech" / "processed" / "test-clean" / "sample-200.csv"


def _ids(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [row["utterance_id"] for row in csv.DictReader(handle)]


def _source() -> dict[str, str]:
    with DEV_SAMPLE.open(encoding="utf-8", newline="") as handle:
        return {row["utterance_id"]: row["reference_text"] for row in csv.DictReader(handle)}


def test_pilot_is_the_first_thirty_development_utterances() -> None:
    dev_ids = _ids(DEV_SAMPLE)
    pilot = load_rows(PILOT)
    assert len(pilot) == 30
    assert [row["utterance_id"] for row in pilot] == dev_ids[:30]
    assert [row["utterance_id"] for row in pilot] == order_utterances(dev_ids, "dev-clean")[:30]
    assert {row["split"] for row in pilot} == {"dev-clean"}
    assert not (set(_ids(PILOT)) & set(_ids(TEST_SAMPLE)))


def test_unannotated_pilot_validates_and_preserves_transcripts() -> None:
    rows = load_rows(PILOT)
    problems = validate_rows(
        rows,
        development_ids=set(_ids(DEV_SAMPLE)),
        heldout_ids=set(_ids(TEST_SAMPLE)),
        source_text=_source(),
    )
    assert problems == []
    assert all(row["annotator_id"] == "not_annotated" for row in rows)
    assert all(row["audio_reviewed"] == "not_performed" for row in rows)
    assert all(row["sentence_type"] == "not_annotated" for row in rows)


def test_changed_transcript_is_rejected() -> None:
    rows = load_rows(PILOT)
    rows[0]["reference_text"] = rows[0]["reference_text"] + " EDIT"
    problems = validate_rows(
        rows,
        development_ids=set(_ids(DEV_SAMPLE)),
        heldout_ids=set(_ids(TEST_SAMPLE)),
        source_text=_source(),
    )
    assert any("reference_text differs" in problem for problem in problems)


def test_judgment_on_an_unannotated_row_is_rejected() -> None:
    rows = load_rows(PILOT)
    rows[0]["sentence_type"] = "declarative"
    problems = validate_rows(
        rows,
        development_ids=set(_ids(DEV_SAMPLE)),
        heldout_ids=set(_ids(TEST_SAMPLE)),
        source_text=_source(),
    )
    assert any("cannot contain a judgment" in problem for problem in problems)


def test_duplicate_and_heldout_and_bad_values_are_rejected() -> None:
    rows = load_rows(PILOT)
    rows[1]["utterance_id"] = rows[0]["utterance_id"]
    problems = validate_rows(
        rows,
        development_ids=set(_ids(DEV_SAMPLE)),
        heldout_ids=set(_ids(TEST_SAMPLE)),
        source_text=_source(),
    )
    assert any("duplicate" in problem for problem in problems)

    heldout = _ids(TEST_SAMPLE)[0]
    rows = load_rows(PILOT)
    rows[0]["utterance_id"] = heldout
    rows[0]["split"] = "test-clean"
    problems = validate_rows(
        rows,
        development_ids=set(_ids(DEV_SAMPLE)),
        heldout_ids=set(_ids(TEST_SAMPLE)),
        source_text=_source(),
    )
    assert any("held-out" in problem for problem in problems)

    rows = load_rows(PILOT)
    rows[0]["annotation_confidence"] = "certain"
    problems = validate_rows(
        rows,
        development_ids=set(_ids(DEV_SAMPLE)),
        heldout_ids=set(_ids(TEST_SAMPLE)),
        source_text=_source(),
    )
    assert any("annotation_confidence" in problem for problem in problems)

    rows = load_rows(PILOT)
    rows[0]["annotator_id"] = "reviewer-a"
    rows[0]["sentence_type"] = "declarative"
    rows[0]["utterance_completeness"] = "complete"
    rows[0]["proposition_summary"] = "A short gloss."
    rows[0]["semantic_coherence"] = "coherent"
    rows[0]["entities_explicitly_mentioned"] = "[]"
    rows[0]["negation_present"] = "absent"
    rows[0]["uncertainty_present"] = "absent"
    rows[0]["temporal_expression_present"] = "absent"
    rows[0]["numerical_expression_present"] = "absent"
    rows[0]["coreference_or_context_dependency"] = "none_observed"
    rows[0]["semantic_ambiguity"] = "none_observed"
    rows[0]["task_intent_status"] = "not_applicable"
    rows[0]["task_intent"] = "not_applicable"
    rows[0]["task_slots"] = "not_annotated"
    rows[0]["annotation_confidence"] = "high"
    rows[0]["audio_reviewed"] = "yes"
    assert validate_rows(
        rows,
        development_ids=set(_ids(DEV_SAMPLE)),
        heldout_ids=set(_ids(TEST_SAMPLE)),
        source_text=_source(),
    ) == []
    rows[0]["entities_explicitly_mentioned"] = "{not-json"
    problems = validate_rows(
        rows,
        development_ids=set(_ids(DEV_SAMPLE)),
        heldout_ids=set(_ids(TEST_SAMPLE)),
        source_text=_source(),
    )
    assert any("not valid JSON" in problem for problem in problems)


def test_phase1c_did_not_change_simulation_hashes() -> None:
    expected = {
        "experiments/B0/summary.json": "3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee",
        "experiments/B1/summary.json": "597a2800c946018467865dfcf3d8e547bc51c10487596cc134ca2181fee695b2",
        "experiments/B2/summary.json": "34a40fdd233f5d4faa00af73c26f1afcc32c4d83922db8df57b7a7184dce0e5d",
        "artifacts/reports/simulation_report.json": "7adf69ee6ac344e7ef205099af3686ddf7cceaffa111a8789f03b83ed8319856",
        "experiments/sim-eval-v2/report.json": "74499b716103e26ef829cb56816bf738d67d3d3e5961848c4cfe37f2e8f4f77d",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
