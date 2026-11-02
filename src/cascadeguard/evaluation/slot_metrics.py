"""Micro slot precision, recall, and F1 on (name, value) pairs."""

from __future__ import annotations


def _f1(precision: float | None, recall: float | None) -> float | None:
    """Harmonic mean. Zero matches with both denominators present is 0, not undefined."""

    if precision is None or recall is None:
        return None
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _pairs(slots: dict[str, str]) -> list[tuple[str, str]]:
    return sorted((key.casefold(), value.casefold().strip()) for key, value in slots.items())


def slot_scores(
    rows: list[tuple[dict[str, str], dict[str, str]]],
) -> dict[str, float | int | None]:
    """Micro-average slot scores. Empty both sides counts as one true positive pair-set."""

    matched = 0
    predicted = 0
    reference = 0
    for reference_slots, predicted_slots in rows:
        reference_pairs = _pairs(reference_slots)
        predicted_pairs = _pairs(predicted_slots)
        if not reference_pairs and not predicted_pairs:
            matched += 1
            predicted += 1
            reference += 1
            continue
        reference_set = set(reference_pairs)
        predicted_set = set(predicted_pairs)
        matched += len(reference_set & predicted_set)
        predicted += len(predicted_set)
        reference += len(reference_set)
    precision = None if predicted == 0 else matched / predicted
    recall = None if reference == 0 else matched / reference
    f1 = _f1(precision, recall)
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "matched_pairs": matched,
        "predicted_pairs": predicted,
        "reference_pairs": reference,
    }


def per_slot_scores(
    rows: list[tuple[dict[str, str], dict[str, str]]],
) -> dict[str, dict[str, float | int | None]]:
    """Precision, recall, and F1 for each slot name that appears in gold or prediction.

    An utterance with neither side containing the slot is not a true positive.
    """

    names: set[str] = set()
    for reference_slots, predicted_slots in rows:
        names.update(key.casefold() for key in reference_slots)
        names.update(key.casefold() for key in predicted_slots)
    report: dict[str, dict[str, float | int | None]] = {}
    for name in sorted(names):
        matched = 0
        predicted = 0
        reference = 0
        for reference_slots, predicted_slots in rows:
            reference_map = {key.casefold(): value.casefold().strip() for key, value in reference_slots.items()}
            predicted_map = {key.casefold(): value.casefold().strip() for key, value in predicted_slots.items()}
            in_reference = name in reference_map
            in_predicted = name in predicted_map
            if in_reference:
                reference += 1
            if in_predicted:
                predicted += 1
            if in_reference and in_predicted and reference_map[name] == predicted_map[name]:
                matched += 1
        precision = None if predicted == 0 else matched / predicted
        recall = None if reference == 0 else matched / reference
        report[name] = {
            "precision": precision,
            "recall": recall,
            "f1": _f1(precision, recall),
            "matched": matched,
            "predicted": predicted,
            "reference": reference,
        }
    return report
