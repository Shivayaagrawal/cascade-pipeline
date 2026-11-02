# Phase 1D.7 evaluation contract

**Date:** 2026-11-02  
**Status:** the Phase 1D.3 formulas, restated for the five identities. No historical number is redefined.  
**Authority:** `docs/PHASE_1D3_METRIC_DEFINITIONS.md` and `experiments/sim-eval-v3/report.json` for the v1-list figures below.

If a denominator is zero, the rate is undefined. It is not stored as zero. No confidence interval and no significance test is part of this contract. The 200 ids are the whole evaluation set, not a sample of speakers.

## Formulas

| Metric | Numerator | Denominator | Abstention |
| --- | --- | --- | --- |
| Intent accuracy | Utterances whose predicted intent string equals the gold intent. | Scored utterances. | A null intent is incorrect. |
| Slot precision | Matched `(name, value)` pairs after casefold. | Predicted pairs. | An empty prediction adds pairs only under the micro rule below. |
| Slot recall | Matched pairs. | Reference pairs. | A missing gold pair is a miss. |
| Slot F1 | Harmonic mean. | Both rates. If both are zero, F1 is 0. If either denominator is zero, F1 is undefined. | The all-utterance column and the committed-only column are different. |
| Exact frame | `frames_equal`: intent and the slot pair sets. | Scored utterances, unless the column says “among commits”. | Incorrect in the all-utterance column. |
| Candidate coverage | Utterances whose list still contains the gold intent cue and every gold slot value in one candidate. | Utterances. The gold sentence is not added. | Does not read the decision. |
| Selective coverage | CONTINUE + RETRY. | All utterances. | CLARIFY and HOLD stay in the denominator and outside the numerator. |
| Selective risk | Committed frames that fail `frames_equal`. | CONTINUE + RETRY. | Outside both counts. Zero commits leave the rate undefined. |
| Unsafe commits | The same numerator and denominator as selective risk for `b2_lexical_v3`. | Commits. | Not unsafe. |
| Recovery action accuracy | Actions equal to derived `expected_recovery`. | All utterances. | Can match a derived CLARIFY or HOLD. The label is derived, not human. |
| Recovery gain | Exact-frame rate of correct commits over all utterances, minus prefix B0’s exact-frame rate on the same ids. | Both rates use all utterances. | Abstention counts as not correct in the achieved rate. |

Micro slot scoring adds one matched pair, one predicted pair, and one reference pair when both sides are empty.

## Frozen v1-list figures

These are `b2_lexical_v3` at `min_support` 1 with no second bundle, except the forced-frame row.

| Measure | Figure | What it is |
| --- | --- | --- |
| Selective coverage | 145/200 | Commits. CONTINUE 145, RETRY 0. |
| Correct commits, abstention scored wrong | 142/200 | The 142 commits whose frame matches gold. The other 55 utterances are scored incorrect. |
| Exact frame among commits | 142/145 | Those matches over the commits only. |
| Unsafe commits and selective risk | 3/145 | The other commits. Ids `utt-121`, `utt-124`, `utt-129`. |
| Abstentions | 55/200 | CLARIFY 48 and HOLD 7. Not unsafe. |
| Recovery gain | 0.71 | 142/200 minus prefix B0 exact frame 0/200. |
| Forced exact frame | 145/200 | `b1_forced_lexical`. Always answers. |

Forced exact frame 145/200 and selective coverage 145/200 share a numerator only as a count. The report does not list the forced selector’s successful ids, so the two 145s do not establish that the same utterances were selected. The 142 and the 3 do partition the 145 lexical commits, because those three numbers come from one selective run.

Prefix B1 exact frame on this list is 1/200. That comparison changes the reader relative to the forced lexical 145/200.

Text WER against the gold sentence is optional and is not speech WER. The historical prefix WER figures stay in `docs/SIMULATION_RESULTS.md`. They are not recomputed here.
