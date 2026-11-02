"""Which information each condition is allowed to see.

Oracle fields never enter a controller. The reference is a separate object.
"""

from __future__ import annotations

CANDIDATE_KEYS = ("candidate_id", "text", "provenance", "rank")
BUNDLE_KEYS = ("bundle_id", "candidates")

CONTRACT = (
    {"item": "candidate_text", "candidate_only": True, "critical_slot_reference": True, "full_referent": True, "oracle_only": False},
    {"item": "candidate_id", "candidate_only": True, "critical_slot_reference": True, "full_referent": True, "oracle_only": False},
    {"item": "candidate_provenance", "candidate_only": True, "critical_slot_reference": True, "full_referent": True, "oracle_only": False},
    {"item": "slots_read_from_candidate", "candidate_only": True, "critical_slot_reference": True, "full_referent": True, "oracle_only": False},
    {"item": "critical_slot_reference", "candidate_only": False, "critical_slot_reference": True, "full_referent": True, "oracle_only": False},
    {"item": "parent_transcript", "candidate_only": False, "critical_slot_reference": False, "full_referent": True, "oracle_only": False},
    {"item": "expected_action", "candidate_only": False, "critical_slot_reference": False, "full_referent": False, "oracle_only": True},
    {"item": "expected_commit", "candidate_only": False, "critical_slot_reference": False, "full_referent": False, "oracle_only": True},
    {"item": "expected_candidate_path", "candidate_only": False, "critical_slot_reference": False, "full_referent": False, "oracle_only": True},
)


def stripped_bundle(case: dict[str, object]) -> dict[str, object]:
    """Candidate-visible fields only. Reference and oracle keys are dropped."""

    return {
        "bundle_id": str(case["candidate_bundle_id"]),
        "candidates": [
            {
                "candidate_id": str(item["candidate_id"]),
                "text": str(item["text"]),
                "provenance": str(item["provenance"]),
                "rank": int(item["rank"]),
            }
            for item in case["candidates"]
        ],
    }
