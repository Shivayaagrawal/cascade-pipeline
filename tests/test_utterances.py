"""Synthetic catalogue tests. No audio and no Common Voice."""

from collections import Counter

from cascadeguard.simulation.error_injector import (
    ERROR_CATEGORIES,
    PROVENANCE_SYNTHETIC_EDIT,
    generate_variants,
)
from cascadeguard.simulation.utterance_generator import INTENTS, generate_utterances


def test_catalogue_shape() -> None:
    rows = generate_utterances()
    assert len(rows) == 200
    counts = Counter(row.intent for row in rows)
    assert set(counts) == set(INTENTS)
    assert set(counts.values()) == {20}
    assert all(row.dataset == "synthetic" for row in rows)
    assert rows[0].text == "Book an appointment for tomorrow"
    assert rows[20].text == "Cancel my appointment"
    assert rows[40].text == "When is my appointment?"
    assert rows[60].text == "What is my account balance?"
    assert rows[80].text == "Transfer 500 rupees"
    assert rows[100].text == "Show my latest transaction"
    assert rows[120].text == "Remind me at 6 PM"
    assert rows[140].text == "Will it rain tomorrow?"
    assert rows[160].text == "Play jazz music"
    assert rows[180].text == "What are your working hours?"
    assert len({row.utterance_id for row in rows}) == 200


def test_three_variants_keep_ids_and_are_not_nbest() -> None:
    rows = generate_utterances()
    variants = generate_variants(rows, seed=17)
    assert len(variants) == 600
    categories = Counter(item.category for item in variants)
    assert set(categories) == set(ERROR_CATEGORIES)
    for item in variants:
        assert item.provenance == PROVENANCE_SYNTHETIC_EDIT
        assert item.variant_id.startswith(item.utterance_id)
        original = next(row for row in rows if row.utterance_id == item.utterance_id)
        assert item.text != original.text
