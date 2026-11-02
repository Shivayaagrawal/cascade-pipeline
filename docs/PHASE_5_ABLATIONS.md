# Phase 5 ablations

Ablations reuse the same 56 test cases and the same predeclared weights. They were not used to pick a new policy. A0 is the full gate.

| Ablation | What changed | Coverage | Unsafe | What moved |
| --- | --- | ---: | ---: | --- |
| A0 full | none | 23/56 | 14/23 | reference |
| A1 modality off | uncertainty and mixed cues no longer block | 41/56 | 32/41 | 18 correct-frame unsafe paths: maybe, possibly, and might, 6 each |
| A2 polarity off | negation no longer blocks | 29/56 | 23/29 | 6 negation commits plus the 3 provenance retries become correct-frame unsafe paths. Safe commits fall from 9 to 6 |
| A3 critical slots off | conflicting frames are no longer held | 26/56 | 17/26 | the 3 two-value bundles are committed as the first, parent-matching frame |
| A4 provenance off | id membership is not checked | 23/56 | 14/23 | no case changed. Every bundle already had unique ids |
| A5 conditionality off | `if` and `unless` no longer block | 29/56 | 20/29 | the 6 `If needed` cases become correct-frame unsafe paths |
| A6 gate off | the raw proposal commits | 53/56 | 47/53 | matches the broad lexical commit pattern. Safe commits fall to 6 |
| A7 recovery off | RETRY becomes HOLD | 20/56 | 14/20 | the 3 provenance retries become unnecessary abstentions. The 14 mutation commits remain |
| A8 risk off | the score is cleared, gates stay on | 23/56 | 14/23 | no case changed |

The risk score added no decision beyond the gates. The provenance switch also added none on this set, because the failure it can see, a missing or duplicate id, was not present in the test bundles. Both of those are reported as no effect, not as evidence that the components are unnecessary in general.

The gate is the component that separates A0 from the lexical commit pattern. Polarity, modality, conditionality, critical-slot conflict, and recovery each changed a specific subset. None of them stopped the 14 in-inventory mutations. Those commits are surface-faithful to the candidate the controller was allowed to see.
