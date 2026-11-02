"""Call run_b1. This module does not reimplement prefix selection."""

from __future__ import annotations

from cascadeguard.asr.base import Hypothesis
from cascadeguard.pipeline import run_b1
from cascadeguard_facade.contracts import (
    AdapterError,
    CandidateBundle,
    NormalizedDecision,
    RawControllerOutput,
    slot_pairs,
)
from cascadeguard_facade.normalization import normalize
from cascadeguard_facade.recovery import empty_raw

STRATEGY = "b1_prefix"


def execute(bundle: CandidateBundle) -> tuple[RawControllerOutput, NormalizedDecision]:
    if bundle.candidate_count == 0:
        raw = empty_raw(STRATEGY, bundle)
        return raw, normalize(raw)
    hypotheses = tuple(
        Hypothesis(item.text, item.provenance, item.rank) for item in bundle.ordered()
    )
    try:
        output = run_b1(bundle.utterance_id, hypotheses)
    except Exception as exc:
        raise AdapterError(STRATEGY, str(exc)) from exc
    raw = RawControllerOutput(
        strategy=STRATEGY,
        utterance_id=output.utterance_id,
        invoked=True,
        text=output.hypothesis_text,
        intent=output.intent,
        slots=slot_pairs(output.slots),
        action=output.action,
        reason="prefix_confidence_then_rank",
        retry_mechanism=None,
        support=None,
        retries=None,
        elapsed_seconds=output.elapsed_seconds,
    )
    return raw, normalize(raw)
