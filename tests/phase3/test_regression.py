"""Phase 2 identities and frozen outputs stay put."""

import hashlib
from pathlib import Path

from cascadeguard.evaluation.semantic_evidence import assess
from cascadeguard.evaluation.selective import forced_selection, recovery_action
from cascadeguard.pipeline import run_b0, run_b1, run_b2
from cascadeguard_facade.contracts import STRATEGIES

ROOT = Path(__file__).resolve().parents[2]
HASHES = {
    "experiments/B0/summary.json": "3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee",
    "experiments/B1/summary.json": "597a2800c946018467865dfcf3d8e547bc51c10487596cc134ca2181fee695b2",
    "experiments/B2/summary.json": "34a40fdd233f5d4faa00af73c26f1afcc32c4d83922db8df57b7a7184dce0e5d",
    "data/synthetic/manifest.csv": "abc3cceec6a90e0953ac6614e1a6fee63b91c1401324798e0232ef1aa4f723e9",
    "data/synthetic/transcripts/variants.csv": "fd4d3d9a66e68dd8e687a8ab4d6c5484d32774c2d9c08f3c1ecb7a7e7fa89f68",
    "data/manual_audit/annotations.csv": "f5ea4fb5c98215dcb80650404091ea6ca31de9da20228f1ce3a0dffba251dd76",
    "data/librispeech/annotations/phase_1c_pilot_30.csv": "56a4dc49b3a2f5add5c361c2b23edde923c8265a998de76c7e5b87462e5d6a5c",
}


def test_five_identities_and_frozen_functions_remain() -> None:
    assert STRATEGIES == {
        "b0_prefix",
        "b1_prefix",
        "b2_prefix_controller",
        "b1_forced_lexical",
        "b2_lexical_v3",
    }
    assert callable(run_b0)
    assert callable(run_b1)
    assert callable(run_b2)
    assert callable(forced_selection)
    assert callable(recovery_action)
    assert callable(assess)


def test_protected_hashes_match_the_phase3_baseline() -> None:
    for relative, expected in HASHES.items():
        digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert digest == expected
