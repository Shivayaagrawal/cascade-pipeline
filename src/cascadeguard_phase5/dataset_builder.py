"""Build synthetic-semantic-integrity-v1 from frozen parents. Parents are not rewritten."""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

from cascadeguard_phase5 import DATASET_ID, SEED
from cascadeguard_phase5.critical_slot_verifier_v5 import value_in_text

SCHEMA = {
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
DATE_INTENTS = {"book_appointment", "cancel_appointment", "check_appointment", "weather_query"}
TARGETS = {
    "clean_affirmative": 30,
    "negation": 30,
    "uncertainty_maybe": 30,
    "uncertainty_possibly": 30,
    "uncertainty_might": 30,
    "conditional_if_needed": 30,
    "critical_date_mutation": 30,
    "critical_time_mutation": 20,
    "critical_amount_mutation": 20,
    "candidate_provenance_conflict": 30,
}
SPLIT_SHARE = {"development": 0.6, "validation": 0.2, "test": 0.2}


def _load_parents(path: Path) -> list[dict[str, object]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _eligible(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    kept = []
    for row in rows:
        required = SCHEMA.get(str(row["intent"]))
        slots = dict(row["slots"])
        if not required or set(slots) != set(required):
            continue
        if any(not value or not value_in_text(str(row["text"]), str(value)) for value in slots.values()):
            continue
        kept.append(row)
    return kept


def _split_ids(ids: list[str], rng: random.Random) -> dict[str, list[str]]:
    order = list(ids)
    rng.shuffle(order)
    count = len(order)
    test = round(0.2 * count)
    validation = round(0.2 * count)
    development = count - test - validation
    sizes = {"development": development, "validation": validation, "test": test}
    assigned: dict[str, list[str]] = {}
    cursor = 0
    for split, size in sizes.items():
        assigned[split] = order[cursor : cursor + size]
        cursor += size
    return assigned


def assign_parents(parents: list[dict[str, object]], seed: int = SEED) -> dict[str, list[dict[str, object]]]:
    rng = random.Random(seed)
    groups = {
        "set_reminder": [row for row in parents if row["intent"] == "set_reminder"],
        "transfer_money": [row for row in parents if row["intent"] == "transfer_money"],
        "other": [row for row in parents if row["intent"] not in {"set_reminder", "transfer_money"}],
    }
    assigned: dict[str, list[dict[str, object]]] = {split: [] for split in SPLIT_SHARE}
    by_id = {str(row["utterance_id"]): row for row in parents}
    for group in groups.values():
        parts = _split_ids([str(row["utterance_id"]) for row in group], rng)
        for split, ids in parts.items():
            assigned[split].extend(by_id[item] for item in ids)
    return assigned


def _replace(text: str, old: str, new: str) -> str | None:
    index_text = text.casefold()
    target = old.casefold()
    start = 0
    while True:
        index = index_text.find(target, start)
        if index < 0:
            return None
        end = index + len(old)
        before = index == 0 or not text[index - 1].isalnum()
        after = end == len(text) or not text[end].isalnum()
        if before and after:
            return " ".join((text[:index] + new + text[end:]).split())
        start = index + 1


def _alternate(inventory: tuple[str, ...], current: str, forced: str | None = None) -> str | None:
    if forced and forced.casefold() != current.casefold():
        return forced
    for value in inventory:
        if value.casefold() != current.casefold():
            return value
    return None


def _construct(parent: dict[str, object], category: str, kind: str, inventory: dict[str, tuple[str, ...]]) -> dict[str, object] | None:
    text = str(parent["text"])
    slots = dict(parent["slots"])
    intent = str(parent["intent"])
    if category == "clean_affirmative" and kind == "please":
        return {"texts": [f"Please {text}"], "provenances": ["synthetic_edit"], "transformation": "please_prefix"}
    if category == "clean_affirmative":
        return {"texts": [text], "provenances": ["reference_passthrough"], "transformation": "clean_referent"}
    if category == "negation":
        value = str(slots[SCHEMA[intent][0]])
        updated = _replace(text, value, f"not {value}")
        if updated is None:
            return None
        return {"texts": [updated], "provenances": ["synthetic_edit"], "transformation": "insert_not"}
    if category == "uncertainty_maybe":
        return {"texts": [f"Maybe {text}"], "provenances": ["synthetic_edit"], "transformation": "maybe_prefix"}
    if category == "uncertainty_possibly":
        return {"texts": [f"Possibly {text}"], "provenances": ["synthetic_edit"], "transformation": "possibly_prefix"}
    if category == "uncertainty_might":
        return {"texts": [f"I might {text[0].casefold()}{text[1:]}"], "provenances": ["synthetic_edit"], "transformation": "might_prefix"}
    if category == "conditional_if_needed":
        return {"texts": [f"If needed {text}"], "provenances": ["synthetic_edit"], "transformation": "if_needed_prefix"}
    if category == "critical_date_mutation":
        if intent not in DATE_INTENTS:
            return None
        current = str(slots["date"])
        forced = "April 3" if current == "April 2" else None
        new = _alternate(inventory["date"], current, forced)
        updated = None if new is None else _replace(text, current, new)
        if updated is None or updated == text or value_in_text(updated, current):
            return None
        return {"texts": [updated], "provenances": ["synthetic_edit"], "transformation": "date_mutation"}
    if category == "critical_time_mutation":
        if intent != "set_reminder":
            return None
        current = str(slots["time"])
        forced = "8 AM" if current == "7 AM" else None
        new = _alternate(inventory["time"], current, forced)
        updated = None if new is None else _replace(text, current, new)
        if updated is None or value_in_text(updated, current):
            return None
        return {"texts": [updated], "provenances": ["synthetic_edit"], "transformation": "time_mutation"}
    if category == "critical_amount_mutation":
        if intent != "transfer_money":
            return None
        current = str(slots["amount"])
        forced = "181" if current == "180" else None
        new = _alternate(inventory["amount"], current, forced)
        updated = None if new is None else _replace(text, current, new)
        if updated is None or value_in_text(updated, current):
            return None
        return {"texts": [updated], "provenances": ["synthetic_edit"], "transformation": "amount_mutation"}
    if category == "candidate_provenance_conflict" and kind == "values":
        name = SCHEMA[intent][0]
        current = str(slots[name])
        new = _alternate(inventory.get(name, ()), current)
        updated = None if new is None else _replace(text, current, new)
        if updated is None or value_in_text(updated, current):
            return None
        return {
            "texts": [text, updated],
            "provenances": ["reference_passthrough", "synthetic_edit"],
            "transformation": "referent_plus_other_value",
        }
    if category == "candidate_provenance_conflict":
        value = str(slots[SCHEMA[intent][0]])
        negated = _replace(text, value, f"not {value}")
        if negated is None:
            return None
        return {
            "texts": [negated, text],
            "provenances": ["synthetic_edit", "reference_passthrough"],
            "transformation": "negated_plus_referent",
        }
    return None


def _quota(split: str, category: str) -> int:
    total = TARGETS[category]
    if split == "test":
        return round(0.2 * total)
    if split == "validation":
        return round(0.2 * total)
    return total - round(0.2 * total) - round(0.2 * total)


def _kinds(category: str, count: int) -> list[str]:
    if category == "clean_affirmative":
        please = max(1, count // 3)
        return ["please"] * please + ["plain"] * (count - please)
    if category == "candidate_provenance_conflict":
        conflicts = count // 2
        return ["negated"] * (count - conflicts) + ["values"] * conflicts
    return ["default"] * count


def build_dataset(annotation_path: Path) -> dict[str, object]:
    inventory = _inventory(_load_parents(annotation_path))
    parents = _eligible(_load_parents(annotation_path))
    assigned = assign_parents(parents)
    cases: list[dict[str, object]] = []
    shortfalls: dict[str, dict[str, int]] = {}
    for split, group in assigned.items():
        for category, _total in TARGETS.items():
            need = _quota(split, category)
            used: set[str] = set()
            made = 0
            cursor = 0
            for kind in _kinds(category, need):
                found = None
                for step in range(len(group)):
                    parent = group[(cursor + step) % len(group)]
                    if str(parent["utterance_id"]) in used:
                        continue
                    built = _construct(parent, category, kind, inventory)
                    if built is not None:
                        found = parent
                        cursor = (cursor + step + 1) % len(group)
                        used.add(str(parent["utterance_id"]))
                        break
                if found is None:
                    break
                case_id = f"p5-{category}-{split[:3]}-{made:02d}"
                candidates = []
                for rank, (text, provenance) in enumerate(zip(built["texts"], built["provenances"], strict=True)):
                    candidates.append(
                        {
                            "candidate_id": f"{case_id}-c{rank}",
                            "text": text,
                            "provenance": provenance,
                            "rank": rank,
                            "candidate_source": "SINGLE_TRANSCRIPT" if len(built["texts"]) == 1 else "SYNTHETIC_PROXY",
                        }
                    )
                cases.append(
                    {
                        "case_id": case_id,
                        "parent_utterance_id": found["utterance_id"],
                        "parent_transcript": found["text"],
                        "candidate_bundle_id": f"{case_id}-bundle",
                        "corruption_category": category,
                        "transformation": built["transformation"],
                        "split": split,
                        "candidates": candidates,
                        "referent": {"intent": found["intent"], "slots": dict(found["slots"])},
                    }
                )
                made += 1
            if made != need:
                shortfalls.setdefault(split, {})[category] = need - made
    return {
        "dataset_id": DATASET_ID,
        "seed": SEED,
        "cases": cases,
        "shortfalls": shortfalls,
        "split_parents": {split: [str(row["utterance_id"]) for row in group] for split, group in assigned.items()},
        "eligible_parents": len(parents),
        "excluded_parents": [
            str(row["utterance_id"])
            for row in _load_parents(annotation_path)
            if str(row["utterance_id"]) not in {str(item["utterance_id"]) for item in parents}
        ],
        "category_counts": dict(Counter(case["corruption_category"] for case in cases)),
    }


def _inventory(rows: list[dict[str, object]]) -> dict[str, tuple[str, ...]]:
    found: dict[str, set[str]] = {}
    for row in rows:
        for name, value in dict(row["slots"]).items():
            if value:
                found.setdefault(name, set()).add(str(value))
    found.setdefault("currency", set()).add("rupees")
    return {name: tuple(sorted(values)) for name, values in found.items()}
