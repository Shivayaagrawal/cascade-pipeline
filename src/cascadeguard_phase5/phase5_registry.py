"""Registration for b2_semantic_v5. b2_semantic_v4 stays on its own registry."""

from __future__ import annotations

from cascadeguard_phase5 import STRATEGY
from cascadeguard_phase5.semantic_controller_v5 import run_semantic_v5


class UnknownPhase5StrategyError(KeyError):
    """The Phase 5 registry only contains b2_semantic_v5."""


def route_phase5(name: str):
    if name != STRATEGY:
        raise UnknownPhase5StrategyError(name)
    return run_semantic_v5
