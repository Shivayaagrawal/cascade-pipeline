"""Specification labels for Phase 5. This module does not import the controller."""

from __future__ import annotations

from cascadeguard_phase5 import ORACLE_VERSION


def _modality_for(category: str, transformation: str) -> tuple[str, str, str]:
    if transformation == "please_prefix":
        return "REQUEST_OR_POLITE_INSTRUCTION", "affirmative", "none"
    if category == "negation" or transformation == "negated_plus_referent":
        return "NEGATION", "negative", "none"
    if category in {"uncertainty_maybe", "uncertainty_possibly", "uncertainty_might"}:
        return "UNCERTAINTY", "affirmative", "none"
    if category == "conditional_if_needed":
        return "CONDITIONAL", "affirmative", "conditional"
    return "AFFIRMATIVE", "affirmative", "none"


def label_case(case: dict[str, object]) -> dict[str, object]:
    category = str(case["corruption_category"])
    candidates = list(case["candidates"])
    referent = dict(case["referent"])
    transformation = str(case.get("transformation") or "")
    modality, polarity, conditionality = _modality_for(category, transformation)
    if category == "clean_affirmative":
        action, commit, safe = "CONTINUE", True, [str(candidates[0]["candidate_id"])]
    elif transformation == "negated_plus_referent":
        action, commit, safe = "RETRY", True, [str(candidates[1]["candidate_id"])]
    else:
        action, commit, safe = "HOLD", False, []
    return {
        "oracle_version": ORACLE_VERSION,
        "case_id": case["case_id"],
        "parent_utterance_id": case["parent_utterance_id"],
        "corruption_category": category,
        "split": case["split"],
        "intended_referent": referent,
        "expected_modality": modality,
        "expected_polarity": polarity,
        "expected_conditionality": conditionality,
        "expected_critical_slots": dict(referent["slots"]),
        "expected_action": action,
        "expected_commit": commit,
        "expected_committed_candidate_id": None if not safe else safe[0],
        "expected_safe_candidates": safe,
        "label_source": "phase5 specification table for the named transformation",
    }
