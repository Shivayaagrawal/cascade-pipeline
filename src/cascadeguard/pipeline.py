"""B0, B1, and B2 on one synthetic utterance. Gold labels are not inputs."""

from __future__ import annotations

import time
from dataclasses import dataclass

from cascadeguard.asr.base import Hypothesis
from cascadeguard.candidates.candidate_manager import (
    ScoredCandidate,
    assert_synthetic_not_nbest,
    score_hypothesis,
    select_candidate,
)
from cascadeguard.recovery.recovery_controller import RecoveryDecision, decide


@dataclass(frozen=True)
class SystemOutput:
    utterance_id: str
    hypothesis_text: str
    intent: str | None
    slots: dict[str, str]
    elapsed_seconds: float
    action: str | None = None


def run_b0(utterance_id: str, one_best: Hypothesis) -> SystemOutput:
    """Single-best transcript passed to NLU."""

    assert_synthetic_not_nbest((one_best,))
    started = time.perf_counter()
    scored = score_hypothesis(one_best)
    elapsed = time.perf_counter() - started
    return SystemOutput(
        utterance_id,
        one_best.text,
        scored.intent,
        scored.slots,
        elapsed,
    )


def run_b1(utterance_id: str, hypotheses: tuple[Hypothesis, ...]) -> SystemOutput:
    """Compare candidates. Provenance must already say synthetic_edit, not N-best."""

    assert_synthetic_not_nbest(hypotheses)
    started = time.perf_counter()
    selected = select_candidate(hypotheses)
    elapsed = time.perf_counter() - started
    return SystemOutput(
        utterance_id,
        selected.hypothesis.text,
        selected.intent,
        selected.slots,
        elapsed,
    )


def run_b2(
    utterance_id: str,
    one_best: Hypothesis,
    alternatives: tuple[Hypothesis, ...],
    max_retries: int = 1,
) -> tuple[SystemOutput, RecoveryDecision]:
    """Diagnose the 1-best parse and optionally retry on other synthetic candidates."""

    assert_synthetic_not_nbest((one_best, *alternatives))
    started = time.perf_counter()
    scored = score_hypothesis(one_best)
    decision = decide(scored, alternatives, max_retries=max_retries)
    elapsed = time.perf_counter() - started
    selected: ScoredCandidate = decision.selected
    output = SystemOutput(
        utterance_id,
        selected.hypothesis.text,
        selected.intent,
        selected.slots,
        elapsed,
        decision.action.value,
    )
    return output, decision
