# Phase 4 implementation blueprint

Phase 4 is a new package, `cascadeguard_phase4`. It calls the frozen adapters and `run_semantic_v4`. It does not edit them.

| Piece | Role |
| --- | --- |
| `dataset_builder.py` | Specification A. Writes texts, ids, and provenance. |
| `independent_oracle.py` | Specification B. Labels a bundle from text and the scenario referent. |
| `candidate_provenance.py` | Reconstructs the candidate id a frozen strategy used. |
| `independent_evaluator.py` | Assigns one outcome from the frozen label and the recorded path. |
| `phase4_metrics.py` | Rates, Wilson intervals, null when the denominator is 0. |
| `statistical_analysis.py` | Parent-cluster bootstrap of paired differences. |
| `execute.py` | Runs E0–E7 and the validation grid. |

Controller logs are written from bundles only. Oracle fields are joined after the strategy returns.

The blueprint does not add a new controller. Ablation A4 has nothing to turn off, because v4 does not check candidate provenance. That ablation is recorded as an absent component.
