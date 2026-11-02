"""v4 evidence, diagnosis, risk gates, and the separate controller."""

import pytest

from cascadeguard.evaluation.semantic_evidence import assess, lexicon_from_utterances
from cascadeguard_facade.commit_policy_v4 import PolicySwitches
from cascadeguard_facade.contracts import STRATEGIES, CandidateBundle, CandidateRecord, UnknownStrategyError
from cascadeguard_facade.failure_diagnosis_v4 import diagnose_failure
from cascadeguard_facade.phase3_registry import route_phase3
from cascadeguard_facade.risk_assessment_v4 import weight_grid
from cascadeguard_facade.router import route
from cascadeguard_facade.semantic_evidence_v4 import assess_v4

WEIGHTS = {"intent": 0.0, "slot": 0.0, "polarity": 0.0, "ambiguity": 0.0, "contradiction": 1.0}


def _bundle(*texts: str) -> CandidateBundle:
    records = tuple(
        CandidateRecord(f"c{index}", text, "synthetic_edit", index, "SYNTHETIC_PROXY")
        for index, text in enumerate(texts)
    )
    return CandidateBundle("utt-x", records, "phase3_transform", "SYNTHETIC_PROXY")


def test_assess_v4_keeps_unknown_distinct_from_negative() -> None:
    lexicon = lexicon_from_utterances()
    unknown = assess_v4("c", "The warehouse is closed today", "synthetic_edit", lexicon)
    negated = assess_v4("c", "Book not an appointment for Monday", "synthetic_edit", lexicon)
    hedged = assess_v4("c", "Maybe Book an appointment for Monday", "synthetic_edit", lexicon)
    assert unknown.polarity == "unknown"
    assert unknown.modality == "unknown"
    assert negated.polarity == "negative"
    assert negated.intent_hypotheses == ("book_appointment",)
    assert hedged.modality == "uncertain"
    assert assess("Book not an appointment for Monday", lexicon).intents == ("book_appointment",)


def test_weather_it_is_not_context_but_that_is() -> None:
    lexicon = lexicon_from_utterances()
    weather = assess_v4("c", "Will it rain Friday?", "synthetic_edit", lexicon)
    referred = assess_v4("c", "Will it rain that?", "synthetic_edit", lexicon)
    assert weather.context_dependencies == ()
    assert "that" in referred.context_dependencies
    assert referred.evidence_spans


def test_negation_holds_and_retry_needs_an_alternate() -> None:
    lexicon = lexicon_from_utterances()
    held = route_phase3("b2_semantic_v4", _bundle("Book not an appointment for Monday"), lexicon, weights=WEIGHTS, threshold=0.25)
    retried = route_phase3(
        "b2_semantic_v4",
        _bundle("Book not an appointment for Monday", "Book an appointment for Monday"),
        lexicon,
        weights=WEIGHTS,
        threshold=0.25,
    )
    assert held.action == "HOLD"
    assert held.reason == "POLARITY_CONFLICT"
    assert held.committed_intent is None
    assert retried.action == "RETRY"
    assert retried.committed_intent == "book_appointment"
    assert retried.committed_slots == (("date", "Monday"),)


def test_contradiction_and_ambiguity_do_not_commit() -> None:
    lexicon = lexicon_from_utterances()
    conflict = route_phase3(
        "b2_semantic_v4",
        _bundle("Will it rain Friday?", "Will it rain Monday?"),
        lexicon,
        weights=WEIGHTS,
        threshold=0.25,
    )
    ambiguous = route_phase3(
        "b2_semantic_v4",
        _bundle("Play jazz music What is my account balance?"),
        lexicon,
        weights=WEIGHTS,
        threshold=0.25,
    )
    assert conflict.action == "HOLD"
    assert conflict.reason == "CRITICAL_SLOT_CONFLICT"
    assert conflict.committed_intent is None
    assert ambiguous.action == "CLARIFY"
    assert ambiguous.committed_intent is None


def test_zero_weights_do_not_override_a_polarity_gate() -> None:
    lexicon = lexicon_from_utterances()
    result = route_phase3(
        "b2_semantic_v4",
        _bundle("Book not an appointment for Monday"),
        lexicon,
        weights={name: 0.0 for name in WEIGHTS},
        threshold=1.0,
    )
    assert result.action == "HOLD"
    assert result.committed_intent is None


def test_empty_bundle_does_not_assess(monkeypatch) -> None:
    def fail(*_args, **_kwargs):
        raise AssertionError("assess_v4 was called")

    monkeypatch.setattr("cascadeguard_facade.semantic_controller_v4.assess_v4", fail)
    result = route_phase3(
        "b2_semantic_v4",
        CandidateBundle("utt-x", (), "phase3_transform", "SYNTHETIC_PROXY"),
        {},
        weights=WEIGHTS,
        threshold=0.25,
    )
    assert result.action == "HOLD"
    assert result.reason == "EMPTY_BUNDLE"
    assert result.raw["invoked_processors"] is False


def test_phase2_registry_rejects_the_new_identity() -> None:
    assert "b2_semantic_v4" not in STRATEGIES
    with pytest.raises(UnknownStrategyError):
        route("b2_semantic_v4", _bundle("Play jazz music"))


def test_weight_grid_is_a_simplex() -> None:
    grids = weight_grid()
    assert len(grids) == 70
    assert all(abs(sum(item.values()) - 1.0) < 1e-9 for item in grids)
    assert all(min(item.values()) >= 0 for item in grids)


def test_diagnosis_can_carry_two_labels() -> None:
    lexicon = lexicon_from_utterances()
    assessment = assess_v4("c", "Book not an appointment for other", "synthetic_edit", lexicon)
    diagnosis = diagnose_failure((assessment,))
    assert "NEGATION_SHIFT" in diagnosis.labels
    assert "SLOT_VALUE_CORRUPTION" in diagnosis.labels
    assert diagnosis.checks_performed is True


def test_ablation_can_commit_a_negated_frame() -> None:
    lexicon = lexicon_from_utterances()
    result = route_phase3(
        "b2_semantic_v4",
        _bundle("Book not an appointment for Monday"),
        lexicon,
        weights=WEIGHTS,
        threshold=0.25,
        switches=PolicySwitches(polarity=False),
    )
    assert result.action == "CONTINUE"
    assert result.committed_intent == "book_appointment"
