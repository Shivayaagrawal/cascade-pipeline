# Phase 4 implementation

The package is `src/cascadeguard_phase4/`. The dataset is `data/phase4/`. The runs are `experiments/phase4/`. No file under `experiments/B0`, `B1`, `B2`, `sim-eval-v2`, `sim-eval-v3`, `sim-eval-v3b`, `data/phase3`, or `data/manual_audit` was edited.

`scripts/build_phase4_dataset.py` wrote 600 bundles and then called the oracle. `scripts/validate_phase4_oracle.py` recomputes those labels. `scripts/run_phase4_evaluation.py` wrote the baseline, the grid, the policy file, the test logs, and the ablations. The test loader is called after `experiments/phase4/validation/frozen_policy.json` is written. `test_cases_read` in that file remains false.

The harness traces candidate ids because the frozen strategies do not emit them. Prefix strategies are traced by the text they returned. Lexical strategies are traced by the earliest candidate whose frozen `assess()` frame equals the committed frame. v4 is traced by the earliest candidate that its own assessment accepts under the switches actually used. A trace that cannot find an id fails the action-path check.

No `b2_semantic_v5` was added. The repeated failures are listed in the limitations as a proposal only.

Policy SHA-256: `82820621bcbff3ac9bd9d3fa88795240d5023a65cd5c61300dfde3fd79162f6c`.
