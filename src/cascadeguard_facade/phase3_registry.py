"""Phase 3 registration. b2_semantic_v4 is not added to the Phase 2 strategy set."""

from __future__ import annotations

from cascadeguard_facade.commit_policy_v4 import PolicySwitches
from cascadeguard_facade.contracts import STRATEGIES, CandidateBundle, UnknownStrategyError
from cascadeguard_facade.semantic_controller_v4 import STRATEGY, ControllerResult, run_semantic_v4

PHASE3_STRATEGIES = frozenset({STRATEGY})


def route_phase3(
    strategy: str,
    bundle: CandidateBundle,
    lexicon: dict[str, tuple[str, ...]],
    *,
    weights: dict[str, float],
    threshold: float,
    switches: PolicySwitches | None = None,
    frozen_recovery: bool = False,
) -> ControllerResult:
    if strategy in STRATEGIES:
        raise UnknownStrategyError(
            f"{strategy} is a Phase 2 identity. Phase 3 does not reroute it."
        )
    if strategy not in PHASE3_STRATEGIES:
        raise UnknownStrategyError(
            f"Unknown Phase 3 strategy {strategy!r}. Expected {STRATEGY}."
        )
    return run_semantic_v4(
        bundle,
        lexicon,
        weights=weights,
        threshold=threshold,
        switches=switches,
        frozen_recovery=frozen_recovery,
    )
