"""Score Phase 3 decisions. Coverage is never returned without selective risk."""

from __future__ import annotations

from cascadeguard.evaluation.intent_metrics import frames_equal
from cascadeguard.evaluation.rates import rate
from cascadeguard.evaluation.slot_metrics import slot_scores


def _slots(text: str) -> dict[str, str]:
    if not text.strip():
        return {}
    parsed = {}
    for part in text.split("|"):
        name, value = part.split("=", 1)
        parsed[name] = value
    return parsed


def summarize(rows: list[dict[str, object]], *, polarity_available: bool) -> dict[str, object]:
    count = len(rows)
    commits = [row for row in rows if row["committed"]]
    unsafe = [row for row in commits if row["unsafe"]]
    selective = [row for row in commits if row["selective_error"]]
    safe_hits = [row for row in commits if row["safe_commit"]]
    slot_rows = [
        (_slots(str(row["expected_slots"])), _slots(str(row["committed_slots"])))
        for row in rows
    ]
    intent_correct = sum(bool(row["intent_correct"]) for row in rows)
    exact = sum(bool(row["exact_frame"]) for row in rows)
    action_correct = sum(bool(row["action_correct"]) for row in rows)
    retry_attempts = [row for row in rows if row["action"] == "RETRY"]
    retry_success = [row for row in retry_attempts if row["retry_success"]]
    polarity_hits = [row for row in rows if row["polarity_correct"]]
    ambiguity_predicted = [row for row in rows if row["predicted_ambiguity"]]
    ambiguity_gold = [row for row in rows if row["expected_ambiguity"] == "competing"]
    ambiguity_true_positive = [
        row for row in ambiguity_gold if row["predicted_ambiguity"]
    ]
    contradiction_gold = [row for row in rows if row["expected_contradiction"] != "none"]
    contradiction_hits = [row for row in contradiction_gold if row["predicted_contradiction"]]
    critical_commits = [row for row in commits if row["critical_slot_case"]]
    critical_unsafe = [row for row in critical_commits if row["critical_slot_error"]]
    forced = [row for row in rows if "forced_exact" in row]
    report = {
        "cases": count,
        "intent_accuracy": rate(intent_correct, count, "no cases"),
        "slot_scores": slot_scores(slot_rows),
        "exact_frame_accuracy": rate(exact, count, "no cases"),
        "coverage": rate(len(commits), count, "no cases"),
        "selective_risk": rate(
            len(selective),
            len(commits),
            "no committed decisions; refusing every input is not a reliability score",
        ),
        "unsafe_commit_rate": rate(
            len(unsafe),
            len(commits),
            "no committed decisions; abstention is not an unsafe commit",
        ),
        "safe_commitment_accuracy": rate(
            len(safe_hits),
            len(commits),
            "no committed decisions",
        ),
        "action_accuracy": rate(action_correct, count, "no cases"),
        "retry_success_rate": rate(
            len(retry_success),
            len(retry_attempts),
            "no retry attempts",
        ),
        "clarify_rate": rate(sum(row["action"] == "CLARIFY" for row in rows), count, "no cases"),
        "hold_rate": rate(sum(row["action"] == "HOLD" for row in rows), count, "no cases"),
        "polarity_accuracy": rate(len(polarity_hits), count, "no cases")
        if polarity_available
        else {"value": None, "numerator": None, "denominator": count, "reason": "strategy does not represent polarity"},
        "ambiguity_precision": rate(
            len(ambiguity_true_positive),
            len(ambiguity_predicted),
            "no predicted ambiguity",
        ),
        "ambiguity_recall": rate(
            len(ambiguity_true_positive),
            len(ambiguity_gold),
            "no ambiguous cases",
        ),
        "contradiction_recall": rate(
            len(contradiction_hits),
            len(contradiction_gold),
            "no contradictory cases",
        ),
        "critical_slot_safety": rate(
            len(critical_commits) - len(critical_unsafe),
            len(critical_commits),
            "no commits on critical-slot cases",
        ),
        "committed_count": len(commits),
        "unsafe_count": len(unsafe),
    }
    if forced:
        report["forced_exact_frame_accuracy"] = rate(
            sum(bool(row["forced_exact"]) for row in forced),
            count,
            "no cases",
        )
        report["coverage_note"] = "Forced selection is scored as an answer, not as coverage."
    return report
