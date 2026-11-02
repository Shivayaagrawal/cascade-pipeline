"""NLU and B0/B1/B2 behaviour on the synthetic grammar."""

import pytest

from cascadeguard.asr.base import Hypothesis, NATIVE_NBEST, SYNTHETIC_EDIT
from cascadeguard.asr.whisper_adapter import WhisperAdapter
from cascadeguard.nlu.intent_classifier import classify_intent
from cascadeguard.nlu.slot_extractor import extract_slots
from cascadeguard.pipeline import run_b0, run_b1, run_b2
from cascadeguard.simulation.utterance_generator import generate_utterances


def test_clean_templates_match_gold() -> None:
    for utterance in generate_utterances():
        prediction = classify_intent(utterance.text)
        assert prediction.ambiguous is False
        assert prediction.intent == utterance.intent
        assert extract_slots(prediction.intent, utterance.text) == utterance.slots


def test_ambiguous_and_incorrect_labels() -> None:
    ambiguous = classify_intent(
        "Book an appointment for tomorrow What is my account balance?"
    )
    assert ambiguous.ambiguous is True
    assert ambiguous.intent is None
    incorrect = classify_intent("The warehouse is closed today")
    assert incorrect.intent is None
    assert incorrect.ambiguous is False


def test_b1_rejects_native_nbest_label() -> None:
    hypotheses = (Hypothesis("Book an appointment for tomorrow", NATIVE_NBEST, 0),)
    with pytest.raises(ValueError):
        run_b1("utt-000", hypotheses)


def test_b0_b1_b2_do_not_need_gold() -> None:
    original = Hypothesis("Book an appointment for tomorrow", SYNTHETIC_EDIT, 0)
    broken = Hypothesis("Book banana tomorrow", SYNTHETIC_EDIT, 1)
    b0 = run_b0("utt-000", broken)
    assert b0.intent is None
    b1 = run_b1("utt-000", (broken, original))
    assert b1.intent == "book_appointment"
    assert b1.slots == {"date": "tomorrow"}
    output, decision = run_b2("utt-000", broken, (original,))
    assert decision.action.value == "RETRY"
    assert output.intent == "book_appointment"


def test_b2_clarify_and_hold() -> None:
    ambiguous = Hypothesis(
        "Book an appointment for tomorrow What is my account balance?",
        SYNTHETIC_EDIT,
        0,
    )
    _, clarify = run_b2("utt-000", ambiguous, ())
    assert clarify.action.value == "CLARIFY"
    unknown = Hypothesis("The warehouse is closed today", SYNTHETIC_EDIT, 0)
    _, hold = run_b2("utt-001", unknown, ())
    assert hold.action.value == "HOLD"


def test_whisper_adapter_does_not_download_when_missing() -> None:
    adapter = WhisperAdapter("tiny")
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        with pytest.raises(RuntimeError, match="not installed"):
            adapter.transcribe("missing.aiff")
    else:
        pytest.skip("faster-whisper is installed; model download is out of scope")
