"""Construction-side names. Outcome rules live in the oracle, not here."""

from __future__ import annotations

FAILURE_CATEGORIES: tuple[str, ...] = (
    "negation_polarity",
    "uncertainty_modality",
    "critical_slot_mutation",
    "temporal_numerical_conflict",
    "semantic_ambiguity",
    "contradictory_candidates",
    "incomplete_required_slots",
    "context_dependency",
    "function_word_damage",
    "candidate_provenance",
)

CLEAN = "clean_control"
CATEGORIES: tuple[str, ...] = FAILURE_CATEGORIES + (CLEAN,)

# Closed-grammar required slots. Empty gold maps are not eligible parents,
# because every intent in this grammar requires at least one slot.
SCHEMA: dict[str, tuple[str, ...]] = {
    "book_appointment": ("date",),
    "cancel_appointment": ("date",),
    "check_appointment": ("date",),
    "check_balance": ("account",),
    "transfer_money": ("amount", "currency"),
    "check_transaction": ("recency",),
    "set_reminder": ("time",),
    "weather_query": ("date",),
    "play_music": ("genre",),
    "general_information": ("topic",),
}

TEMPORAL_SLOTS = frozenset({"date", "time", "amount", "recency"})
TARGET_FAILURE = 50
TARGET_CLEAN = 100
SPLIT_FRACTIONS = ("development", "validation", "test")
