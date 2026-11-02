"""Closed set of 200 synthetic utterances with intent and slot labels."""

from __future__ import annotations

from dataclasses import dataclass

DATASET_LABEL = "synthetic"

INTENTS: tuple[str, ...] = (
    "book_appointment",
    "cancel_appointment",
    "check_appointment",
    "check_balance",
    "transfer_money",
    "check_transaction",
    "set_reminder",
    "weather_query",
    "play_music",
    "general_information",
)

_DATES: tuple[str, ...] = (
    "tomorrow",
    "Friday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Saturday",
    "Sunday",
    "next week",
    "this evening",
    "noon",
    "3 PM",
    "today",
    "April 2",
    "May 5",
    "June 10",
    "July 1",
    "August 12",
    "September 9",
    "October 3",
)

_ACCOUNTS: tuple[str, ...] = (
    "account",
    "savings account",
    "checking account",
    "salary account",
    "current account",
    "joint account",
    "travel account",
    "student account",
    "business account",
    "family account",
    "primary account",
    "secondary account",
    "card account",
    "wallet",
    "deposit account",
    "tax account",
    "expense account",
    "holiday account",
    "emergency account",
    "daily account",
)

_AMOUNTS: tuple[str, ...] = (
    "500",
    "100",
    "250",
    "1000",
    "50",
    "75",
    "200",
    "300",
    "400",
    "750",
    "1500",
    "2000",
    "20",
    "40",
    "60",
    "80",
    "120",
    "180",
    "900",
    "650",
)

_RECENCY: tuple[str, ...] = (
    "latest",
    "last",
    "previous",
    "recent",
    "newest",
    "first",
    "second",
    "third",
    "pending",
    "cleared",
    "failed",
    "large",
    "small",
    "card",
    "cash",
    "online",
    "weekly",
    "monthly",
    "yesterday",
    "today",
)

_TIMES: tuple[str, ...] = (
    "6 PM",
    "7 AM",
    "8 PM",
    "9 AM",
    "5 PM",
    "4 PM",
    "10 AM",
    "11 AM",
    "1 PM",
    "2 PM",
    "3 PM",
    "12 PM",
    "6 AM",
    "7 PM",
    "8 AM",
    "9 PM",
    "10 PM",
    "11 PM",
    "noon",
    "midnight",
)

_GENRES: tuple[str, ...] = (
    "jazz",
    "classical",
    "rock",
    "pop",
    "blues",
    "folk",
    "hip hop",
    "electronic",
    "country",
    "reggae",
    "metal",
    "soul",
    "disco",
    "ambient",
    "opera",
    "punk",
    "latin",
    "indie",
    "acoustic",
    "instrumental",
)

_TOPICS: tuple[str, ...] = (
    "working hours",
    "Saturday hours",
    "branch address",
    "phone number",
    "support email",
    "holiday calendar",
    "membership rules",
    "fee schedule",
    "lost card process",
    "password reset",
    "branch manager",
    "complaint desk",
    "service status",
    "queue time",
    "document list",
    "identification rules",
    "closing time",
    "opening time",
    "parking rules",
    "wheelchair access",
)


@dataclass(frozen=True)
class Utterance:
    """One original synthetic utterance. Not a Common Voice row."""

    utterance_id: str
    intent: str
    text: str
    slots: dict[str, str]
    dataset: str = DATASET_LABEL

    def to_row(self) -> dict[str, str]:
        return {
            "utterance_id": self.utterance_id,
            "intent": self.intent,
            "text": self.text,
            "slots": _format_slots(self.slots),
            "dataset": self.dataset,
            "synthetic": "true",
        }


def _format_slots(slots: dict[str, str]) -> str:
    parts = [f"{key}={value}" for key, value in sorted(slots.items())]
    return "|".join(parts)


def _check_count(name: str, values: tuple[str, ...]) -> None:
    if len(values) != 20:
        raise ValueError(f"{name} must contain 20 values, found {len(values)}")


def generate_utterances() -> list[Utterance]:
    """Return 10 intents × 20 utterances in a fixed order."""

    _check_count("dates", _DATES)
    _check_count("accounts", _ACCOUNTS)
    _check_count("amounts", _AMOUNTS)
    _check_count("recency", _RECENCY)
    _check_count("times", _TIMES)
    _check_count("genres", _GENRES)
    _check_count("topics", _TOPICS)

    rows: list[Utterance] = []

    def add(intent: str, text: str, slots: dict[str, str]) -> None:
        utterance_id = f"utt-{len(rows):03d}"
        rows.append(Utterance(utterance_id, intent, text, dict(slots)))

    add("book_appointment", "Book an appointment for tomorrow", {"date": "tomorrow"})
    for date in _DATES[1:]:
        add("book_appointment", f"Book an appointment for {date}", {"date": date})

    add("cancel_appointment", "Cancel my appointment", {})
    for date in _DATES[1:]:
        add("cancel_appointment", f"Cancel my appointment for {date}", {"date": date})

    add("check_appointment", "When is my appointment?", {})
    for date in _DATES[1:]:
        add("check_appointment", f"When is my {date} appointment?", {"date": date})

    for account in _ACCOUNTS:
        add("check_balance", f"What is my {account} balance?", {"account": account})

    for amount in _AMOUNTS:
        add(
            "transfer_money",
            f"Transfer {amount} rupees",
            {"amount": amount, "currency": "rupees"},
        )

    for recency in _RECENCY:
        add(
            "check_transaction",
            f"Show my {recency} transaction",
            {"recency": recency},
        )

    for when in _TIMES:
        add("set_reminder", f"Remind me at {when}", {"time": when})

    for when in _DATES:
        add("weather_query", f"Will it rain {when}?", {"date": when})

    for genre in _GENRES:
        add("play_music", f"Play {genre} music", {"genre": genre})

    for topic in _TOPICS:
        add(
            "general_information",
            f"What are your {topic}?",
            {"topic": topic},
        )

    if len(rows) != 200:
        raise ValueError(f"Expected 200 utterances, built {len(rows)}")
    return rows
