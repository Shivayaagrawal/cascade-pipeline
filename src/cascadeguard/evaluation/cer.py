"""Character error rate. Spaces that survive normalization are characters."""

from __future__ import annotations

from cascadeguard.evaluation.textnorm import normalize
from cascadeguard.evaluation.wer import _distance


def corpus_cer(pairs: list[tuple[str, str]]) -> dict[str, float | int | None]:
    """Micro-average CER on the normalized string, including spaces."""

    edits = 0
    characters = 0
    excluded = 0
    for reference, hypothesis in pairs:
        reference_chars = list(normalize(reference))
        if not reference_chars:
            excluded += 1
            continue
        hypothesis_chars = list(normalize(hypothesis))
        edits += _distance(reference_chars, hypothesis_chars)
        characters += len(reference_chars)
    rate = None if characters == 0 else edits / characters
    return {
        "cer": rate,
        "edits": edits,
        "reference_characters": characters,
        "utterances": len(pairs),
        "excluded_empty_reference": excluded,
    }
