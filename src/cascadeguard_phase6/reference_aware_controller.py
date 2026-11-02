"""Condition B. v5 is called unchanged. Its commit is not accepted until the reference matches."""

from __future__ import annotations

from dataclasses import dataclass

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard_phase5.commit_policy_v5 import GateSwitches, apply_gate, execution_allowed
from cascadeguard_phase5.critical_slot_verifier_v5 import support_in_candidate
from cascadeguard_phase5.modality_analyzer_v5 import analyze_modality
from cascadeguard_phase5.semantic_controller_v5 import run_semantic_v5
from cascadeguard_phase5.semantic_evidence_v5 import read_candidate
from cascadeguard_phase6 import STRATEGY_REFERENCE
from cascadeguard_phase5.candidate_provenance_v5 import validate_bundle as _validate_bundle
from cascadeguard_phase6.critical_slot_comparator import compare_reference
from cascadeguard_phase6.evidence_contract import stripped_bundle


@dataclass(frozen=True)
class ReferenceSwitches:
    modality: bool = True
    polarity: bool = True
    conditionality: bool = True
    provenance: bool = True
    gate: bool = True
    recovery: bool = True
    reference: bool = True


def _gates(switches: ReferenceSwitches) -> GateSwitches:
    return GateSwitches(
        modality=switches.modality,
        polarity=switches.polarity,
        critical_slots=True,
        provenance=switches.provenance,
        conditionality=switches.conditionality,
        gate=switches.gate,
        recovery=switches.recovery,
        risk=True,
    )


def _annotate(bundle: dict[str, object], lexicon: dict[str, tuple[str, ...]]) -> list[dict[str, object]]:
    annotated = []
    for item in bundle["candidates"]:
        reading = read_candidate(str(item["text"]), lexicon)
        modality = analyze_modality(str(item["text"])).as_dict()
        annotated.append({**item, "reading": reading, "modality": modality})
    return annotated


def _eligible(item: dict[str, object], reference: dict[str, object] | None, lexicon, switches: ReferenceSwitches) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    allowed, modality_reasons = execution_allowed(item["modality"], _gates(switches))
    if not allowed:
        reasons.extend(modality_reasons)
    frame = item["reading"]["frame"]
    if frame is None:
        reasons.append("MISSING_REQUIRED_SLOT")
    else:
        support = support_in_candidate(dict(frame["slots"]), str(item["text"]), lexicon)
        if support["blocking_reasons"]:
            reasons.extend(str(reason) for reason in support["blocking_reasons"])
        if item["reading"]["unrecognized"]:
            reasons.append("OUT_OF_INVENTORY")
        if switches.reference:
            if reference is None:
                reasons.append("MISSING_REFERENCE")
            else:
                compared = compare_reference(frame, reference)
                if not compared["match"]:
                    reasons.extend(compared["reasons"])
    return not reasons, list(dict.fromkeys(reasons))


def run_reference_aware(
    case: dict[str, object],
    reference: dict[str, object] | None,
    lexicon: dict[str, tuple[str, ...]] | None = None,
    switches: ReferenceSwitches | None = None,
) -> dict[str, object]:
    switches = switches or ReferenceSwitches()
    lexicon = lexicon if lexicon is not None else lexicon_from_utterances()
    bundle = stripped_bundle(case)
    candidate_only = run_semantic_v5(bundle, lexicon)
    candidates = list(bundle["candidates"])
    if not candidates:
        normalized = {"action": "HOLD", "committed": False, "committed_candidate_id": None, "committed_frame": None, "blocking_reasons": ["EMPTY_BUNDLE"], "gate_passed": True}
        return _pack(candidate_only, {"action": "HOLD", "candidate_id": None, "frame": None, "reasons": ["EMPTY_BUNDLE"]}, normalized, reference, switches)
    valid, validity = _validate_bundle(candidates)
    if not valid:
        raw = {"action": "HOLD", "candidate_id": None, "frame": None, "reasons": [validity]}
        normalized = apply_gate(raw, [], lexicon, _gates(switches))
        return _pack(candidate_only, raw, normalized, reference, switches)
    if not switches.reference:
        adopted = candidate_only["normalized"]
        return _pack(candidate_only, candidate_only["raw"], adopted, reference, switches)
    if switches.reference and (reference is None or reference.get("reference_provenance") != "EXPLICIT"):
        raw = {"action": "HOLD", "candidate_id": None, "frame": None, "reasons": ["MISSING_REFERENCE"]}
        normalized = apply_gate(dict(raw), [], lexicon, _gates(switches))
        return _pack(candidate_only, raw, normalized, reference, switches)

    annotated = _annotate(bundle, lexicon)
    if not switches.gate:
        complete = [item for item in annotated if item["reading"]["frame"] is not None]
        if not complete:
            raw = {"action": "HOLD", "candidate_id": None, "frame": None, "reasons": ["NO_COMPLETE_FRAME"]}
        else:
            action = "CONTINUE" if complete[0]["candidate_id"] == annotated[0]["candidate_id"] else "RETRY"
            raw = {"action": action, "candidate_id": complete[0]["candidate_id"], "frame": complete[0]["reading"]["frame"], "reasons": []}
        normalized = apply_gate(dict(raw), annotated, lexicon, _gates(switches))
        return _pack(candidate_only, raw, normalized, reference, switches)

    if any(len(item["reading"]["intents"]) > 1 for item in annotated):
        raw = {"action": "CLARIFY", "candidate_id": None, "frame": None, "reasons": ["MULTIPLE_INTENTS"]}
        normalized = apply_gate(dict(raw), annotated, lexicon, _gates(switches))
        return _pack(candidate_only, raw, normalized, reference, switches)

    checked = [(item, *_eligible(item, reference, lexicon, switches)) for item in annotated]
    eligible = [item for item, ok, _reasons in checked if ok]
    blocking = [reason for _item, ok, reasons in checked if not ok for reason in reasons]
    if not eligible:
        raw = {"action": "HOLD", "candidate_id": None, "frame": None, "reasons": blocking or ["NO_SAFE_CANDIDATE"]}
    elif eligible[0]["candidate_id"] == annotated[0]["candidate_id"]:
        raw = {"action": "CONTINUE", "candidate_id": eligible[0]["candidate_id"], "frame": eligible[0]["reading"]["frame"], "reasons": []}
    elif switches.recovery:
        raw = {"action": "RETRY", "candidate_id": eligible[0]["candidate_id"], "frame": eligible[0]["reading"]["frame"], "reasons": []}
    else:
        raw = {"action": "HOLD", "candidate_id": None, "frame": None, "reasons": ["RECOVERY_DISABLED"]}
    normalized = apply_gate(dict(raw), annotated, lexicon, _gates(switches))
    if normalized["committed"] and switches.reference:
        checked_again = compare_reference(normalized["committed_frame"], reference)
        if not checked_again["match"]:
            normalized = {
                "action": "HOLD",
                "committed": False,
                "committed_candidate_id": None,
                "committed_frame": None,
                "blocking_reasons": checked_again["reasons"],
                "gate_passed": True,
            }
    return _pack(candidate_only, raw, normalized, reference, switches)


def _pack(candidate_only, raw, normalized, reference, switches: ReferenceSwitches) -> dict[str, object]:
    return {
        "strategy": STRATEGY_REFERENCE,
        "evidence_condition": "critical_slot_reference" if reference and reference.get("reference_scope") != "full_referent" else "full_referent" if reference else "reference_absent",
        "reference_id": None if reference is None else reference.get("reference_id"),
        "candidate_only_action": candidate_only["normalized"]["action"],
        "candidate_only_committed": candidate_only["normalized"]["committed"],
        "raw": {"action": raw["action"], "candidate_id": raw.get("candidate_id"), "frame": raw.get("frame"), "reasons": list(raw.get("reasons") or [])},
        "normalized": normalized,
        "switches": {
            "modality": switches.modality,
            "polarity": switches.polarity,
            "conditionality": switches.conditionality,
            "provenance": switches.provenance,
            "gate": switches.gate,
            "recovery": switches.recovery,
            "reference": switches.reference,
        },
    }
