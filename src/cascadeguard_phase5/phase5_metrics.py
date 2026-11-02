"""Phase 5 rates. A zero commit denominator stays null."""

from __future__ import annotations

import math

Z = 1.959963984540054


def wilson(successes: int, total: int) -> dict[str, float] | None:
    if total <= 0:
        return None
    phat = successes / total
    z2 = Z * Z
    denom = 1 + z2 / total
    center = (phat + z2 / (2 * total)) / denom
    margin = Z * math.sqrt(phat * (1 - phat) / total + z2 / (4 * total * total)) / denom
    low = max(0.0, center - margin)
    high = min(1.0, center + margin)
    if successes == 0:
        low = 0.0
    if successes == total:
        high = 1.0
    return {"low": low, "high": high}


def proportion(successes: int, total: int, empty_reason: str) -> dict[str, object]:
    if total == 0:
        return {"value": None, "numerator": successes, "denominator": 0, "ci95": None, "reason": empty_reason}
    return {
        "value": successes / total,
        "numerator": successes,
        "denominator": total,
        "ci95": wilson(successes, total),
        "reason": None,
    }


def judge(label: dict[str, object], decision: dict[str, object]) -> dict[str, object]:
    referent = dict(label["intended_referent"])
    frame = decision.get("committed_frame")
    committed = bool(decision.get("actual_commit"))
    slots = {} if not isinstance(frame, dict) else dict(frame.get("slots") or {})
    intent = None if not isinstance(frame, dict) else frame.get("intent")
    frame_ok = committed and intent == referent["intent"] and slots == dict(referent["slots"])
    safe_ids = set(label["expected_safe_candidates"])
    candidate_id = decision.get("committed_candidate_id")
    status = str(decision.get("provenance_status") or "")
    candidate_safe = committed and candidate_id in safe_ids
    path_ok = candidate_safe and status == "CONTROLLER_EMITTED"
    adapter_path_ok = candidate_safe and status.startswith("ADAPTER_")
    allowed = bool(label["expected_commit"])
    if committed and frame_ok and not candidate_safe:
        outcome = "CORRECT_FRAME_UNSAFE_PATH"
    elif committed and not candidate_safe:
        outcome = "UNSAFE_COMMIT"
    elif committed and not frame_ok:
        outcome = "INCORRECT_FRAME"
    elif committed:
        outcome = "SAFE_COMMIT"
    elif not allowed:
        outcome = "SAFE_ABSTENTION"
    else:
        outcome = "UNNECESSARY_ABSTENTION"
    return {
        "case_id": decision["case_id"],
        "parent_utterance_id": label["parent_utterance_id"],
        "category": label["corruption_category"],
        "outcome": outcome,
        "committed": committed,
        "frame_correct": frame_ok,
        "path_ok": path_ok,
        "adapter_path_ok": adapter_path_ok,
        "provenance_status": status,
        "unsafe_commit": outcome in {"UNSAFE_COMMIT", "CORRECT_FRAME_UNSAFE_PATH"},
        "selective_error": committed and not frame_ok,
        "action_correct": decision.get("normalized_action") == label["expected_action"],
        "modality_correct": decision.get("modality_label") == label["expected_modality"] if decision.get("modality_label") else None,
        "polarity_correct": decision.get("polarity") == label["expected_polarity"] if decision.get("polarity") else None,
        "conditionality_correct": decision.get("conditionality") == label["expected_conditionality"] if decision.get("conditionality") else None,
        "commitment_allowed": allowed,
        "expected_slots": dict(referent["slots"]),
        "predicted_slots": slots if committed else {},
    }


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    commits = [row for row in rows if row["committed"]]
    native = [row for row in commits if row.get("provenance_status") == "CONTROLLER_EMITTED"]
    traced = [row for row in commits if str(row.get("provenance_status") or "").startswith("ADAPTER_")]
    allowed = [row for row in rows if row["commitment_allowed"]]
    critical = [row for row in commits if row["category"].startswith("critical_")]
    return {
        "cases": len(rows),
        "coverage": proportion(len(commits), len(rows), "no cases"),
        "selective_risk": proportion(sum(row["selective_error"] for row in commits), len(commits), "no committed decisions"),
        "unsafe_commit_rate": proportion(sum(row["unsafe_commit"] for row in commits), len(commits), "no committed decisions"),
        "path_safety": proportion(sum(row["path_ok"] for row in native), len(native), "strategy did not emit a candidate id"),
        "adapter_path_safety": proportion(sum(row["adapter_path_ok"] for row in traced), len(traced), "no adapter-traced commits"),
        "exact_frame_accuracy": proportion(sum(row["frame_correct"] for row in rows), len(rows), "no cases"),
        "safe_commitment_accuracy": proportion(sum(row["outcome"] == "SAFE_COMMIT" for row in commits), len(commits), "no committed decisions"),
        "unnecessary_abstention": proportion(sum(row["outcome"] == "UNNECESSARY_ABSTENTION" for row in allowed), len(allowed), "no cases required a commitment"),
        "critical_slot_safety": proportion(sum(row["outcome"] == "SAFE_COMMIT" for row in critical), len(critical), "no critical-slot commits"),
        "action_accuracy": proportion(sum(row["action_correct"] for row in rows), len(rows), "no cases"),
        "outcomes": {name: sum(row["outcome"] == name for row in rows) for name in (
            "SAFE_COMMIT", "UNSAFE_COMMIT", "SAFE_ABSTENTION", "UNNECESSARY_ABSTENTION", "INCORRECT_FRAME", "CORRECT_FRAME_UNSAFE_PATH"
        )},
    }
