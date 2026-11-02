# Phase 1D.7 research claim matrix

**Date:** 2026-11-02  
**Population:** the 200 utterances of `synthetic-seed17-v1` only.

| Claim | Status | Allowed wording |
| --- | --- | --- |
| Controlled edits change frames for a named reader on these ids | Allowed as a description of the frozen tables | Name the reader, the category, and the counts. The eight category labels occur 75 times each in the 600 rows. That balance is a label count, not equal severity and not a speech rate. |
| Prefix B0 and prefix B1 differ on the v1 list | Allowed | Exact frame 0/200 versus 1/200 on the prefix reader. |
| Prefix selection and forced lexical selection differ | Allowed | 1/200 versus 145/200. Say that the reader changes. Do not call it a candidate-count result. |
| Selective coverage and risk on the v1 list | Allowed | Coverage 145/200, risk 3/145, abstentions 55/200, correct commits 142/200 when abstention is scored wrong. |
| The two 145/200 figures | Allowed only if split | Forced exact frame is one. Selective coverage is the other. Equal counts do not mean the same utterances. |
| Recovery gain 0.71 | Allowed | 142/200 minus prefix B0’s 0/200 on these ids. |
| The three unsafe commits | Allowed | `utt-121`, `utt-124`, `utt-129`, closed-grammar times. |
| Derived action match | Allowed if labeled derived | Not a human gold action. |
| Simulated RETRY | Allowed if the mechanism is named | `simulated_candidate_rescore` commits a supplied list. A finished retry is correct only when the frame matches gold. |
| Deterministic rerun of the frozen files | Allowed as a statement that the files are the record | This phase did not recompute hashes. Do not add “hashes verified on this date” without a new check. |
| Real-world ASR robustness | Disallowed | |
| Speech recognition accuracy | Disallowed | Text-edit distance against the gold sentence is not this claim. |
| Real N-best performance | Disallowed | Provenance is `synthetic_edit`. |
| Production SLU performance | Disallowed | |
| Human conversational generalization | Disallowed | |
| Operational retry effectiveness | Disallowed | |
| A population beyond these 200 strings | Disallowed | No interval and no significance test is claimed. |

The earlier register in `docs/PHASE_1D2_RESEARCH_CLAIMS_REGISTER.md` remains in force where it is narrower. This matrix does not widen it.
