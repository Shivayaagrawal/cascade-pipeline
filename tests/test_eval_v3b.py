"""Audit records for sim-eval-v3. These tests do not rewrite that experiment."""

import json
from pathlib import Path

import pytest

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard.evaluation.v3_metrics import selective_report
from cascadeguard.evaluation.v3b_audit import (
    OUTPUT_DIR_NAME,
    REQUESTED_CONDITIONS,
    ablation_table,
    assert_audit_destination,
    candidate_evidence_record,
    decision_log,
    decision_log_row,
    lexical_timing,
    log_mismatches,
    mismatches_against_frozen,
    published_slot_metrics,
)
from cascadeguard.simulation.candidate_diversity import v1_candidate_texts
from cascadeguard.simulation.utterance_generator import Utterance, generate_utterances

ROOT = Path(__file__).resolve().parents[1]


def _lexicon():
    return lexicon_from_utterances(generate_utterances())


def test_negation_and_uncertainty_stay_unavailable() -> None:
    record = candidate_evidence_record("do not transfer 500 rupees maybe", _lexicon())
    assert "transfer_money" in record["intent_evidence"]
    assert record["slot_evidence"]["amount"] == ["500"]
    assert record["negation_evidence"]["available"] is False
    assert record["uncertainty_evidence"]["available"] is False
    assert "present" not in record["negation_evidence"]
    assert "present" not in record["uncertainty_evidence"]


def test_wrong_commit_is_unsafe_and_retry_is_not_scored_as_success() -> None:
    utterance = Utterance(
        "utt-x",
        "transfer_money",
        "Transfer 500 rupees",
        {"amount": "500", "currency": "rupees"},
    )
    row = decision_log_row(utterance, ["transfer of 750 in rupees"], _lexicon())
    assert row["selected_action"] == "CONTINUE"
    assert row["expected_action"] == "CLARIFY"
    assert row["safety_outcome"]["action_matches_expected"] is False
    assert row["safety_outcome"]["committed"] is True
    assert row["safety_outcome"]["frame_matches_reference"] is False
    assert row["safety_outcome"]["unsafe_decision"] is True
    assert row["safety_outcome"]["slot_critical_unsafe"] is True
    assert row["safety_outcome"]["recovery_improved_semantic_correctness"]["available"] is False


def test_abstention_is_not_an_unsafe_decision() -> None:
    utterance = Utterance(
        "utt-x",
        "transfer_money",
        "Transfer 500 rupees",
        {"amount": "500", "currency": "rupees"},
    )
    row = decision_log_row(utterance, ["transfer of missing in rupees"], _lexicon())
    assert row["selected_action"] == "CLARIFY"
    assert row["expected_action"] == "CLARIFY"
    assert row["safety_outcome"]["committed"] is False
    assert row["safety_outcome"]["unsafe_decision"] is False
    assert row["safety_outcome"]["frame_matches_reference"] is None
    assert row["safety_outcome"]["action_matches_expected"] is True


def test_slot_metrics_publish_precision_recall_and_f1() -> None:
    utterances = generate_utterances()
    grouped = v1_candidate_texts(utterances, 17)
    selective = selective_report(utterances, grouped, _lexicon())
    published = published_slot_metrics(selective)
    for name in (
        "b1_selector_all_inputs",
        "forced_selector_all_inputs",
        "selective_all_inputs_abstention_is_empty_prediction",
        "selective_committed_decisions_only",
    ):
        block = published[name]
        assert block["precision"] is not None
        assert block["recall"] is not None
        assert block["f1"] is not None
        assert block["precision_denominator"] == "predicted_pairs"
        assert block["recall_denominator"] == "reference_pairs"


def test_timing_is_lexical_processing_only() -> None:
    utterances = generate_utterances()[:2]
    grouped = v1_candidate_texts(utterances, 17)
    timing = lexical_timing(utterances, grouped, _lexicon())
    assert timing["measure"] == "lexical_processing_only"
    assert timing["asr_latency"] is False
    assert timing["audio_decoded"] is False
    assert timing["assess_seconds"]["n"] == 2
    assert timing["recovery_action_seconds"]["n"] == 2
    assert timing["what_was_timed"].endswith("This is not ASR latency.")


def test_ablation_maps_six_names_without_a_new_selector() -> None:
    utterances = generate_utterances()[:1]
    selective = selective_report(utterances, v1_candidate_texts(utterances, 17), _lexicon())
    table = ablation_table(selective, frozen_recovery=None)
    names = [row["requested_condition"] for row in table["rows"]]
    assert names == list(REQUESTED_CONDITIONS)
    assert table["not_a_new_performance_experiment"] is True
    by_name = {row["requested_condition"]: row for row in table["rows"]}
    assert by_name["semantic_evidence_preservation_disabled"]["distinct_from_another_row"] is False
    assert by_name["slot_aware_selection_disabled"]["same_implementation_as"] == (
        "existing_baseline_candidate_selection"
    )
    assert by_name["full_synthetic_v3"]["same_recomputed_call_as"] == "recovery_disabled"
    assert by_name["full_synthetic_v3"]["cited_recovery_condition_not_recomputed"] is None
    assert by_name["selective_prediction_disabled"]["implementation"].endswith("forced_selection")


def test_decision_log_matches_frozen_v1_aggregate() -> None:
    frozen = json.loads((ROOT / "experiments" / "sim-eval-v3" / "report.json").read_text(encoding="utf-8"))
    utterances = generate_utterances()
    grouped = v1_candidate_texts(utterances, 17)
    lexicon = _lexicon()
    selective = selective_report(utterances, grouped, lexicon)
    assert mismatches_against_frozen(selective, frozen["selector_comparison"]["v1_injector"]) == []
    rows = decision_log(utterances, grouped, lexicon)
    assert [row["utterance_id"] for row in rows] == [f"utt-{index:03d}" for index in range(200)]
    assert log_mismatches(rows, selective) == []
    candidates = [
        item
        for row in rows
        for item in row["triggering_evidence"]["candidates"]
    ]
    assert all(item["negation_evidence"]["available"] is False for item in candidates)
    assert all(item["uncertainty_evidence"]["available"] is False for item in candidates)


def test_output_directory_cannot_be_v3() -> None:
    assert OUTPUT_DIR_NAME == "sim-eval-v3b"
    assert_audit_destination(Path("/tmp/sim-eval-v3b"))
    with pytest.raises(ValueError):
        assert_audit_destination(Path("/tmp/sim-eval-v3"))
