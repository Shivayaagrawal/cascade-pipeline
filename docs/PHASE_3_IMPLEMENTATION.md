# Phase 3 implementation

`b2_semantic_v4` is registered in `phase3_registry.py`. It is not a member of `STRATEGIES`. `route("b2_semantic_v4")` still raises `UnknownStrategyError`.

| Module | Role |
| --- | --- |
| `semantic_evidence_v4.py` | `assess_v4` |
| `failure_diagnosis_v4.py` | `diagnose_failure` |
| `risk_assessment_v4.py` | Indicator score, quarter-weight grid, thresholds |
| `commit_policy_v4.py` | Gates and actions |
| `semantic_controller_v4.py` | Bundle in, raw diagnosis and normalized action out |
| `phase3_dataset.py` | Challenge builder |
| `phase3_metrics.py` | Rates, with forced selection kept out of coverage |
| `scripts/run_phase3.py` | Validation selection, then test evaluation |

An empty bundle returns before `assess_v4` is called. The raw dictionary is built from the assessments and is not rewritten by normalization. The normalized action, reason, and committed slots are separate fields.

The five Phase 2 adapters are not edited. `assess()`, `run_b0`, `run_b1`, `run_b2`, `forced_selection`, and `recovery_action` are not edited.

The test evaluation command was run twice. The first pass counted forced selection as coverage. The second pass reports that answer as `forced_exact_frame_accuracy` and sets E3 coverage to 0. The frozen weights were not edited between the passes.
