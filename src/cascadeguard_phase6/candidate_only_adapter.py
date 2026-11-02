"""Condition A. The frozen controller sees a stripped bundle and nothing else."""

from __future__ import annotations

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard_phase5.semantic_controller_v5 import run_semantic_v5
from cascadeguard_phase6.evidence_contract import stripped_bundle


def run_candidate_only(case: dict[str, object], lexicon: dict[str, tuple[str, ...]] | None = None) -> dict[str, object]:
    bundle = stripped_bundle(case)
    if set(bundle) - {"bundle_id", "candidates"}:
        raise RuntimeError("candidate-only bundle carries a non-candidate field")
    result = run_semantic_v5(bundle, lexicon if lexicon is not None else lexicon_from_utterances())
    result["evidence_condition"] = "candidate_only"
    return result
