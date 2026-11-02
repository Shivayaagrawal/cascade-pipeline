"""Frozen baseline adapters for the Phase 5 bundles.

Adapter-matched ids are labeled ADAPTER_TEXT_MATCH or ADAPTER_FRAME_MATCH.
They are not recorded as ids emitted by those strategies.
"""

from __future__ import annotations

from cascadeguard.evaluation.semantic_evidence import assess, frame_is_complete
from cascadeguard_facade.adapters import b0_prefix, b1_forced_lexical, b1_prefix, b2_lexical_v3, b2_prefix_controller
from cascadeguard_facade.commit_policy_v4 import PolicySwitches
from cascadeguard_facade.contracts import CandidateBundle, CandidateRecord
from cascadeguard_facade.semantic_controller_v4 import run_semantic_v4

PHASE3_WEIGHTS = {"intent": 0.0, "slot": 0.0, "polarity": 0.0, "ambiguity": 0.0, "contradiction": 1.0}
PHASE3_THRESHOLD = 0.25


def to_bundle(case: dict[str, object]) -> CandidateBundle:
    source = "SINGLE_TRANSCRIPT" if len(case["candidates"]) == 1 else "SYNTHETIC_PROXY"
    candidates = tuple(
        CandidateRecord(
            str(item["candidate_id"]),
            str(item["text"]),
            str(item["provenance"]),
            int(item["rank"]),
            source,
        )
        for item in case["candidates"]
    )
    return CandidateBundle(str(case["case_id"]), candidates, "synthetic_edit", source)


def _text_id(case: dict[str, object], text: str | None) -> str | None:
    if not text:
        return None
    hits = [str(item["candidate_id"]) for item in case["candidates"] if item["text"] == text]
    return hits[0] if len(hits) == 1 else None


def _frame_id(case: dict[str, object], lexicon: dict[str, tuple[str, ...]], intent: str | None, slots: dict[str, str]) -> str | None:
    if intent is None:
        return None
    hits = []
    for item in case["candidates"]:
        frame = frame_is_complete(assess(str(item["text"]), lexicon))
        if frame is not None and frame[0] == intent and dict(frame[1]) == slots:
            hits.append(str(item["candidate_id"]))
    return hits[0] if hits else None


def _decision(case, action, committed, frame, candidate_id, status, reason) -> dict[str, object]:
    return {
        "case_id": case["case_id"],
        "actual_commit": committed,
        "committed_frame": frame if committed else None,
        "committed_candidate_id": candidate_id if committed else None,
        "provenance_status": status,
        "normalized_action": action,
        "modality_label": None,
        "polarity": None,
        "conditionality": None,
        "reason": reason,
    }


def run_baseline(name: str, case: dict[str, object], lexicon: dict[str, tuple[str, ...]]) -> dict[str, object]:
    bundle = to_bundle(case)
    if name == "b0_prefix":
        raw, normalized = b0_prefix.execute(bundle)
        status = "ADAPTER_TEXT_MATCH"
        candidate_id = bundle.ordered()[0].candidate_id if bundle.candidate_count else None
    elif name == "b1_prefix":
        raw, normalized = b1_prefix.execute(bundle)
        status = "ADAPTER_TEXT_MATCH"
        candidate_id = _text_id(case, raw.text)
    elif name == "b2_prefix_controller":
        raw, normalized = b2_prefix_controller.execute(bundle)
        status = "ADAPTER_TEXT_MATCH"
        candidate_id = _text_id(case, raw.text)
    elif name == "b1_forced_lexical":
        raw, normalized = b1_forced_lexical.execute(bundle, lexicon)
        frame = None if normalized.answered_frame is None else {
            "intent": normalized.answered_frame.intent,
            "slots": normalized.answered_frame.as_dict(),
        }
        return _decision(case, normalized.action, False, frame, None, "NOT_A_COMMIT", normalized.reason)
    elif name == "b2_lexical_v3":
        raw, normalized = b2_lexical_v3.execute(bundle, lexicon)
        status = "ADAPTER_FRAME_MATCH"
        committed = normalized.committed_frame
        slots = {} if committed is None else committed.as_dict()
        intent = None if committed is None else committed.intent
        candidate_id = _frame_id(case, lexicon, intent, slots)
    else:
        result = run_semantic_v4(
            bundle,
            lexicon,
            weights=PHASE3_WEIGHTS,
            threshold=PHASE3_THRESHOLD,
            switches=PolicySwitches(),
        )
        status = "ADAPTER_FRAME_MATCH"
        slots = dict(result.committed_slots)
        intent = result.committed_intent
        candidate_id = _frame_id(case, lexicon, intent, slots)
        committed = intent is not None
        frame = None if not committed else {"intent": intent, "slots": slots}
        return _decision(case, result.action, committed, frame, candidate_id, status, result.reason)
    committed_frame = normalized.committed_frame
    committed = committed_frame is not None and committed_frame.intent is not None
    frame = None if not committed else {"intent": committed_frame.intent, "slots": committed_frame.as_dict()}
    return _decision(case, normalized.action, committed, frame, candidate_id, status, normalized.reason)


def v5_decision(case: dict[str, object], result: dict[str, object]) -> dict[str, object]:
    normalized = result["normalized"]
    modality = result.get("modality") or {}
    return _decision(
        case,
        normalized["action"],
        bool(normalized["committed"]),
        normalized["committed_frame"],
        normalized["committed_candidate_id"],
        str(result["provenance"]["provenance_status"]),
        ",".join(normalized["blocking_reasons"]),
    ) | {
        "modality_label": modality.get("modality"),
        "polarity": modality.get("polarity"),
        "conditionality": modality.get("conditionality"),
        "raw_action": result["raw"]["action"],
        "risk": result["risk"],
        "execution_time_ms": result["execution_time_ms"],
        "timings_ms": result.get("timings_ms"),
    }
