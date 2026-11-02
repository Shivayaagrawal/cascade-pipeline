# Phase 4 results

Hypothesis configuration: Phase 3 weights, threshold 0.25, test split, 120 cases, 20 parent clusters. Intervals are Wilson intervals for single rates and parent-cluster bootstrap intervals for differences. Full JSON is under `experiments/phase4/final_test/phase3_config/`.

## Primary comparison

| Strategy | Coverage | Selective risk | Unsafe commits | Path safety | Safe-commit accuracy |
| --- | --- | --- | --- | --- | --- |
| E0 prefix | 99/120 | 61/99 | 79/99 | 20/99 | 18/99 |
| E1 prefix | 99/120 | 61/99 | 79/99 | 20/99 | 18/99 |
| E2 prefix recovery | 96/120 | 58/96 | 76/96 | 20/96 | 18/96 |
| E3 forced lexical | 0/120 | null | null | null | null |
| E4 lexical v3 | 69/120 | 10/69 | 49/69 | 20/69 | 20/69 |
| E5 diagnosis, frozen action | 69/120 | 10/69 | 49/69 | 20/69 | 20/69 |
| E6 gates, no retry | 47/120 | 10/47 | 27/47 | 20/47 | 20/47 |
| E7 semantic v4 | 56/120 | 10/56 | 27/56 | 29/56 | 29/56 |

E3's forced exact-frame accuracy is 79/120. That is not coverage.

E7 exact frame is 46/120 (Wilson 0.301 to 0.473). Action accuracy is 93/120 (0.692 to 0.841). Unsafe-commit Wilson interval: 0.357 to 0.610. Path safety: 0.390 to 0.643. Coverage: 0.380 to 0.556.

Per-case unsafe commits, E7 minus E0: −0.433, bootstrap interval −0.487 to −0.374. E7 minus E4: −0.183, interval −0.214 to −0.143. Coverage, E7 minus E0: −0.358, interval −0.415 to −0.296. E7 minus E4: −0.108, interval −0.134 to −0.081.

## Where the 56 E7 commits come from

| Category | E7 outcomes on 10 test cases, or 20 clean |
| --- | --- |
| Clean controls | 20 `SAFE_COMMIT` |
| Provenance pairs | 9 `SAFE_COMMIT` of the referent candidate, 1 empty-bundle `SAFE_ABSTENTION` |
| Negation, context, contradiction, incompleteness, ambiguity, temporal conflict | `SAFE_ABSTENTION` |
| Slot mutation | 10 `UNSAFE_COMMIT` of the replacement value |
| Function-word damage | 10 `CORRECT_FRAME_UNSAFE_PATH` |
| Uncertainty | 3 `SAFE_ABSTENTION` on `Maybe`; 7 `CORRECT_FRAME_UNSAFE_PATH` on `Possibly`, `might`, and `If needed` |

The 10 selective errors are the 10 mutation commits. The other 17 unsafe commits match the referent frame and come from a candidate the oracle does not permit. Path safety is what separates those 17 from a frame-only score.

E4 commits the negated string's frame on all 10 negation cases and on all 9 provenance pairs. E0 commits those strings as well, and the prefix slot span includes the word `not` or the hedge, so the frame is usually wrong rather than parent-matching. On temporal conflicts E0 commits the first candidate, which is the referent text, while the oracle permits neither side. That is a correct frame on an unsafe path.

## Sensitivity cell

Threshold 0 on the test split: coverage 9/120, unsafe commits 0/9, path safety 9/9, unnecessary abstention 20/29. The 9 commits are the provenance retries. Clean controls are held. This cell wins the predeclared rule and does not answer H7.

## Ablations

Counts are commits and unsafe commits on the same 120 cases.

| Ablation | What changed |
| --- | --- |
| A1 polarity off | 10 negation holds and 9 provenance safe commits become correct-frame unsafe paths. Unsafe commits 46/66. |
| A2 modality off | The 3 `Maybe` holds become correct-frame unsafe paths. The other 7 uncertainty cases were already committed. |
| A3 critical slots off | 10 temporal conflicts become correct-frame unsafe paths. Mutation commits were already unsafe. |
| A4 provenance check | 0 cases changed. v4 has no provenance check to disable. |
| A5 completeness off | 0 cases changed. Incomplete bundles have no second complete frame to commit. |
| A6 contradiction off | 0 cases changed. The slot gate already holds the conflicting bundles. |
| A7 ambiguity off | 10 actions change from `CLARIFY` to `HOLD`. Commit counts do not change. |
| A8 v4 policy off | Matches the lexical operating point: 49 unsafe commits out of 69. |

## Hypotheses

H1 is supported for E0, E1, and E2 on the per-case unsafe-commit difference. H2 is supported as more safe commits per case (difference +0.075, interval 0.053 to 0.088). The conditional path-safety rate is also higher, 29/56 against 20/99 and 20/69, and its interval is wide. H3 is supported on this slice: E7 makes no negation commit, while E0 and E4 commit all 10. The per-commit rate for E7 is null, not zero. H4 is contradicted: E7 commits all 10 mutated values. Critical-slot safety on those commits is 0/10. H5 is supported on the 10 provenance cases: 9 safe retries and 1 empty hold, with no invalid path. H6 is supported as a coverage cost. H7 is supported for this configuration: 20/20 clean controls are safe commits, Wilson interval 0.839 to 1. The threshold-0 cell contradicts H7.

No hypothesis is a general safety guarantee. The test slice has 20 parent clusters.
