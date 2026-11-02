"""Router accepts only the five identities."""

import pytest

from cascadeguard_facade.contracts import CandidateBundle, CandidateRecord, UnknownStrategyError
from cascadeguard_facade.router import route


def test_unknown_strategy_is_rejected() -> None:
    bundle = CandidateBundle(
        "utt-000",
        (CandidateRecord("c0", "hello", "synthetic_edit", 0, "SYNTHETIC_PROXY"),),
        "v1_injector",
        "SYNTHETIC_PROXY",
    )
    with pytest.raises(UnknownStrategyError):
        route("b3_new_selector", bundle)


def test_route_records_provenance() -> None:
    bundle = CandidateBundle(
        "utt-000",
        (CandidateRecord("c0", "Book an appointment for tomorrow", "synthetic_edit", 0, "SYNTHETIC_PROXY"),),
        "v1_injector",
        "SYNTHETIC_PROXY",
    )
    record = route("b0_prefix", bundle, gold_intent="book_appointment", gold_slots={"date": "tomorrow"})
    assert record.candidate_provenance == ("synthetic_edit",)
    assert record.evaluation is not None
    assert record.evaluation.exact_frame is True
    assert record.raw is not record.normalized
