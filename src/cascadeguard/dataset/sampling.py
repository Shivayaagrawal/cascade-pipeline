"""Deterministic utterance order. This module does not read audio or transcripts."""

from __future__ import annotations

import hashlib

from cascadeguard.dataset.acquisition import APPROVED_SPLITS

DEFAULT_SEED = 17
DEVELOPMENT_PILOT = 200
DEVELOPMENT_MAX = 500
HELDOUT_EVALUATION = 200


def order_utterances(utterance_ids: list[str], split: str, seed: int = DEFAULT_SEED) -> list[str]:
    """Return IDs in a stable order that does not use file size.

    The key is the SHA-256 of ``seed:split:utterance_id``. Equal keys keep
    lexicographic ID order. The development pilot is a prefix of the longer
    development sample when both use this order.
    """

    if split not in APPROVED_SPLITS:
        raise ValueError(f"split {split!r} is not an approved split")
    if len(set(utterance_ids)) != len(utterance_ids):
        raise ValueError("duplicate utterance IDs")

    def key(utterance_id: str) -> tuple[str, str]:
        digest = hashlib.sha256(f"{seed}:{split}:{utterance_id}".encode("utf-8")).hexdigest()
        return (digest, utterance_id)

    return sorted(utterance_ids, key=key)
