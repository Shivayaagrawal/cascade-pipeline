"""Commit, clarify, or hold. A confident intent does not replace a missing slot."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from cascadeguard.evaluation.semantic_evidence import (
    CRITICAL_SLOTS,
    Evidence,
    assess,
    frame_is_complete,
    intent_hits,
    value_in_text,
)
from cascadeguard.simulation.utterance_generator import Utterance


class SelectiveAction(str, Enum):
    COMMIT = "commit"
    CLARIFY = "clarify"
    HOLD = "hold"


class RecoveryAction(str, Enum):
    CONTINUE = "CONTINUE"
    RETRY = "RETRY"
    CLARIFY = "CLARIFY"
    HOLD = "HOLD"


SIMULATED_RETRY = "simulated_candidate_rescore"


@dataclass(frozen=True)
class SelectiveDecision:
    action: SelectiveAction
    intent: str | None
    slots: dict[str, str]
    support: int
    reason: str


def decide_selective(
    candidates: list[str],
    lexicon: dict[str, tuple[str, ...]],
    min_support: int = 1,
) -> SelectiveDecision:
    """Commit only when one complete frame is supported by enough candidates.

    `min_support` is the number of complete candidates that must carry each
    critical slot value. It is not a threshold fit to the v1 or v2 scores.
    """

    if min_support < 1:
        raise ValueError("min_support must be at least 1")
    evidences = [assess(text, lexicon) for text in candidates]
    complete = [item for item in evidences if frame_is_complete(item) is not None]
    if not complete:
        if any(len(item.intents) > 1 for item in evidences):
            return SelectiveDecision(SelectiveAction.CLARIFY, None, {}, 0, "multiple_intents_in_a_candidate")
        if any(len(item.intents) == 1 for item in evidences):
            return SelectiveDecision(SelectiveAction.CLARIFY, None, {}, 0, "intent_without_required_slots")
        return SelectiveDecision(SelectiveAction.HOLD, None, {}, 0, "no_intent_evidence")
    intents = {item.intents[0] for item in complete}
    if len(intents) != 1:
        return SelectiveDecision(SelectiveAction.HOLD, None, {}, 0, "intent_disagreement")
    intent = next(iter(intents))
    frame: dict[str, str] = {}
    for name in CRITICAL_SLOTS[intent]:
        values = {item.slots[name][0] for item in complete}
        if len(values) != 1:
            return SelectiveDecision(SelectiveAction.CLARIFY, intent, {}, len(complete), "slot_value_disagreement")
        value = next(iter(values))
        if len(complete) < min_support:
            return SelectiveDecision(
                SelectiveAction.CLARIFY,
                intent,
                {},
                len(complete),
                "slot_support_below_threshold",
            )
        frame[name] = value
    return SelectiveDecision(SelectiveAction.COMMIT, intent, frame, len(complete), "evidence_agrees")


def recovery_action(
    primary: list[str],
    lexicon: dict[str, tuple[str, ...]],
    retry_candidates: list[str] | None = None,
    min_support: int = 1,
) -> tuple[RecoveryAction, SelectiveDecision, str]:
    """Map evidence to CONTINUE, CLARIFY, HOLD, or a labelled simulated RETRY.

    RETRY is returned only when the caller passes a second bundle and that bundle
    can commit. The second bundle is not an ASR decode.
    """

    decision = decide_selective(primary, lexicon, min_support=min_support)
    if decision.action is SelectiveAction.COMMIT:
        return RecoveryAction.CONTINUE, decision, "primary_bundle"
    if retry_candidates is None:
        if decision.action is SelectiveAction.CLARIFY:
            return RecoveryAction.CLARIFY, decision, "primary_bundle"
        return RecoveryAction.HOLD, decision, "primary_bundle"
    retry = decide_selective(retry_candidates, lexicon, min_support=min_support)
    if retry.action is SelectiveAction.COMMIT:
        return RecoveryAction.RETRY, retry, SIMULATED_RETRY
    if decision.action is SelectiveAction.CLARIFY or retry.action is SelectiveAction.CLARIFY:
        return RecoveryAction.CLARIFY, decision, "primary_bundle"
    return RecoveryAction.HOLD, decision, "primary_bundle"


def forced_selection(
    candidates: list[str],
    lexicon: dict[str, tuple[str, ...]],
) -> tuple[str | None, dict[str, str]]:
    """Always return one frame. This is a selector, not a safety decision.

    Preference order, without gold labels: one intent, then more filled critical
    slots, then the earlier candidate. A partial frame is returned when slots disagree
    or are missing. Callers must not treat that frame as a commit.
    """

    if not candidates:
        raise ValueError("Candidate list is empty")
    evidences = [assess(text, lexicon) for text in candidates]

    def sort_key(pair: tuple[int, Evidence]) -> tuple[int, int, int]:
        index, evidence = pair
        if len(evidence.intents) != 1:
            return (0, 0, -index)
        intent = evidence.intents[0]
        filled = sum(1 for name in CRITICAL_SLOTS[intent] if len(evidence.slots.get(name, ())) == 1)
        return (1, filled, -index)

    _, evidence = max(enumerate(evidences), key=sort_key)
    if len(evidence.intents) != 1:
        return None, {}
    intent = evidence.intents[0]
    frame: dict[str, str] = {}
    for name in CRITICAL_SLOTS[intent]:
        values = evidence.slots.get(name, ())
        if len(values) == 1:
            frame[name] = values[0]
    return intent, frame


def lexical_frame_preserved(utterance: Utterance, text: str) -> bool:
    """True when one string contains the gold intent cue and every gold slot value."""

    if utterance.intent not in intent_hits(text):
        return False
    if len(intent_hits(text)) != 1:
        return False
    return all(value_in_text(text, value) for value in utterance.slots.values())


def candidate_disagrees(candidates: list[str], lexicon: dict[str, tuple[str, ...]]) -> bool:
    """True when candidates support different intents or one candidate supports two."""

    evidences = [assess(text, lexicon) for text in candidates]
    singles = {item.intents[0] for item in evidences if len(item.intents) == 1}
    return len(singles) > 1 or any(len(item.intents) > 1 for item in evidences)


def gold_slots_missing(utterance: Utterance, candidates: list[str]) -> tuple[str, ...]:
    """Gold slot values absent from every candidate. Empty gold slots return nothing."""

    missing = []
    for name, value in utterance.slots.items():
        if not any(value_in_text(text, value) for text in candidates):
            missing.append(name)
    return tuple(missing)
