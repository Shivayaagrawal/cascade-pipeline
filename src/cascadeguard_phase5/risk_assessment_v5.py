"""Interpretable risk flags. They never override a failed commit gate."""

from __future__ import annotations


def risk_factors(readings: list[dict[str, object]], modalities: list[dict[str, object]], diagnosis: dict[str, object]) -> dict[str, object]:
    labels = set(diagnosis["labels"])
    flags = {
        "modality_uncertainty": int(any(item["modality"] in {"UNCERTAINTY", "AMBIGUOUS_OR_MIXED"} for item in modalities)),
        "polarity_conflict": int(any(item["polarity"] == "negative" for item in modalities)),
        "conditionality_unresolved": int(any(item["conditionality"] == "conditional" for item in modalities)),
        "critical_slot_conflict": int("OUT_OF_INVENTORY" in labels or "CONFLICTING_FRAMES" in labels),
        "missing_required_slot": int("INCOMPLETE_FRAME" in labels),
        "candidate_provenance_failure": 0,
        "multiple_plausible_frames": int("MULTIPLE_INTENTS" in labels or "CONFLICTING_FRAMES" in labels),
        "incomplete_evidence": int(any(not item["intents"] for item in readings) if readings else 1),
    }
    score = sum(flags.values()) / len(flags)
    return {"flags": flags, "score": score, "overrides_gate": False}
