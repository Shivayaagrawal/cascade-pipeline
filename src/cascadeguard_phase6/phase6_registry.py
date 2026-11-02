"""Phase 6 identities. b2_semantic_v5 stays on the Phase 5 registry."""

from __future__ import annotations

from cascadeguard_phase6 import STRATEGY_CANDIDATE, STRATEGY_REFERENCE
from cascadeguard_phase6.candidate_only_adapter import run_candidate_only
from cascadeguard_phase6.reference_aware_controller import run_reference_aware


def route_phase6(name: str):
    if name == STRATEGY_CANDIDATE:
        return run_candidate_only
    if name == STRATEGY_REFERENCE:
        return run_reference_aware
    raise KeyError(name)
