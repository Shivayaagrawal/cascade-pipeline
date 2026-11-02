# Phase 3B research audit

This audit reads the saved Phase 3 decision logs, the challenge table, and the metric code. It does not change the controller, the challenge set, the frozen policy, or the experiment outputs. Nothing was retuned on the test split.

The implementation remains technically complete. The research conclusion stays provisional. The defensible claim is the one in the last section, not a claim that E7 is the best system overall.

## Metric definitions

The scorer in `scripts/run_phase3.py` and `phase3_metrics.py` uses three different denominators.

| Measure | Numerator | Denominator | Empty denominator |
| --- | --- | --- | --- |
| Coverage | A frame was committed | All cases in the split | Null, not zero |
| Selective risk | Committed frame differs from the parent intent and slots | Commits only | Null. Abstention is not a risk of zero. |
| Unsafe-commit rate | Commit on a case whose metadata says `expected_commit_safety` is false | Commits only | Null. Abstention is not an unsafe commit. |

Recomputing the saved test logs reproduces the reported table. E0 is 26/40 coverage, selective risk 21/26, unsafe 24/26. E4 is 12/40, selective risk 0/12, unsafe 8/12. E7 is 4/40, selective risk 0/4, unsafe 0/4. E3 coverage is 0/40. Its 17/40 figure is forced exact-frame accuracy, stored separately.

Two definitions are weaker than their names.

Safe-commit accuracy does not require the action to match the expected action. A commit of the parent frame is marked safe whenever the case metadata allows a commit. On the two test negations that include the original sentence as an alternate, E4 commits from the negated string itself, with reason `evidence_agrees`, and is still scored safe. The metadata allows the commit because the prescribed action is `RETRY` of the parent frame. The scorer does not check that the system used that path.

Critical-slot safety, on ablation A3, is 5/5. Those five commits are the contradiction cases, the committed slots match the parent, and the metric therefore calls them safe. The unsafe-commit rate on the same run is 5/9, and selective risk is 0/9. A forbidden commit of the original value is invisible to selective risk and to critical-slot safety. Only the unsafe-commit rate sees it. Those three numbers must not be described as the same event.

## Why E4's eight commits are unsafe

E4 commits 12 test frames. All 12 match the parent intent and slots. Eight are unsafe. Four are scored safe, with the caveat above.

The eight unsafe commits are every test case in two categories:

| Category | Test cases | What the text says | What lexical recovery does |
| --- | ---: | --- | --- |
| `NEGATION_SHIFT` without an alternate | 3 | `not` is inserted after the first token, for example "Remind not me at 11 PM" | `evidence_agrees` and `CONTINUE`. The word `not` is not a slot or an intent cue, so the parent frame is still complete. |
| `UNCERTAINTY_OR_MODALITY` | 5 | The sentence is prefixed with "Maybe" | The same `CONTINUE`. "Maybe" is not an intent or slot cue. |

The frames are correct relative to the parent. They are unsafe because the operator says a negated request and a hedged request must not be committed. Lexical v3 has no representation of either signal. That is why exact-frame correctness and unsafe-commit rate come apart.

The other two negation commits, "Book not an appointment for April 2" and "Transfer not 50 rupees", are the ones scored safe. Each bundle also contains the original sentence. E4 never needs that alternate. It commits the negated string and receives credit because the case-level flag is true.

## What the four E7 commits actually are

E7's four test commits are the only four test cases whose metadata allows a commit. It holds or clarifies the other 36. The zero unsafe-commit count is four allowed commits and no forbidden ones, not a sample of unsafe situations that were all avoided while still answering.

| Case | Action | Why a frame is available |
| --- | --- | --- |
| `p3-negation_shift-tes-02` | `RETRY` | The bundle contains both "Book not an appointment for April 2" and the original "Book an appointment for April 2". The commit is the original sentence. |
| `p3-negation_shift-tes-04` | `RETRY` | Same pattern for "Transfer not 50 rupees" plus "Transfer 50 rupees". |
| `p3-function_word_damage-tes-01` | `CONTINUE` | "banana are your Saturday hours?" still matches `general_information` because the lexical cue includes " your ", and the topic remains. |
| `p3-function_word_damage-tes-03` | `CONTINUE` | "banana my yesterday transaction" still matches `check_transaction` on the word "transaction", and "yesterday" remains the slot. |

The two retries are safe only because the dataset plants the parent sentence beside the negation. The two continues are safe only because the first-token replacement leaves a lexical cue intact. E7 does not commit a negated sentence that has no clean alternate, a "Maybe" sentence, a placeholder slot, a missing slot, a context word, an ambiguous line, or a value conflict.

Validation has the same shape. Its four safety-true cases are two negation retries and two function-word continues. The reported validation result, 0 unsafe commits out of 4 commits and coverage 4/32, is those four cases.

## Category balance

Counts are balanced by construction. Development, validation, and test contain 21, 4, and 5 cases in every category. No category is missing.

The imbalance is in how many cases permit a commit. Across the whole 240, 26 cases are marked safe to commit: 14 negation rows that carry the original sentence, and 12 function-word rows whose damaged text still matches the parent. The test split has four of those. A zero unsafe count on four commits does not estimate a rate for the other six failure types, because the prescribed action there is to abstain.

## Weight search

All 350 validation configurations have zero unsafe commits. The gates, not the weights, produce that result. Among those 350, 224 also share the best safe-commit accuracy, the best selective risk, and the best coverage, which is 4/32. The other 126 configurations cover only 2/32. They hold the recoverable `banana` sentences when the intent weight is large enough to cross the threshold. They do not create unsafe commits.

The recorded choice, contradiction weight 1 and threshold 0.25, is the lexicographic minimum of those 224 ties. It is not evidence that contradiction should weigh more than polarity, slots, intent, or ambiguity. Ablation A7, which turns the score off, matches E7 on every test case. At the selected weights the intent indicator is multiplied by zero, so function-word damage does not affect the score either.

The search is reproducible. It is not a stable identification of a risk model.

## Ablations

Headline equality does not mean the component is idle.

| Ablation | Cases whose action or reason changes | What changes |
| --- | --- | --- |
| A1 polarity | 5 negation cases | Three holds become commits of the negated sentence and are unsafe. Two retries become continues of the same parent frame and stay scored safe. |
| A2 ambiguity | 5 ambiguity cases | `CLARIFY` becomes `HOLD`. Coverage and unsafe commits stay the same. The action label changes. |
| A3 critical slots | 5 contradiction cases commit; 2 slot-placeholder reasons change | Five new unsafe commits. Selective risk stays 0 because the committed frame is the parent. Critical-slot safety is reported as 5/5. |
| A4 contradiction | 0 | No test case changes. The slot gate already holds the conflicting bundles. |
| A5 completeness | 8 | The action stays `HOLD`. The reason changes from `INCOMPLETE_FRAME` to `INSUFFICIENT_EVIDENCE`. Coverage, risk, and action accuracy do not move. |
| A6 modality | 5 "Maybe" cases | All five become unsafe commits of an otherwise complete frame. |
| A7 risk score | 0 | No test case changes at these weights. |
| A8 v4 policy removed | All 40 | The action falls back to frozen lexical recovery, with the same 8 unsafe commits as E4 and E5. |

A1, A3, and A6 have measurable effects on unsafe commits. A2 and A5 have effects that the headline coverage and risk rates do not show. A4 and A7 are not shown to be necessary by this test split. That does not show they would be unnecessary on a set where a conflict is not already caught by another gate, or where the score is the only thing standing between a commit and a hold.

## Circularity and sample size

E7 action accuracy is 40/40 because the controller implements the operators that wrote the expected actions. The baselines were not written from those operators, so their disagreements are informative. E7's agreement is an implementation check.

Forty test cases, and four commits, are too few for a safety guarantee. Every configuration already had zero validation unsafe commits, so the validation sample also did not stress the score.

## Conclusion

In this controlled synthetic text-only set, `b2_semantic_v4` commits four of forty test cases and makes no commit that the operator marked unsafe. The frozen prefix baselines commit about two thirds of the cases and most of those commits are marked unsafe. Lexical v3 commits twelve parent-matching frames, eight of which are marked unsafe because negation and "Maybe" are invisible to it. These figures describe a safety-coverage tradeoff on this challenge set. They do not establish better general-purpose SLU performance.

Action accuracy is not independent validation of the diagnosis rules. The selected risk weights are one of 224 equally scoring configurations. A larger challenge set, with labels that the controller does not already implement, would be required before those conclusions could be treated as robust. This audit does not build that set.
