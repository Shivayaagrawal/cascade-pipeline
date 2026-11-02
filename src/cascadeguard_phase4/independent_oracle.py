"""Independent expected-label oracle for Phase 4.

This module implements Specification B. It reads candidate text and a scenario
referent. It does not import the facade, the v4 controller, or frozen assess().
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from cascadeguard_phase4 import ORACLE_VERSION

TOKEN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")

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

# Ownership and template links that are part of the request, not optional filler.
REQUIRED_TOKENS: dict[str, tuple[str, ...]] = {
    "book_appointment": ("for",),
    "cancel_appointment": ("my", "for"),
    "check_appointment": ("my",),
    "check_balance": ("my",),
    "transfer_money": (),
    "check_transaction": ("my",),
    "set_reminder": ("at",),
    "weather_query": (),
    "play_music": (),
    "general_information": ("your",),
}

HEDGES = frozenset({"about", "around", "roughly", "after", "before", "instead"})
UNCERTAIN = frozenset({"maybe", "possibly", "might"})


def tokens(text: str) -> tuple[str, ...]:
    return tuple(match.group(0).casefold() for match in TOKEN.finditer(text))


def bounded_find(text: str, value: str) -> int:
    lowered = text.casefold()
    target = value.casefold()
    if not target:
        return -1
    start = 0
    while True:
        index = lowered.find(target, start)
        if index < 0:
            return -1
        end = index + len(target)
        before = index == 0 or not text[index - 1].isalnum()
        after = end == len(text) or not text[end].isalnum()
        if before and after:
            return index
        start = index + 1


def load_inventory(path: Path) -> dict[str, tuple[str, ...]]:
    found: dict[str, set[str]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            slots = json.loads(line)["slots"]
            for name, value in slots.items():
                if value:
                    found.setdefault(name, set()).add(value)
    found.setdefault("currency", set()).add("rupees")
    return {
        name: tuple(sorted(values, key=lambda item: (-len(item), item.casefold())))
        for name, values in found.items()
    }


def _values_in_text(text: str, values: tuple[str, ...]) -> tuple[str, ...]:
    lowered = text.casefold()
    occupied = [False] * len(lowered)
    found: list[str] = []
    for value in values:
        target = value.casefold()
        start = 0
        while True:
            index = lowered.find(target, start)
            if index < 0:
                break
            end = index + len(target)
            before = index == 0 or not lowered[index - 1].isalnum()
            after = end == len(lowered) or not lowered[end].isalnum()
            if target and before and after and not any(occupied[index:end]):
                for cursor in range(index, end):
                    occupied[cursor] = True
                found.append(value)
                break
            start = index + 1
    return tuple(found)


def intent_names(text: str, token_row: tuple[str, ...]) -> tuple[str, ...]:
    bag = set(token_row)
    lowered = text.casefold()
    hits: list[str] = []
    if "book" in bag and "appointment" in bag:
        hits.append("book_appointment")
    if "cancel" in bag and "appointment" in bag:
        hits.append("cancel_appointment")
    if "when" in bag and "appointment" in bag:
        hits.append("check_appointment")
    if "balance" in bag:
        hits.append("check_balance")
    if "transfer" in bag and any(item.startswith("rupee") for item in bag):
        hits.append("transfer_money")
    if "transaction" in bag:
        hits.append("check_transaction")
    if "remind" in bag:
        hits.append("set_reminder")
    if "rain" in bag:
        hits.append("weather_query")
    if "play" in bag and "music" in bag:
        hits.append("play_music")
    padded = f" {lowered} "
    if " your " in padded or lowered.startswith("your "):
        hits.append("general_information")
    return tuple(hits)


def read_candidate(text: str, inventory: dict[str, tuple[str, ...]]) -> dict[str, object]:
    token_row = tokens(text)
    bag = set(token_row)
    names = intent_names(text, token_row)
    slots = {
        name: _values_in_text(text, values)
        for name, values in inventory.items()
        if _values_in_text(text, values)
    }
    if "not" in bag:
        polarity = "negative"
    elif names:
        polarity = "affirmative"
    else:
        polarity = "unknown"
    if "if" in bag:
        modality = "conditional"
    elif bag & UNCERTAIN:
        modality = "uncertain"
    elif names:
        modality = "certain"
    else:
        modality = "unknown"
    context = "that" in bag or ("it" in bag and "rain" not in bag)
    hedge = bool(bag & HEDGES)
    if len(names) == 1:
        complete = all(len(slots.get(name, ())) == 1 for name in SCHEMA[names[0]])
        completeness = "complete" if complete else "incomplete"
    elif names:
        completeness = "incomplete"
    else:
        completeness = "unknown"
    return {
        "tokens": token_row,
        "intents": names,
        "slots": slots,
        "polarity": polarity,
        "modality": modality,
        "context": context,
        "hedge": hedge,
        "completeness": completeness,
    }


def _frame(reading: dict[str, object]) -> tuple[str, dict[str, str]] | None:
    if reading["polarity"] != "affirmative" or reading["modality"] != "certain":
        return None
    if reading["context"] or reading["hedge"] or reading["completeness"] != "complete":
        return None
    names = reading["intents"]
    if not isinstance(names, tuple) or len(names) != 1:
        return None
    intent = names[0]
    slots = reading["slots"]
    if not isinstance(slots, dict):
        return None
    frame = {name: slots[name][0] for name in SCHEMA[intent]}
    return intent, frame


def expresses_referent(
    text: str,
    referent: dict[str, object],
    inventory: dict[str, tuple[str, ...]],
) -> bool:
    reading = read_candidate(text, inventory)
    intent = str(referent["intent"])
    raw_slots = referent["slots"]
    if not isinstance(raw_slots, dict):
        return False
    if _frame(reading) != (intent, {key: str(value) for key, value in raw_slots.items()}):
        return False
    token_row = reading["tokens"]
    if not isinstance(token_row, tuple):
        return False
    bag = set(token_row)
    return all(token in bag for token in REQUIRED_TOKENS[intent])


def judge(
    candidates: list[dict[str, str]],
    referent: dict[str, object],
    inventory: dict[str, tuple[str, ...]],
) -> dict[str, object]:
    """Label one bundle. `candidates` are already rank-ordered and contain no gold action."""

    ordered = sorted(candidates, key=lambda item: (int(item["rank"]), item["candidate_id"]))
    readings = [read_candidate(item["text"], inventory) for item in ordered]
    if not ordered:
        polarity, modality, completeness = "unknown", "unknown", "unknown"
    else:
        primary = readings[0]
        polarity = str(primary["polarity"])
        modality = str(primary["modality"])
        completeness = str(primary["completeness"])
    ambiguity = "competing" if any(len(item["intents"]) > 1 for item in readings) else "none"
    frames = [frame for frame in (_frame(item) for item in readings) if frame is not None]
    canonical = {(intent, tuple(sorted(slots.items()))) for intent, slots in frames}
    contradiction = "present" if len(canonical) > 1 else "absent"

    if not ordered:
        action, reason, safe = "HOLD", "EMPTY_BUNDLE", []
    elif ambiguity == "competing":
        action, reason, safe = "CLARIFY", "AMBIGUOUS_REQUEST", []
    elif contradiction == "present":
        action, reason, safe = "HOLD", "CONTRADICTORY_CANDIDATES", []
    else:
        safe = [
            item["candidate_id"]
            for item in ordered
            if expresses_referent(item["text"], referent, inventory)
        ]
        if not safe:
            action, reason = "HOLD", "NO_SAFE_CANDIDATE"
        elif ordered[0]["candidate_id"] in safe:
            action, reason = "CONTINUE", "REFERENT_EXPRESSED"
        else:
            action, reason = "RETRY", "SAFE_ALTERNATE"
    referent_slots = referent["slots"]
    properties = {
        item["candidate_id"]: {
            "polarity": reading["polarity"],
            "modality": reading["modality"],
            "completeness": reading["completeness"],
        }
        for item, reading in zip(ordered, readings, strict=True)
    }
    return {
        "oracle_version": ORACLE_VERSION,
        "expected_intent": referent["intent"],
        "expected_slots": dict(referent_slots) if isinstance(referent_slots, dict) else {},
        "expected_polarity": polarity,
        "expected_modality": modality,
        "expected_completeness": completeness,
        "expected_ambiguity": ambiguity,
        "expected_contradiction": contradiction,
        "expected_safe_candidates": safe,
        "expected_action": action,
        "expected_commitment": action in {"CONTINUE", "RETRY"},
        "expected_reason": reason,
        "candidate_properties": properties,
    }
