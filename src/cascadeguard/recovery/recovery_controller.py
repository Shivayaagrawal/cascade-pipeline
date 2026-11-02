"""Bounded CONTINUE / RETRY / CLARIFY / HOLD controller."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from cascadeguard.asr.base import Hypothesis
from cascadeguard.candidates.candidate_manager import ScoredCandidate, score_hypothesis
from cascadeguard.recovery.failure_detector import FailureKind, detect_failure


class RecoveryAction(str, Enum):
    CONTINUE = "CONTINUE"
    RETRY = "RETRY"
    CLARIFY = "CLARIFY"
    HOLD = "HOLD"


@dataclass(frozen=True)
class RecoveryDecision:
    action: RecoveryAction
    selected: ScoredCandidate
    retries: int
    failure: FailureKind


def decide(
    one_best: ScoredCandidate,
    alternatives: tuple[Hypothesis, ...],
    max_retries: int = 1,
) -> RecoveryDecision:
    """Choose one action. Alternatives are other hypotheses, not gold labels."""

    failure = detect_failure(one_best)
    if failure is FailureKind.NONE:
        return RecoveryDecision(RecoveryAction.CONTINUE, one_best, 0, failure)
    if failure is FailureKind.AMBIGUOUS:
        return RecoveryDecision(RecoveryAction.CLARIFY, one_best, 0, failure)
    if max_retries < 1 or not alternatives:
        return RecoveryDecision(RecoveryAction.HOLD, one_best, 0, failure)

    best_alternative = max(
        (score_hypothesis(hypothesis) for hypothesis in alternatives),
        key=lambda item: (item.confidence, -item.hypothesis.rank),
    )
    if best_alternative.confidence > one_best.confidence and detect_failure(best_alternative) is FailureKind.NONE:
        return RecoveryDecision(RecoveryAction.RETRY, best_alternative, 1, failure)
    if detect_failure(best_alternative) is FailureKind.AMBIGUOUS:
        return RecoveryDecision(RecoveryAction.CLARIFY, one_best, 1, failure)
    return RecoveryDecision(RecoveryAction.HOLD, one_best, 1, failure)
