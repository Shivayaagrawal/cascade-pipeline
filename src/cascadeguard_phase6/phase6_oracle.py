"""Specification labels. This module does not import either controller."""

from __future__ import annotations

from cascadeguard_phase6 import ORACLE_VERSION


def _modality(category: str, transformation: str) -> tuple[str, str, str]:
    if transformation == "please_prefix":
        return "REQUEST_OR_POLITE_INSTRUCTION", "affirmative", "none"
    if category == "negation" or transformation == "negated_plus_referent":
        return "NEGATION", "negative", "none"
    if category == "uncertainty" or transformation.endswith("_prefix") and transformation.split("_")[0] in {"maybe", "possibly", "might"}:
        return "UNCERTAINTY", "affirmative", "none"
    if category == "conditionality":
        return "CONDITIONAL", "affirmative", "conditional"
    return "AFFIRMATIVE", "affirmative", "none"


def _decision(action: str, commit: bool, candidate_id: str | None) -> dict[str, object]:
    return {
        "expected_action": action,
        "expected_commit": commit,
        "expected_candidate_path": None if candidate_id is None else candidate_id,
        "expected_safe_candidates": [] if candidate_id is None else [candidate_id],
    }


def label_case(case: dict[str, object]) -> dict[str, object]:
    category = str(case["corruption_category"])
    transformation = str(case["transformation"])
    candidates = list(case["candidates"])
    first = str(candidates[0]["candidate_id"])
    second = str(candidates[1]["candidate_id"]) if len(candidates) > 1 else None
    modality, polarity, conditionality = _modality(category, transformation)
    if category in {"clean_affirmative", "clean_polite_instruction"}:
        candidate = critical = full = _decision("CONTINUE", True, first)
    elif transformation == "maybe_on_parent_transcript_only":
        candidate = critical = _decision("CONTINUE", True, first)
        full = _decision("HOLD", False, None)
    elif transformation == "negated_plus_referent":
        candidate = critical = full = _decision("RETRY", True, second)
    elif transformation == "referent_plus_other_value":
        candidate = _decision("HOLD", False, None)
        critical = full = _decision("CONTINUE", True, first)
    elif category == "ambiguous_candidate_bundle":
        candidate = critical = full = _decision("CLARIFY", False, None)
    else:
        candidate = critical = full = _decision("HOLD", False, None)
    referent = dict(case["referent"])
    return {
        "oracle_version": ORACLE_VERSION,
        "case_id": case["case_id"],
        "parent_utterance_id": case["parent_utterance_id"],
        "corruption_category": category,
        "transformation": transformation,
        "split": case["split"],
        "intended_referent": referent,
        "expected_intent": referent["intent"],
        "expected_modality": modality,
        "expected_polarity": polarity,
        "expected_conditionality": conditionality,
        "expected_critical_slots": dict(referent["slots"]),
        "candidate_only": candidate,
        "critical_slot_reference": critical,
        "full_referent": full,
        "label_source": "phase6 specification table for the named transformation",
    }
