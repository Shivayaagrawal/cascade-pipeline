"""Call run_b0. This module does not reimplement the prefix parser."""

from __future__ import annotations

from cascadeguard.asr.base import Hypothesis
from cascadeguard.pipeline import run_b0
from cascadeguard_facade.contracts import (
    AdapterError,
    CandidateBundle,
    NormalizedDecision,
    RawControllerOutput,
    slot_pairs,
)
from cascadeguard_facade.normalization import normalize
from cascadeguard_facade.recovery import empty_raw

STRATEGY = "b0_prefix"


def execute(bundle: CandidateBundle) -> tuple[RawControllerOutput, NormalizedDecision]:
    if bundle.candidate_count == 0:
        raw = empty_raw(STRATEGY, bundle)
        return raw, normalize(raw)
    hypothesis = Hypothesis(
        bundle.ordered()[0].text,
        bundle.ordered()[0].provenance,
        bundle.ordered()[0].rank,
    )
    try:
        output = run_b0(bundle.utterance_id, hypothesis)
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
        reason="prefix_parse",
        retry_mechanism=None,
        support=None,
        retries=None,
        elapsed_seconds=output.elapsed_seconds,
    )
    return raw, normalize(raw)
