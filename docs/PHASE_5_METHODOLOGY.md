# Phase 5 methodology

## Identities

Phase 5 experiment ids are local to `experiments/phase5/`. They are not the Phase 4 ids.

| Phase 5 id | Strategy | Phase 4 name to avoid confusing with it |
| --- | --- | --- |
| E0 | `b0_prefix` | E0 was also `b0_prefix` |
| E1 | `b1_prefix` | E1 was also `b1_prefix` |
| E2 | `b2_prefix_controller` | E2 was also the prefix controller |
| E3 | `b1_forced_lexical` | E3 was also forced selection, and it is not coverage |
| E4 | `b2_lexical_v3` | Phase 4 E4 was lexical v3 |
| E5 | `b2_semantic_v4` | Phase 4 E5 was the lexical ablation. Phase 4 E7 was v4 |
| E6 | `b2_semantic_v5` | No Phase 4 counterpart |

v4 is called with the frozen Phase 3 weights: contradiction 1, every other weight 0, threshold 0.25. Those weights were not refit.

## Policy

The gate switches all default to on. There is no weight grid. `experiments/phase5/run-20261102-stage4-scored/validation/frozen_policy.json` was written with `test_cases_read: false` before test lines were parsed. Policy SHA-256 `0840ee89f84553b2d345d56c141056f57428950320904b23abd11f91ac7393b9`. Git commit `f55b5bd5b74d760e00f3178a35cd9b9512fd1ccf`. Python 3.13.7. Seed `20261105`.

An earlier directory, `run-20261102-stage4`, scored adapter-traced safe candidates as unsafe paths. The controller was not changed between the two directories. The scored directory is the one cited.

## Metrics

Coverage is commits over all cases. Selective risk is incorrect frames over commits. Unsafe-commit rate is unsafe commits over commits. A commit is unsafe when the candidate id is not in the oracle's safe set. A correct frame from a candidate outside that set is `CORRECT_FRAME_UNSAFE_PATH` and counts as unsafe. Native path safety is safe ids emitted by the controller over controller-emitted commits. Adapter path safety is the same ratio for ids matched by the adapter, and it is reported separately. A missing strategy id is not native path safety. Rates with a zero denominator are null.

E3 records a forced frame and `actual_commit` false. Its coverage is 0. Unnecessary abstention on E3 is the cases the oracle wanted committed, which forced selection does not commit.

Wilson intervals use z = 1.959963984540054. A zero or full numerator is clamped to 0 or 1. Parent-cluster bootstrap resamples the parents that actually appear in the paired cases, 1000 draws. Unsafe uses seed `20261105`. Coverage uses seed `20261106`. The estimate is the mean within-parent difference, E6 minus the other strategy, of a per-case indicator. It is not a conditional rate among commits.

`execution_time_ms` is `perf_counter` around the controller. It is not ASR latency.

## Oracle limitation

The oracle and the controller were written in the same session. Agreement with the oracle is agreement with that specification. It is not human gold, inter-annotator agreement, or audio review. Modality labels describe the primary candidate. A successful RETRY emits the modality of the selected candidate, so those cases can miss the primary-text modality label even when the action is the one the specification asked for.
