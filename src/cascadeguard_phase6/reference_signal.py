"""Explicit reference objects. They are not candidates and not oracle labels."""

from __future__ import annotations


def critical_slot_reference(case_id: str, intent: str, slots: dict[str, str]) -> dict[str, object]:
    return {
        "reference_id": f"ref-{case_id}",
        "reference_source": "authorized_synthetic_parent",
        "reference_scope": "critical_slots",
        "intent": intent,
        "critical_slots": {
            name: {"value": value, "source": "parent_referent"}
            for name, value in slots.items()
        },
        "reference_provenance": "EXPLICIT",
    }


def full_referent_reference(case_id: str, intent: str, slots: dict[str, str], transcript: str) -> dict[str, object]:
    signal = critical_slot_reference(case_id, intent, slots)
    signal["reference_scope"] = "full_referent"
    signal["parent_transcript"] = transcript
    return signal


def partial_reference(signal: dict[str, object]) -> dict[str, object]:
    """Drop one critical field. The missing value must not be inferred."""

    copied = {
        "reference_id": signal["reference_id"],
        "reference_source": signal["reference_source"],
        "reference_scope": signal["reference_scope"],
        "intent": signal["intent"],
        "critical_slots": dict(signal["critical_slots"]),
        "reference_provenance": signal["reference_provenance"],
    }
    if "parent_transcript" in signal:
        copied["parent_transcript"] = signal["parent_transcript"]
    slots = dict(copied["critical_slots"])
    if slots:
        slots.pop(next(iter(slots)))
    copied["critical_slots"] = slots
    return copied
