"""Protected Phase 1-3 artifacts and the controller import boundary."""

from __future__ import annotations

import hashlib
from pathlib import Path

PROTECTED = {
    "experiments/B0/summary.json": "3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee",
    "experiments/B1/summary.json": "597a2800c946018467865dfcf3d8e547bc51c10487596cc134ca2181fee695b2",
    "experiments/B2/summary.json": "34a40fdd233f5d4faa00af73c26f1afcc32c4d83922db8df57b7a7184dce0e5d",
    "artifacts/reports/simulation_report.json": "7adf69ee6ac344e7ef205099af3686ddf7cceaffa111a8789f03b83ed8319856",
    "experiments/sim-eval-v2/report.json": "74499b716103e26ef829cb56816bf738d67d3d3e5961848c4cfe37f2e8f4f77d",
    "experiments/sim-eval-v3/report.json": "7d1ca46400795908f6ffcd17091d4348e633493923fc030e5160e9f2ff8a8cd6",
    "experiments/sim-eval-v3b/report.json": "4c47b2b04e42b06972f7bd9e10da51d219d18a46e273d71fc50e78f2070631cf",
    "experiments/sim-eval-v3b/decision_log.jsonl": "9c486601dcac141ccf7453f84b144fbd5d5c491da1b1a32542e7a14a796a4e75",
    "configs/evaluation_v3.yaml": "ac4bb7ea743195e6ea860a4f2c34dc546437321f28c811055782fe4b1c5ed842",
    "data/librispeech/annotations/phase_1c_pilot_30.csv": "56a4dc49b3a2f5add5c361c2b23edde923c8265a998de76c7e5b87462e5d6a5c",
    "data/synthetic/manifest.csv": "abc3cceec6a90e0953ac6614e1a6fee63b91c1401324798e0232ef1aa4f723e9",
    "data/synthetic/transcripts/variants.csv": "fd4d3d9a66e68dd8e687a8ab4d6c5484d32774c2d9c08f3c1ecb7a7e7fa89f68",
    "docs/PHASE_3B_RESEARCH_AUDIT.md": "f025cb4bf387faea68a1e7cf574f15c47a3afc83c0a36c7264cb7399bec8560b",
}


def test_protected_hashes_and_controller_boundary():
    for relative, digest in PROTECTED.items():
        assert hashlib.sha256(Path(relative).read_bytes()).hexdigest() == digest
    controller = Path("src/cascadeguard_facade/semantic_controller_v4.py").read_text(encoding="utf-8")
    policy = Path("src/cascadeguard_facade/commit_policy_v4.py").read_text(encoding="utf-8")
    risk = Path("src/cascadeguard_facade/risk_assessment_v4.py").read_text(encoding="utf-8")
    assert "cascadeguard_phase4" not in controller
    assert "cascadeguard_phase4" not in policy
    assert "cascadeguard_phase4" not in risk
