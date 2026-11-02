# Phase 3 results

These numbers are the second test scoring pass. They use `phase3-policy-v1`, frozen on the 32 validation cases before this test pass. The test split has 40 cases, five in each category. This is a synthetic text simulation. It is not a speech result.

E7's action accuracy is agreement with labels that were written from the same operators the controller implements. It is not an independent discovery that those operators are the right safety policy. The informative contrast is what the frozen baselines do on the same bundles.

## Test split, coverage beside selective risk

| Condition | Coverage | Selective risk | Unsafe-commit rate | Exact frame |
| --- | --- | --- | --- | --- |
| E0 prefix B0 | 26/40 | 21/26 | 24/26 | 5/40 |
| E1 prefix B1 | 27/40 | 21/27 | 24/27 | 6/40 |
| E2 prefix B2 | 26/40 | 20/26 | 23/26 | 6/40 |
| E3 forced lexical | 0/40 | null, no safety commits | null, no safety commits | 0/40 as commits. Forced exact frame 17/40, reported separately. |
| E4 lexical v3 | 12/40 | 0/12 | 8/12 | 12/40 |
| E5 diagnosis plus frozen lexical action | 12/40 | 0/12 | 8/12 | 12/40 |
| E6 gates, retry off | 2/40 | 0/2 | 0/2 | 2/40 |
| E7 `b2_semantic_v4` | 4/40 | 0/4 | 0/4 | 4/40 |

E4 shows the metric split directly. All 12 commits match the parent intent and slots, so selective risk is 0/12. Eight of those commits were still unsafe because the case metadata says the frame should not have been committed. Abstentions are not in the unsafe numerator.

E0 and E1 have no recovery action, so action accuracy is 0/40. That is a property of the baseline, not a failure to emit `HOLD`. E2 action accuracy is 15/40. E7 action accuracy is 40/40 against the operator labels.

E7 also records polarity accuracy 35/40, ambiguity precision and recall 5/5, contradiction recall 5/5, clarify 5/40, hold 31/40, and retry success 2/2. The five polarity misses are two retries, whose committed polarity is the affirmative alternate while the case label stores the primary negation, and three function-word holds whose damaged text no longer supports an intent, so polarity stays `unknown` rather than `affirmative`. Critical-slot safety is null: E7 made no commits on slot-corruption or contradiction cases.

E6's action accuracy is 38/40. The two misses are the negation cases where E7 retries and E6 holds. That is the coverage difference between 2/40 and 4/40.

## Ablations on the same 40 cases

Weights were not refit.

| Ablation | Coverage | Selective risk | Unsafe commits | Action accuracy |
| --- | --- | --- | --- | --- |
| A1 polarity off | 7/40 | 0/7 | 3/7 | 0.875 |
| A2 ambiguity off | 4/40 | 0/4 | 0/4 | 0.875 |
| A3 critical slots off | 9/40 | 0/9 | 5/9 | 0.875 |
| A4 contradiction off | 4/40 | 0/4 | 0/4 | 1.0 |
| A5 completeness off | 4/40 | 0/4 | 0/4 | 1.0 |
| A6 modality off | 9/40 | 0/9 | 5/9 | 0.875 |
| A7 risk score off | 4/40 | 0/4 | 0/4 | 1.0 |
| A8 v4 policy off | 12/40 | 0/12 | 8/12 | 0.25 |

A4, A5, and A7 do not move the headline rates on this test split. Slot conflicts are already stopped by the critical-slot gate, so turning contradiction detection off does not add commits here. Turning the risk score off does not add commits at the frozen threshold. A1, A3, and A6 do add unsafe commits.

## Hypotheses

| ID | Reading on this test split |
| --- | --- |
| H1 | A1 adds 3 unsafe commits that E7 does not make. Polarity changes commitment inside this grammar. |
| H2 | A2 keeps coverage and unsafe commits unchanged and lowers action accuracy to 0.875. The action label changes. The commit set does not. |
| H3 | A3 adds 5 unsafe commits. The critical-slot gate is doing that work on this set. |
| H4 | Not supported as a separate effect. A4 matches E7 because the slot gate already holds those bundles. |
| H5 | Not supported as a separate effect. A5 matches E7. |
| H6 | E7's operating point is 4/40 coverage with selective risk 0/4 and unsafe-commit rate 0/4. E0 is 26/40 with selective risk 21/26 and unsafe-commit rate 24/26. E7 avoids the baseline's unsafe commits by answering much less often. That is a different point, not by itself a proof that the balance is the useful one. |
| H7 | E5 still makes 8 unsafe commits out of 12. E7 makes none out of 4. Diagnosis without the v4 policy does not produce E7's commit behavior. |

No threshold curve was drawn on the test split. Doing that would have reused the test cases as a sweep. The validation grid is stored in `experiments/phase3/validation_search.json`.

The Phase 2 LLM audit remains 30/30 on original transcripts and 57/90 intent, 43/90 slots on edited rows. Those figures were not used as labels here.
