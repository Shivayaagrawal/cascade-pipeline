"""Slot extraction for synthetic templates. Missing slots stay missing."""

from __future__ import annotations


def _after(text: str, prefix: str) -> str | None:
    lowered = text.casefold()
    if not lowered.startswith(prefix):
        return None
    return text[len(prefix) :].strip()


def extract_slots(intent: str | None, text: str) -> dict[str, str]:
    """Extract slots only when the synthetic template prefix matches."""

    if intent is None:
        return {}
    lowered = text.casefold()
    if intent == "book_appointment":
        value = _after(text, "book an appointment for ")
        return {"date": value} if value else {}
    if intent == "cancel_appointment":
        if lowered == "cancel my appointment":
            return {}
        value = _after(text, "cancel my appointment for ")
        return {"date": value} if value else {}
    if intent == "check_appointment":
        if lowered == "when is my appointment?":
            return {}
        if lowered.startswith("when is my ") and lowered.endswith(" appointment?"):
            value = text[len("when is my ") : -len(" appointment?")].strip()
            return {"date": value} if value else {}
        return {}
    if intent == "check_balance":
        if lowered.startswith("what is my ") and lowered.endswith(" balance?"):
            value = text[len("what is my ") : -len(" balance?")].strip()
            return {"account": value} if value else {}
        return {}
    if intent == "transfer_money":
        value = _after(text, "transfer ")
        if value is None or not value.casefold().endswith(" rupees"):
            return {}
        amount = value[: -len(" rupees")].strip()
        if not amount:
            return {}
        return {"amount": amount, "currency": "rupees"}
    if intent == "check_transaction":
        if lowered.startswith("show my ") and lowered.endswith(" transaction"):
            value = text[len("show my ") : -len(" transaction")].strip()
            return {"recency": value} if value else {}
        return {}
    if intent == "set_reminder":
        value = _after(text, "remind me at ")
        return {"time": value} if value else {}
    if intent == "weather_query":
        if lowered.startswith("will it rain ") and lowered.endswith("?"):
            value = text[len("will it rain ") : -1].strip()
            return {"date": value} if value else {}
        return {}
    if intent == "play_music":
        if lowered.startswith("play ") and lowered.endswith(" music"):
            value = text[len("play ") : -len(" music")].strip()
            return {"genre": value} if value else {}
        return {}
    if intent == "general_information":
        if lowered.startswith("what are your ") and lowered.endswith("?"):
            value = text[len("what are your ") : -1].strip()
            return {"topic": value} if value else {}
        return {}
    return {}
