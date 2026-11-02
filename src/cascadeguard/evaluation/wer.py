"""Word error rate for the synthetic track."""

from __future__ import annotations

from cascadeguard.evaluation.textnorm import normalize


def _distance(reference: list[str], hypothesis: list[str]) -> int:
    rows = len(reference) + 1
    columns = len(hypothesis) + 1
    table = [[0] * columns for _ in range(rows)]
    for i in range(rows):
        table[i][0] = i
    for j in range(columns):
        table[0][j] = j
    for i in range(1, rows):
        for j in range(1, columns):
            cost = 0 if reference[i - 1] == hypothesis[j - 1] else 1
            table[i][j] = min(
                table[i - 1][j] + 1,
                table[i][j - 1] + 1,
                table[i - 1][j - 1] + cost,
            )
    return table[-1][-1]


def utterance_wer(reference: str, hypothesis: str) -> float | None:
    """Return edit distance over reference length. None when the reference is empty."""

    reference_tokens = normalize(reference).split()
    if not reference_tokens:
        return None
    hypothesis_tokens = normalize(hypothesis).split()
    return _distance(reference_tokens, hypothesis_tokens) / len(reference_tokens)


def corpus_wer(pairs: list[tuple[str, str]]) -> dict[str, float | int | None]:
    """Micro-average WER. Empty references are counted and excluded from the ratio."""

    edits = 0
    words = 0
    excluded = 0
    for reference, hypothesis in pairs:
        reference_tokens = normalize(reference).split()
        if not reference_tokens:
            excluded += 1
            continue
        hypothesis_tokens = normalize(hypothesis).split()
        edits += _distance(reference_tokens, hypothesis_tokens)
        words += len(reference_tokens)
    rate = None if words == 0 else edits / words
    return {
        "wer": rate,
        "edits": edits,
        "reference_words": words,
        "utterances": len(pairs),
        "excluded_empty_reference": excluded,
    }
