"""Route one of the five identities. Unknown names are rejected."""

from __future__ import annotations

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard_facade.adapters import (
    b0_prefix,
    b1_forced_lexical,
    b1_prefix,
    b2_lexical_v3,
    b2_prefix_controller,
)
from cascadeguard_facade.audit import make_record
from cascadeguard_facade.contracts import (
    STRATEGIES,
    AuditRecord,
    CandidateBundle,
    UnknownStrategyError,
)
from cascadeguard_facade.evaluation import evaluate_decision
from cascadeguard_facade.recovery import empty_audit


def route(
    strategy: str,
    bundle: CandidateBundle,
    *,
    retry_bundle: CandidateBundle | None = None,
    lexicon: dict[str, tuple[str, ...]] | None = None,
    min_support: int = 1,
    gold_intent: str | None = None,
    gold_slots: dict[str, str] | None = None,
) -> AuditRecord:
    """Run one identity.

    Gold is applied only after the adapter returns. An empty bundle returns
    HOLD / EMPTY_BUNDLE and does not call an adapter.
    """

    if strategy not in STRATEGIES:
        raise UnknownStrategyError(
            f"Unknown strategy {strategy!r}. Expected one of {sorted(STRATEGIES)}."
        )
    if bundle.candidate_count == 0:
        record = empty_audit(strategy, bundle)
        return _with_gold(record, gold_intent, gold_slots)
    if strategy == "b0_prefix":
        raw, normalized = b0_prefix.execute(bundle)
    elif strategy == "b1_prefix":
        raw, normalized = b1_prefix.execute(bundle)
    elif strategy == "b2_prefix_controller":
        raw, normalized = b2_prefix_controller.execute(bundle)
    else:
        words = lexicon if lexicon is not None else lexicon_from_utterances()
        if strategy == "b1_forced_lexical":
            raw, normalized = b1_forced_lexical.execute(bundle, words)
        else:
            raw, normalized = b2_lexical_v3.execute(
                bundle,
                words,
                retry_bundle=retry_bundle,
                min_support=min_support,
            )
    record = make_record(bundle, raw, normalized)
    return _with_gold(record, gold_intent, gold_slots)


def _with_gold(
    record: AuditRecord,
    gold_intent: str | None,
    gold_slots: dict[str, str] | None,
) -> AuditRecord:
    if gold_intent is None:
        return record
    evaluation = evaluate_decision(record.normalized, gold_intent, gold_slots or {})
    return AuditRecord(
        strategy=record.strategy,
        utterance_id=record.utterance_id,
        candidate_ids=record.candidate_ids,
        candidate_provenance=record.candidate_provenance,
        raw=record.raw,
        normalized=record.normalized,
        evaluation=evaluation,
    )
