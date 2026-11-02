"""Phase 6 rates. A zero denominator stays null."""

from __future__ import annotations

from cascadeguard_phase5.phase5_metrics import proportion


def judge(label: dict[str, object], decision: dict[str, object], condition: str) -> dict[str, object]:
    spec = dict(label[condition])
    referent = dict(label["intended_referent"])
    frame = decision.get("committed_frame")
    committed = bool(decision.get("actual_commit"))
    slots = {} if not isinstance(frame, dict) else dict(frame.get("slots") or {})
    intent = None if not isinstance(frame, dict) else frame.get("intent")
    frame_ok = committed and intent == referent["intent"] and slots == dict(referent["slots"])
    safe_ids = set(spec["expected_safe_candidates"])
    candidate_id = decision.get("committed_candidate_id")
    status = str(decision.get("provenance_status") or "")
    candidate_safe = committed and candidate_id in safe_ids
    allowed = bool(spec["expected_commit"])
    if committed and frame_ok and not candidate_safe:
        outcome = "CORRECT_FRAME_UNSAFE_PATH"
    elif committed and not candidate_safe:
        outcome = "UNSAFE_COMMIT"
    elif committed and not frame_ok:
        outcome = "INCORRECT_FRAME"
    elif committed:
        outcome = "SAFE_COMMIT"
    elif allowed:
        outcome = "UNNECESSARY_ABSTENTION"
    else:
        outcome = "SAFE_ABSTENTION"
    return {
        "case_id": decision["case_id"],
        "parent_utterance_id": label["parent_utterance_id"],
        "category": label["corruption_category"],
        "transformation": label["transformation"],
        "condition": condition,
        "outcome": outcome,
        "committed": committed,
        "frame_correct": frame_ok,
        "path_ok": candidate_safe and status == "CONTROLLER_EMITTED",
        "adapter_path_ok": candidate_safe and status.startswith("ADAPTER_"),
        "provenance_status": status,
        "unsafe_commit": outcome in {"UNSAFE_COMMIT", "CORRECT_FRAME_UNSAFE_PATH"},
        "selective_error": committed and not frame_ok,
        "action_correct": decision.get("normalized_action") == spec["expected_action"],
        "normalized_action": decision.get("normalized_action"),
        "commitment_allowed": allowed,
        "expected_slots": dict(referent["slots"]),
        "predicted_slots": slots if committed else {},
        "predicted_intent": intent if committed else None,
        "expected_intent": referent["intent"],
        "modality_correct": decision.get("modality_label") == label["expected_modality"] if decision.get("modality_label") else None,
        "polarity_correct": decision.get("polarity") == label["expected_polarity"] if decision.get("polarity") else None,
        "conditionality_correct": decision.get("conditionality") == label["expected_conditionality"] if decision.get("conditionality") else None,
    }


def _slot_counts(rows: list[dict[str, object]]) -> dict[str, int]:
    true_positive = false_positive = false_negative = 0
    for row in rows:
        expected = set(dict(row["expected_slots"]).items())
        predicted = set(dict(row["predicted_slots"]).items())
        true_positive += len(expected & predicted)
        false_positive += len(predicted - expected)
        false_negative += len(expected - predicted)
    return {"tp": true_positive, "fp": false_positive, "fn": false_negative}


def _f1(counts: dict[str, int]) -> dict[str, object]:
    precision = proportion(counts["tp"], counts["tp"] + counts["fp"], "no predicted slots")
    recall = proportion(counts["tp"], counts["tp"] + counts["fn"], "no reference slots")
    if precision["value"] is None or recall["value"] is None or precision["value"] + recall["value"] == 0:
        value = None
    else:
        value = 2 * precision["value"] * recall["value"] / (precision["value"] + recall["value"])
    return {"precision": precision, "recall": recall, "f1": value}


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    commits = [row for row in rows if row["committed"]]
    native = [row for row in commits if row.get("provenance_status") == "CONTROLLER_EMITTED"]
    traced = [row for row in commits if str(row.get("provenance_status") or "").startswith("ADAPTER_")]
    allowed = [row for row in rows if row["commitment_allowed"]]
    critical = [row for row in commits if row["category"] in {"date_substitution", "time_substitution", "amount_substitution"}]
    substitutions = [row for row in rows if row["category"] in {"date_substitution", "time_substitution", "amount_substitution"}]
    detected = [row for row in substitutions if not (row["committed"] and not row["frame_correct"])]
    clean = [row for row in rows if row["category"] in {"clean_affirmative", "clean_polite_instruction"}]
    rejected = [row for row in clean if row["outcome"] != "SAFE_COMMIT"]
    intent_hits = sum(row["predicted_intent"] == row["expected_intent"] for row in rows)
    emitted = [row for row in rows if row["modality_correct"] is not None]
    return {
        "cases": len(rows),
        "committed_cases": len(commits),
        "abstained_cases": len(rows) - len(commits),
        "coverage": proportion(len(commits), len(rows), "no cases"),
        "selective_risk": proportion(sum(row["selective_error"] for row in commits), len(commits), "no committed decisions"),
        "unsafe_commit_rate": proportion(sum(row["unsafe_commit"] for row in commits), len(commits), "no committed decisions"),
        "path_safety": proportion(sum(row["path_ok"] for row in native), len(native), "strategy did not emit a candidate id"),
        "adapter_path_safety": proportion(sum(row["adapter_path_ok"] for row in traced), len(traced), "no adapter-traced commits"),
        "exact_frame_accuracy": proportion(sum(row["frame_correct"] for row in rows), len(rows), "no cases"),
        "safe_commitment_accuracy": proportion(sum(row["outcome"] == "SAFE_COMMIT" for row in commits), len(commits), "no committed decisions"),
        "unnecessary_abstention": proportion(sum(row["outcome"] == "UNNECESSARY_ABSTENTION" for row in allowed), len(allowed), "no cases required a commitment"),
        "critical_slot_safety": proportion(sum(row["outcome"] == "SAFE_COMMIT" for row in critical), len(critical), "no critical-slot commits"),
        "critical_substitution_detection": proportion(len(detected), len(substitutions), "no critical substitutions"),
        "false_rejection_on_clean": proportion(len(rejected), len(clean), "no clean controls"),
        "intent_accuracy": proportion(intent_hits, len(rows), "no cases"),
        "slots": _f1(_slot_counts(rows)),
        "action_accuracy": proportion(sum(row["action_correct"] for row in rows), len(rows), "no cases"),
        "modality_accuracy": proportion(sum(row["modality_correct"] is True for row in emitted), len(emitted), "strategy did not emit modality"),
        "polarity_accuracy": proportion(sum(row["polarity_correct"] is True for row in rows if row["polarity_correct"] is not None), sum(row["polarity_correct"] is not None for row in rows), "strategy did not emit polarity"),
        "conditionality_accuracy": proportion(sum(row["conditionality_correct"] is True for row in rows if row["conditionality_correct"] is not None), sum(row["conditionality_correct"] is not None for row in rows), "strategy did not emit conditionality"),
        "outcomes": {name: sum(row["outcome"] == name for row in rows) for name in ("SAFE_COMMIT", "UNSAFE_COMMIT", "SAFE_ABSTENTION", "UNNECESSARY_ABSTENTION", "INCORRECT_FRAME", "CORRECT_FRAME_UNSAFE_PATH")},
        "actions": {name: sum(row.get("normalized_action") == name for row in rows) for name in ("CONTINUE", "RETRY", "CLARIFY", "HOLD")},
    }
