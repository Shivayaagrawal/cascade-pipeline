"""Critical-value checks.

The controller calls support_in_candidate(). It does not receive the oracle referent.
compare_to_referent() is for the evaluator and the unit tests.
"""

from __future__ import annotations

import re

MONTHS = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)
DATE_PHRASE = re.compile(
    r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2})\b",
    re.IGNORECASE,
)
TIME_PHRASE = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*([AaPp][Mm])\b")
AMOUNT_TOKEN = re.compile(r"\b\d+\b")


def normalize_value(slot: str, value: str) -> str:
    text = " ".join(value.split())
    if slot == "time":
        match = TIME_PHRASE.search(text)
        if text.casefold() == "noon":
            return "12:00"
        if text.casefold() == "midnight":
            return "00:00"
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2) or "0")
            if match.group(3).casefold() == "pm" and hour != 12:
                hour += 12
            if match.group(3).casefold() == "am" and hour == 12:
                hour = 0
            return f"{hour:02d}:{minute:02d}"
    if slot == "amount":
        digits = re.sub(r"\D", "", text)
        if digits:
            return str(int(digits))
    return text.casefold()


def _known(lexicon: dict[str, tuple[str, ...]], slot: str) -> set[str]:
    return {item.casefold() for item in lexicon.get(slot, ())}


def unrecognized_values(text: str, lexicon: dict[str, tuple[str, ...]]) -> tuple[dict[str, str], ...]:
    """Critical spans that are not in the closed inventory. The referent is not used."""

    found: list[dict[str, str]] = []
    dates = _known(lexicon, "date")
    times = _known(lexicon, "time")
    amounts = _known(lexicon, "amount")
    for match in DATE_PHRASE.finditer(text):
        phrase = f"{match.group(1)} {int(match.group(2))}"
        if phrase.casefold() not in dates and match.group(0).casefold() not in dates:
            found.append({"slot": "date", "value": match.group(0), "status": "OUT_OF_INVENTORY"})
    for match in TIME_PHRASE.finditer(text):
        if match.group(0).casefold() not in times:
            found.append({"slot": "time", "value": match.group(0), "status": "OUT_OF_INVENTORY"})
    if re.search(r"\brupees?\b", text, re.IGNORECASE):
        for match in AMOUNT_TOKEN.finditer(text):
            if match.group(0) not in amounts:
                found.append({"slot": "amount", "value": match.group(0), "status": "OUT_OF_INVENTORY"})
    return tuple(found)


def value_in_text(text: str, value: str) -> bool:
    lowered = text.casefold()
    target = value.casefold()
    start = 0
    while True:
        index = lowered.find(target, start)
        if index < 0:
            return False
        end = index + len(target)
        before = index == 0 or not text[index - 1].isalnum()
        after = end == len(text) or not text[end].isalnum()
        if before and after:
            return True
        start = index + 1


def support_in_candidate(
    frame: dict[str, str] | None,
    text: str,
    lexicon: dict[str, tuple[str, ...]],
) -> dict[str, object]:
    """A committed frame may contain only values evidenced by this candidate."""

    extras = unrecognized_values(text, lexicon)
    checks: list[dict[str, str]] = []
    if frame:
        for slot, value in frame.items():
            status = "SUPPORTED" if value_in_text(text, value) else "UNSUPPORTED"
            checks.append(
                {
                    "slot": slot,
                    "candidate_value": value,
                    "normalized_candidate": normalize_value(slot, value),
                    "status": status,
                }
            )
    blocking = [item["slot"] for item in checks if item["status"] != "SUPPORTED"]
    blocking.extend(item["value"] for item in extras)
    status = "CONFLICT" if extras or blocking else "SUPPORTED"
    reasons: list[str] = []
    if extras:
        reasons.append("OUT_OF_INVENTORY")
    if any(item["status"] == "UNSUPPORTED" for item in checks):
        reasons.append("FRAME_NOT_IN_CANDIDATE")
    return {
        "verified": not reasons,
        "status": status if reasons else "SUPPORTED",
        "checks": checks,
        "unrecognized": list(extras),
        "blocking_reasons": reasons,
    }


def compare_to_referent(
    referent: dict[str, str],
    candidate_values: dict[str, str],
) -> dict[str, object]:
    """Evaluator comparison. The controller does not call this with oracle labels."""

    checks = []
    for slot, parent_value in sorted(referent.items()):
        candidate_value = candidate_values.get(slot)
        if candidate_value is None:
            status = "MISSING"
        elif normalize_value(slot, parent_value) == normalize_value(slot, candidate_value):
            status = "MATCH"
        else:
            status = "CONFLICT"
        checks.append(
            {
                "slot": slot,
                "referent_value": parent_value,
                "candidate_value": candidate_value,
                "normalized_referent": normalize_value(slot, parent_value),
                "normalized_candidate": None if candidate_value is None else normalize_value(slot, candidate_value),
                "status": status,
            }
        )
    reasons = ["CRITICAL_SLOT_CONFLICT" if item["status"] == "CONFLICT" else "MISSING_CRITICAL_SLOT" for item in checks if item["status"] != "MATCH"]
    return {
        "verified": not reasons,
        "status": "CONFLICT" if any(item["status"] == "CONFLICT" for item in checks) else ("MISSING" if reasons else "MATCH"),
        "checks": checks,
        "blocking_reasons": reasons,
    }
