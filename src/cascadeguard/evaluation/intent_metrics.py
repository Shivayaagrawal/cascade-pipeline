"""Intent accuracy and exact frame match."""

from __future__ import annotations


def _norm_slots(slots: dict[str, str]) -> frozenset[tuple[str, str]]:
    return frozenset((key.casefold(), value.casefold().strip()) for key, value in slots.items())


def frames_equal(
    reference_intent: str,
    reference_slots: dict[str, str],
    predicted_intent: str | None,
    predicted_slots: dict[str, str],
) -> bool:
    """True when intent and every slot pair match."""

    return predicted_intent == reference_intent and _norm_slots(reference_slots) == _norm_slots(
        predicted_slots
    )


def intent_accuracy(pairs: list[tuple[str, str | None]]) -> float | None:
    """Fraction of utterances whose predicted intent equals the reference intent."""

    if not pairs:
        return None
    correct = sum(1 for reference, predicted in pairs if predicted == reference)
    return correct / len(pairs)


def exact_frame_match(
    rows: list[tuple[str, dict[str, str], str | None, dict[str, str]]],
) -> float | None:
    """Intent and every slot pair must match. Partial slot credit is not a frame match."""

    if not rows:
        return None
    correct = 0
    for reference_intent, reference_slots, predicted_intent, predicted_slots in rows:
        if frames_equal(reference_intent, reference_slots, predicted_intent, predicted_slots):
            correct += 1
    return correct / len(rows)


def semantic_error_rate(
    rows: list[tuple[str, dict[str, str], str | None, dict[str, str]]],
) -> float | None:
    """One minus exact frame match. This name is used only on the synthetic track."""

    matched = exact_frame_match(rows)
    if matched is None:
        return None
    return 1.0 - matched
