# Phase 5 limitations

This is a controlled synthetic text evaluation. It is not a speech-recognition result, not an audio review, and not a claim about conversational systems.

The oracle is a specification table written in the same session as the controller. Matching it is not independent human validation. There is no inter-annotator agreement.

The test has 56 cases on 14 of 40 test parents. Parent lists do not overlap, but the category allocator never reached the other 26 test parents. Intervals from 14 clusters are wide. A zero unsafe count would still not have been a safety guarantee, and the unsafe count is not zero.

v5 commits every in-inventory single-candidate substitution in the test split: 6 dates, 4 times, and 4 amounts. Critical-slot safety among those commits is 0/14. The controller was not given the referent, so it cannot see that 8 AM replaced 7 AM when both are legal inventory values. Closing that gap by passing the referent would make the test circular.

`April 3` occurs only in development, which was not scored. `181` occurs only in validation, where it was held. The test split does not measure out-of-inventory blocking.

Retry is a choice among the supplied candidates. It is not a second decode, and there is no ASR latency. Candidate bundles are synthetic edits or a passthrough of the parent text, not recognizer N-best lists.

Modality is a small rule list: `not` and contractions, `maybe` / `possibly` / `might` / lowercase `may`, `if` / `unless`, and polite `please` / `could you` / `can you`. The month `May` is excluded by case. These rules do not cover the rest of English.

A controller that holds everything is safe and not useful. v5 did not do that on the clean controls. The coverage cost against v4 and the prefix baselines is part of the result.

Baselines do not emit candidate ids. Their native path safety is null. Adapter matches are a separate number. For v4's three provenance retries, the action was RETRY and the earliest frame match still points at the negated string, so those commits were not counted as safe paths.
