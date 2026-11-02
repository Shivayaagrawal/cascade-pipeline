# Phase 4 validation report

Validation has 120 cases. The Phase 3 configuration, scored before the grid was used to change anything, gives E7 coverage 56/120, unsafe commits 27/56, and path safety 29/56. The same three counts appear on the later test split. That is a property of this generator, not a reason to refit.

## Grid

All 350 cells were scored. 280 cells have 27 unsafe commits. 70 cells have 0 unsafe commits. Those 70 are every cell with threshold 0. At threshold 0 the frozen score blocks every `CONTINUE`, including clean controls. `RETRY` still fires, so 9 provenance retries remain and all 9 are safe. Coverage at that point is 9/120, and unnecessary abstention is 20/29.

The Phase 3 cell, threshold 0.25, is not in the 70-cell tie. The lexicographic rule therefore selects contradiction weight 1 and threshold 0. The validation curve at the Phase 3 weights is:

| Threshold | Coverage | Unsafe commits | Unnecessary abstention |
| ---: | --- | --- | --- |
| 0 | 9/120 | 0/9 | 20/29 |
| 0.25 | 56/120 | 27/56 | 0/29 |
| 0.5 | 56/120 | 27/56 | 0/29 |
| 0.75 | 56/120 | 27/56 | 0/29 |
| 1 | 56/120 | 27/56 | 0/29 |

Thresholds above 0 do not move E7, because the unsafe continues on this set have risk score 0. The gates never label a substituted lexicon value, a hedge, or `possibly` as a failure, so the score stays below every positive threshold.

The frozen policy records both cells. Hypotheses use threshold 0.25. Threshold 0 is the sensitivity run.
