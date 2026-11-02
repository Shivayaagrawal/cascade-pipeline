# Phase 5 results

Cited run: `experiments/phase5/run-20261102-stage4-scored`. Test n = 56. Validation was scored first and was not used to change the switches. Development was not scored.

On this synthetic test slice, `b2_semantic_v5` committed 23/56 cases. Nine of those commits were safe under the specification, and 14 were unsafe. The 14 unsafe commits are every critical-slot mutation in the test split. Native path safety among v5 commits is 9/23. Coverage is lower than every baseline that is allowed to commit. Holding every case would have been safer and is not what this controller did: the six clean controls, including both `Please` prefixes, were committed, and unnecessary abstention is 0/9.

## Test headlines

| Id | Coverage | Unsafe commits | Native path safety | Safe commits | Exact frame |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 prefix one-best | 48/56 | 42/48 | null, id not emitted | 4 | 7/56 |
| E1 prefix multi | 48/56 | 42/48 | null | 4 | 7/56 |
| E2 prefix controller | 48/56 | 42/48 | null | 4 | 7/56 |
| E3 forced lexical | 0/56 | null | null | 0 | 0/56 |
| E4 lexical v3 | 53/56 | 47/53 | null | 6 | 39/56 |
| E5 semantic v4 | 41/56 | 35/41 | null | 6 | 27/56 |
| E6 semantic v5 | 23/56 | 14/23 | 9/23 | 9 | 9/56 |

E3's forced exact-frame count is not coverage. Its nine unnecessary abstentions are the nine cases the oracle marked committable.

Adapter path safety, which is not native emission, is 6/48 for E0–E2, 6/53 for E4, and 6/41 for E5. Those six are the clean controls. v5 has no adapter-traced commits because its ids are `CONTROLLER_EMITTED`.

## Parent-cluster bootstrap, E6 minus the other strategy

Fourteen parents appear in the paired test cases. The interval has to lie entirely on one side of zero to count as a directional result on this slice.

| Contrast | Per-case unsafe | Coverage |
| --- | --- | --- |
| E6 − E0, E1, and E2 | −0.250, CI −0.429 to −0.089 | −0.223, CI −0.393 to −0.080 |
| E6 − E4 | −0.295, CI −0.455 to −0.134 | −0.268, CI −0.446 to −0.089 |
| E6 − E5 | −0.188, CI −0.295 to −0.080 | −0.161, CI −0.268 to −0.054 |

All five coverage intervals are below zero, and all five unsafe intervals are below zero. v5 produced fewer per-case unsafe commits and covered fewer cases than E0, E1, E2, E4, and E5 on these 14 clusters. That is a safety–coverage tradeoff on this slice. It is not a general SLU result.

## By category, E6

| Category | Test outcome |
| --- | --- |
| clean_affirmative | 6/6 safe commits, including 2 `Please` prefixes |
| negation | 6/6 safe abstentions |
| uncertainty_maybe, possibly, might | 6/6 safe abstentions each |
| conditional_if_needed | 6/6 safe abstentions |
| critical date, time, amount | 6, 4, and 4 unsafe commits |
| provenance, negated plus clean | 3/3 RETRY safe commits of the clean id |
| provenance, two values | 3/3 safe abstentions |

E5 held negation and `maybe`, and committed `possibly`, `might`, and `if needed` as correct frames on an unsafe path (6 each). E5 also committed all 14 mutated values. On the three negated-plus-clean bundles, v4's action was RETRY, but v4 does not emit an id. The earliest frame match is the negated string, because that string still contains the time, so those three were not credited as safe paths. v5 emitted the clean candidate id.

The two prefix `Please` lines are incorrect frames for E0. v5 committed both.

Modality agreement for v5 is 53/56. The three misses are the successful retries: the label describes the negated primary string, and the emitted reading is the affirmative candidate that was committed. Polarity has the same three misses. Conditionality is 56/56. Prefix strategies do not emit modality, so their modality accuracy is null.

Validation, before the test file was parsed, had the same shape at 22/56 coverage, 13/22 unsafe, and 9 safe commits. The validation case `p5-critical_amount_mutation-val-03` ("181") was held. No test case contains `181` or `April 3`.

Mean controller time on the test rows was about 0.09 ms. That is not ASR latency.
