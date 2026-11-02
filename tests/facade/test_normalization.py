"""Commit rules. Raw text on CLARIFY and HOLD is not a committed frame."""

from cascadeguard_facade.adapters import b2_lexical_v3, b2_prefix_controller
from cascadeguard_facade.contracts import CandidateBundle, CandidateRecord
from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances


def _bundle(*texts: str) -> CandidateBundle:
    records = tuple(
        CandidateRecord(f"c{index}", text, "synthetic_edit", index, "SYNTHETIC_PROXY")
        for index, text in enumerate(texts)
    )
    return CandidateBundle("utt-000", records, "v1_injector", "SYNTHETIC_PROXY")


def test_prefix_hold_keeps_raw_text_and_commits_nothing() -> None:
    raw, normalized = b2_prefix_controller.execute(_bundle("hello there"))
    assert raw.action == "HOLD"
    assert raw.text == "hello there"
    assert normalized.action == "HOLD"
    assert normalized.committed_frame is None
    assert normalized.answered_frame is None


def test_prefix_clarify_does_not_commit() -> None:
    text = "What is my savings account balance? Book an appointment for tomorrow"
    raw, normalized = b2_prefix_controller.execute(_bundle(text))
    assert raw.action == "CLARIFY"
    assert raw.text == text
    assert normalized.committed_frame is None


def test_prefix_retry_commits_the_alternative() -> None:
    raw, normalized = b2_prefix_controller.execute(
        _bundle("hello there", "Book an appointment for tomorrow")
    )
    assert raw.action == "RETRY"
    assert normalized.committed_frame is not None
    assert normalized.committed_frame.intent == "book_appointment"
    assert normalized.retry_mechanism is None


def test_incomplete_lexical_evidence_does_not_commit() -> None:
    lexicon = lexicon_from_utterances()
    raw, normalized = b2_lexical_v3.execute(
        _bundle("Book an appointment"),
        lexicon,
    )
    assert raw.invoked is True
    assert raw.action in {"CLARIFY", "HOLD"}
    assert normalized.committed_frame is None


def test_lexical_clarify_does_not_invent_a_question() -> None:
    lexicon = lexicon_from_utterances()
    raw, normalized = b2_lexical_v3.execute(
        _bundle("Book an appointment for someday"),
        lexicon,
    )
    assert raw.action == "CLARIFY"
    assert normalized.committed_frame is None
    assert "question" not in raw.reason
