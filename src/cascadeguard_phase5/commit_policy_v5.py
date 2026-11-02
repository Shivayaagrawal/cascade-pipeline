"""The only function that may turn a proposal into a committed frame."""

from __future__ import annotations

from dataclasses import dataclass

from cascadeguard_phase5.candidate_provenance_v5 import lookup
from cascadeguard_phase5.critical_slot_verifier_v5 import support_in_candidate


@dataclass(frozen=True)
class GateSwitches:
    modality: bool = True
    polarity: bool = True
    critical_slots: bool = True
    provenance: bool = True
    conditionality: bool = True
    gate: bool = True
    recovery: bool = True
    risk: bool = True


def execution_allowed(modality: dict[str, object], switches: GateSwitches) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if switches.polarity and (modality["polarity"] == "negative" or modality["modality"] == "NEGATION"):
        reasons.append("POLARITY_BLOCKS_EXECUTION")
    if switches.modality and modality["modality"] in {"UNCERTAINTY", "AMBIGUOUS_OR_MIXED"}:
        reasons.append("MODALITY_NOT_EXECUTION_READY")
    if switches.conditionality and (modality["conditionality"] == "conditional" or modality["modality"] == "CONDITIONAL"):
        reasons.append("CONDITIONALITY_UNRESOLVED")
    return not reasons, reasons


def apply_gate(
    proposal: dict[str, object],
    candidates: list[dict[str, object]],
    lexicon: dict[str, tuple[str, ...]],
    switches: GateSwitches,
) -> dict[str, object]:
    """Copy the proposal into a normalized decision. The proposal object is not edited."""

    action = str(proposal["action"])
    candidate_id = proposal.get("candidate_id")
    frame = proposal.get("frame")
    reasons: list[str] = []
    if not switches.gate:
        committed = action in {"CONTINUE", "RETRY"} and isinstance(frame, dict)
        return {
            "action": action,
            "committed": committed,
            "committed_candidate_id": candidate_id if committed else None,
            "committed_frame": frame if committed else None,
            "blocking_reasons": ["GATE_DISABLED"],
            "gate_passed": False,
        }
    if action in {"HOLD", "CLARIFY"}:
        return {
            "action": action,
            "committed": False,
            "committed_candidate_id": None,
            "committed_frame": None,
            "blocking_reasons": list(proposal.get("reasons") or []),
            "gate_passed": True,
        }
    if action == "RETRY" and not switches.recovery:
        reasons.append("RECOVERY_DISABLED")
    if switches.provenance:
        if not candidate_id or lookup(candidates, str(candidate_id)) is None:
            reasons.append("CANDIDATE_NOT_IN_BUNDLE")
    selected = lookup(candidates, None if candidate_id is None else str(candidate_id))
    modality = {} if selected is None else dict(selected.get("modality") or {})
    if selected is not None:
        allowed, modality_reasons = execution_allowed(modality, switches)
        if not allowed:
            reasons.extend(modality_reasons)
        reading = selected.get("reading") or {}
        slots = dict(frame["slots"]) if isinstance(frame, dict) else {}
        if not reading.get("frame"):
            reasons.append("MISSING_REQUIRED_SLOT")
        elif isinstance(frame, dict) and (reading["frame"]["intent"] != frame["intent"] or reading["frame"]["slots"] != slots):
            reasons.append("FRAME_DOES_NOT_MATCH_CANDIDATE")
        if switches.critical_slots:
            support = support_in_candidate(slots, str(selected["text"]), lexicon)
            if support["blocking_reasons"]:
                reasons.extend(str(item) for item in support["blocking_reasons"])
            if reading.get("unrecognized"):
                reasons.append("OUT_OF_INVENTORY")
    elif switches.provenance:
        reasons.append("MISSING_CANDIDATE_ID")
    if action not in {"CONTINUE", "RETRY"}:
        reasons.append("ACTION_CANNOT_COMMIT")
    if reasons:
        return {
            "action": "HOLD",
            "committed": False,
            "committed_candidate_id": None,
            "committed_frame": None,
            "blocking_reasons": list(dict.fromkeys(reasons)),
            "gate_passed": True,
        }
    return {
        "action": action,
        "committed": True,
        "committed_candidate_id": candidate_id,
        "committed_frame": frame,
        "blocking_reasons": [],
        "gate_passed": True,
    }
