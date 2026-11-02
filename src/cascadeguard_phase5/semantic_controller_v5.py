"""b2_semantic_v5. Raw proposals and normalized decisions are separate objects."""

from __future__ import annotations

import time

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard_phase5 import STRATEGY
from cascadeguard_phase5.candidate_provenance_v5 import ProvenanceRecord, lookup, validate_bundle
from cascadeguard_phase5.commit_policy_v5 import GateSwitches, apply_gate
from cascadeguard_phase5.failure_diagnosis_v5 import diagnose
from cascadeguard_phase5.modality_analyzer_v5 import analyze_modality
from cascadeguard_phase5.risk_assessment_v5 import risk_factors
from cascadeguard_phase5.semantic_evidence_v5 import read_candidate


def _hold(reason: str) -> dict[str, object]:
    return {"action": "HOLD", "candidate_id": None, "frame": None, "reasons": [reason]}


def _proposal_from(candidate: dict[str, object], action: str) -> dict[str, object]:
    frame = candidate["reading"]["frame"]
    return {"action": action, "candidate_id": candidate["candidate_id"], "frame": frame, "reasons": []}


def run_semantic_v5(
    bundle: dict[str, object],
    lexicon: dict[str, tuple[str, ...]] | None = None,
    switches: GateSwitches | None = None,
) -> dict[str, object]:
    switches = switches or GateSwitches()
    lexicon = lexicon if lexicon is not None else lexicon_from_utterances()
    started = time.perf_counter()
    candidates = list(bundle.get("candidates") or [])
    bundle_id = str(bundle.get("bundle_id") or bundle.get("case_id") or "")
    if not candidates:
        raw = _hold("EMPTY_BUNDLE")
        normalized = apply_gate(raw, [], lexicon, switches)
        elapsed = (time.perf_counter() - started) * 1000
        return _pack(bundle_id, raw, normalized, [], {}, {"flags": {}, "score": None, "overrides_gate": False}, elapsed, False)
    valid, validity = validate_bundle(candidates)
    if not valid:
        raw = _hold(validity)
        normalized = apply_gate(raw, candidates, lexicon, switches)
        elapsed = (time.perf_counter() - started) * 1000
        return _pack(bundle_id, raw, normalized, candidates, {}, {"flags": {}, "score": None, "overrides_gate": False}, elapsed, False)

    analysis_started = time.perf_counter()
    annotated: list[dict[str, object]] = []
    for item in candidates:
        reading = read_candidate(str(item["text"]), lexicon)
        modality = analyze_modality(str(item["text"])).as_dict()
        annotated.append({**item, "reading": reading, "modality": modality})
    analysis_ms = (time.perf_counter() - analysis_started) * 1000
    readings = [item["reading"] for item in annotated]
    modalities = [item["modality"] for item in annotated]
    diagnosis = diagnose(readings)
    risk = risk_factors(readings, modalities, diagnosis) if switches.risk else {
        "flags": {},
        "score": None,
        "overrides_gate": False,
    }
    if any(len(item["reading"]["intents"]) > 1 for item in annotated):
        raw = {"action": "CLARIFY", "candidate_id": None, "frame": None, "reasons": ["MULTIPLE_INTENTS"]}
    elif switches.critical_slots and "CONFLICTING_FRAMES" in diagnosis["labels"]:
        raw = _hold("CONFLICTING_FRAMES")
    else:
        complete = [item for item in annotated if item["reading"]["frame"] is not None]
        if not complete:
            raw = _hold("NO_SAFE_CANDIDATE")
        elif complete[0]["candidate_id"] == annotated[0]["candidate_id"]:
            raw = _proposal_from(complete[0], "CONTINUE")
        elif switches.recovery:
            raw = _proposal_from(complete[0], "RETRY")
        else:
            raw = _hold("RECOVERY_DISABLED")
    verify_started = time.perf_counter()
    normalized = apply_gate(dict(raw), annotated, lexicon, switches)
    if (
        not normalized["committed"]
        and switches.recovery
        and switches.gate
        and "CONFLICTING_FRAMES" not in diagnosis["labels"]
    ):
        for item in annotated:
            if item["candidate_id"] == raw.get("candidate_id"):
                continue
            if item["reading"]["frame"] is None:
                continue
            retry = _proposal_from(item, "RETRY")
            attempted = apply_gate(retry, annotated, lexicon, switches)
            if attempted["committed"]:
                normalized = attempted
                break
    verify_ms = (time.perf_counter() - verify_started) * 1000
    elapsed = (time.perf_counter() - started) * 1000
    packed = _pack(bundle_id, raw, normalized, annotated, diagnosis, risk, elapsed, True)
    packed["timings_ms"] = {
        "controller": elapsed,
        "semantic_analysis": analysis_ms,
        "critical_slot_and_provenance": verify_ms,
    }
    return packed


def _pack(bundle_id, raw, normalized, annotated, diagnosis, risk, elapsed, invoked) -> dict[str, object]:
    selected_id = normalized["committed_candidate_id"] if normalized["committed"] else raw.get("candidate_id")
    selected = lookup(annotated, None if selected_id is None else str(selected_id))
    frame = normalized["committed_frame"] if normalized["committed"] else None
    status = "CONTROLLER_EMITTED" if normalized["committed"] else "NO_COMMIT"
    provenance = ProvenanceRecord(
        bundle_id,
        None if selected is None else str(selected["candidate_id"]),
        None if selected is None else int(selected["candidate_index"]),
        None if selected is None else str(selected["text"]),
        None if selected is None else str(selected.get("provenance")),
        ",".join(normalized["blocking_reasons"]) or str(raw["action"]),
        None if selected_id is None else str(selected_id),
        None if not normalized["committed"] else str(normalized["committed_candidate_id"]),
        None if not isinstance(frame, dict) else dict(frame["slots"]),
        status,
    )
    modality = {} if selected is None else dict(selected.get("modality") or {})
    if not modality and annotated and isinstance(annotated[0], dict):
        modality = dict(annotated[0].get("modality") or {})
    return {
        "strategy": STRATEGY,
        "processors_invoked": invoked,
        "raw": {
            "action": raw["action"],
            "candidate_id": raw.get("candidate_id"),
            "frame": raw.get("frame"),
            "reasons": list(raw.get("reasons") or []),
        },
        "normalized": normalized,
        "provenance": provenance.as_dict(),
        "modality": modality,
        "diagnosis": diagnosis,
        "risk": risk,
        "candidates": [
            {
                "candidate_id": item.get("candidate_id"),
                "text": item.get("text"),
                "modality": item.get("modality"),
                "frame": None if not isinstance(item.get("reading"), dict) else item["reading"].get("frame"),
            }
            for item in annotated
            if isinstance(item, dict) and "reading" in item
        ],
        "execution_time_ms": elapsed,
    }
