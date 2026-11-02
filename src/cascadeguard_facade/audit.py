"""Build audit records. Raw and normalized objects stay side by side."""

from __future__ import annotations

from cascadeguard_facade.contracts import (
    AuditRecord,
    CandidateBundle,
    EvaluationResult,
    NormalizedDecision,
    RawControllerOutput,
)


def make_record(
    bundle: CandidateBundle,
    raw: RawControllerOutput,
    normalized: NormalizedDecision,
    evaluation: EvaluationResult | None = None,
) -> AuditRecord:
    ordered = bundle.ordered()
    return AuditRecord(
        strategy=normalized.strategy,
        utterance_id=bundle.utterance_id,
        candidate_ids=tuple(item.candidate_id for item in ordered),
        candidate_provenance=tuple(item.provenance for item in ordered),
        raw=raw,
        normalized=normalized,
        evaluation=evaluation,
    )
