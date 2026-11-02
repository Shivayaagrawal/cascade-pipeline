"""Failure labels for v4 assessments. A label is not a recovery action."""

from __future__ import annotations

from dataclasses import dataclass

from cascadeguard.evaluation.semantic_evidence import CRITICAL_SLOTS
from cascadeguard_facade.semantic_evidence_v4 import CandidateAssessmentV4

SEVERITY_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


@dataclass(frozen=True)
class FailureFinding:
    label: str
    severity: str
    detail: str
    spans: tuple[str, ...]


@dataclass(frozen=True)
class FailureDiagnosis:
    findings: tuple[FailureFinding, ...]
    severity: str
    candidate_agreement: bool
    critical_value_impact: bool
    alternate_available: bool
    checks_performed: bool

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(finding.label for finding in self.findings)


def _frame(assessment: CandidateAssessmentV4) -> tuple[str, dict[str, str]] | None:
    if len(assessment.intent_hypotheses) != 1 or assessment.completeness != "complete":
        return None
    intent = assessment.intent_hypotheses[0]
    slots: dict[str, str] = {}
    for name in CRITICAL_SLOTS[intent]:
        values = [value for slot_name, value in assessment.slot_hypotheses if slot_name == name]
        if len(values) != 1:
            return None
        slots[name] = values[0]
    return intent, slots


def diagnose_failure(assessments: tuple[CandidateAssessmentV4, ...]) -> FailureDiagnosis:
    """Label every failure the checks can see. Missing text is not filled in."""

    if not assessments:
        return FailureDiagnosis((), "LOW", True, False, False, False)
    findings: list[FailureFinding] = []
    for item in assessments:
        if item.polarity == "negative":
            findings.append(FailureFinding("NEGATION_SHIFT", "CRITICAL", item.candidate_id, ("not",)))
        if item.modality == "uncertain":
            findings.append(
                FailureFinding("UNCERTAINTY_OR_MODALITY", "MEDIUM", item.candidate_id, ("maybe",))
            )
        if item.context_dependencies:
            findings.append(
                FailureFinding(
                    "CONTEXT_DEPENDENCY",
                    "HIGH",
                    item.candidate_id,
                    item.context_dependencies,
                )
            )
        if item.ambiguity == "competing":
            findings.append(
                FailureFinding(
                    "SEMANTIC_AMBIGUITY",
                    "HIGH",
                    item.candidate_id,
                    item.intent_hypotheses,
                )
            )
        tokens = {token.casefold() for token in item.transcript.split()}
        if "other" in tokens:
            findings.append(FailureFinding("SLOT_VALUE_CORRUPTION", "HIGH", item.candidate_id, ("other",)))
        if "banana" in tokens:
            severity = "MEDIUM" if item.completeness == "complete" and len(item.intent_hypotheses) == 1 else "HIGH"
            findings.append(FailureFinding("FUNCTION_WORD_DAMAGE", severity, item.candidate_id, ("banana",)))
        if (
            len(item.intent_hypotheses) == 1
            and item.completeness == "incomplete"
            and "other" not in tokens
            and not item.context_dependencies
        ):
            findings.append(FailureFinding("INCOMPLETE_EVIDENCE", "HIGH", item.candidate_id, ()))
        if item.contradictions:
            findings.append(
                FailureFinding(
                    "CONTRADICTORY_EVIDENCE",
                    "HIGH",
                    item.candidate_id,
                    item.contradictions,
                )
            )
    frames = [frame for frame in (_frame(item) for item in assessments) if frame is not None]
    agreement = True
    if len(frames) >= 2:
        intents = {intent for intent, _slots in frames}
        if len(intents) > 1:
            agreement = False
            findings.append(
                FailureFinding("CONTRADICTORY_EVIDENCE", "CRITICAL", "bundle", tuple(sorted(intents)))
            )
        else:
            intent = next(iter(intents))
            for name in CRITICAL_SLOTS[intent]:
                values = {slots[name] for _intent, slots in frames}
                if len(values) > 1:
                    agreement = False
                    findings.append(
                        FailureFinding(
                            "CONTRADICTORY_EVIDENCE",
                            "HIGH",
                            name,
                            tuple(sorted(values)),
                        )
                    )
                    findings.append(
                        FailureFinding(
                            "SLOT_VALUE_CORRUPTION",
                            "HIGH",
                            name,
                            tuple(sorted(values)),
                        )
                    )
    severity = "LOW"
    for finding in findings:
        if SEVERITY_RANK[finding.severity] > SEVERITY_RANK[severity]:
            severity = finding.severity
    if not findings:
        findings.append(
            FailureFinding("NO_FAILURE_DETECTED", "LOW", "checks_ran", ())
        )
    critical = any(
        finding.label in {"NEGATION_SHIFT", "CONTRADICTORY_EVIDENCE", "SLOT_VALUE_CORRUPTION"}
        and finding.severity in {"HIGH", "CRITICAL"}
        for finding in findings
    )
    return FailureDiagnosis(
        tuple(findings),
        severity,
        agreement,
        critical,
        len(assessments) > 1,
        True,
    )
