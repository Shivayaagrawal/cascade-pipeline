# Phase 1D.4 protocol review

**Date:** 2026-11-02  
**Requested at:** 17:39 +05:30.  
**Object of review:** the eight Phase 1D.3 documents.  
**Result:** the protocol is approved as a methodology. Approval does not acquire a dataset and does not authorize implementation.  
**Phase 1D.3 files:** not edited.

The check below reads the frozen reports and the scoring functions those reports name. It does not rerun an experiment and does not replace a stored number.

## Review A. Research questions

RQ1 through RQ4 each name a scope, an independent variable, a dependent variable, a comparison, a metric, and a limitation. The hypotheses say what would reject them. They are not written as findings.

| Question | Answerable on the frozen sample | Not answerable now |
| --- | --- | --- |
| RQ1 | Lexical reader, written edits, same 200 ids, against the gold-transcript oracle. | Speech. The prefix reader does not have the same category table. |
| RQ2 | Prefix reader only: rank-0 exact frame 0/200 versus list exact frame 1/200. | A same-reader lexical test of candidate count. The frozen lexical 145/200 changes the reader. N-best lists. |
| RQ3 | Selective coverage, selective risk, and the abstention column on the v1 list, including `min_support` 1, 2, and 3. | A support chosen on a held-out speech split. |
| RQ4 | Derived actions and `simulated_candidate_rescore` on named written bundles. | Human action labels. A second decode. |

Those limits are already stated in `docs/PHASE_1D3_RESEARCH_QUESTIONS.md`. They are scope, not defects.

## Review B. Comparisons

| Comparison | Verdict |
| --- | --- |
| Prefix B0, B1, and B2 on the v1 injector list | Valid. One reader family, one id set, one gold set. B0 sees the rank-0 string. B1 sees the three written variants. |
| Prefix B1 exact frame 1/200 versus forced lexical 145/200 | A reader change on the same strings. The protocol forbids reading it as a pure candidate-count gain. |
| Forced lexical selection versus the v3 selective layer | Valid as a commit-rule comparison on one reader. Forced always returns a frame. Selective can abstain. |
| Prefix controller versus v3 recovery | The protocol keeps them in separate columns. Pooling is not allowed. |

No comparison in the protocol is labelled as a candidate-count result when the reader also changes.

## Review C. Metrics and the 142/200 check

Source: `experiments/sim-eval-v3/report.json`, object `selector_comparison.v1_injector`, and the same counts in `experiments/sim-eval-v3b/report.json`. The v3b decision log has one row for each of `utt-000` through `utt-199`.

| Stored field | Numerator | Denominator | What it is |
| --- | --- | --- | --- |
| `decision_coverage` | 145 | 200 | CONTINUE 145 and RETRY 0. |
| `selective_risk` | 3 | 145 | Frame mismatches among those commits. |
| `unsafe_commitment` | 3 | 145 | Same numerator and same denominator as selective risk. |
| `accuracy_on_committed_decisions.exact_frame_accuracy` | 142 | 145 | Commits whose frame matches gold. |
| `accuracy_counting_abstention_as_incorrect.exact_frame_accuracy` | 142 | 200 | Those 142 matches, with each abstention scored incorrect. |
| `forced_slot_aware_selector.exact_frame_accuracy` | 145 | 200 | Forced selection. This selector does not abstain. |
| `recovery_gain_over_b0.value` |  |  | Stored value 0.71, equal to 142/200 minus 0/200. |

The 142/200 figure is the selective layer with abstention counted wrong. It is not a forced-selection score. Forced selection’s exact-frame count is the other 145/200. Coverage is also 145/200, and it counts commits rather than exact frames. Equal numerators do not make those two 145s the same measurement. The report does not list the forced selector’s successful ids, so this review does not claim they are the same utterances as the 145 commits.

Inside the selective layer the identity holds on the stored fields and on the decision log:

- 142 correct commits plus 3 unsafe commits equals 145 commits.
- The 3 unsafe ids are `utt-121`, `utt-124`, and `utt-129`.
- All 55 CLARIFY and HOLD rows are marked not unsafe.
- The gold-frame test for the 142 and for the 3 is the stored `frame_matches_reference` flag, which the v3 scorer sets with `frames_equal`.

Zero commits leave selective risk undefined. The v1-list always-HOLD point stores `selective_risk.value` as null and denominator 0. The slot-removed and split lists do the same. Abstention is an error only in the all-utterance exact-frame column. It is outside the risk fraction.

Empty gold slots and an empty prediction contribute one matched pair-set in micro slot scoring. The abstention column has 154 matched pairs against 152 on the committed-only column. The two extra matches agree with that empty-pair rule. They are not a second definition of an exact frame.

WER and CER remain the frozen synthetic prefix counts. No LibriSpeech hypothesis is scored. v3b `asr_latency` is false. Its timing is lexical processing.

The prose in `docs/SIMULATION_EVAL_V3.md` prints recovery gain as 0.710. The stored JSON value is 0.71. Both equal 142/200 − 0/200. This is display precision, not a different result.

## Review D. Recovery

The protocol separates four label sources. Derived `expected_recovery` is an evaluation rule. No human action label exists. A simulated RETRY is correct only when the committed frame matches gold. The second-bundle condition stores RETRY 198, exact frame among those commits 198/198, and mechanism `simulated_candidate_rescore`. The v1 list stores RETRY 0. Action accuracy 192/200 is derived agreement. Annotator agreement is not claimed.

## Review E. Statistics

Rates in the protocol are tied to numerators and denominators. Risk appears with coverage. The `min_support` curve remains 145/200 with 3/145, 74/200 with 0/74, and 8/200 with 0/8, plus always-HOLD with risk undefined. Category tables are marked exploratory. No confidence interval and no significance test is reported as computed. The 200 utterances are one synthetic seed, not a speech population.

## Review F. Reproducibility

The protocol names seed 17, the immutable directories, a new directory for later work, the SHA-256 manifest, `test-clean` isolation, and future decoder and licence records. The integrity commands in `docs/PHASE_1D4_APPROVAL_RECORD.md` matched that manifest. The only archive files found under `data/` are `data/librispeech/archives/dev-clean.tar.gz` and `data/librispeech/archives/test-clean.tar.gz`. Their contents were not opened.

`docs/PHASE_1D_BLOCKERS.md` still names Phase 1D.3 as the next design step. `docs/PHASE_1D3_BLOCKERS.md` already records that sentence as historical. It is a pointer, not a contradiction in the metric or comparison rules.
