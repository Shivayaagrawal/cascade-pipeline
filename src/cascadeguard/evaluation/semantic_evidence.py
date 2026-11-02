"""Lexical evidence for the synthetic grammar.

This layer does not use gold labels. It looks for closed-grammar cues and lexicon values.
A confident intent does not fill in a slot that the text does not contain.
"""

from __future__ import annotations

from dataclasses import dataclass

from cascadeguard.simulation.utterance_generator import Utterance, generate_utterances

# Every schema slot is critical. Intent evidence does not fill a missing one.
# The first cancel and check-appointment rows have no gold date. A commit still
# requires a date, because the schema lists that slot and the text cannot show
# that the date was never spoken.
CRITICAL_SLOTS: dict[str, tuple[str, ...]] = {
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


@dataclass(frozen=True)
class Evidence:
    """What one candidate string supports. Slot lists are lexicon matches, not gold."""

    intents: tuple[str, ...]
    slots: dict[str, tuple[str, ...]]


def lexicon_from_utterances(utterances: list[Utterance] | None = None) -> dict[str, tuple[str, ...]]:
    """Inventory of slot values in the closed grammar, not the label of one row."""

    rows = utterances if utterances is not None else generate_utterances()
    found: dict[str, set[str]] = {}
    for row in rows:
        for name, value in row.slots.items():
            found.setdefault(name, set()).add(value)
    found.setdefault("currency", set()).add("rupees")
    return {
        name: tuple(sorted(values, key=lambda item: (-len(item), item.casefold())))
        for name, values in found.items()
    }


def intent_hits(text: str) -> tuple[str, ...]:
    """Intent cues. More than one hit means the string does not support a single intent."""

    lowered = text.casefold()
    hits: list[str] = []
    if "book" in lowered and "appointment" in lowered:
        hits.append("book_appointment")
    if "cancel" in lowered and "appointment" in lowered:
        hits.append("cancel_appointment")
    if "when" in lowered and "appointment" in lowered:
        hits.append("check_appointment")
    if "balance" in lowered:
        hits.append("check_balance")
    if "transfer" in lowered and "rupee" in lowered:
        hits.append("transfer_money")
    if "transaction" in lowered:
        hits.append("check_transaction")
    if "remind" in lowered:
        hits.append("set_reminder")
    if "rain" in lowered:
        hits.append("weather_query")
    if "play" in lowered and "music" in lowered:
        hits.append("play_music")
    if "tell me your " in lowered or " your " in lowered or lowered.startswith("your "):
        hits.append("general_information")
    return tuple(hits)


def value_in_text(text: str, value: str) -> bool:
    """True when the whole lexicon value occurs on token boundaries."""

    lowered = text.casefold()
    target = value.casefold()
    if not target:
        return False
    start = 0
    while True:
        index = lowered.find(target, start)
        if index < 0:
            return False
        if _bounded(lowered, index, index + len(target)):
            return True
        start = index + 1


def _bounded(text: str, start: int, end: int) -> bool:
    """A lexicon value must begin and end on a token boundary."""

    before = start == 0 or not text[start - 1].isalnum()
    after = end == len(text) or not text[end].isalnum()
    return before and after


def _find_values(text: str, values: tuple[str, ...]) -> tuple[str, ...]:
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
            if target and _bounded(lowered, index, end) and not any(occupied[index:end]):
                for cursor in range(index, end):
                    occupied[cursor] = True
                found.append(value)
                break
            start = index + 1
    return tuple(found)


def assess(text: str, lexicon: dict[str, tuple[str, ...]]) -> Evidence:
    """Read intent cues and lexicon slot values from one candidate."""

    slots = {
        name: _find_values(text, values)
        for name, values in lexicon.items()
        if _find_values(text, values)
    }
    return Evidence(intent_hits(text), slots)


def frame_is_complete(evidence: Evidence) -> tuple[str, dict[str, str]] | None:
    """Return a frame only when one intent has every critical slot, with one value each."""

    if len(evidence.intents) != 1:
        return None
    intent = evidence.intents[0]
    frame: dict[str, str] = {}
    for name in CRITICAL_SLOTS[intent]:
        values = evidence.slots.get(name, ())
        if len(values) != 1:
            return None
        frame[name] = values[0]
    return intent, frame
