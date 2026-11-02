"""Decide whether a parse is safe to keep. Injected error labels are not inputs."""

from __future__ import annotations

from enum import Enum

from cascadeguard.candidates.candidate_manager import ScoredCandidate


class FailureKind(str, Enum):
    NONE = "none"
    AMBIGUOUS = "ambiguous"
    UNKNOWN = "unknown"
    LOW_CONFIDENCE = "low_confidence"


def detect_failure(scored: ScoredCandidate) -> FailureKind:
    """Classify the parse from confidence and ambiguity only."""

    if scored.ambiguous:
        return FailureKind.AMBIGUOUS
    if scored.intent is None or scored.confidence == 0.0:
        return FailureKind.UNKNOWN
    if scored.confidence < 1.0:
        return FailureKind.LOW_CONFIDENCE
    return FailureKind.NONE
