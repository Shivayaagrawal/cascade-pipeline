"""Call recovery_action. RETRY stays simulated_candidate_rescore."""

from __future__ import annotations

from cascadeguard.evaluation.selective import recovery_action
from cascadeguard_facade.contracts import (
    AdapterError,
    CandidateBundle,
    NormalizedDecision,
    RawControllerOutput,
    slot_pairs,
)
from cascadeguard_facade.normalization import normalize
from cascadeguard_facade.recovery import empty_raw

STRATEGY = "b2_lexical_v3"


def execute(
    bundle: CandidateBundle,
    lexicon: dict[str, tuple[str, ...]],
    retry_bundle: CandidateBundle | None = None,
    min_support: int = 1,
) -> tuple[RawControllerOutput, NormalizedDecision]:
    if bundle.candidate_count == 0:
        raw = empty_raw(STRATEGY, bundle)
        return raw, normalize(raw)
    primary = [item.text for item in bundle.ordered()]
    retry = None if retry_bundle is None else [item.text for item in retry_bundle.ordered()]
    try:
        action, decision, mechanism = recovery_action(
            primary,
            lexicon,
            retry_candidates=retry,
            min_support=min_support,
        )
    except Exception as exc:
        raise AdapterError(STRATEGY, str(exc)) from exc
    raw = RawControllerOutput(
        strategy=STRATEGY,
        utterance_id=bundle.utterance_id,
        invoked=True,
        text=None,
        intent=decision.intent,
        slots=slot_pairs(decision.slots),
        action=action.value,
        reason=decision.reason,
        retry_mechanism=mechanism if action.value == "RETRY" else None,
        support=decision.support,
        retries=1 if action.value == "RETRY" else 0,
        elapsed_seconds=None,
    )
    return raw, normalize(raw)
