"""Score controller outputs against frozen oracle labels. Does not diagnose text itself."""

from __future__ import annotations

OUTCOMES = (
    "SAFE_COMMIT",
    "UNSAFE_COMMIT",
    "SAFE_ABSTENTION",
    "UNNECESSARY_ABSTENTION",
    "INVALID_ACTION_PATH",
    "INCORRECT_FRAME",
    "CORRECT_FRAME_UNSAFE_PATH",
)

UNSAFE_OUTCOMES = frozenset({"UNSAFE_COMMIT", "CORRECT_FRAME_UNSAFE_PATH"})


def frames_equal(
    expected_intent: str | None,
    expected_slots: dict[str, str],
    intent: str | None,
    slots: dict[str, str],
) -> bool:
    return intent == expected_intent and dict(expected_slots) == dict(slots)


def judge_output(label: dict[str, object], decision: dict[str, object]) -> dict[str, object]:
    committed = bool(decision["committed"])
    intent = decision.get("committed_intent")
    raw_slots = decision.get("committed_slots") or {}
    slots = dict(raw_slots)
    candidate_id = decision.get("committed_candidate_id")
    safe_ids = set(label["expected_safe_candidates"])
    frame_ok = committed and frames_equal(
        str(label["expected_intent"]),
        dict(label["expected_slots"]),
        None if intent is None else str(intent),
        slots,
    )
    candidate_safe = committed and candidate_id in safe_ids
    consistent = bool(decision["action_path_consistent"])
    if not consistent:
        outcome = "INVALID_ACTION_PATH"
    elif committed and frame_ok and not candidate_safe:
        outcome = "CORRECT_FRAME_UNSAFE_PATH"
    elif committed and not candidate_safe:
        outcome = "UNSAFE_COMMIT"
    elif committed and not frame_ok:
        outcome = "INCORRECT_FRAME"
    elif committed:
        outcome = "SAFE_COMMIT"
    elif not label["expected_commitment"]:
        outcome = "SAFE_ABSTENTION"
    else:
        outcome = "UNNECESSARY_ABSTENTION"
    properties = label.get("candidate_properties") or {}
    if committed and candidate_id in properties:
        polarity_target = properties[candidate_id]["polarity"]
        modality_target = properties[candidate_id]["modality"]
    else:
        polarity_target = label["expected_polarity"]
        modality_target = label["expected_modality"]
    emitted_polarity = decision.get("emitted_polarity")
    emitted_modality = decision.get("emitted_modality")
    return {
        "case_id": decision["case_id"],
        "strategy_id": decision["strategy_id"],
        "outcome": outcome,
        "committed": committed,
        "frame_correct": frame_ok,
        "candidate_safe": candidate_safe,
        "selective_error": committed and not frame_ok,
        "unsafe_commit": outcome in UNSAFE_OUTCOMES,
        "action_correct": decision.get("action") == label["expected_action"],
        "polarity_correct": None if emitted_polarity is None else emitted_polarity == polarity_target,
        "modality_correct": None if emitted_modality is None else emitted_modality == modality_target,
        "commitment_allowed": bool(label["expected_commitment"]),
        "category": label.get("case_category"),
        "parent_id": label.get("parent_id"),
    }
