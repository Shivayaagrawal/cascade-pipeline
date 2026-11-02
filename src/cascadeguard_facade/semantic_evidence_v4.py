"""Versioned semantic evidence. assess() is not modified."""

from __future__ import annotations

import re
from dataclasses import dataclass

from cascadeguard.evaluation.semantic_evidence import (
    CRITICAL_SLOTS,
    assess,
    frame_is_complete,
)

_NOT = re.compile(r"\bnot\b", re.IGNORECASE)
_MAYBE = re.compile(r"\bmaybe\b", re.IGNORECASE)
_TOKEN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


@dataclass(frozen=True)
class EvidenceSpan:
    field: str
    start: int
    end: int
    text: str


@dataclass(frozen=True)
class CandidateAssessmentV4:
    candidate_id: str
    transcript: str
    intent_hypotheses: tuple[str, ...]
    slot_hypotheses: tuple[tuple[str, str], ...]
    polarity: str
    modality: str
    temporal_values: tuple[str, ...]
    numerical_values: tuple[str, ...]
    completeness: str
    ambiguity: str
    contradictions: tuple[str, ...]
    context_dependencies: tuple[str, ...]
    evidence_spans: tuple[EvidenceSpan, ...]
    provenance: str
    extraction_status: str
    interpretation_status: str
    commit_eligibility: str


def _spans(text: str, field: str, needle: str) -> tuple[EvidenceSpan, ...]:
    if not needle:
        return ()
    found: list[EvidenceSpan] = []
    start = 0
    lowered = text.casefold()
    target = needle.casefold()
    while True:
        index = lowered.find(target, start)
        if index < 0:
            break
        end = index + len(target)
        before = index == 0 or not text[index - 1].isalnum()
        after = end == len(text) or not text[end].isalnum()
        if before and after:
            found.append(EvidenceSpan(field, index, end, text[index:end]))
            break
        start = index + 1
    return tuple(found)


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(match.group(0) for match in _TOKEN.finditer(text))


def assess_v4(
    candidate_id: str,
    transcript: str,
    provenance: str,
    lexicon: dict[str, tuple[str, ...]],
) -> CandidateAssessmentV4:
    """Extract, interpret, and mark preliminary eligibility. Gold is not an argument."""

    evidence = assess(transcript, lexicon)
    intents = tuple(evidence.intents)
    slot_rows: list[tuple[str, str]] = []
    spans: list[EvidenceSpan] = []
    for name, values in evidence.slots.items():
        for value in values:
            slot_rows.append((name, value))
            spans.extend(_spans(transcript, f"slot:{name}", value))
    tokens = tuple(token.casefold() for token in _tokens(transcript))
    weather = "rain" in transcript.casefold()
    context = []
    if "that" in tokens:
        context.append("that")
        spans.extend(_spans(transcript, "context", "that"))
    if "it" in tokens and not weather:
        context.append("it")
        spans.extend(_spans(transcript, "context", "it"))
    if _NOT.search(transcript):
        polarity = "negative"
        spans.extend(_spans(transcript, "polarity", "not"))
    elif intents:
        polarity = "affirmative"
    else:
        polarity = "unknown"
    if _MAYBE.search(transcript):
        modality = "uncertain"
        spans.extend(_spans(transcript, "modality", "maybe"))
    elif intents:
        modality = "certain"
    else:
        modality = "unknown"
    if len(intents) > 1:
        ambiguity = "competing"
    else:
        ambiguity = "none"
    frame = frame_is_complete(evidence)
    if frame is not None:
        completeness = "complete"
    elif intents:
        completeness = "incomplete"
    else:
        completeness = "unknown"
    contradictions = []
    if intents:
        for name in CRITICAL_SLOTS[intents[0]] if len(intents) == 1 else ():
            values = evidence.slots.get(name, ())
            if len(values) > 1:
                contradictions.append(f"{name}:{'|'.join(values)}")
    temporal = tuple(
        value
        for name in ("date", "time")
        for value in evidence.slots.get(name, ())
    )
    numerical = tuple(match.group(0) for match in re.finditer(r"\b\d+\b", transcript))
    blocked = (
        polarity == "negative"
        or modality == "uncertain"
        or ambiguity == "competing"
        or completeness != "complete"
        or bool(context)
        or "other" in tokens
        or bool(contradictions)
    )
    return CandidateAssessmentV4(
        candidate_id=candidate_id,
        transcript=transcript,
        intent_hypotheses=intents,
        slot_hypotheses=tuple(slot_rows),
        polarity=polarity,
        modality=modality,
        temporal_values=temporal,
        numerical_values=numerical,
        completeness=completeness,
        ambiguity=ambiguity,
        contradictions=tuple(contradictions),
        context_dependencies=tuple(context),
        evidence_spans=tuple(spans),
        provenance=provenance,
        extraction_status="extracted",
        interpretation_status="interpreted" if len(intents) == 1 else "unresolved",
        commit_eligibility="blocked" if blocked else "eligible",
    )
