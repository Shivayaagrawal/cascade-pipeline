# Phase 6 results

Cited run: `experiments/phase6/run-20261102-phase6`. Test n = 36, on 14 parent clusters. The policy was frozen before the test labels were parsed. Development was not scored. Validation was not used to change the switches.

On this slice, the critical-slot reference removed every in-inventory substitution commit that candidate-only v5 made, and it did not reject any of the 7 clean or polite controls. Coverage fell from 19/36 to 11/36. The unsafe-commit rate among E4's 11 commits is 0/11. Critical-slot safety is null, because E4 made no commit in the substitution categories. Those rows are abstentions. Null is not a claim of zero risk over a broader set.

## Test headlines

| Id | Coverage | Unsafe commits | Substitution detection | Clean false rejections | Safe commits |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 prefix | 34/36 | 26/34 | 0/11 | 2/7 | 6 |
| E1 lexical v3 | 31/36 | 23/31 | 2/11 | 0/7 | 8 |
| E2 semantic v4 | 24/36 | 16/24 | 2/11 | 0/7 | 8 |
| E3 candidate-only v5 | 19/36 | 9/19 | 2/11 | 0/7 | 10 |
| E4 critical-slot reference | 11/36 | 0/11 | 11/11 | 0/7 | 11 |
| E5 full transcript | 10/36 | 0/10 | 11/11 | 0/7 | 10 |

E0's two clean false rejections are the polite prefixes. Prefix extraction misses the slot. E4 committed both.

Native path safety is 10/19 for E3 and 11/11 for E4. E0–E2 did not emit ids, so their native path safety is null. Adapter path safety is a separate field in the run summary.

## E3 versus E4

Parent-cluster bootstrap, E4 minus E3, 14 clusters:

- Per-case unsafe commits: −0.518, CI −0.741 to −0.277.
- Per-case coverage: −0.500, CI −0.750 to −0.205.

Both intervals are entirely below zero. The reference condition produced fewer unsafe cases per parent and covered fewer cases. The coverage drop is the nine in-inventory substitutions that v5 committed and E4 held, minus one two-value bundle that v5 held and E4 committed because the reference identifies the matching candidate. Net commits: 19 − 9 + 1 = 11.

## By category

| Category | E3 | E4 | E5 |
| --- | --- | --- | --- |
| clean, including 5 plain | 5 safe commits | 5 safe commits | 5 safe commits |
| polite | 2 safe commits | 2 safe commits | 2 safe commits |
| negation, uncertainty, conditionality, ambiguity | held | held | held |
| date substitution | 1 hold, 2 unsafe commits | 3 holds | 3 holds |
| time substitution | 4 unsafe commits | 4 holds | 4 holds |
| amount substitution | 1 hold, 3 unsafe commits | 4 holds | 4 holds |
| provenance | 2 safe retries, 1 hold | 3 safe commits | 3 safe commits |
| parent transcript cue | 1 safe commit | 1 safe commit | 1 hold |

The two holds shared by E3 and E4 are `April 3` and `181`. Both values are outside the lexicon, so the candidate frame is incomplete before any reference is consulted. The nine other substitution commits are in-inventory. v5 commits them. The reference holds them. That is the information boundary, not a defect in the candidate-only gate.

E5 matches E4 on every substitution. It differs on the one predeclared row whose parent transcript is `Maybe` plus the clean sentence. Mode 1 commits that candidate. Mode 2 holds it. The transcript added one decision on this test set, and that decision was not a critical-value substitution.

Validation, scored after the policy file existed, had the same shape: E3 21/36 coverage and 11/21 unsafe; E4 11/36 coverage, 0/11 unsafe, 11/11 substitution holds, 0/7 clean false rejections. E4 action agreement with the specification was 36/36 on validation and is agreement with a same-session table, not a separate annotation.
