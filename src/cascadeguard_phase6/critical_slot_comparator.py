"""Compare a candidate frame with an explicit reference. The referent is an argument."""

from __future__ import annotations

from cascadeguard.evaluation.semantic_evidence import CRITICAL_SLOTS
from cascadeguard_phase5.critical_slot_verifier_v5 import normalize_value
from cascadeguard_phase5.modality_analyzer_v5 import analyze_modality


def compare_reference(frame: dict[str, object] | None, reference: dict[str, object]) -> dict[str, object]:
    reasons: list[str] = []
    if reference.get("reference_provenance") != "EXPLICIT":
        reasons.append("INVALID_REFERENCE")
    if not reference.get("reference_id"):
        reasons.append("MISSING_REFERENCE_ID")
    if frame is None:
        reasons.append("MISSING_CANDIDATE_FRAME")
        return {"match": False, "reasons": reasons}
    if reference.get("intent") != frame.get("intent"):
        reasons.append("REFERENCE_INTENT_CONFLICT")
    required = CRITICAL_SLOTS.get(str(frame.get("intent")), ())
    supplied = dict(reference.get("critical_slots") or {})
    for name in required:
        spec = supplied.get(name)
        if not isinstance(spec, dict) or not spec.get("value"):
            reasons.append("MISSING_REFERENCE_FIELD")
            continue
        candidate_value = dict(frame.get("slots") or {}).get(name)
        if candidate_value is None:
            reasons.append("MISSING_CRITICAL_SLOT")
        elif normalize_value(name, str(candidate_value)) != normalize_value(name, str(spec["value"])):
            reasons.append("REFERENCE_SLOT_CONFLICT")
    if reference.get("reference_scope") == "full_referent":
        transcript = reference.get("parent_transcript")
        if not isinstance(transcript, str) or not transcript.strip():
            reasons.append("MISSING_PARENT_TRANSCRIPT")
        else:
            reading = analyze_modality(transcript)
            if not reading.is_execution_ready:
                reasons.append("PARENT_REFERENT_NOT_EXECUTION_READY")
    return {"match": not reasons, "reasons": list(dict.fromkeys(reasons))}
