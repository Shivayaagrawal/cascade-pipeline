"""Call run_b2. CLARIFY and HOLD text stays in the raw copy only."""

from __future__ import annotations

from cascadeguard.asr.base import Hypothesis
from cascadeguard.pipeline import run_b2
from cascadeguard_facade.contracts import (
    AdapterError,
    CandidateBundle,
    NormalizedDecision,
    RawControllerOutput,
    slot_pairs,
)
from cascadeguard_facade.normalization import normalize
from cascadeguard_facade.recovery import empty_raw

STRATEGY = "b2_prefix_controller"


def execute(bundle: CandidateBundle) -> tuple[RawControllerOutput, NormalizedDecision]:
    if bundle.candidate_count == 0:
        raw = empty_raw(STRATEGY, bundle)
        return raw, normalize(raw)
    ordered = bundle.ordered()
    one_best = Hypothesis(ordered[0].text, ordered[0].provenance, ordered[0].rank)
    alternatives = tuple(
        Hypothesis(item.text, item.provenance, item.rank) for item in ordered[1:]
    )
    try:
        output, decision = run_b2(bundle.utterance_id, one_best, alternatives)
    except Exception as exc:
        raise AdapterError(STRATEGY, str(exc)) from exc
    selected = decision.selected
    raw = RawControllerOutput(
        strategy=STRATEGY,
        utterance_id=output.utterance_id,
        invoked=True,
        text=selected.hypothesis.text,
        intent=selected.intent,
        slots=slot_pairs(selected.slots),
        action=decision.action.value,
        reason=decision.failure.value,
        retry_mechanism=None,
        support=None,
        retries=decision.retries,
        elapsed_seconds=output.elapsed_seconds,
    )
    return raw, normalize(raw)
