# Phase 1D.4 issues register

**Date:** 2026-11-02  
**Rule:** a finding is recorded here. The Phase 1D.3 documents were not changed. No frozen number was replaced.

| ID | Severity | Status | Finding | Proposed correction | Applied |
| --- | --- | --- | --- | --- | --- |
| I-1 | Clarification | Closed by inspection | The review question referred to a 142/200 forced-selection score with abstention counted wrong. The frozen field `accuracy_counting_abstention_as_incorrect.exact_frame_accuracy` is the selective layer: 142/200. Forced selection does not abstain. Its exact-frame field is 145/200. | None. The protocol already assigns 142/200 to the selective layer and 145/200 exact frames to forced selection. | No edit required. |
| I-2 | Minor wording | Open, not material | In `docs/PHASE_1D3_EXPERIMENTAL_PROTOCOL.md`, the v1 lexical row writes `b1_forced_lexical` 145/200 beside selective coverage 145/200. A reader can treat the two 145s as one measurement. | When that cell is next edited, write “forced exact frame 145/200” and “selective coverage 145/200”. | Not applied. This review does not edit the protocol. |
| I-3 | Minor wording | Open, not material | H3 says the selective rule has fewer unsafe commits than the forced rule. Forced selection has no `unsafe_commitment` field. Selective risk is defined only for CONTINUE and RETRY. | State the forced side as exact-frame mismatches on all 200 utterances. The frozen exact-frame numerator is 145, so the mismatch count is 200 − 145 = 55. Do not call 55/200 selective risk. | Not applied. The metric document already fixes the selective-risk denominator, so this does not contradict a stored result. |
| I-4 | Display | Closed | `docs/SIMULATION_EVAL_V3.md` and the protocol print recovery gain as 0.710. `experiments/sim-eval-v3/report.json` stores 0.71. | Keep citing 0.71, or 142/200 minus 0/200. | Not applied. The fraction is the same. |
| I-5 | Pointer | Open, outside the protocol | `docs/PHASE_1D_BLOCKERS.md` still says the next design step is Phase 1D.3. | Point that sentence at Phase 1D.4 when blockers are next updated. | Not applied. `docs/PHASE_1D3_BLOCKERS.md` already explains the older sentence. |

No issue is a numerical contradiction. I-2 and I-3 can be applied in a later documentation edit after this record. They are not required before the methodology is approved, and they were not made in this phase.

## Population check for 142 and 145

Counted from the existing v3b decision log, without rescoring:

| Quantity | Count |
| --- | --- |
| Rows | 200, ids `utt-000` through `utt-199` |
| CONTINUE | 145 |
| RETRY | 0 |
| CLARIFY | 48 |
| HOLD | 7 |
| Commits whose stored `frame_matches_reference` is true | 142 |
| Commits whose stored `frame_matches_reference` is false | 3 |
| Abstentions with `unsafe_decision` true | 0 |
| Unsafe ids | `utt-121`, `utt-124`, `utt-129` |

142 and 3 partition the 145 commits. The 142/200 rate uses that same id set and scores the other 55 utterances as incorrect. Coverage 145/200 uses that same id set and does not apply the gold-frame test. The gold-frame test is what separates the 142 from the 3.
