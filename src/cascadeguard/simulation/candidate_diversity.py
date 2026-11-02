"""Alternate synthetic candidate lists.

None of these lists is allowed to contain the gold transcript.
The gold string is an oracle-only input.
"""

from __future__ import annotations

from cascadeguard.simulation.error_injector import generate_variants
from cascadeguard.simulation.utterance_generator import Utterance


def gold_is_absent(gold_text: str, candidates: list[str]) -> bool:
    """True when no candidate is, or contains, the original sentence."""

    gold = gold_text.casefold()
    return all(gold not in candidate.casefold() for candidate in candidates)


def gold_is_not_exact(gold_text: str, candidates: list[str]) -> bool:
    """True when no candidate is exactly the original sentence.

    The v1 ambiguous edit appends a second question, so the original wording can
    remain inside a longer string. That edit is not a separate gold candidate.
    """

    gold = gold_text.casefold()
    return all(candidate.casefold() != gold for candidate in candidates)


def paraphrases(utterance: Utterance) -> list[str]:
    """Three wordings that keep slot values without copying the gold sentence."""

    slots = utterance.slots
    intent = utterance.intent
    if intent == "book_appointment":
        date = slots["date"]
        forms = [
            f"booking request {date} for an appointment",
            f"appointment slot {date} to book",
            f"need to book appointment on {date}",
        ]
    elif intent == "cancel_appointment":
        if "date" in slots:
            date = slots["date"]
            forms = [
                f"cancel appointment dated {date}",
                f"appointment cancel for {date}",
                f"please cancel that appointment {date}",
            ]
        else:
            forms = [
                "cancel the appointment now",
                "appointment should cancel",
                "please cancel that appointment",
            ]
    elif intent == "check_appointment":
        if "date" in slots:
            date = slots["date"]
            forms = [
                f"when appointment falls on {date}",
                f"appointment when scheduled {date}",
                f"ask when the appointment is {date}",
            ]
        else:
            forms = [
                "when appointment happens",
                "appointment when scheduled",
                "ask when the appointment is",
            ]
    elif intent == "check_balance":
        account = slots["account"]
        forms = [
            f"balance of the {account}",
            f"{account} balance inquiry",
            f"asking the balance for {account}",
        ]
    elif intent == "transfer_money":
        amount = slots["amount"]
        forms = [
            f"transfer of {amount} in rupees",
            f"rupees {amount} to transfer",
            f"send a transfer of {amount} rupees",
        ]
    elif intent == "check_transaction":
        recency = slots["recency"]
        forms = [
            f"transaction marked {recency}",
            f"{recency} transaction lookup",
            f"show transaction that is {recency}",
        ]
    elif intent == "set_reminder":
        when = slots["time"]
        forms = [
            f"remind about {when}",
            f"reminder set {when}",
            f"at {when} remind me",
        ]
    elif intent == "weather_query":
        date = slots["date"]
        forms = [
            f"rain expected {date}",
            f"{date} rain check",
            f"will rain fall {date}",
        ]
    elif intent == "play_music":
        genre = slots["genre"]
        forms = [
            f"music to play is {genre}",
            f"play some {genre} music now",
            f"{genre} music play request",
        ]
    elif intent == "general_information":
        topic = slots["topic"]
        forms = [
            f"tell me your {topic}",
            f"information on your {topic}",
            f"question about your {topic}",
        ]
    else:
        raise ValueError(intent)
    if not gold_is_absent(utterance.text, forms):
        raise ValueError(f"Paraphrase copied the gold transcript for {utterance.utterance_id}")
    return forms


def slot_removed(utterance: Utterance) -> list[str]:
    """Intent wording kept where possible, gold slot values deleted."""

    forms = []
    for suffix in ("", " please", " now"):
        text = paraphrases(utterance)[0]
        for value in sorted(utterance.slots.values(), key=len, reverse=True):
            text = text.replace(value, "missing")
        forms.append(text + suffix)
    if not gold_is_absent(utterance.text, forms):
        raise ValueError(f"Slot-removed candidate copied gold for {utterance.utterance_id}")
    return forms


def split_evidence(utterance: Utterance) -> list[str]:
    """Put intent words and slot values in different candidates. No candidate has both as gold."""

    removed = slot_removed(utterance)[0]
    values = " ".join(utterance.slots.values()) if utterance.slots else "unspecified"
    forms = [removed, values, "The warehouse is closed today"]
    if not gold_is_absent(utterance.text, forms):
        raise ValueError(f"Split candidate copied gold for {utterance.utterance_id}")
    return forms


def v1_candidate_texts(utterances: list[Utterance], seed: int) -> dict[str, list[str]]:
    """The original three injected variants. Gold text is not added."""

    grouped: dict[str, list[str]] = {row.utterance_id: [] for row in utterances}
    for variant in generate_variants(utterances, seed):
        grouped[variant.utterance_id].append(variant.text)
    for row in utterances:
        if not gold_is_not_exact(row.text, grouped[row.utterance_id]):
            raise ValueError(f"V1 list contains the gold transcript for {row.utterance_id}")
    return grouped
