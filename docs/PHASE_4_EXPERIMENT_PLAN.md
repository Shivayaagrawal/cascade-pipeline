# Phase 4 experiment plan

## Order

1. Score E0–E7 on validation with Phase 3 weights and threshold 0.25.
2. Score the 350-cell weight and threshold grid on validation for E7 only.
3. Write `experiments/phase4/validation/frozen_policy.json`.
4. Only then read the test split.
5. Score E0–E7 once on the test split with the Phase 3 configuration.
6. If the grid winner differs, score that E7 cell once on the test split.
7. Score A1–A8 on the test split with the Phase 3 configuration. Ablations are not used to change the frozen policy.

Development cases are not scored.

## Selection rule

Fewest unsafe commits, then fewest invalid paths, then highest safe-commitment accuracy, then lowest selective risk, then highest coverage, then lowest unnecessary abstention. If the Phase 3 cell ties on those six fields, keep it. Otherwise take lexicographic weights and the lowest threshold.

The rule is allowed to select a cell that commits very little. The validation curve is saved so that tradeoff stays visible. Hypotheses still refer to the unmodified Phase 3 configuration.

## Strategies

E0 `b0_prefix`, E1 `b1_prefix`, E2 `b2_prefix_controller`, E3 `b1_forced_lexical`, E4 `b2_lexical_v3`, E5 v4 diagnosis with frozen lexical action, E6 v4 gates with retry disabled, E7 `b2_semantic_v4`.

Lexical retry is not given a second bundle. The frozen function only retries when the caller passes one, and Phase 4 does not invent one.

## Ablations

A1 polarity, A2 modality, A3 critical slots, A5 completeness, A6 contradiction, A7 ambiguity. A8 replaces the v4 policy with frozen lexical recovery. A4 is the missing provenance check and is expected to match E7.
