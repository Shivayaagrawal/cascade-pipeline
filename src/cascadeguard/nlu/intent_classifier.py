"""Intent cues for the synthetic grammar."""

from __future__ import annotations

from dataclasses import dataclass

_CUES: tuple[tuple[str, str], ...] = (
    ("book_appointment", "book an appointment for "),
    ("cancel_appointment", "cancel my appointment"),
    ("check_appointment", "when is my appointment"),
    ("check_balance", " balance?"),
    ("transfer_money", "transfer "),
    ("check_transaction", " transaction"),
    ("set_reminder", "remind me at "),
    ("weather_query", "will it rain "),
    ("play_music", " music"),
    ("general_information", "what are your "),
)


@dataclass(frozen=True)
class IntentPrediction:
    intent: str | None
    ambiguous: bool
    matched_intents: tuple[str, ...]


def _matched(text: str) -> list[str]:
    lowered = text.casefold()
    found: list[str] = []
    for intent, cue in _CUES:
        if intent == "play_music":
            if lowered.startswith("play ") and cue in lowered:
                found.append(intent)
            continue
        if intent == "transfer_money":
            if lowered.startswith("transfer ") and "rupees" in lowered:
                found.append(intent)
            continue
        if intent == "check_balance":
            if "what is my " in lowered and " balance?" in lowered:
                found.append(intent)
            continue
        if intent == "check_appointment":
            if lowered.startswith("when is my ") and "appointment" in lowered:
                found.append(intent)
            continue
        if cue in lowered:
            found.append(intent)
    return found


def classify_intent(text: str) -> IntentPrediction:
    """Return one intent, or ambiguous when more than one cue matches."""

    matched = tuple(_matched(text))
    if len(matched) == 1:
        return IntentPrediction(matched[0], False, matched)
    if len(matched) == 0:
        return IntentPrediction(None, False, matched)
    return IntentPrediction(None, True, matched)
