"""Score facade decisions with the existing metric functions."""

from __future__ import annotations

from cascadeguard.evaluation.intent_metrics import frames_equal
from cascadeguard.evaluation.rates import rate
from cascadeguard.evaluation.slot_metrics import slot_scores
from cascadeguard_facade.contracts import (
    CONTROLLER_STRATEGIES,
    AuditRecord,
    EvaluationResult,
    NormalizedDecision,
    SemanticFrame,
    slot_pairs,
)


def scoring_frame(decision: NormalizedDecision) -> SemanticFrame | None:
    """Forced lexical answers are scored from answered_frame, not as safety commits."""

    if decision.strategy == "b1_forced_lexical":
        return decision.answered_frame
    if decision.committed_frame is not None:
        return decision.committed_frame
    return None


def evaluate_decision(
    decision: NormalizedDecision,
    gold_intent: str,
    gold_slots: dict[str, str],
) -> EvaluationResult:
    frame = scoring_frame(decision)
    predicted_intent = None if frame is None else frame.intent
    predicted_slots = {} if frame is None else frame.as_dict()
    exact = frames_equal(gold_intent, gold_slots, predicted_intent, predicted_slots)
    committed = decision.committed
    abstained = decision.action in {"CLARIFY", "HOLD"} or (
        decision.strategy in CONTROLLER_STRATEGIES and not committed
    )
    unsafe = (not exact) if committed else None
    intent_correct = predicted_intent == gold_intent
    return EvaluationResult(
        utterance_id=decision.utterance_id,
        strategy=decision.strategy,
        intent_correct=intent_correct,
        exact_frame=exact,
        committed=committed,
        abstained=abstained,
        unsafe=unsafe,
        slot_reference=slot_pairs(gold_slots),
        slot_predicted=slot_pairs(predicted_slots),
    )


def selective_summary(records: list[AuditRecord]) -> dict[str, object]:
    """Coverage and risk for controller records. Other identities are omitted."""

    rows = [item for item in records if item.strategy in CONTROLLER_STRATEGIES]
    committed = [item for item in rows if item.normalized.committed]
    unsafe = [
        item
        for item in committed
        if item.evaluation is not None and item.evaluation.unsafe is True
    ]
    return {
        "selective_coverage": rate(
            len(committed),
            len(rows),
            "no controller records",
        ),
        "selective_risk": rate(
            len(unsafe),
            len(committed),
            "no committed decisions; refusing every input is not a reliability score",
        ),
    }


def slot_summary(records: list[AuditRecord]) -> dict[str, object]:
    pairs = [
        (dict(item.evaluation.slot_reference), dict(item.evaluation.slot_predicted))
        for item in records
        if item.evaluation is not None
    ]
    return slot_scores(pairs)
