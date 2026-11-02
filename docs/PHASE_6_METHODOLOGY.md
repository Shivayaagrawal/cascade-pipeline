# Phase 6 methodology

## Identities

These ids belong to `experiments/phase6/`. They are not Phase 5 ids. Phase 5 E3 was forced lexical and Phase 5 E6 was `b2_semantic_v5`.

| Phase 6 id | What ran | Evidence |
| --- | --- | --- |
| E0 | frozen `b0_prefix` | candidate text, adapter id |
| E1 | frozen `b2_lexical_v3` | candidate text, adapter id |
| E2 | frozen `b2_semantic_v4`, Phase 3 weights, threshold 0.25 | candidate text, adapter id |
| E3 | unchanged `b2_semantic_v5` | candidate bundle only |
| E4 | `b2_reference_aware_v1` | candidates plus critical-slot reference |
| E5 | same checker | candidates plus parent transcript |

E0–E2 ids are adapter matches. They are not native emissions. E3 does not receive the reference file.

## Policy

`experiments/phase6/run-20261102-phase6/validation/frozen_policy.json` was written before any oracle line was parsed. `test_cases_read` is false. `validation_used_for_selection` is false. Policy SHA-256 `6f976bb1f01d4ba005ac1dbdb0dae1fe2ff2a02f38169d9a218d6514073e6b22`. Git `f55b5bd5b74d760e00f3178a35cd9b9512fd1ccf`. Python 3.13.7. Seed `20261106`.

The Phase 5 controller file hash recorded with the run is `65573cb4f53ead1b4bed2dff467db48f7e41e948cee2096766885da1bbf8f500`.

## Metrics

Coverage is commits over all cases. Selective risk is incorrect committed frames over commits. Unsafe-commit rate is unsafe commits over commits. A commit whose candidate id is outside the condition's safe set is unsafe. A correct frame from such a candidate is `CORRECT_FRAME_UNSAFE_PATH` and counts as unsafe. Native path safety uses only ids the controller emitted. Adapter path safety is separate. Critical-slot safety is safe commits among commits in the three substitution categories. If that denominator is zero, the rate is null. Substitution detection is substitution rows that were not committed with the wrong frame, over all substitution rows. A hold-everything run can score perfectly on detection and still fail the clean controls. False rejection is clean or polite rows that are not safe commits.

Wilson intervals use the Phase 5 implementation, z = 1.959963984540054. The parent-cluster bootstrap resamples the 14 parents that appear in both E3 and E4, 1000 draws. Unsafe uses seed `20261106`. Coverage uses seed `20261107`. The estimate is E4 minus E3 on a per-case indicator. It is not a rate among commits. Development was not scored.

Controller timings are `perf_counter` durations. They are not ASR latency.

The oracle and the checker were written in the same session. Agreement with the specification is not independent human annotation.
