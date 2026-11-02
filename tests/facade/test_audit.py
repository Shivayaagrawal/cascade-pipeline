"""Audit records keep raw output beside the normalized decision."""

from cascadeguard_facade.contracts import CandidateBundle, CandidateRecord
from cascadeguard_facade.router import route


def test_audit_fields_are_present_for_each_identity() -> None:
    bundle = CandidateBundle(
        "utt-000",
        (
            CandidateRecord("c0", "hello there", "synthetic_edit", 0, "SYNTHETIC_PROXY"),
            CandidateRecord("c1", "Book an appointment for tomorrow", "synthetic_edit", 1, "SYNTHETIC_PROXY"),
        ),
        "v1_injector",
        "SYNTHETIC_PROXY",
    )
    for strategy in (
        "b0_prefix",
        "b1_prefix",
        "b2_prefix_controller",
        "b1_forced_lexical",
        "b2_lexical_v3",
    ):
        record = route(strategy, bundle)
        assert record.strategy == strategy
        assert record.utterance_id == "utt-000"
        assert record.candidate_ids == ("c0", "c1")
        assert record.raw.strategy == strategy
        assert record.normalized.strategy == strategy
        assert record.raw is not record.normalized
