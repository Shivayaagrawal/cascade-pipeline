"""Zero denominators stay null, and Wilson intervals stay inside the unit interval."""

from cascadeguard_phase4.path_safety import path_safety
from cascadeguard_phase4.phase4_metrics import proportion, summarize, wilson


def test_zero_commit_rate_is_null():
    rated = proportion(0, 0, "no committed decisions")
    assert rated["value"] is None
    assert rated["reason"] == "no committed decisions"
    rows = [
        {
            "committed": False,
            "selective_error": False,
            "unsafe_commit": False,
            "candidate_safe": False,
            "outcome": "SAFE_ABSTENTION",
            "frame_correct": False,
            "action_correct": True,
            "polarity_correct": None,
            "modality_correct": None,
            "commitment_allowed": False,
            "category": "negation_polarity",
            "expected_slots": {"date": "Friday"},
            "predicted_slots": {},
        }
    ]
    summary = summarize(rows)
    assert summary["unsafe_commit_rate"]["value"] is None
    assert summary["coverage"]["numerator"] == 0
    assert path_safety(rows)["value"] is None


def test_wilson_bounds():
    interval = wilson(0, 4)
    assert interval is not None
    assert 0 <= interval["low"] <= interval["high"] <= 1
    assert interval["high"] > 0
