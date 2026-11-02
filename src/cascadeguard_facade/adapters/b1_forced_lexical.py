"""Call forced_selection. The returned frame is not a safety commit."""

from __future__ import annotations

from cascadeguard.evaluation.selective import forced_selection
from cascadeguard_facade.contracts import (
    AdapterError,
    CandidateBundle,
    NormalizedDecision,
    RawControllerOutput,
    slot_pairs,
)
from cascadeguard_facade.normalization import normalize
from cascadeguard_facade.recovery import empty_raw

STRATEGY = "b1_forced_lexical"


def execute(
    bundle: CandidateBundle,
    lexicon: dict[str, tuple[str, ...]],
) -> tuple[RawControllerOutput, NormalizedDecision]:
    if bundle.candidate_count == 0:
        raw = empty_raw(STRATEGY, bundle)
        return raw, normalize(raw)
    texts = [item.text for item in bundle.ordered()]
    try:
        intent, slots = forced_selection(texts, lexicon)
    except Exception as exc:
        raise AdapterError(STRATEGY, str(exc)) from exc
    raw = RawControllerOutput(
        strategy=STRATEGY,
        utterance_id=bundle.utterance_id,
        invoked=True,
        text=None,
        intent=intent,
        slots=slot_pairs(slots),
        action=None,
        reason="forced_selection",
        retry_mechanism=None,
        support=None,
        retries=None,
        elapsed_seconds=None,
    )
    return raw, normalize(raw)
