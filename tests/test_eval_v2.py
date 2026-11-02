"""Evaluation v2 contracts. These tests do not run the initial experiment."""

from cascadeguard.candidates.candidate_manager import ScoredCandidate
from cascadeguard.evaluation.latency_stats import summarize_seconds
from cascadeguard.evaluation.oracle import oracle_summary
from cascadeguard.evaluation.policy_eval import action_report, expected_action
from cascadeguard.evaluation.rates import rate
from cascadeguard.evaluation.slot_metrics import per_slot_scores
from cascadeguard.asr.base import SYNTHETIC_EDIT, Hypothesis


def _scored(intent: str | None, slots: dict[str, str], ambiguous: bool = False) -> ScoredCandidate:
    return ScoredCandidate(
        Hypothesis("text", SYNTHETIC_EDIT, 0),
        intent,
        slots,
        ambiguous,
        0.0 if ambiguous or intent is None else 1.0,
    )


def test_expected_action_order() -> None:
    assert expected_action(
        category="deletion",
        one_best_ambiguous=True,
        one_best_frame_ok=True,
        other_candidate_frame_ok=False,
    ) == "CLARIFY"
    assert expected_action(
        category="ambiguous_transcript",
        one_best_ambiguous=False,
        one_best_frame_ok=False,
        other_candidate_frame_ok=True,
    ) == "CLARIFY"
    assert expected_action(
        category="deletion",
        one_best_ambiguous=False,
        one_best_frame_ok=True,
        other_candidate_frame_ok=False,
    ) == "CONTINUE"
    assert expected_action(
        category="substitution",
        one_best_ambiguous=False,
        one_best_frame_ok=False,
        other_candidate_frame_ok=True,
    ) == "RETRY"
    assert expected_action(
        category="incorrect_transcript",
        one_best_ambiguous=False,
        one_best_frame_ok=False,
        other_candidate_frame_ok=False,
    ) == "HOLD"


def test_undefined_rates_are_not_zero() -> None:
    empty = rate(0, 0, "B0 had no exact-frame successes")
    assert empty["value"] is None
    assert empty["reason"] == "B0 had no exact-frame successes"
    report = action_report(
        [
            {
                "expected": "HOLD",
                "actual": "HOLD",
                "b0_frame_ok": False,
                "b2_frame_ok": False,
                "committed": False,
            }
        ]
    )
    assert report["false_recovery"]["value"] is None
    assert report["asr_decode"] is False
    assert report["retry_mechanism"] == "simulated_candidate_rescore"


def test_oracle_does_not_require_gold_text() -> None:
    summary = oracle_summary(
        [
            (
                "book_appointment",
                {"date": "tomorrow"},
                (
                    _scored("check_balance", {"account": "account"}),
                    _scored("book_appointment", {"date": "tomorrow"}),
                ),
            ),
            (
                "play_music",
                {"genre": "jazz"},
                (_scored(None, {}),),
            ),
        ]
    )
    assert summary["complete_frame_oracle_coverage"]["numerator"] == 1
    assert summary["utterances_with_no_recoverable_frame"] == 1
    assert summary["gold_transcript_included"] is False
    assert summary["candidate_oracle_intent_accuracy"]["value"] == 0.5


def test_per_slot_and_latency() -> None:
    scores = per_slot_scores(
        [
            ({"date": "Friday"}, {"date": "Friday"}),
            ({"date": "Monday"}, {"date": "other"}),
            ({}, {"date": "Friday"}),
        ]
    )
    assert scores["date"]["reference"] == 2
    assert scores["date"]["matched"] == 1
    assert scores["date"]["predicted"] == 3
    zeros = per_slot_scores([({"date": "Friday"}, {"date": "other"})])
    assert zeros["date"]["f1"] == 0.0
    stats = summarize_seconds([1, 2, 3, 4])
    assert stats["median"] == 2.5
    assert stats["p95"] == 4
    assert summarize_seconds([])["mean"] is None
