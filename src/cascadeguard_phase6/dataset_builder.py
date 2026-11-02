"""Build synthetic-reference-integrity-v1 from frozen parents. Parents are not rewritten."""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

from cascadeguard_phase5.critical_slot_verifier_v5 import value_in_text
from cascadeguard_phase6 import DATASET_ID, SEED

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
    "clean_affirmative": 24,
    "clean_polite_instruction": 12,
    "negation": 24,
    "uncertainty": 24,
    "conditionality": 12,
    "date_substitution": 16,
    "time_substitution": 20,
    "amount_substitution": 20,
    "candidate_provenance_conflict": 16,
    "ambiguous_candidate_bundle": 12,
    "parent_transcript_cue": 6,
}


def _load(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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


def _inventory(rows: list[dict[str, object]]) -> dict[str, tuple[str, ...]]:
    found: dict[str, set[str]] = {}
    for row in rows:
        for name, value in dict(row["slots"]).items():
            if value:
                found.setdefault(name, set()).add(str(value))
    found.setdefault("currency", set()).add("rupees")
    return {name: tuple(sorted(values)) for name, values in found.items()}


def _parts(ids: list[str], rng: random.Random) -> dict[str, list[str]]:
    order = list(ids)
    rng.shuffle(order)
    test = round(0.2 * len(order))
    validation = round(0.2 * len(order))
    development = len(order) - test - validation
    sizes = {"development": development, "validation": validation, "test": test}
    assigned: dict[str, list[str]] = {}
    cursor = 0
    for split, size in sizes.items():
        assigned[split] = order[cursor : cursor + size]
        cursor += size
    return assigned


def assign_parents(parents: list[dict[str, object]], seed: int = SEED) -> dict[str, object]:
    by_id = {str(row["utterance_id"]): row for row in parents}
    april = sorted((row for row in parents if row["slots"].get("date") == "April 2"), key=lambda row: str(row["utterance_id"]))
    seven = sorted((row for row in parents if row["slots"].get("time") == "7 AM"), key=lambda row: str(row["utterance_id"]))
    amount = sorted((row for row in parents if row["slots"].get("amount") == "180"), key=lambda row: str(row["utterance_id"]))
    if not april or not seven or not amount:
        raise RuntimeError("A predeclared test parent is missing from the frozen pool.")
    pinned = [amount[0], april[0], seven[0]]
    pinned_ids = {str(row["utterance_id"]) for row in pinned}
    remaining = [row for row in parents if str(row["utterance_id"]) not in pinned_ids]
    groups = {
        "set_reminder": [row for row in remaining if row["intent"] == "set_reminder"],
        "transfer_money": [row for row in remaining if row["intent"] == "transfer_money"],
        "other": [row for row in remaining if row["intent"] not in {"set_reminder", "transfer_money"}],
    }
    assigned = {"development": [], "validation": [], "test": [by_id[str(row["utterance_id"])] for row in pinned]}
    rng = random.Random(seed)
    for group in groups.values():
        parts = _parts([str(row["utterance_id"]) for row in group], rng)
        for split, ids in parts.items():
            assigned[split].extend(by_id[item] for item in ids)
    return {
        "rows": assigned,
        "preassigned_test": {
            "amount_180": str(amount[0]["utterance_id"]),
            "april_2": str(april[0]["utterance_id"]),
            "time_7am": str(seven[0]["utterance_id"]),
        },
    }


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
    if category == "clean_affirmative":
        return {"texts": [text], "provenances": ["reference_passthrough"], "transformation": "clean_referent"}
    if category == "clean_polite_instruction":
        return {"texts": [f"Please {text}"], "provenances": ["synthetic_edit"], "transformation": "please_prefix"}
    if category == "parent_transcript_cue":
        return {"texts": [text], "provenances": ["reference_passthrough"], "transformation": "maybe_on_parent_transcript_only", "full_transcript": f"Maybe {text}"}
    if category == "negation":
        value = str(slots[SCHEMA[intent][0]])
        updated = _replace(text, value, f"not {value}")
        return None if updated is None else {"texts": [updated], "provenances": ["synthetic_edit"], "transformation": "insert_not"}
    if category == "uncertainty":
        prefix = {"maybe": "Maybe", "possibly": "Possibly", "might": "I might"}[kind]
        body = text if kind != "might" else f"{text[0].casefold()}{text[1:]}"
        return {"texts": [f"{prefix} {body}"], "provenances": ["synthetic_edit"], "transformation": f"{kind}_prefix"}
    if category == "conditionality":
        return {"texts": [f"If needed {text}"], "provenances": ["synthetic_edit"], "transformation": "if_needed_prefix"}
    if category == "ambiguous_candidate_bundle":
        extra = " Show my yesterday transaction." if intent == "check_balance" else " What is my account balance?"
        return {"texts": [text + extra], "provenances": ["synthetic_edit"], "transformation": "second_intent"}
    if category in {"date_substitution", "time_substitution", "amount_substitution"}:
        name = {"date_substitution": "date", "time_substitution": "time", "amount_substitution": "amount"}[category]
        if name not in slots:
            return None
        current = str(slots[name])
        forced = {"April 2": "April 3", "7 AM": "8 AM", "6 PM": "5 PM", "180": "181"}.get(current)
        new = _alternate(inventory.get(name, ()), current, forced)
        updated = None if new is None else _replace(text, current, new)
        if updated is None or value_in_text(updated, current):
            return None
        kind_name = "out_of_inventory" if forced in {"April 3", "181"} else "in_inventory"
        return {"texts": [updated], "provenances": ["synthetic_edit"], "transformation": f"{name}_{kind_name}"}
    if category == "candidate_provenance_conflict" and kind == "values":
        name = SCHEMA[intent][0]
        current = str(slots[name])
        new = _alternate(inventory.get(name, ()), current)
        updated = None if new is None else _replace(text, current, new)
        if updated is None or value_in_text(updated, current):
            return None
        return {"texts": [text, updated], "provenances": ["reference_passthrough", "synthetic_edit"], "transformation": "referent_plus_other_value"}
    if category == "candidate_provenance_conflict":
        value = str(slots[SCHEMA[intent][0]])
        negated = _replace(text, value, f"not {value}")
        if negated is None:
            return None
        return {"texts": [negated, text], "provenances": ["synthetic_edit", "reference_passthrough"], "transformation": "negated_plus_referent"}
    return None


def _quota(split: str, total: int) -> int:
    test = round(0.2 * total)
    validation = round(0.2 * total)
    if split == "test":
        return test
    if split == "validation":
        return validation
    return total - test - validation


def _kinds(category: str, count: int) -> list[str]:
    if category == "uncertainty":
        return [["maybe", "possibly", "might"][index % 3] for index in range(count)]
    if category == "candidate_provenance_conflict":
        half = count // 2
        return ["negated"] * (count - half) + ["values"] * half
    return ["default"] * count


def _order(group: list[dict[str, object]], category: str) -> list[dict[str, object]]:
    if category == "date_substitution":
        return sorted(group, key=lambda row: (row["slots"].get("date") != "April 2", str(row["utterance_id"])))
    if category == "time_substitution":
        return sorted(group, key=lambda row: (row["slots"].get("time") != "7 AM", str(row["utterance_id"])))
    if category == "amount_substitution":
        return sorted(group, key=lambda row: (row["slots"].get("amount") != "180", str(row["utterance_id"])))
    if category == "parent_transcript_cue":
        return sorted(group, key=lambda row: (row["intent"] != "play_music", str(row["utterance_id"])))
    return sorted(group, key=lambda row: str(row["utterance_id"]))


def build_dataset(annotation_path: Path) -> dict[str, object]:
    rows = _load(annotation_path)
    inventory = _inventory(rows)
    parents = _eligible(rows)
    assignment = assign_parents(parents)
    cases: list[dict[str, object]] = []
    shortfalls: dict[str, dict[str, int]] = {}
    for split, group in assignment["rows"].items():
        for category, total in TARGETS.items():
            need = _quota(split, total)
            used: set[str] = set()
            made = 0
            ordered = _order(group, category)
            for kind in _kinds(category, need):
                found = None
                built = None
                for parent in ordered:
                    if str(parent["utterance_id"]) in used:
                        continue
                    built = _construct(parent, category, kind, inventory)
                    if built is not None:
                        found = parent
                        used.add(str(parent["utterance_id"]))
                        break
                if found is None or built is None:
                    break
                case_id = f"p6-{category}-{split[:3]}-{made:02d}"
                candidates = []
                for rank, (text, provenance) in enumerate(zip(built["texts"], built["provenances"], strict=True)):
                    candidates.append(
                        {
                            "candidate_id": f"{case_id}-c{rank}",
                            "text": text,
                            "provenance": provenance,
                            "rank": rank,
                        }
                    )
                cases.append(
                    {
                        "case_id": case_id,
                        "parent_utterance_id": found["utterance_id"],
                        "parent_transcript": found["text"],
                        "full_referent_transcript": built.get("full_transcript", found["text"]),
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
        "preassigned_test": assignment["preassigned_test"],
        "split_parents": {split: [str(row["utterance_id"]) for row in group] for split, group in assignment["rows"].items()},
        "eligible_parents": len(parents),
        "excluded_parents": [str(row["utterance_id"]) for row in rows if str(row["utterance_id"]) not in {str(item["utterance_id"]) for item in parents}],
        "category_counts": dict(Counter(case["corruption_category"] for case in cases)),
        "multiple_slot_category": "not built; transfer_money is the only two-slot intent and its second slot is always rupees",
    }
