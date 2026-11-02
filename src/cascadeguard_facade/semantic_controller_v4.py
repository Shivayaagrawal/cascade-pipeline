"""b2_semantic_v4. It is not one of the five Phase 2 identities."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from cascadeguard.evaluation.selective import recovery_action
from cascadeguard_facade.commit_policy_v4 import PolicySwitches, decide_commit
from cascadeguard_facade.contracts import CandidateBundle
from cascadeguard_facade.failure_diagnosis_v4 import diagnose_failure
from cascadeguard_facade.risk_assessment_v4 import risk_score
from cascadeguard_facade.semantic_evidence_v4 import CandidateAssessmentV4, assess_v4

STRATEGY = "b2_semantic_v4"


@dataclass(frozen=True)
class ControllerResult:
    strategy: str
    raw: dict[str, object]
    action: str | None
    reason: str
    committed_intent: str | None
    committed_slots: tuple[tuple[str, str], ...]
    answered_intent: str | None
    answered_slots: tuple[tuple[str, str], ...]
    polarity: str
    risk: dict[str, object]
    candidate_provenance: tuple[str, ...]
    candidate_ids: tuple[str, ...]


def _empty(bundle: CandidateBundle) -> ControllerResult:
    raw = {
        "invoked_processors": False,
        "assessments": [],
        "diagnosis_labels": [],
        "reason": "EMPTY_BUNDLE",
    }
    return ControllerResult(
        STRATEGY,
        raw,
        "HOLD",
        "EMPTY_BUNDLE",
        None,
        (),
        None,
        (),
        "unknown",
        {},
        (),
        (),
    )


def run_semantic_v4(
    bundle: CandidateBundle,
    lexicon: dict[str, tuple[str, ...]],
    *,
    weights: dict[str, float],
    threshold: float,
    switches: PolicySwitches | None = None,
    frozen_recovery: bool = False,
) -> ControllerResult:
    """Diagnose the bundle. frozen_recovery uses recovery_action instead of the v4 policy."""

    if bundle.candidate_count == 0:
        return _empty(bundle)
    switches = switches or PolicySwitches()
    ordered = bundle.ordered()
    assessments = tuple(
        assess_v4(item.candidate_id, item.text, item.provenance, lexicon) for item in ordered
    )
    diagnosis = diagnose_failure(assessments)
    risk = risk_score(assessments, diagnosis, weights, threshold)
    raw = {
        "invoked_processors": True,
        "assessments": [asdict(item) for item in assessments],
        "diagnosis_labels": list(diagnosis.labels),
        "diagnosis_severity": diagnosis.severity,
        "candidate_agreement": diagnosis.candidate_agreement,
        "critical_value_impact": diagnosis.critical_value_impact,
    }
    if frozen_recovery:
        decision_action, decision, _mechanism = _lexical(ordered, lexicon)
        return _from_lexical(bundle, raw, risk, decision_action, decision)
    decision = decide_commit(assessments, diagnosis, risk, switches)
    return ControllerResult(
        STRATEGY,
        raw,
        decision.action,
        decision.reason,
        decision.committed_intent,
        decision.committed_slots,
        decision.answered_intent,
        decision.answered_slots,
        decision.polarity,
        {
            "indicators": risk.indicators,
            "weights": risk.weights,
            "score": risk.score,
            "threshold": risk.threshold,
            "blocks_continue": risk.blocks_continue,
        },
        tuple(item.provenance for item in ordered),
        tuple(item.candidate_id for item in ordered),
    )


def _lexical(ordered, lexicon):
    texts = [item.text for item in ordered]
    return recovery_action(texts, lexicon)


def _from_lexical(bundle, raw, risk, action, decision) -> ControllerResult:
    commit = action.value in {"CONTINUE", "RETRY"}
    slots = tuple(sorted(decision.slots.items())) if commit else ()
    intent = decision.intent if commit else None
    raw = dict(raw)
    raw["frozen_recovery_action"] = action.value
    raw["frozen_recovery_reason"] = decision.reason
    polarity = "unknown"
    assessments = raw.get("assessments") or []
    if assessments:
        polarity = str(assessments[0]["polarity"])
    return ControllerResult(
        STRATEGY,
        raw,
        action.value,
        decision.reason,
        intent,
        slots,
        decision.intent if commit else None,
        tuple(sorted(decision.slots.items())) if commit else (),
        polarity,
        {
            "indicators": risk.indicators,
            "weights": risk.weights,
            "score": risk.score,
            "threshold": risk.threshold,
            "blocks_continue": risk.blocks_continue,
        },
        tuple(item.provenance for item in bundle.ordered()),
        tuple(item.candidate_id for item in bundle.ordered()),
    )
