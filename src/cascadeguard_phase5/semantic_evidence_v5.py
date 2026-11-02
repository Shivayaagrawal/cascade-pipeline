"""Read a candidate with the frozen lexical assessor. Gold is not an argument."""

from __future__ import annotations

from cascadeguard.evaluation.semantic_evidence import CRITICAL_SLOTS, assess, frame_is_complete
from cascadeguard_phase5.critical_slot_verifier_v5 import unrecognized_values


def read_candidate(text: str, lexicon: dict[str, tuple[str, ...]]) -> dict[str, object]:
    evidence = assess(text, lexicon)
    frame = frame_is_complete(evidence)
    intent = None if frame is None else frame[0]
    slots = {} if frame is None else dict(frame[1])
    return {
        "intents": list(evidence.intents),
        "frame": None if intent is None else {"intent": intent, "slots": slots},
        "intent": intent,
        "slots": slots,
        "unrecognized": list(unrecognized_values(text, lexicon)),
        "required": list(CRITICAL_SLOTS.get(intent, ())) if intent else [],
    }
