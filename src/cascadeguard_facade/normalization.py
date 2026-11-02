"""Map raw controller results onto commit rules without editing those results."""

from __future__ import annotations

from cascadeguard_facade.contracts import (
    COMMITTING_ACTIONS,
    NormalizedDecision,
    RawControllerOutput,
    SemanticFrame,
)


def _frame_from_raw(raw: RawControllerOutput) -> SemanticFrame:
    return SemanticFrame(raw.intent, raw.slots)


def normalize(raw: RawControllerOutput) -> NormalizedDecision:
    """Apply the facade commit rule.

    B0 and prefix B1 always answer, so the parse is the committed frame.
    Forced lexical selection returns a frame for exact-match scoring, and the
    existing function says that frame is not a safety commit. The answered
    frame is kept, and the committed frame stays empty.
    CONTINUE and RETRY commit the selected frame. CLARIFY and HOLD do not,
    even when the raw prefix output still carries one-best text.
    """

    if not raw.invoked:
        return NormalizedDecision(
            raw.strategy,
            raw.utterance_id,
            "HOLD",
            raw.reason or "EMPTY_BUNDLE",
            None,
            None,
            None,
        )
    if raw.strategy == "b1_forced_lexical":
        return NormalizedDecision(
            raw.strategy,
            raw.utterance_id,
            None,
            "forced_selection_is_not_a_safety_commit",
            None,
            _frame_from_raw(raw),
            None,
        )
    if raw.strategy in {"b0_prefix", "b1_prefix"}:
        frame = _frame_from_raw(raw)
        return NormalizedDecision(
            raw.strategy,
            raw.utterance_id,
            None,
            "always_answers",
            frame,
            frame,
            None,
        )
    if raw.action in {"CLARIFY", "HOLD"}:
        return NormalizedDecision(
            raw.strategy,
            raw.utterance_id,
            raw.action,
            raw.reason or raw.action,
            None,
            None,
            None,
        )
    if raw.action in COMMITTING_ACTIONS:
        frame = _frame_from_raw(raw)
        mechanism = raw.retry_mechanism if raw.action == "RETRY" else None
        return NormalizedDecision(
            raw.strategy,
            raw.utterance_id,
            raw.action,
            raw.reason or raw.action,
            frame,
            frame,
            mechanism,
        )
    return NormalizedDecision(
        raw.strategy,
        raw.utterance_id,
        raw.action,
        raw.reason or "unrecognized_action",
        None,
        _frame_from_raw(raw) if raw.intent is not None or raw.slots else None,
        None,
    )
