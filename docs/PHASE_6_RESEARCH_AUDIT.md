# Phase 6 research audit

The cited run is `experiments/phase6/run-20261102-phase6`. This note checks whether the logs support the claims. It does not add a controller.

## Denominators

Coverage uses all 36 test cases. Unsafe-commit rate and path safety use commits. E4's critical-slot safety uses commits in the substitution categories. There are none, so the rate is null. Substitution detection uses all 11 substitution rows, including abstentions. Those are different questions. A7 and A8 show why: detection can be 11/11 while clean false rejections are 7/7 and coverage is 0/36.

The bootstrap uses 14 parent clusters, the intersection of parents that appear in E3 and E4, not the 42 ids on the test list. Both the unsafe interval and the coverage interval for E4 minus E3 lie entirely below zero.

## What the files show

E3 commits 9 in-inventory substitutions and holds `April 3` and `181`. E4 holds all 11 substitutions, commits the two-value candidate that matches the reference, and commits all 7 clean and polite controls. E5 matches E4 except for the one `Maybe` transcript, which it holds. A1, with the reference check off, returns the v5 commits. A2, A3, and A4 each release the modality class they disable and leave substitution detection unchanged. A5 changes no row. A6 releases the in-inventory commits. A7 and A8 hold everything.

The Phase 5 controller file hash stored in the run matches the file that was called. The policy hash is `6f976bb1f01d4ba005ac1dbdb0dae1fe2ff2a02f38169d9a218d6514073e6b22`, written with `test_cases_read` false and `validation_used_for_selection` false.

## What they do not show

They do not show that v5 learned to see substitutions. The same function still commits them when the reference is withheld. They do not show a human-validated oracle, a large parent sample, or a speech system. They do not show that a full transcript generally beats a slot reference. They show one constructed counterexample and 35 agreements.

The supported conclusion is narrow. On this synthetic set, candidate-only verification can enforce modality, lexicon membership, and candidate-internal support. It cannot see that a complete in-inventory value replaced a different authorized value. An explicit critical-slot reference detects those rows here, at a coverage cost equal to the unsafe commits it removes, without rejecting the clean controls in this test. That reference is additional information, not a better reading of the candidate.
