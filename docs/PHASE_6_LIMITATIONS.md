# Phase 6 limitations

This is a synthetic text comparison. It is not a speech-recognition result, not an audio review, and not evidence about conversational systems. The candidates are constructed edits, not recognizer N-best lists. Retry chooses among the supplied strings. It is not a second decode. Recorded durations are not ASR latency.

The oracle is a specification written in the same session as the checker. Matching it is not human gold and not inter-annotator agreement.

The test has 36 cases on 14 of 42 test parents. The bootstrap uses those 14 clusters. The intervals are wide. Zero unsafe commits among 11 commits is not a safety guarantee outside this slice.

`181` does not occur as a parent amount. `April 3` does not occur as a parent date. Each of those substitutions is one test row. The 6 PM to 5 PM substitution is a validation row, because that parent was not preassigned to test. The multiple-slot category was not built: the only two-slot intent is `transfer_money`, and its currency slot is always `rupees`.

Out-of-inventory behavior in Phase 5's test split was not measured, and these two Phase 6 rows do not create a general out-of-inventory claim.

Mode 2's extra decision rests on one constructed `Maybe` transcript. The other parent transcripts are the frozen templates. This run does not show that full transcripts usually add information beyond critical slots.

E4's substitution detection is 11/11 because it abstains. A7 and A8 also score 11/11 by holding every row, including all 7 clean controls. Detection without the clean-control count is the wrong summary.

The reference is an experimental authorization, not a component a deployed candidate-only system has. Giving v5 the referent and then calling the result candidate-only would make the comparison circular. This run keeps those conditions apart.
