"""Proportions with Wilson intervals. A zero denominator stays null."""

from __future__ import annotations

import math

from cascadeguard_phase4.independent_evaluator import UNSAFE_OUTCOMES

Z = 1.959963984540054


def wilson(successes: int, total: int) -> dict[str, float] | None:
    if total <= 0:
        return None
    phat = successes / total
    z2 = Z * Z
    denom = 1 + z2 / total
    center = (phat + z2 / (2 * total)) / denom
    margin = Z * math.sqrt(phat * (1 - phat) / total + z2 / (4 * total * total)) / denom
    return {"low": max(0.0, center - margin), "high": min(1.0, center + margin)}


def proportion(successes: int, total: int, empty_reason: str) -> dict[str, object]:
    if total == 0:
        return {
            "value": None,
            "numerator": successes,
            "denominator": 0,
            "percentage": None,
            "ci95": None,
            "reason": empty_reason,
        }
    return {
        "value": successes / total,
        "numerator": successes,
        "denominator": total,
        "percentage": 100 * successes / total,
        "ci95": wilson(successes, total),
        "reason": None,
    }


def _slot_scores(rows: list[dict[str, object]]) -> dict[str, float | int]:
    matched = predicted = reference = 0
    for row in rows:
        expected = set(dict(row["expected_slots"]).items())
        predicted_pairs = set(dict(row["predicted_slots"]).items()) if row["committed"] else set()
        matched += len(expected & predicted_pairs)
        predicted += len(predicted_pairs)
        reference += len(expected)
    precision = matched / predicted if predicted else None
    recall = matched / reference if reference else None
    if precision is None or recall is None or precision + recall == 0:
        f1 = None
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "matched_pairs": matched,
        "predicted_pairs": predicted,
        "reference_pairs": reference,
    }


def summarize(rows: list[dict[str, object]], *, category: str | None = None) -> dict[str, object]:
    chosen = [row for row in rows if category is None or row["category"] == category]
    count = len(chosen)
    commits = [row for row in chosen if row["committed"]]
    allowed = [row for row in chosen if row["commitment_allowed"]]
    critical = [
        row
        for row in commits
        if row["category"]
        in {
            "critical_slot_mutation",
            "temporal_numerical_conflict",
            "contradictory_candidates",
        }
    ]
    polarity_rows = [row for row in chosen if row["polarity_correct"] is not None]
    modality_rows = [row for row in chosen if row["modality_correct"] is not None]
    return {
        "cases": count,
        "category": category,
        "coverage": proportion(len(commits), count, "no cases"),
        "selective_risk": proportion(
            sum(bool(row["selective_error"]) for row in commits),
            len(commits),
            "no committed decisions; abstention is not a selective error",
        ),
        "unsafe_commit_rate": proportion(
            sum(bool(row["unsafe_commit"]) for row in commits),
            len(commits),
            "no committed decisions; abstention is not an unsafe commit",
        ),
        "path_safety": proportion(
            sum(bool(row["candidate_safe"]) for row in commits),
            len(commits),
            "no committed candidate paths",
        ),
        "unsafe_selection_rate": proportion(
            sum(not bool(row["candidate_safe"]) for row in commits),
            len(commits),
            "no committed candidate paths",
        ),
        "safe_commitment_accuracy": proportion(
            sum(row["outcome"] == "SAFE_COMMIT" for row in commits),
            len(commits),
            "no committed decisions",
        ),
        "correct_candidate_commitment": proportion(
            sum(row["outcome"] == "SAFE_COMMIT" for row in allowed),
            len(allowed),
            "no cases required a commitment",
        ),
        "unnecessary_abstention": proportion(
            sum(row["outcome"] == "UNNECESSARY_ABSTENTION" for row in allowed),
            len(allowed),
            "no cases required a commitment",
        ),
        "action_path_consistency": proportion(
            sum(row["outcome"] != "INVALID_ACTION_PATH" for row in chosen),
            count,
            "no cases",
        ),
        "exact_frame_accuracy": proportion(
            sum(bool(row["frame_correct"]) for row in chosen),
            count,
            "no cases",
        ),
        "action_accuracy": proportion(
            sum(bool(row["action_correct"]) for row in chosen),
            count,
            "no cases",
        ),
        "polarity_accuracy": proportion(
            sum(bool(row["polarity_correct"]) for row in polarity_rows),
            len(polarity_rows),
            "strategy does not represent polarity",
        ),
        "modality_accuracy": proportion(
            sum(bool(row["modality_correct"]) for row in modality_rows),
            len(modality_rows),
            "strategy does not represent modality",
        ),
        "critical_slot_safety": proportion(
            sum(row["outcome"] == "SAFE_COMMIT" for row in critical),
            len(critical),
            "no commits on critical-slot categories; this is not a perfect score",
        ),
        "outcomes": {name: sum(row["outcome"] == name for row in chosen) for name in (
            "SAFE_COMMIT",
            "UNSAFE_COMMIT",
            "SAFE_ABSTENTION",
            "UNNECESSARY_ABSTENTION",
            "INVALID_ACTION_PATH",
            "INCORRECT_FRAME",
            "CORRECT_FRAME_UNSAFE_PATH",
        )},
        "unsafe_outcomes_included": sorted(UNSAFE_OUTCOMES),
        "slot_scores": _slot_scores(chosen),
    }
