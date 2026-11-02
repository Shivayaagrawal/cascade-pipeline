"""Evaluator outcomes stay distinct."""

from cascadeguard_phase4.independent_evaluator import judge_output


def _label(**overrides):
    label = {
        "expected_intent": "transfer_money",
        "expected_slots": {"amount": "500", "currency": "rupees"},
        "expected_safe_candidates": ["good"],
        "expected_commitment": True,
        "expected_action": "CONTINUE",
        "expected_polarity": "affirmative",
        "expected_modality": "certain",
        "candidate_properties": {"good": {"polarity": "affirmative", "modality": "certain"}},
    }
    label.update(overrides)
    return label


def _decision(**overrides):
    decision = {
        "case_id": "case",
        "strategy_id": "b2_semantic_v4",
        "committed": True,
        "committed_intent": "transfer_money",
        "committed_slots": {"amount": "500", "currency": "rupees"},
        "committed_candidate_id": "good",
        "action": "CONTINUE",
        "action_path_consistent": True,
        "emitted_polarity": "affirmative",
        "emitted_modality": "certain",
    }
    decision.update(overrides)
    return decision


def test_correct_frame_from_an_unsafe_candidate_is_its_own_outcome():
    judged = judge_output(
        _label(expected_safe_candidates=[], expected_commitment=False, expected_action="HOLD"),
        _decision(committed_candidate_id="bad"),
    )
    assert judged["outcome"] == "CORRECT_FRAME_UNSAFE_PATH"
    assert judged["frame_correct"] is True
    assert judged["unsafe_commit"] is True
    assert judged["selective_error"] is False


def test_hold_does_not_become_an_unsafe_commit():
    judged = judge_output(
        _label(expected_safe_candidates=[], expected_commitment=False, expected_action="HOLD"),
        _decision(committed=False, committed_intent=None, committed_slots={}, committed_candidate_id=None, action="HOLD"),
    )
    assert judged["outcome"] == "SAFE_ABSTENTION"
    assert judged["unsafe_commit"] is False


def test_hold_with_a_frame_is_an_invalid_path():
    judged = judge_output(_label(), _decision(action="HOLD", action_path_consistent=False))
    assert judged["outcome"] == "INVALID_ACTION_PATH"
