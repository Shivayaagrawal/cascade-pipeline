"""Coverage, selective risk, and the v3 recovery contract.

Gold labels are used only while scoring. Selectors do not receive them.
"""

from __future__ import annotations

from cascadeguard.asr.base import REFERENCE_PASSTHROUGH, SYNTHETIC_EDIT, Hypothesis
from cascadeguard.candidates.candidate_manager import score_hypothesis, select_candidate
from cascadeguard.evaluation.intent_metrics import frames_equal, intent_accuracy
from cascadeguard.evaluation.rates import rate
from cascadeguard.evaluation.semantic_evidence import CRITICAL_SLOTS, assess, frame_is_complete
from cascadeguard.evaluation.selective import (
    RecoveryAction,
    SelectiveAction,
    SelectiveDecision,
    candidate_disagrees,
    forced_selection,
    gold_slots_missing,
    lexical_frame_preserved,
    recovery_action,
)
from cascadeguard.evaluation.semantic_evidence import intent_hits
from cascadeguard.evaluation.slot_metrics import slot_scores
from cascadeguard.simulation.utterance_generator import Utterance


def candidate_information(
    utterances: list[Utterance],
    grouped: dict[str, list[str]],
    lexicon: dict[str, tuple[str, ...]],
) -> dict[str, object]:
    """Information present in a candidate list. The gold transcript is not added."""

    intent_hits_n = 0
    slot_hits_n = 0
    frame_hits_n = 0
    disagree_n = 0
    missing_n = 0
    for utterance in utterances:
        candidates = grouped[utterance.utterance_id]
        if any(utterance.intent in intent_hits(text) for text in candidates):
            intent_hits_n += 1
        if not gold_slots_missing(utterance, candidates):
            slot_hits_n += 1
        if any(lexical_frame_preserved(utterance, text) for text in candidates):
            frame_hits_n += 1
        if candidate_disagrees(candidates, lexicon):
            disagree_n += 1
        if gold_slots_missing(utterance, candidates):
            missing_n += 1
    count = len(utterances)
    return {
        "candidate_oracle_intent_coverage": rate(intent_hits_n, count, "no utterances"),
        "candidate_oracle_slot_coverage": rate(slot_hits_n, count, "no utterances"),
        "complete_frame_oracle_coverage": rate(frame_hits_n, count, "no utterances"),
        "candidate_disagreement": rate(disagree_n, count, "no utterances"),
        "missing_gold_slots": rate(missing_n, count, "no utterances"),
        "utterances_with_no_complete_frame": count - frame_hits_n,
        "gold_transcript_included": False,
    }


def expected_recovery(
    utterance: Utterance,
    primary: list[str],
    retry: list[str] | None = None,
) -> str:
    """Expected action from the gold frame and the candidate strings.

    This label does not read the selective decision.

    1. A primary candidate that preserves the gold intent and every gold slot
       value expects CONTINUE.
    2. Otherwise a supplied retry bundle that preserves that frame expects RETRY.
       Without a retry bundle this step does not apply.
    3. Otherwise an intent cue with a missing gold slot, a split across candidates,
       or more than one intent cue in a candidate expects CLARIFY.
    4. Otherwise HOLD.
    """

    if any(lexical_frame_preserved(utterance, text) for text in primary):
        return RecoveryAction.CONTINUE.value
    if retry is not None and any(lexical_frame_preserved(utterance, text) for text in retry):
        return RecoveryAction.RETRY.value
    intent_somewhere = any(utterance.intent in intent_hits(text) for text in primary)
    slots_missing = bool(gold_slots_missing(utterance, primary))
    ambiguous = any(len(intent_hits(text)) > 1 for text in primary)
    split = intent_somewhere and not slots_missing
    if ambiguous or (intent_somewhere and slots_missing) or split:
        return RecoveryAction.CLARIFY.value
    return RecoveryAction.HOLD.value


def slot_critical_mismatch(utterance: Utterance, decision: SelectiveDecision) -> bool:
    """True when a commit is missing a critical slot or carries a different value."""

    if decision.action is not SelectiveAction.COMMIT or decision.intent is None:
        return False
    if decision.intent != utterance.intent:
        return True
    for name in CRITICAL_SLOTS[utterance.intent]:
        gold_value = utterance.slots.get(name)
        predicted = decision.slots.get(name)
        if gold_value is None:
            if predicted is not None:
                return True
            continue
        if predicted is None or predicted.casefold() != gold_value.casefold():
            return True
    return False


def _frame_rows(
    utterances: list[Utterance],
    frames: list[tuple[str | None, dict[str, str]]],
) -> dict[str, object]:
    pairs = [(utterance.intent, frame[0]) for utterance, frame in zip(utterances, frames, strict=True)]
    slot_rows = [(utterance.slots, frame[1]) for utterance, frame in zip(utterances, frames, strict=True)]
    exact = [
        (utterance.intent, utterance.slots, frame[0], frame[1])
        for utterance, frame in zip(utterances, frames, strict=True)
    ]
    correct = sum(
        1
        for utterance, frame in zip(utterances, frames, strict=True)
        if frames_equal(utterance.intent, utterance.slots, frame[0], frame[1])
    )
    return {
        "intent_accuracy": intent_accuracy(pairs),
        "slot_f1": slot_scores(slot_rows)["f1"],
        "slot_scores": slot_scores(slot_rows),
        "exact_frame_accuracy": rate(correct, len(utterances), "no utterances"),
    }


def b1_frames(
    utterances: list[Utterance],
    grouped: dict[str, list[str]],
) -> list[tuple[str | None, dict[str, str]]]:
    """Existing prefix-cue selector. It does not read gold labels."""

    frames = []
    for utterance in utterances:
        hypotheses = tuple(
            Hypothesis(text, SYNTHETIC_EDIT, index)
            for index, text in enumerate(grouped[utterance.utterance_id])
        )
        chosen = select_candidate(hypotheses)
        frames.append((chosen.intent, chosen.slots))
    return frames


def selective_report(
    utterances: list[Utterance],
    grouped: dict[str, list[str]],
    lexicon: dict[str, tuple[str, ...]],
    *,
    retry_grouped: dict[str, list[str]] | None = None,
    min_support: int = 1,
    b0_exact: int | None = None,
) -> dict[str, object]:
    """Score commit, clarify, and hold. Accuracy is always paired with coverage."""

    decisions: list[SelectiveDecision] = []
    actions: list[str] = []
    mechanisms: list[str] = []
    expected: list[str] = []
    for utterance in utterances:
        primary = grouped[utterance.utterance_id]
        retry = None if retry_grouped is None else retry_grouped[utterance.utterance_id]
        action, decision, mechanism = recovery_action(
            primary,
            lexicon,
            retry_candidates=retry,
            min_support=min_support,
        )
        decisions.append(decision)
        actions.append(action.value)
        mechanisms.append(mechanism)
        expected.append(expected_recovery(utterance, primary, retry))

    # CONTINUE commits the primary frame. RETRY commits the second bundle's frame.
    # CLARIFY and HOLD do not commit.
    committed_rows = []
    forced_frames = []
    abstaining_frames = []
    for utterance, decision, action in zip(utterances, decisions, actions, strict=True):
        forced_frames.append(forced_selection(grouped[utterance.utterance_id], lexicon))
        if action in {RecoveryAction.CONTINUE.value, RecoveryAction.RETRY.value}:
            committed_rows.append((utterance, decision))
            abstaining_frames.append((decision.intent, decision.slots))
        else:
            abstaining_frames.append((None, {}))

    unsafe = 0
    slot_critical = 0
    correct_commits = 0
    for utterance, decision in committed_rows:
        matches = frames_equal(utterance.intent, utterance.slots, decision.intent, decision.slots)
        if matches:
            correct_commits += 1
        else:
            unsafe += 1
        if slot_critical_mismatch(utterance, decision):
            slot_critical += 1

    clarify_predicted = [
        (utterance, action, label)
        for utterance, action, label in zip(utterances, actions, expected, strict=True)
        if action == RecoveryAction.CLARIFY.value
    ]
    clarify_expected = [
        (utterance, action, label)
        for utterance, action, label in zip(utterances, actions, expected, strict=True)
        if label == RecoveryAction.CLARIFY.value
    ]
    clarify_true = sum(1 for _, action, label in clarify_predicted if label == action)
    clarify_found = sum(1 for _, action, label in clarify_expected if action == label)
    action_matches = sum(
        1 for action, label in zip(actions, expected, strict=True) if action == label
    )
    count = len(utterances)
    b0_rate = None if b0_exact is None else rate(b0_exact, count, "no utterances")
    achieved = rate(correct_commits, count, "no utterances")
    gain = None
    if b0_rate is not None and achieved["value"] is not None and b0_rate["value"] is not None:
        gain = achieved["value"] - b0_rate["value"]
    committed_frames = [(item[1].intent, item[1].slots) for item in committed_rows]
    committed_utterances = [item[0] for item in committed_rows]
    return {
        "decision_coverage": rate(
            len(committed_rows),
            count,
            "no utterances",
        ),
        "selective_risk": rate(
            unsafe,
            len(committed_rows),
            "no committed decisions; refusing every input is not a reliability score",
        ),
        "unsafe_commitment": rate(
            unsafe,
            len(committed_rows),
            "no CONTINUE or simulated RETRY committed a frame",
        ),
        "slot_critical_unsafe_commitment": rate(
            slot_critical,
            len(committed_rows),
            "no CONTINUE or simulated RETRY committed a frame",
        ),
        "accuracy_on_committed_decisions": (
            _frame_rows(committed_utterances, committed_frames) if committed_rows else None
        ),
        "accuracy_counting_abstention_as_incorrect": _frame_rows(utterances, abstaining_frames),
        "clarification_precision": rate(
            clarify_true,
            len(clarify_predicted),
            "no CLARIFY decisions",
        ),
        "clarification_recall": rate(
            clarify_found,
            len(clarify_expected),
            "no utterance expected CLARIFY",
        ),
        "action_accuracy": rate(action_matches, count, "no utterances"),
        "recovery_gain_over_b0": {
            "value": gain,
            "achieved_exact_frames_over_all_inputs": achieved,
            "b0_exact_frames": b0_rate,
            "definition": (
                "Exact-frame rate of committed correct decisions, with abstention "
                "counted as not correct, minus the B0 exact-frame rate on the same ids."
            ),
        },
        "action_counts": {
            action: sum(1 for item in actions if item == action)
            for action in ("CONTINUE", "RETRY", "CLARIFY", "HOLD")
        },
        "retry_mechanism_counts": {
            "simulated_candidate_rescore": sum(1 for item in mechanisms if item == "simulated_candidate_rescore"),
            "primary_bundle": sum(1 for item in mechanisms if item == "primary_bundle"),
        },
        "forced_slot_aware_selector": _frame_rows(utterances, forced_frames),
        "b1_selector": _frame_rows(utterances, b1_frames(utterances, grouped)),
        "min_support": min_support,
        "asr_decode": False,
    }


def risk_coverage_curve(
    utterances: list[Utterance],
    grouped: dict[str, list[str]],
    lexicon: dict[str, tuple[str, ...]],
    supports: tuple[int, ...] = (1, 2, 3),
) -> list[dict[str, object]]:
    """Coverage and selective risk at each agreement level, plus always-HOLD."""

    points = []
    for support in supports:
        report = selective_report(utterances, grouped, lexicon, min_support=support)
        points.append(
            {
                "rule": f"min_support_{support}",
                "decision_coverage": report["decision_coverage"],
                "selective_risk": report["selective_risk"],
                "unsafe_commitment": report["unsafe_commitment"],
                "slot_critical_unsafe_commitment": report["slot_critical_unsafe_commitment"],
            }
        )
    points.append(
        {
            "rule": "always_hold",
            "decision_coverage": rate(0, len(utterances), "no utterances"),
            "selective_risk": rate(
                0,
                0,
                "no committed decisions; an always-HOLD system has no reliability score",
            ),
            "unsafe_commitment": rate(0, 0, "no committed decisions"),
            "slot_critical_unsafe_commitment": rate(0, 0, "no committed decisions"),
        }
    )
    return points


def b0_exact_count(utterances: list[Utterance], grouped: dict[str, list[str]]) -> int:
    """Exact frames from the first candidate only, using the prefix parser."""

    correct = 0
    for utterance in utterances:
        scored = score_hypothesis(Hypothesis(grouped[utterance.utterance_id][0], SYNTHETIC_EDIT, 0))
        if frames_equal(utterance.intent, utterance.slots, scored.intent, scored.slots):
            correct += 1
    return correct


def gold_transcript_oracle(
    utterances: list[Utterance],
    lexicon: dict[str, tuple[str, ...]],
) -> dict[str, object]:
    """Score the reference text alone. This condition is not a candidate list."""

    lexical_frames = []
    prefix_frames = []
    for utterance in utterances:
        completed = frame_is_complete(assess(utterance.text, lexicon))
        if completed is None:
            lexical_frames.append((None, {}))
        else:
            lexical_frames.append(completed)
        scored = score_hypothesis(Hypothesis(utterance.text, REFERENCE_PASSTHROUGH, 0))
        prefix_frames.append((scored.intent, scored.slots))
    return {
        "gold_transcript_included": True,
        "label": "separate condition; the gold transcript is not added to ordinary candidate lists",
        "lexical_evidence": _frame_rows(utterances, lexical_frames),
        "prefix_nlu": _frame_rows(utterances, prefix_frames),
    }


def category_selective_report(
    utterances: list[Utterance],
    grouped: dict[str, list[str]],
    lexicon: dict[str, tuple[str, ...]],
    categories: dict[str, str],
) -> dict[str, object]:
    """Run the selective layer inside each corruption category."""

    by_category: dict[str, list[Utterance]] = {}
    for utterance in utterances:
        by_category.setdefault(categories[utterance.utterance_id], []).append(utterance)
    report = {}
    for category, rows in by_category.items():
        subset = {row.utterance_id: grouped[row.utterance_id] for row in rows}
        information = candidate_information(rows, subset, lexicon)
        selected = selective_report(rows, subset, lexicon)
        report[category] = {
            "n": len(rows),
            "candidate_oracle_intent_coverage": information["candidate_oracle_intent_coverage"],
            "candidate_oracle_slot_coverage": information["candidate_oracle_slot_coverage"],
            "complete_frame_oracle_coverage": information["complete_frame_oracle_coverage"],
            "intent_accuracy": selected["accuracy_counting_abstention_as_incorrect"]["intent_accuracy"],
            "slot_f1": selected["accuracy_counting_abstention_as_incorrect"]["slot_f1"],
            "exact_frame_accuracy": selected["accuracy_counting_abstention_as_incorrect"]["exact_frame_accuracy"],
            "decision_coverage": selected["decision_coverage"],
            "selective_risk": selected["selective_risk"],
            "unsafe_commitment": selected["unsafe_commitment"],
            "slot_critical_unsafe_commitment": selected["slot_critical_unsafe_commitment"],
            "intent_accuracy_on_committed_decisions": (
                None
                if selected["accuracy_on_committed_decisions"] is None
                else selected["accuracy_on_committed_decisions"]["intent_accuracy"]
            ),
        }
    return report
