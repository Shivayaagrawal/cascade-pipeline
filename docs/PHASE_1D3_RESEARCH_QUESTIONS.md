# Phase 1D.3 research questions

**Date:** 2026-11-02  
**Status:** protocol. No new experiment was run.  
**Scope of any current answer:** the closed synthetic grammar, utterance ids `utt-000` through `utt-199`, seed 17.

These questions are tests. A result that rejects a hypothesis stays in the report. Frozen counts from v1, v2, v3, and v3b are observations of this sample. They do not confirm a hypothesis about speech, about another grammar, or about a recognizer’s N-best list.

The questions are narrower than `docs/RESEARCH_QUESTIONS.md`, which still names a future speech dataset. This file is the protocol for what can be claimed from the assets that exist. Ruan et al., Interspeech 2020, used 1-best Amazon Transcribe hypotheses and a matched-entity slot score. Cascade Pipeline does not reproduce that paper. Its primary slot score keeps pairs that an ASR error would have removed.

## Systems under comparison

| Name | What it does | Input it actually sees |
| --- | --- | --- |
| `b0_prefix` | Prefix parser on one transcript | Rank-0 string of the named list |
| `b1_prefix` | Prefix parser, then `select_candidate` | Every string in the named list |
| `b1_forced_lexical` | Lexical reader, then `forced_selection` | Every string in the named list. Always returns one frame. |
| `b2_prefix_controller` | Frozen `decide()` on prefix scores | One-best plus the other written candidates |
| `b2_lexical_v3` | `decide_selective` and `recovery_action` | The primary bundle, and a second bundle only when the condition supplies one |

`b1_prefix` and `b1_forced_lexical` are different readers. A gain that appears only when the reader changes is a reader result. `b2_prefix_controller` and `b2_lexical_v3` are different action rules. Their action counts are not pooled.

## RQ1. Transcript corruption and frame extraction

**Question.** How does transcript corruption affect semantic frame extraction in the existing closed-grammar synthetic setting?

| Item | Definition |
| --- | --- |
| Independent variable | Corruption condition applied to the written sentence: the gold sentence alone, or one named edit category. |
| Dependent variables | Intent accuracy, slot micro-F1, exact-frame accuracy, under the formulas in `docs/PHASE_1D3_METRIC_DEFINITIONS.md`. |
| Controlled variables | Seed 17, the 200 ids, the named reader, the synthetic gold frame, and exclusion of the gold sentence from ordinary candidate lists. |
| Comparison groups | Gold-transcript oracle versus each corruption condition, scored by the same reader. |
| Evaluation metric | Exact-frame accuracy is primary. Intent accuracy and slot micro-F1 are reported with it. |
| Required evidence | Paired counts on the same ids, with the reader named. |
| Current limitation | The edits are written. The lexical reader’s category tables are in `docs/SIMULATION_EVAL_V3.md`. Negation is an edit category, and the reader does not return a negation finding, so a frame can still match after “not” is inserted. Rank-0 category cells have 25 utterances. |

**H1.** For a fixed reader, a condition that removes or replaces a gold slot token has a higher exact-frame error than the gold-transcript oracle on these ids.

H1 is rejected for that reader if the corrupted condition’s exact-frame error is not higher. The v3 tables are one observation of this grammar. They are not a measurement of how often those edits occur in speech.

## RQ2. Proxy candidates and selection

**Question.** Can multiple proxy transcript candidates improve semantic selection compared with the single-transcript baseline?

| Item | Definition |
| --- | --- |
| Independent variable | One transcript versus a named proxy list, with the reader held fixed. |
| Dependent variables | Exact-frame accuracy, intent accuracy, slot micro-F1. |
| Controlled variables | Same ids, same gold frames, same candidate budget inside the comparison, gold sentence excluded. |
| Comparison groups | `b0_prefix` versus `b1_prefix` on the v1 injector list. Separately, `b1_forced_lexical` on a named list versus the same lexical reader on the rank-0 string only, if that single-string lexical count is computed later. The frozen 145/200 figure is the forced lexical selector on the full v1 list. It is not the prefix comparison. |
| Evaluation metric | Exact-frame accuracy. The forced selector always answers, so abstention is not part of this question. |
| Required evidence | The reader, the list, and the candidate count, stated together. |
| Current limitation | Every current candidate has provenance `synthetic_edit`. A gain on these lists does not estimate N-best selection. Changing from the prefix reader to the lexical reader is not an estimate of adding candidates. |

**H2.** For a fixed reader and a named proxy list, selection over the list has higher exact-frame accuracy than the rank-0 transcript alone.

H2 is rejected for that reader and list if the list accuracy is not higher. A subset gain is reported with the subset rule. The frozen prefix comparison on the v1 list is exact frame 0/200 for B0 and 1/200 for B1. That pair uses one reader. The lexical forced count of 145/200 uses another reader and is not the test of H2.

## RQ3. Selective commitment

**Question.** Can selective commitment reduce unsafe semantic decisions, and what coverage cost does it introduce?

| Item | Definition |
| --- | --- |
| Independent variable | Commit rule: forced selection, or selective commitment at a stated `min_support`. |
| Dependent variables | Unsafe commits, selective coverage, selective risk. |
| Controlled variables | Same list, same lexical reader, same gold frames. `min_support` is 1, 2, or 3 and is named before the curve is interpreted. |
| Comparison groups | `b1_forced_lexical` versus `b2_lexical_v3` at each stated support. Always-HOLD is the zero-coverage end of the curve. |
| Evaluation metric | Selective risk among CONTINUE and RETRY, reported beside coverage. Exact-frame accuracy over all 200, with abstention counted incorrect, is a separate column. |
| Required evidence | Both the risk fraction and the coverage fraction. A missing risk denominator stays undefined. |
| Current limitation | On the v1 list the selective layer commits 145/200 with selective risk 3/145. The three errors are reminder times that are still legal grammar values. Agreement with another wrong legal value is not detected. Support 2 was not a threshold chosen on a held-out split. |

**H3.** On a fixed list, the selective rule has fewer unsafe commits than the forced rule, and the coverage at that rule is reported in the same table.

H3 is rejected if the unsafe-commit count does not fall, or if the fall is produced by changing the denominator. Coverage is reported when the count falls and when it does not. The forced selector’s 145/200 exact frames are a different quantity from the selective layer’s 142/200 exact frames with abstention counted wrong.

## RQ4. Recovery actions under simulation

**Question.** How do recovery actions behave under the existing simulated conditions?

| Item | Definition |
| --- | --- |
| Independent variable | Controller identity, and whether a second written bundle is supplied. |
| Dependent variables | Counts of CONTINUE, RETRY, CLARIFY, and HOLD; derived action accuracy; recovery gain; selective risk on the commits. |
| Controlled variables | `expected_recovery` is computed from the gold frame and the strings before the decision is read. Gold is not an input to either controller. |
| Comparison groups | `b2_prefix_controller` on the v1 cascade, reported from the frozen v2 record. Separately, `b2_lexical_v3` on a named primary bundle, with and without a named second bundle. |
| Evaluation metric | Derived action accuracy over all utterances, plus selective risk on commits. A human gold action is not available, so this accuracy is not a gold-action score. |
| Required evidence | The mechanism string on every RETRY. The only current mechanism is `simulated_candidate_rescore`. |
| Current limitation | The v1 list produces RETRY 0. The published second-bundle condition produces 198 simulated retries. A finished retry is a commit of the second bundle. It matches gold only when the committed frame equals the gold frame. |

**H4.** Supplying a second written bundle that still contains the gold frame increases the number of correct committed frames relative to the same primary bundle with no second bundle.

H4 is rejected for that pair of bundles if the count of correct commits does not rise. A rise under `simulated_candidate_rescore` describes the written bundles. It does not describe a second decode.

## What these questions do not ask

An end-to-end speech-to-intent model is outside this protocol. A candidate list with no provenance is outside it. A comparison of two systems on different utterance ids is outside it. LibriSpeech can host a later WER and CER question. It has no intent or slot gold, so it cannot answer RQ1 through RQ4.
