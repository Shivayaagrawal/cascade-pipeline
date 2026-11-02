"""Upper bound inside a fixed candidate list. The gold transcript is not added."""

from __future__ import annotations

from cascadeguard.candidates.candidate_manager import ScoredCandidate
from cascadeguard.evaluation.intent_metrics import frames_equal
from cascadeguard.evaluation.rates import rate
from cascadeguard.evaluation.slot_metrics import slot_scores


def _slot_f1(reference: dict[str, str], predicted: dict[str, str]) -> float:
    scores = slot_scores([(reference, predicted)])
    f1 = scores["f1"]
    if f1 is None:
        return -1.0
    return float(f1)


def oracle_summary(
    rows: list[tuple[str, dict[str, str], tuple[ScoredCandidate, ...]]],
) -> dict[str, object]:
    """Score whether any supplied candidate, after NLU, keeps intent, slots, or the frame.

    `rows` items are (gold intent, gold slots, scored candidates). Selection of the
    slot-oracle candidate uses gold slot overlap. The controller never calls this.
    """

    intent_hits = 0
    frame_hits = 0
    chosen: list[tuple[dict[str, str], dict[str, str]]] = []
    no_frame = 0
    for gold_intent, gold_slots, candidates in rows:
        if any(item.intent == gold_intent for item in candidates):
            intent_hits += 1
        framed = [
            item
            for item in candidates
            if frames_equal(gold_intent, gold_slots, item.intent, item.slots)
        ]
        if framed:
            frame_hits += 1
        else:
            no_frame += 1
        if candidates:
            best = max(
                candidates,
                key=lambda item: (_slot_f1(gold_slots, item.slots), item.intent == gold_intent),
            )
            chosen.append((gold_slots, best.slots))
    count = len(rows)
    return {
        "candidate_oracle_intent_accuracy": rate(
            intent_hits, count, "no utterances"
        ),
        "candidate_oracle_slot_f1": slot_scores(chosen) if chosen else None,
        "complete_frame_oracle_coverage": rate(frame_hits, count, "no utterances"),
        "utterances_with_no_recoverable_frame": no_frame,
        "gold_transcript_included": False,
    }
