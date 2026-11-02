"""Evaluation v3 contracts. These tests do not run the v1 or v2 experiments."""

import pytest

from cascadeguard.evaluation.rates import rate
from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard.evaluation.selective import (
    RecoveryAction,
    SelectiveAction,
    decide_selective,
    recovery_action,
)
from cascadeguard.evaluation.v3_metrics import (
    expected_recovery,
    risk_coverage_curve,
    selective_report,
    slot_critical_mismatch,
)
from cascadeguard.simulation.candidate_diversity import (
    gold_is_absent,
    gold_is_not_exact,
    paraphrases,
    v1_candidate_texts,
)
from cascadeguard.simulation.utterance_generator import Utterance, generate_utterances


def _lexicon():
    return lexicon_from_utterances(generate_utterances())


def test_missing_amount_does_not_commit() -> None:
    decision = decide_selective(["transfer of missing in rupees"], _lexicon())
    assert decision.action is SelectiveAction.CLARIFY
    assert decision.slots == {}
    assert decision.reason == "intent_without_required_slots"


def test_corrupted_critical_amount_is_not_committed_when_candidates_disagree() -> None:
    lexicon = _lexicon()
    wrong_only = decide_selective(["transfer of 750 in rupees"], lexicon)
    assert wrong_only.action is SelectiveAction.COMMIT
    assert wrong_only.slots["amount"] == "750"
    gold = Utterance("utt-x", "transfer_money", "Transfer 500 rupees", {"amount": "500", "currency": "rupees"})
    assert slot_critical_mismatch(gold, wrong_only) is True
    disagreed = decide_selective(
        ["transfer of 750 in rupees", "transfer of 500 in rupees"],
        lexicon,
    )
    assert disagreed.action is SelectiveAction.CLARIFY
    assert disagreed.reason == "slot_value_disagreement"
    assert slot_critical_mismatch(gold, disagreed) is False


def test_no_intent_holds() -> None:
    decision = decide_selective(["The warehouse is closed today"], _lexicon())
    assert decision.action is SelectiveAction.HOLD
    assert decision.reason == "no_intent_evidence"


def test_every_recovery_action() -> None:
    lexicon = _lexicon()
    continue_action, continue_decision, continue_source = recovery_action(
        ["transfer of 500 in rupees", "send a transfer of 500 rupees"],
        lexicon,
    )
    assert continue_action is RecoveryAction.CONTINUE
    assert continue_decision.action is SelectiveAction.COMMIT
    assert continue_source == "primary_bundle"

    clarify_action, _, _ = recovery_action(["transfer of missing in rupees"], lexicon)
    assert clarify_action is RecoveryAction.CLARIFY

    hold_action, _, _ = recovery_action(["The warehouse is closed today"], lexicon)
    assert hold_action is RecoveryAction.HOLD

    retry_action, retry_decision, retry_source = recovery_action(
        ["transfer of missing in rupees"],
        lexicon,
        retry_candidates=["transfer of 500 in rupees"],
    )
    assert retry_action is RecoveryAction.RETRY
    assert retry_decision.slots["amount"] == "500"
    assert retry_source == "simulated_candidate_rescore"
    no_retry, _, source = recovery_action(["transfer of missing in rupees"], lexicon, retry_candidates=None)
    assert no_retry is RecoveryAction.CLARIFY
    assert source == "primary_bundle"


def test_abstention_does_not_invent_a_zero_risk() -> None:
    utterance = Utterance("utt-x", "transfer_money", "Transfer 500 rupees", {"amount": "500", "currency": "rupees"})
    report = selective_report([utterance], {"utt-x": ["The warehouse is closed today"]}, _lexicon())
    assert report["decision_coverage"]["value"] == 0
    assert report["selective_risk"]["value"] is None
    assert "not a reliability score" in report["selective_risk"]["reason"]
    assert report["accuracy_counting_abstention_as_incorrect"]["exact_frame_accuracy"]["value"] == 0
    curve = risk_coverage_curve([utterance], {"utt-x": ["The warehouse is closed today"]}, _lexicon())
    assert curve[-1]["rule"] == "always_hold"
    assert curve[-1]["selective_risk"]["value"] is None
    assert curve[-1]["decision_coverage"]["numerator"] == 0


def test_expected_actions_do_not_read_the_decision() -> None:
    gold = Utterance("utt-x", "book_appointment", "Book an appointment for tomorrow", {"date": "tomorrow"})
    assert expected_recovery(gold, ["booking request tomorrow for an appointment"]) == "CONTINUE"
    assert expected_recovery(
        gold,
        ["booking request missing for an appointment"],
        retry=["booking request tomorrow for an appointment"],
    ) == "RETRY"
    assert expected_recovery(gold, ["booking request missing for an appointment"]) == "CLARIFY"
    assert expected_recovery(gold, ["The warehouse is closed today"]) == "HOLD"


def test_zero_denominator_rate_stays_undefined() -> None:
    empty = rate(0, 0, "no CLARIFY decisions")
    assert empty["value"] is None
    assert empty["denominator"] == 0


def test_gold_transcript_stays_out_of_candidate_lists() -> None:
    rows = generate_utterances()
    assert [row.utterance_id for row in rows] == [f"utt-{index:03d}" for index in range(200)]
    assert generate_utterances()[0].text == rows[0].text
    v1 = v1_candidate_texts(rows, 17)
    for row in rows:
        assert gold_is_not_exact(row.text, v1[row.utterance_id])
        assert gold_is_absent(row.text, paraphrases(row))
        assert row.text.casefold() not in " ".join(paraphrases(row)).casefold()


def test_amount_inside_a_longer_number_is_not_a_slot() -> None:
    lexicon = _lexicon()
    decision = decide_selective(["Transfer 751 rupees"], lexicon)
    assert decision.action is SelectiveAction.CLARIFY
    assert "amount" not in decision.slots
    whole = decide_selective(["Transfer 1000 rupees"], lexicon)
    assert whole.action is SelectiveAction.COMMIT
    assert whole.slots["amount"] == "1000"


def test_support_threshold_rejects_a_single_witness() -> None:
    decision = decide_selective(["transfer of 500 in rupees"], _lexicon(), min_support=2)
    assert decision.action is SelectiveAction.CLARIFY
    assert decision.reason == "slot_support_below_threshold"
    with pytest.raises(ValueError):
        decide_selective(["transfer of 500 in rupees"], _lexicon(), min_support=0)
