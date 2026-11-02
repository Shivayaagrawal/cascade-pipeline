"""Metric definitions used by the synthetic report."""

from cascadeguard.evaluation.cer import corpus_cer
from cascadeguard.evaluation.intent_metrics import exact_frame_match, semantic_error_rate
from cascadeguard.evaluation.slot_metrics import slot_scores
from cascadeguard.evaluation.wer import corpus_wer, utterance_wer


def test_wer_and_empty_reference() -> None:
    assert utterance_wer("a b c", "a x c") == pytest_approx_third()
    assert utterance_wer("", "a") is None
    summary = corpus_wer([("a b c", "a x c"), ("", "a")])
    assert summary["reference_words"] == 3
    assert summary["edits"] == 1
    assert summary["excluded_empty_reference"] == 1


def pytest_approx_third() -> float:
    return 1 / 3


def test_cer_counts_characters() -> None:
    summary = corpus_cer([("ab", "ac")])
    assert summary["reference_characters"] == 2
    assert summary["edits"] == 1


def test_slots_and_semantic_error() -> None:
    scores = slot_scores([({"date": "Tomorrow"}, {"date": "tomorrow"})])
    assert scores["f1"] == 1.0
    rows = [
        ("book_appointment", {"date": "tomorrow"}, "book_appointment", {"date": "other"}),
    ]
    assert exact_frame_match(rows) == 0.0
    assert semantic_error_rate(rows) == 1.0
    empty = slot_scores([({}, {})])
    assert empty["f1"] == 1.0
