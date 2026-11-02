# Phase 6 ablations

Ablations use the 36 test cases. Each one changes a single factor on the reference-aware checker. They were not used to pick a new policy. A0 is E4.

| Ablation | Change | Coverage | Unsafe | Substitution detection | Clean false rejections |
| --- | --- | ---: | ---: | ---: | ---: |
| A0 | none | 11/36 | 0/11 | 11/11 | 0/7 |
| A1 | reference check off | 19/36 | 9/19 | 2/11 | 0/7 |
| A2 | modality off | 16/36 | 5/16 | 11/11 | 0/7 |
| A3 | polarity off | 16/36 | 7/16 | 11/11 | 0/7 |
| A4 | conditionality off | 13/36 | 2/13 | 11/11 | 0/7 |
| A5 | provenance check off | 11/36 | 0/11 | 11/11 | 0/7 |
| A6 | commitment gate off | 32/36 | 23/32 | 2/11 | 0/7 |
| A7 | one reference field removed | 0/36 | null | 11/11 | 7/7 |
| A8 | reference removed | 0/36 | null | 11/11 | 7/7 |

A1 returns the frozen v5 decision. The nine in-inventory substitutions are unsafe again, and the two-value bundle that the reference would have committed becomes an unnecessary abstention under the reference specification. The reference check is the factor that separates A0 from A1.

A2 commits the five uncertainty rows as correct frames on a path the specification does not allow. A3 does the same for the five negation rows and the two negated-plus-clean bundles, where the first candidate still contains the parent's slot. A4 does it for the two `If needed` rows. Substitution detection stays 11/11 in A2–A4 because the reference comparison is still on. Modality and the reference answer different failures.

A5 changes nothing. Every test bundle already had unique candidate ids, so the switch had nothing to reject.

A6 commits the earliest complete frame and skips the reference comparison. Detection falls to 2/11, the two out-of-inventory rows that never form a complete frame. The gate is what keeps the in-inventory substitutions from being committed.

A7 and A8 commit nothing. Their 11/11 detection score is the hold-everything pattern. They also reject all 7 clean controls, which is 11 unnecessary abstentions against the cases the specification says to commit. A missing reference is not evidence that the candidate is safe, and it is not a reason to invent the missing value.
