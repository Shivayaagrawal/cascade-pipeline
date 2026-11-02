# Phase 5 research audit

The implementation is frozen at `experiments/phase5/run-20261102-stage4-scored`. This note checks whether those files support a conclusion. It does not add a controller.

## Denominators

Coverage uses all 56 test cases. Unsafe-commit rate, selective risk, path safety, and safe-commit accuracy use commits only. E3 has no commits, so those rates are null rather than zero. E6's 14 unsafe commits are also its 14 selective errors: each committed frame is the mutated value, not the parent. Exact frame accuracy counts abstention as a miss, so E6 is 9/56 there and 9/23 among commits. Those are different measures.

Native path safety is 9/23 for E6 because the controller wrote the candidate id. It is null for E0–E5, with the reason that the strategy did not emit an id. Adapter path safety is stored beside it and is not substituted into the native rate.

The parent-cluster intervals use 14 clusters, the parents that actually received test cases, not the 40 parents on the test list.

## What the files show

v5 committed fewer unsafe cases per parent than E0, E1, E2, E4, and E5, and the coverage intervals are also entirely below zero. The category log is specific. Negation, maybe, possibly, might, and if-needed were held. Both polite controls were committed. The three negated-plus-clean bundles were retries of the emitted clean id. The three two-value bundles were held. All 14 in-inventory mutations were committed and scored unsafe.

v4, on the same bundles, held negation and maybe, and committed possibly, might, if-needed, and all 14 mutations. Its three provenance actions were RETRY, without an emitted id.

A1, A2, A3, A5, A6, and A7 each change a named subset. A4 and A8 change nothing. The risk score did not add a decision beyond the gates. The provenance check did not fire, because no test bundle had a missing or duplicate id.

## What the files do not show

They do not show that in-inventory substitution was solved. They do not show that April 3 was held on the test set, because April 3 is not in the test set. The validation hold on 181 is one validation case. They do not show human agreement, audio review, recognizer N-best behavior, or a latency claim. Action agreement with the specification is not independent evidence for the rules, because the specification and the controller were written together.

The defensible reading is the same shape as the earlier phases, on a harder slice: v5 is more conservative than the frozen baselines here, the conservatism has a coverage cost, and the remaining unsafe commits are exactly the substitutions a candidate-faithful gate cannot see without the referent.
