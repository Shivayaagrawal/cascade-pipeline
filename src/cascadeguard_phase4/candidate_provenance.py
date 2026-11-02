"""Record which candidate a frozen strategy actually used.

Strategies that do not emit an id are traced from their own frozen readers.
This module is not the oracle and does not decide safety.
"""

from __future__ import annotations

from cascadeguard.evaluation.semantic_evidence import assess, frame_is_complete
from cascadeguard.evaluation.semantic_evidence import CRITICAL_SLOTS
from cascadeguard_facade.commit_policy_v4 import PolicySwitches
from cascadeguard_facade.contracts import CandidateBundle
from cascadeguard_facade.semantic_evidence_v4 import assess_v4


def _by_text(bundle: CandidateBundle, text: str | None) -> str | None:
    if text is None:
        return None
    for item in bundle.ordered():
        if item.text == text:
            return item.candidate_id
    return None


def lexical_source(
    bundle: CandidateBundle,
    lexicon: dict[str, tuple[str, ...]],
    intent: str | None,
    slots: tuple[tuple[str, str], ...],
) -> str | None:
    if intent is None:
        return None
    wanted = dict(slots)
    for item in bundle.ordered():
        frame = frame_is_complete(assess(item.text, lexicon))
        if frame is None:
            continue
        got_intent, got_slots = frame
        if got_intent == intent and got_slots == wanted:
            return item.candidate_id
    return None


def v4_source(
    bundle: CandidateBundle,
    lexicon: dict[str, tuple[str, ...]],
    intent: str | None,
    slots: tuple[tuple[str, str], ...],
    switches: PolicySwitches,
) -> str | None:
    if intent is None:
        return None
    wanted = dict(slots)
    for item in bundle.ordered():
        assessment = assess_v4(item.candidate_id, item.text, item.provenance, lexicon)
        if switches.polarity and assessment.polarity != "affirmative":
            continue
        if switches.modality and assessment.modality != "certain":
            continue
        if assessment.context_dependencies:
            continue
        if switches.ambiguity and assessment.ambiguity != "none":
            continue
        if switches.contradiction and assessment.contradictions:
            continue
        if len(assessment.intent_hypotheses) != 1:
            continue
        if assessment.completeness != "complete":
            continue
        if assessment.intent_hypotheses[0] != intent:
            continue
        got: dict[str, str] = {}
        failed = False
        for name in CRITICAL_SLOTS[intent]:
            values = [value for slot_name, value in assessment.slot_hypotheses if slot_name == name]
            if len(values) != 1:
                failed = True
                break
            got[name] = values[0]
        if not failed and got == wanted:
            return item.candidate_id
    return None


def action_path_consistent(
    strategy: str,
    action: str | None,
    committed: bool,
    candidate_id: str | None,
    bundle_ids: set[str],
) -> bool:
    """Prefix strategies have no recovery action. A commit from them is still a commit."""

    if strategy in {"b0_prefix", "b1_prefix"}:
        return True
    if strategy == "b1_forced_lexical":
        return not committed
    if action in {"HOLD", "CLARIFY"}:
        return not committed
    if action in {"CONTINUE", "RETRY"}:
        return committed and candidate_id in bundle_ids
    return not committed
