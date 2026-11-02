"""Controlled transcript variants. These are not ASR N-best lists."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass

from cascadeguard.simulation.utterance_generator import Utterance

ERROR_CATEGORIES: tuple[str, ...] = (
    "deletion",
    "substitution",
    "insertion",
    "entity_corruption",
    "number_corruption",
    "negation_corruption",
    "ambiguous_transcript",
    "incorrect_transcript",
)

PROVENANCE_SYNTHETIC_EDIT = "synthetic_edit"
INCORRECT_TEXT = "The warehouse is closed today"
AMBIGUOUS_SUFFIX = " What is my account balance?"


@dataclass(frozen=True)
class TranscriptVariant:
    """One synthetic hypothesis tied to an original utterance id."""

    utterance_id: str
    variant_id: str
    category: str
    text: str
    provenance: str
    synthetic: bool = True

    def to_row(self) -> dict[str, str]:
        return {
            "utterance_id": self.utterance_id,
            "variant_id": self.variant_id,
            "category": self.category,
            "text": self.text,
            "provenance": self.provenance,
            "synthetic": "true",
        }


def categories_for_index(index: int) -> tuple[str, str, str]:
    """Pick three distinct categories from the utterance index. No RNG."""

    first = index % len(ERROR_CATEGORIES)
    return (
        ERROR_CATEGORIES[first],
        ERROR_CATEGORIES[(first + 3) % len(ERROR_CATEGORIES)],
        ERROR_CATEGORIES[(first + 5) % len(ERROR_CATEGORIES)],
    )


def _tokens(text: str) -> list[str]:
    return text.split()


def _join(tokens: list[str]) -> str:
    return " ".join(tokens)


def _replace_span(text: str, old: str, new: str) -> str:
    lowered = text.casefold()
    target = old.casefold()
    start = lowered.find(target)
    if start < 0:
        return text
    return text[:start] + new + text[start + len(old) :]


def apply_category(text: str, slots: dict[str, str], category: str, rng: random.Random) -> str:
    """Return a changed transcript. The category name is analysis metadata."""

    tokens = _tokens(text)
    if category == "deletion":
        if len(tokens) < 2:
            return text + " deleted"
        index = rng.randrange(len(tokens))
        del tokens[index]
        return _join(tokens)
    if category == "substitution":
        if not tokens:
            return "banana"
        index = rng.randrange(len(tokens))
        tokens[index] = "banana"
        return _join(tokens)
    if category == "insertion":
        index = 1 if len(tokens) > 1 else 0
        tokens.insert(index, "please")
        return _join(tokens)
    if category == "entity_corruption":
        for value in sorted(slots.values(), key=len, reverse=True):
            if value and value.casefold() in text.casefold():
                return _replace_span(text, value, "other")
        return text + " other"
    if category == "number_corruption":
        match = re.search(r"\d+", text)
        if match is not None:
            number = int(match.group(0))
            return text[: match.start()] + str(number + 1) + text[match.end() :]
        if tokens:
            tokens[0] = "9"
            return _join(tokens)
        return "9"
    if category == "negation_corruption":
        if " not " in f" {text.casefold()} ":
            return re.sub(r"\bnot\b", "", text, count=1, flags=re.IGNORECASE).replace("  ", " ").strip()
        if tokens:
            tokens.insert(1 if len(tokens) > 1 else 0, "not")
            return _join(tokens)
        return "not"
    if category == "ambiguous_transcript":
        return text.rstrip() + AMBIGUOUS_SUFFIX
    if category == "incorrect_transcript":
        return INCORRECT_TEXT
    raise ValueError(f"Unknown error category: {category}")


def generate_variants(utterances: list[Utterance], seed: int) -> list[TranscriptVariant]:
    """Build three synthetic variants per utterance. Provenance is never N-best."""

    variants: list[TranscriptVariant] = []
    for index, utterance in enumerate(utterances):
        for offset, category in enumerate(categories_for_index(index)):
            rng = random.Random(f"{seed}:{utterance.utterance_id}:{category}")
            text = apply_category(utterance.text, utterance.slots, category, rng)
            if text == utterance.text:
                text = text + " changed"
            variants.append(
                TranscriptVariant(
                    utterance_id=utterance.utterance_id,
                    variant_id=f"{utterance.utterance_id}-v{offset}",
                    category=category,
                    text=text,
                    provenance=PROVENANCE_SYNTHETIC_EDIT,
                )
            )
    return variants
