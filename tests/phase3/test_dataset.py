"""Dataset and empty-slot eligibility."""

import csv
import json
from pathlib import Path

from cascadeguard.evaluation.semantic_evidence import CRITICAL_SLOTS
from cascadeguard_facade.phase3_dataset import eligible, legitimate_empty_slot_intent, load_parents

ROOT = Path(__file__).resolve().parents[2]


def test_no_intent_has_an_empty_required_slot_list() -> None:
    assert all(not legitimate_empty_slot_intent(intent) for intent in CRITICAL_SLOTS)


def test_empty_gold_maps_are_excluded() -> None:
    parents = load_parents(ROOT / "data/synthetic/manifest.csv")
    empty = [parent for parent in parents if not parent.slots]
    assert {parent.utterance_id for parent in empty} == {"utt-020", "utt-040"}
    assert all(not eligible(parent) for parent in empty)


def test_challenge_set_is_partitioned_by_parent() -> None:
    rows = list(csv.DictReader((ROOT / "data/phase3/challenge_cases.csv").open()))
    splits = json.loads((ROOT / "data/phase3/splits.json").read_text())
    assert len(rows) == 240
    assert len({row["case_id"] for row in rows}) == 240
    counts: dict[str, int] = {}
    seen: dict[str, set[str]] = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
        seen.setdefault(row["parent_id"], set()).add(row["split"])
        assert splits["parents"][row["parent_id"]] == row["split"]
        assert row["dataset"] == "synthetic-semantic-challenge-v1"
    assert counts == {name: 30 for name in counts}
    assert len(counts) == 8
    assert all(len(splits_for_parent) == 1 for splits_for_parent in seen.values())
    assert "utt-020" not in splits["parents"]
    assert "utt-040" not in splits["parents"]
    assert splits["seed"] == 20261103
    assert splits["counts"] == {"development": 138, "validation": 30, "test": 30}
