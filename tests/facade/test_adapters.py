"""Each adapter calls the existing function for its identity."""

import pytest

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard_facade.contracts import AdapterError
from cascadeguard_facade.adapters import (
    b0_prefix,
    b1_forced_lexical,
    b1_prefix,
    b2_lexical_v3,
    b2_prefix_controller,
)
from cascadeguard_facade.contracts import CandidateBundle, CandidateRecord


def _bundle(*texts: str) -> CandidateBundle:
    records = tuple(
        CandidateRecord(f"c{index}", text, "synthetic_edit", index, "SYNTHETIC_PROXY")
        for index, text in enumerate(texts)
    )
    return CandidateBundle("utt-000", records, "v1_injector", "SYNTHETIC_PROXY")


def test_b0_uses_the_first_rank() -> None:
    raw, normalized = b0_prefix.execute(_bundle("Book an appointment for tomorrow", "hello"))
    assert raw.invoked is True
    assert raw.intent == "book_appointment"
    assert normalized.committed_frame is not None
    assert normalized.committed_frame.intent == "book_appointment"


def test_b1_prefix_selects_without_gold() -> None:
    raw, normalized = b1_prefix.execute(
        _bundle("hello", "Book an appointment for tomorrow")
    )
    assert raw.reason == "prefix_confidence_then_rank"
    assert normalized.answered_frame is not None
    assert normalized.answered_frame.intent == "book_appointment"


def test_b2_prefix_continue_on_a_clean_template() -> None:
    raw, normalized = b2_prefix_controller.execute(
        _bundle("Book an appointment for tomorrow")
    )
    assert raw.action == "CONTINUE"
    assert normalized.committed_frame is not None
    assert normalized.action == "CONTINUE"


def test_forced_lexical_is_not_a_safety_commit() -> None:
    lexicon = lexicon_from_utterances()
    raw, normalized = b1_forced_lexical.execute(
        _bundle("Book an appointment for tomorrow"),
        lexicon,
    )
    assert raw.invoked is True
    assert raw.intent == "book_appointment"
    assert normalized.committed_frame is None
    assert normalized.answered_frame is not None
    assert normalized.answered_frame.intent == "book_appointment"


def test_adapter_wraps_processor_exceptions(monkeypatch) -> None:
    def fail(*_args, **_kwargs):
        raise RuntimeError("parser unavailable")

    monkeypatch.setattr("cascadeguard_facade.adapters.b0_prefix.run_b0", fail)
    with pytest.raises(AdapterError, match="b0_prefix"):
        b0_prefix.execute(_bundle("Book an appointment for tomorrow"))


def test_lexical_retry_names_simulated_rescore() -> None:
    lexicon = lexicon_from_utterances()
    primary = _bundle("hello")
    retry = _bundle("Book an appointment for tomorrow")
    raw, normalized = b2_lexical_v3.execute(primary, lexicon, retry_bundle=retry)
    assert raw.action == "RETRY"
    assert raw.retry_mechanism == "simulated_candidate_rescore"
    assert normalized.retry_mechanism == "simulated_candidate_rescore"
    assert normalized.committed_frame is not None
    assert "decode" not in (raw.retry_mechanism or "")
