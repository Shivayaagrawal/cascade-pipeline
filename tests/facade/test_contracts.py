"""Contract validation."""

import pytest

from cascadeguard_facade.contracts import (
    STRATEGIES,
    CandidateBundle,
    CandidateRecord,
    InvalidBundleError,
    InvalidProvenanceError,
)


def test_five_identities_are_exact() -> None:
    assert STRATEGIES == {
        "b0_prefix",
        "b1_prefix",
        "b2_prefix_controller",
        "b1_forced_lexical",
        "b2_lexical_v3",
    }


def test_native_nbest_is_rejected() -> None:
    with pytest.raises(InvalidProvenanceError):
        CandidateRecord("c", "hello", "native_nbest", 0, "SYNTHETIC_PROXY")


def test_duplicate_candidate_ids_are_rejected() -> None:
    one = CandidateRecord("same", "a", "synthetic_edit", 0, "SYNTHETIC_PROXY")
    two = CandidateRecord("same", "b", "synthetic_edit", 1, "SYNTHETIC_PROXY")
    with pytest.raises(InvalidBundleError):
        CandidateBundle("utt-000", (one, two), "v1_injector", "SYNTHETIC_PROXY")
