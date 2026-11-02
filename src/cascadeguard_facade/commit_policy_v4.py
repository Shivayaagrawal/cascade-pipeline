"""Safe-commit rules. The risk score cannot override a critical gate."""

from __future__ import annotations

from dataclasses import dataclass

from cascadeguard.evaluation.semantic_evidence import CRITICAL_SLOTS
from cascadeguard_facade.failure_diagnosis_v4 import FailureDiagnosis
from cascadeguard_facade.risk_assessment_v4 import RiskBreakdown
from cascadeguard_facade.semantic_evidence_v4 import CandidateAssessmentV4


@dataclass(frozen=True)
class PolicySwitches:
    polarity: bool = True
    ambiguity: bool = True
    critical_slots: bool = True
    contradiction: bool = True
    completeness: bool = True
    modality: bool = True
    risk_score: bool = True
    allow_retry: bool = True


@dataclass(frozen=True)
class CommitDecision:
    action: str
    reason: str
    committed_intent: str | None
    committed_slots: tuple[tuple[str, str], ...]
    answered_intent: str | None
    answered_slots: tuple[tuple[str, str], ...]
    polarity: str


def _frame(
    item: CandidateAssessmentV4,
    switches: PolicySwitches,
) -> tuple[str, tuple[tuple[str, str], ...]] | None:
    """A complete single-intent frame. Ablation switches skip the check they remove."""

    if len(item.intent_hypotheses) != 1 or item.completeness != "complete":
        return None
    if switches.polarity and item.polarity != "affirmative":
        return None
    if switches.modality and item.modality != "certain":
        return None
    if item.context_dependencies:
        return None
    if switches.ambiguity and item.ambiguity != "none":
        return None
    if switches.contradiction and item.contradictions:
        return None
    intent = item.intent_hypotheses[0]
    slots: list[tuple[str, str]] = []
    for name in CRITICAL_SLOTS[intent]:
        values = [value for slot_name, value in item.slot_hypotheses if slot_name == name]
        if len(values) != 1:
            return None
        slots.append((name, values[0]))
    return intent, tuple(slots)


def _safe_frames(
    assessments: tuple[CandidateAssessmentV4, ...],
    switches: PolicySwitches,
) -> list[tuple[str, tuple[tuple[str, str], ...]]]:
    frames = []
    for item in assessments:
        frame = _frame(item, switches)
        if frame is not None:
            frames.append(frame)
    return frames


def decide_commit(
    assessments: tuple[CandidateAssessmentV4, ...],
    diagnosis: FailureDiagnosis,
    risk: RiskBreakdown,
    switches: PolicySwitches,
) -> CommitDecision:
    if not assessments:
        return CommitDecision("HOLD", "EMPTY_BUNDLE", None, (), None, (), "unknown")
    primary = assessments[0]
    labels = set(diagnosis.labels)
    frames = _safe_frames(assessments, switches)
    unique_frames = tuple(dict.fromkeys(frames))
    slot_conflict = any(
        finding.label == "SLOT_VALUE_CORRUPTION" and finding.spans != ("other",)
        for finding in diagnosis.findings
    )
    placeholder = any(
        finding.label == "SLOT_VALUE_CORRUPTION" and finding.spans == ("other",)
        for finding in diagnosis.findings
    )
    intent_conflict = any(
        finding.label == "CONTRADICTORY_EVIDENCE" and finding.severity == "CRITICAL"
        for finding in diagnosis.findings
    )

    def hold(reason: str) -> CommitDecision:
        return CommitDecision("HOLD", reason, None, (), None, (), primary.polarity)

    def answer_from(frame: tuple[str, tuple[tuple[str, str], ...]], action: str, reason: str) -> CommitDecision:
        intent, slots = frame
        return CommitDecision(action, reason, intent, slots, intent, slots, "affirmative")

    if switches.polarity and "NEGATION_SHIFT" in labels:
        if switches.allow_retry and len(unique_frames) == 1 and any(item.polarity == "negative" for item in assessments):
            return answer_from(unique_frames[0], "RETRY", "ALTERNATE_CANDIDATE_AVAILABLE")
        return hold("POLARITY_CONFLICT")
    if slot_conflict or placeholder:
        if switches.critical_slots:
            return hold("CRITICAL_SLOT_CONFLICT")
        if frames:
            return answer_from(frames[0], "CONTINUE", "SAFE_COMPLETE_FRAME")
    if switches.contradiction and (
        intent_conflict or ("CONTRADICTORY_EVIDENCE" in labels and len(unique_frames) != 1)
    ):
        return hold("CONTRADICTORY_EVIDENCE")
    if switches.ambiguity and "SEMANTIC_AMBIGUITY" in labels:
        if switches.allow_retry and len(unique_frames) == 1:
            return answer_from(unique_frames[0], "RETRY", "ALTERNATE_CANDIDATE_AVAILABLE")
        return CommitDecision("CLARIFY", "AMBIGUOUS_INTENT", None, (), None, (), primary.polarity)
    if switches.modality and "UNCERTAINTY_OR_MODALITY" in labels:
        return hold("INSUFFICIENT_EVIDENCE")
    if "CONTEXT_DEPENDENCY" in labels:
        return hold("INSUFFICIENT_EVIDENCE")
    if switches.completeness and "INCOMPLETE_EVIDENCE" in labels:
        if switches.allow_retry and len(unique_frames) == 1:
            return answer_from(unique_frames[0], "RETRY", "ALTERNATE_CANDIDATE_AVAILABLE")
        return hold("INCOMPLETE_FRAME")
    if "FUNCTION_WORD_DAMAGE" in labels and not unique_frames:
        return hold("INSUFFICIENT_EVIDENCE")
    if len(unique_frames) == 1:
        if switches.risk_score and risk.blocks_continue:
            return hold("INSUFFICIENT_EVIDENCE")
        return answer_from(unique_frames[0], "CONTINUE", "SAFE_COMPLETE_FRAME")
    if len(unique_frames) > 1:
        if switches.contradiction or switches.critical_slots:
            return hold("CONTRADICTORY_EVIDENCE")
        return answer_from(frames[0], "CONTINUE", "SAFE_COMPLETE_FRAME")
    return hold("INSUFFICIENT_EVIDENCE")
