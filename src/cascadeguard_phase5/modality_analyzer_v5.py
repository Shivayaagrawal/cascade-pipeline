"""Deterministic modality rules for the closed synthetic grammar.

This is not a general language model. confidence is 1.0 for one clear class,
0.5 when cues mix, and 0.0 when the string is empty. It is not a probability.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TOKEN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", re.IGNORECASE)
NOT = re.compile(r"\bnot\b", re.IGNORECASE)
CONTRACTION = re.compile(r"\b(?:do|does|did|is|are|was|were|have|has|had|would|should|could|can|will|wo)n'?t\b|\bdon't\b|\bdont\b", re.IGNORECASE)
UNCERTAIN = re.compile(r"\b(?:maybe|possibly|might)\b", re.IGNORECASE)
MODAL_MAY = re.compile(r"(?<![A-Za-z])may(?![A-Za-z])")
CONDITIONAL = re.compile(r"\b(?:if|unless)\b", re.IGNORECASE)
POLITE = re.compile(r"\bplease\b|\bcould you\b|\bcan you\b", re.IGNORECASE)


@dataclass(frozen=True)
class ModalityReading:
    modality: str
    polarity: str
    conditionality: str
    confidence: float
    matched_evidence: tuple[str, ...]
    explanation: str
    is_execution_ready: bool
    transcript: str

    def as_dict(self) -> dict[str, object]:
        return {
            "modality": self.modality,
            "polarity": self.polarity,
            "conditionality": self.conditionality,
            "confidence": self.confidence,
            "matched_evidence": list(self.matched_evidence),
            "explanation": self.explanation,
            "is_execution_ready": self.is_execution_ready,
            "transcript": self.transcript,
        }


def _evidence(pattern: re.Pattern[str], text: str) -> list[str]:
    return [match.group(0) for match in pattern.finditer(text)]


def analyze_modality(text: str) -> ModalityReading:
    """Classify one candidate string. The original text is retained."""

    transcript = text
    if not text.strip():
        return ModalityReading(
            "AMBIGUOUS_OR_MIXED",
            "unknown",
            "none",
            0.0,
            (),
            "The candidate text is empty.",
            False,
            transcript,
        )
    negative = _evidence(NOT, text) + _evidence(CONTRACTION, text)
    uncertain = _evidence(UNCERTAIN, text) + _evidence(MODAL_MAY, text)
    conditional = _evidence(CONDITIONAL, text)
    polite = _evidence(POLITE, text)
    polarity = "negative" if negative else "affirmative"
    conditionality = "conditional" if conditional else "none"
    families = [name for name, found in (("negation", negative), ("uncertainty", uncertain), ("conditional", conditional)) if found]
    evidence = tuple(negative + uncertain + conditional + polite)
    if len(families) > 1:
        return ModalityReading(
            "AMBIGUOUS_OR_MIXED",
            polarity,
            conditionality,
            0.5,
            evidence,
            "Negation, uncertainty, and conditionality do not combine into one executable instruction.",
            False,
            transcript,
        )
    if negative:
        return ModalityReading(
            "NEGATION",
            "negative",
            "none",
            1.0,
            evidence,
            "A negation cue blocks execution. The word cancel is not one of those cues.",
            False,
            transcript,
        )
    if uncertain:
        return ModalityReading(
            "UNCERTAINTY",
            "affirmative",
            "none",
            1.0,
            evidence,
            "An uncertainty cue blocks execution. The month May is not one of those cues.",
            False,
            transcript,
        )
    if conditional:
        return ModalityReading(
            "CONDITIONAL",
            "affirmative",
            "conditional",
            1.0,
            evidence,
            "A conditional cue blocks execution until the condition is resolved.",
            False,
            transcript,
        )
    if polite:
        return ModalityReading(
            "REQUEST_OR_POLITE_INSTRUCTION",
            "affirmative",
            "none",
            1.0,
            evidence,
            "Polite wording stays execution-ready. It is not uncertainty.",
            True,
            transcript,
        )
    return ModalityReading(
        "AFFIRMATIVE",
        "affirmative",
        "none",
        1.0,
        (),
        "No negation, uncertainty, condition, or polite cue was found.",
        True,
        transcript,
    )
