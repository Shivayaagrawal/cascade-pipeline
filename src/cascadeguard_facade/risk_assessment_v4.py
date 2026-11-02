"""Aggregate risk. Critical gates do not read this score."""

from __future__ import annotations

from dataclasses import dataclass

from cascadeguard_facade.failure_diagnosis_v4 import FailureDiagnosis
from cascadeguard_facade.semantic_evidence_v4 import CandidateAssessmentV4

WEIGHT_NAMES = ("intent", "slot", "polarity", "ambiguity", "contradiction")


@dataclass(frozen=True)
class RiskBreakdown:
    indicators: dict[str, int]
    weights: dict[str, float]
    score: float
    threshold: float
    blocks_continue: bool


def indicators(assessments: tuple[CandidateAssessmentV4, ...], diagnosis: FailureDiagnosis) -> dict[str, int]:
    labels = set(diagnosis.labels)
    intent_uncertain = any(len(item.intent_hypotheses) != 1 for item in assessments) or (
        "FUNCTION_WORD_DAMAGE" in labels
    )
    slot_uncertain = "INCOMPLETE_EVIDENCE" in labels or "SLOT_VALUE_CORRUPTION" in labels
    return {
        "intent": int(intent_uncertain),
        "slot": int(slot_uncertain),
        "polarity": int("NEGATION_SHIFT" in labels),
        "ambiguity": int("SEMANTIC_AMBIGUITY" in labels),
        "contradiction": int("CONTRADICTORY_EVIDENCE" in labels),
    }


def risk_score(
    assessments: tuple[CandidateAssessmentV4, ...],
    diagnosis: FailureDiagnosis,
    weights: dict[str, float],
    threshold: float,
) -> RiskBreakdown:
    flags = indicators(assessments, diagnosis)
    score = sum(flags[name] * float(weights[name]) for name in WEIGHT_NAMES)
    return RiskBreakdown(flags, dict(weights), score, threshold, score >= threshold)


def weight_grid() -> tuple[dict[str, float], ...]:
    """Nonnegative quarter-weights that sum to 1. Declared before any split is scored."""

    grids: list[dict[str, float]] = []
    for intent in range(5):
        for slot in range(5 - intent):
            for polarity in range(5 - intent - slot):
                for ambiguity in range(5 - intent - slot - polarity):
                    contradiction = 4 - intent - slot - polarity - ambiguity
                    units = (intent, slot, polarity, ambiguity, contradiction)
                    grids.append(
                        {name: unit / 4 for name, unit in zip(WEIGHT_NAMES, units, strict=True)}
                    )
    return tuple(grids)


def thresholds() -> tuple[float, ...]:
    """Declared before validation scoring. 0 holds every scored continue."""

    return (0.0, 0.25, 0.5, 0.75, 1.0)
