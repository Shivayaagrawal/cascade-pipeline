"""Select a candidate without reading gold labels."""

from __future__ import annotations

from dataclasses import dataclass

from cascadeguard.asr.base import Hypothesis, NATIVE_NBEST, SYNTHETIC_EDIT
from cascadeguard.nlu.intent_classifier import classify_intent
from cascadeguard.nlu.slot_extractor import extract_slots


@dataclass(frozen=True)
class ScoredCandidate:
    hypothesis: Hypothesis
    intent: str | None
    slots: dict[str, str]
    ambiguous: bool
    confidence: float


def score_hypothesis(hypothesis: Hypothesis) -> ScoredCandidate:
    """Score a transcript from cues only. Gold intent is not an input."""

    if hypothesis.provenance == NATIVE_NBEST and hypothesis.text.startswith("SYNTHETIC:"):
        raise ValueError("A synthetic marker cannot be labeled native_nbest")
    prediction = classify_intent(hypothesis.text)
    slots = {} if prediction.ambiguous else extract_slots(prediction.intent, hypothesis.text)
    if prediction.ambiguous or prediction.intent is None:
        confidence = 0.0
    elif not slots and prediction.intent in {"book_appointment", "transfer_money", "play_music"}:
        confidence = 0.5
    else:
        confidence = 1.0
    return ScoredCandidate(hypothesis, prediction.intent, slots, prediction.ambiguous, confidence)


def select_candidate(hypotheses: tuple[Hypothesis, ...]) -> ScoredCandidate:
    """Prefer a confident parse, then the earlier rank. Do not use gold labels."""

    if not hypotheses:
        raise ValueError("Candidate list is empty")
    for hypothesis in hypotheses:
        if hypothesis.provenance == NATIVE_NBEST:
            continue
        if hypothesis.provenance != SYNTHETIC_EDIT and hypothesis.provenance != "reference_passthrough":
            if hypothesis.provenance == NATIVE_NBEST:
                raise ValueError("Synthetic comparison cannot relabel provenance")
    scored = [score_hypothesis(hypothesis) for hypothesis in hypotheses]
    scored.sort(key=lambda item: (-item.confidence, item.hypothesis.rank))
    return scored[0]


def assert_synthetic_not_nbest(hypotheses: tuple[Hypothesis, ...]) -> None:
    """Fail if a synthetic_edit row was renamed to native_nbest."""

    for hypothesis in hypotheses:
        if hypothesis.provenance == NATIVE_NBEST:
            raise ValueError(
                "native_nbest is reserved for an ordered list returned by a recognizer"
            )
