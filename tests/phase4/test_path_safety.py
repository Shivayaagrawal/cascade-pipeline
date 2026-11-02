"""A retry id has to belong to the bundle that was actually supplied."""

from cascadeguard_facade.contracts import CandidateBundle, CandidateRecord
from cascadeguard_phase4.candidate_provenance import action_path_consistent


def _bundle() -> CandidateBundle:
    return CandidateBundle(
        "case",
        (
            CandidateRecord("a", "Transfer 500 rupees", "reference_passthrough", 0, "SINGLE_TRANSCRIPT"),
        ),
        "phase4_text_edit",
        "SINGLE_TRANSCRIPT",
    )


def test_retry_outside_the_bundle_is_inconsistent():
    bundle = _bundle()
    assert action_path_consistent("b2_semantic_v4", "RETRY", True, "missing", {item.candidate_id for item in bundle.ordered()}) is False
    assert action_path_consistent("b2_semantic_v4", "HOLD", False, None, {"a"}) is True
    assert action_path_consistent("b1_forced_lexical", None, False, None, {"a"}) is True
    assert action_path_consistent("b0_prefix", None, True, "a", {"a"}) is True
