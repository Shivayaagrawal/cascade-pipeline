"""Normalization used by the synthetic simulation only."""

from __future__ import annotations

import unicodedata


def normalize(text: str) -> str:
    """NFC, casefold, and collapse whitespace. Punctuation is kept on both sides."""

    normalized = unicodedata.normalize("NFC", text).casefold()
    return " ".join(normalized.split())
