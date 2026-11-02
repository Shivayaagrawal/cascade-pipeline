"""Facade-level bundle checks. Existing processors are not called from here."""

from __future__ import annotations

from cascadeguard_facade.contracts import (
    AuditRecord,
    CandidateBundle,
    NormalizedDecision,
    RawControllerOutput,
)


def empty_raw(strategy: str, bundle: CandidateBundle) -> RawControllerOutput:
    return RawControllerOutput(
        strategy=strategy,
        utterance_id=bundle.utterance_id,
        invoked=False,
        text=None,
        intent=None,
        slots=(),
        action="HOLD",
        reason="EMPTY_BUNDLE",
        retry_mechanism=None,
        support=None,
        retries=None,
        elapsed_seconds=None,
    )


def empty_decision(strategy: str, bundle: CandidateBundle) -> NormalizedDecision:
    return NormalizedDecision(
        strategy,
        bundle.utterance_id,
        "HOLD",
        "EMPTY_BUNDLE",
        None,
        None,
        None,
    )


def empty_audit(strategy: str, bundle: CandidateBundle) -> AuditRecord:
    raw = empty_raw(strategy, bundle)
    return AuditRecord(
        strategy=strategy,
        utterance_id=bundle.utterance_id,
        candidate_ids=(),
        candidate_provenance=(),
        raw=raw,
        normalized=empty_decision(strategy, bundle),
        evaluation=None,
    )
