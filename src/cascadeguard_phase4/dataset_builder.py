"""Specification A. Builds transcripts and provenance. Does not assign safety labels."""

from __future__ import annotations

import json
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from cascadeguard_phase4 import CONSTRUCTION_VERSION, DATASET_ID, SEED
from cascadeguard_phase4.challenge_schema import (
    CATEGORIES,
    CLEAN,
    FAILURE_CATEGORIES,
    SCHEMA,
    TARGET_CLEAN,
    TARGET_FAILURE,
    TEMPORAL_SLOTS,
)
from cascadeguard_phase4.independent_oracle import bounded_find, load_inventory

ANNOTATIONS = Path("data/synthetic/annotations/annotations.jsonl")


@dataclass(frozen=True)
class Parent:
    parent_id: str
    intent: str
    text: str
    slots: dict[str, str]


def _collapse(text: str) -> str:
    return " ".join(text.split())


def _replace_value(text: str, old: str, new: str) -> str | None:
    index = bounded_find(text, old)
    if index < 0:
        return None
    return _collapse(text[:index] + new + text[index + len(old) :])


def load_parents(path: Path = ANNOTATIONS) -> list[Parent]:
    rows: list[Parent] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            rows.append(
                Parent(item["utterance_id"], item["intent"], item["text"], dict(item["slots"]))
            )
    return rows


def eligible(parents: list[Parent]) -> list[Parent]:
    kept: list[Parent] = []
    for parent in parents:
        required = SCHEMA.get(parent.intent)
        if not required:
            continue
        if set(parent.slots) != set(required):
            continue
        if any(not value or bounded_find(parent.text, value) < 0 for value in parent.slots.values()):
            continue
        kept.append(parent)
    return kept


def _primary(parent: Parent) -> str:
    return SCHEMA[parent.intent][0]


def _mutate_text(parent: Parent, inventory: dict[str, tuple[str, ...]]) -> str | None:
    name = _primary(parent)
    old = parent.slots[name]
    for new in inventory.get(name, ()):
        if new == old:
            continue
        updated = _replace_value(parent.text, old, new)
        if updated is None:
            continue
        matches = [value for value in inventory[name] if bounded_find(updated, value) >= 0]
        if matches == [new] and bounded_find(updated, old) < 0:
            return updated
    return None


def _negate(parent: Parent) -> str | None:
    updated = _replace_value(parent.text, parent.slots[_primary(parent)], f"not {parent.slots[_primary(parent)]}")
    if updated is None or " not " not in f" {updated.casefold()} ":
        return None
    return updated


def _uncertainty(parent: Parent, kind: str) -> str:
    if kind == "maybe":
        return f"Maybe {parent.text}"
    if kind == "possibly":
        return f"Possibly {parent.text}"
    if kind == "might":
        return f"I might {parent.text[0].casefold()}{parent.text[1:]}"
    return f"If needed {parent.text}"


def _damage(parent: Parent) -> str | None:
    text = parent.text
    intent = parent.intent
    if intent in {"book_appointment", "cancel_appointment"} and " for " in text:
        return text.replace(" for ", " after ", 1)
    if intent == "set_reminder" and " at " in text:
        return text.replace(" at ", " before ", 1)
    if intent == "transfer_money":
        return _replace_value(text, parent.slots["amount"], f"about {parent.slots['amount']}")
    if intent in {"check_balance", "check_transaction", "check_appointment"} and " my " in text:
        return text.replace(" my ", " the ", 1)
    if intent == "weather_query" and text.startswith("Will it rain "):
        return text.replace("Will it rain ", "Will it rain after ", 1)
    if intent == "play_music" and text.endswith(" music"):
        return text + " instead"
    if intent == "general_information" and text.endswith("?"):
        return text[:-1] + " instead?"
    return None


def _ambiguity(parent: Parent) -> str:
    if parent.intent == "check_balance":
        return parent.text + " Show my yesterday transaction."
    return parent.text + " What is my account balance?"


def _second_intent(parent: Parent) -> str:
    if parent.intent == "check_balance":
        return "Play jazz music"
    return "What is my account balance?"


def construct(parent: Parent, category: str, kind: str, inventory: dict[str, tuple[str, ...]]) -> dict[str, object] | None:
    if category == "negation_polarity":
        text = _negate(parent)
        if text is None:
            return None
        return _one(text, "synthetic_edit", "insert_not_before_critical_value")
    if category == "uncertainty_modality":
        return _one(_uncertainty(parent, kind), "synthetic_edit", f"modality_{kind}")
    if category == "critical_slot_mutation":
        text = _mutate_text(parent, inventory)
        if text is None:
            return None
        return _one(text, "synthetic_edit", "replace_primary_critical_value")
    if category == "temporal_numerical_conflict":
        if parent.slots[_primary(parent)] and _primary(parent) not in TEMPORAL_SLOTS and "amount" not in parent.slots and "date" not in parent.slots and "time" not in parent.slots and "recency" not in parent.slots:
            return None
        if not any(name in TEMPORAL_SLOTS for name in parent.slots):
            return None
        text = _mutate_text(parent, inventory)
        if text is None:
            return None
        return _two(parent.text, text, "reference_and_mutated_value")
    if category == "semantic_ambiguity":
        return _one(_ambiguity(parent), "synthetic_edit", "append_second_request")
    if category == "contradictory_candidates":
        return _two(parent.text, _second_intent(parent), "parent_and_other_intent")
    if category == "incomplete_required_slots":
        text = _replace_value(parent.text, parent.slots[_primary(parent)], "")
        if text is None or bounded_find(text, parent.slots[_primary(parent)]) >= 0:
            return None
        return _one(text, "synthetic_edit", "delete_primary_critical_value")
    if category == "context_dependency":
        text = _replace_value(parent.text, parent.slots[_primary(parent)], "that")
        if text is None:
            return None
        return _one(text, "synthetic_edit", "replace_primary_value_with_that")
    if category == "function_word_damage":
        text = _damage(parent)
        if text is None or text == parent.text:
            return None
        return _one(text, "synthetic_edit", "alter_link_or_add_hedge")
    if category == "candidate_provenance" and kind == "empty":
        return {"texts": [], "provenances": [], "transformation": "empty_bundle"}
    if category == "candidate_provenance":
        text = _negate(parent)
        if text is None:
            return None
        return _two_provenance(text, parent.text, "negated_candidate_plus_referent")
    if category == CLEAN and kind == "please":
        return _one(f"Please {parent.text}", "synthetic_edit", "please_prefix_not_uncertainty")
    if category == CLEAN and kind == "agree":
        return {
            "texts": [parent.text, parent.text],
            "provenances": ["reference_passthrough", "synthetic_edit"],
            "transformation": "two_agreeing_copies",
        }
    if category == CLEAN:
        return _one(parent.text, "reference_passthrough", "clean_referent")
    return None


def _one(text: str, provenance: str, transformation: str) -> dict[str, object]:
    return {"texts": [text], "provenances": [provenance], "transformation": transformation}


def _two(first: str, second: str, transformation: str) -> dict[str, object]:
    return {
        "texts": [first, second],
        "provenances": ["reference_passthrough", "synthetic_edit"],
        "transformation": transformation,
    }


def _two_provenance(unsafe: str, safe: str, transformation: str) -> dict[str, object]:
    return {
        "texts": [unsafe, safe],
        "provenances": ["synthetic_edit", "reference_passthrough"],
        "transformation": transformation,
    }


def _split_sizes(count: int) -> dict[str, int]:
    test = round(0.20 * count)
    validation = round(0.20 * count)
    return {
        "development": count - validation - test,
        "validation": validation,
        "test": test,
    }


def _targets(split: str) -> dict[str, int]:
    if split == "development":
        failure, clean = 30, 60
    else:
        failure, clean = 10, 20
    goals = {category: failure for category in FAILURE_CATEGORIES}
    goals[CLEAN] = clean
    return goals


def _kinds(category: str, split: str, count: int) -> list[str]:
    if category == "uncertainty_modality":
        cycle = ("maybe", "possibly", "might", "conditional")
        return [cycle[index % 4] for index in range(count)]
    if category == "candidate_provenance":
        empty = {"development": 4, "validation": 1, "test": 1}[split]
        return ["pair"] * (count - empty) + ["empty"] * empty
    if category == CLEAN:
        please = {"development": 6, "validation": 2, "test": 2}[split]
        agree = {"development": 12, "validation": 4, "test": 4}[split]
        return ["please"] * please + ["agree"] * agree + ["plain"] * (count - please - agree)
    return ["default"] * count


def _take(
    parents: list[Parent],
    cursor: list[int],
    used: set[str],
    builder,
) -> tuple[Parent, dict[str, object]] | None:
    count = len(parents)
    for step in range(count):
        parent = parents[(cursor[0] + step) % count]
        if parent.parent_id in used:
            continue
        built = builder(parent)
        if built is not None:
            used.add(parent.parent_id)
            cursor[0] = (cursor[0] + step + 1) % count
            return parent, built
    return None


def build_split(
    split: str,
    parents: list[Parent],
    inventory: dict[str, tuple[str, ...]],
) -> tuple[list[dict[str, object]], dict[str, int]]:
    cases: list[dict[str, object]] = []
    shortfall: dict[str, int] = {}
    goals = _targets(split)
    for category in CATEGORIES:
        cursor = [0]
        used: set[str] = set()
        made = 0
        for kind in _kinds(category, split, goals[category]):
            found = _take(
                parents,
                cursor,
                used,
                lambda parent, category=category, kind=kind: construct(parent, category, kind, inventory),
            )
            if found is None:
                break
            parent, built = found
            index = made
            case_id = f"p4-{category}-{split[:3]}-{index:02d}"
            texts = list(built["texts"])
            provenances = list(built["provenances"])
            candidates = []
            for rank, (text, provenance) in enumerate(zip(texts, provenances, strict=True)):
                candidates.append(
                    {
                        "candidate_id": f"{case_id}-c{rank}",
                        "text": text,
                        "provenance": provenance,
                        "rank": rank,
                    }
                )
            source = "SINGLE_TRANSCRIPT" if len(candidates) <= 1 else "SYNTHETIC_PROXY"
            cases.append(
                {
                    "case_id": case_id,
                    "parent_id": parent.parent_id,
                    "case_category": category,
                    "split": split,
                    "transformation": built["transformation"],
                    "construction_version": CONSTRUCTION_VERSION,
                    "candidate_source": source,
                    "generation_method": "phase4_text_edit",
                    "candidates": candidates,
                    "referent": {
                        "intent": parent.intent,
                        "slots": dict(parent.slots),
                    },
                }
            )
            made += 1
        if made != goals[category]:
            shortfall[category] = goals[category] - made
    return cases, shortfall


def assign_parents(parents: list[Parent], seed: int = SEED) -> dict[str, list[Parent]]:
    order = list(parents)
    random.Random(seed).shuffle(order)
    sizes = _split_sizes(len(order))
    assigned: dict[str, list[Parent]] = {}
    cursor = 0
    for split in ("development", "validation", "test"):
        assigned[split] = order[cursor : cursor + sizes[split]]
        cursor += sizes[split]
    return assigned


def build_all(annotation_path: Path = ANNOTATIONS) -> dict[str, object]:
    inventory = load_inventory(annotation_path)
    parents = eligible(load_parents(annotation_path))
    assigned = assign_parents(parents)
    cases: list[dict[str, object]] = []
    shortfalls: dict[str, dict[str, int]] = {}
    for split, group in assigned.items():
        built, short = build_split(split, group, inventory)
        cases.extend(built)
        if short:
            shortfalls[split] = short
    counts = Counter(item["case_category"] for item in cases)
    return {
        "dataset_id": DATASET_ID,
        "seed": SEED,
        "eligible_parents": len(parents),
        "excluded_parents": [
            parent.parent_id
            for parent in load_parents(annotation_path)
            if parent.parent_id not in {item.parent_id for item in parents}
        ],
        "split_parent_counts": {split: len(group) for split, group in assigned.items()},
        "split_parents": {split: [item.parent_id for item in group] for split, group in assigned.items()},
        "cases": cases,
        "shortfalls": shortfalls,
        "category_counts": dict(counts),
        "inventory": inventory,
        "targets": {"failure_each": TARGET_FAILURE, "clean": TARGET_CLEAN},
    }
