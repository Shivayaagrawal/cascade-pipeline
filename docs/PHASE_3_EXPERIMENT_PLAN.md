# Phase 3 experiment plan

All outputs are under `experiments/phase3/`. Frozen B0, B1, B2, v2, v3, and v3b directories were not rewritten.

The compared conditions use the same 40 test cases and the same candidate bundles. Development cases were not mixed into the test table. Validation was used only to freeze `phase3-policy-v1`.

| ID | What runs |
| --- | --- |
| E0 | Frozen `run_b0` on the first candidate. It always answers, so a returned frame is a commit. |
| E1 | Frozen `run_b1` on the bundle. It always answers. |
| E2 | Frozen `run_b2`. `CONTINUE` and `RETRY` commit. `CLARIFY` and `HOLD` do not. |
| E3 | Frozen `forced_selection`. The frame is an answer. It is not coverage. |
| E4 | Frozen `recovery_action` on the bundle texts. |
| E5 | v4 diagnosis, action from frozen `recovery_action`. |
| E6 | v4 gates with retry disabled. |
| E7 | `b2_semantic_v4` with the frozen weights and threshold. |

Ablations turn one switch off and leave the frozen weights in place. They are not retuned.

| Ablation | Switch off |
| --- | --- |
| A1 | Polarity gate |
| A2 | Ambiguity gate |
| A3 | Critical-slot gate |
| A4 | Contradiction gate |
| A5 | Completeness gate |
| A6 | Modality gate |
| A7 | Risk score |
| A8 | The v4 recovery policy. Same action source as E5. |

Coverage and selective risk are reported together. Unsafe-commit rate is a different numerator: a commit whose challenge metadata says the commit was not safe. A commit can match the parent slots and still be unsafe. Abstention is not an unsafe commit. A zero commit count leaves selective risk and the unsafe-commit rate null.

E0 through E4 do not emit polarity. Their polarity accuracy is null for that reason. E5 through E7 and the ablations do.
