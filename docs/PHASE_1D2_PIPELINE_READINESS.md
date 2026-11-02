# Phase 1D.2 pipeline readiness

**Date:** 2026-11-02  
**Scope:** design and readiness. No new experimental behavior was added.

Two stacks already exist. They are not interchangeable.

| Stack | Entry | What it reads | Status |
| --- | --- | --- | --- |
| Frozen v1 cascade | `run_b0`, `run_b1`, `run_b2` | Prefix intent cues and slot extractor | Implemented on synthetic transcripts. Summaries are frozen. |
| v3 lexical layer | `assess`, `decide_selective`, `recovery_action` | Closed-grammar cues and lexicon values | Implemented and frozen as `sim-eval-v3`. v3b audits it. |

Neither stack calls a recognizer.

## B0

B0 is one transcript, then NLU, then one frame.

| Requirement | Current contract | Ready without a new dataset |
| --- | --- | --- |
| ASR interface | `ASRBackend.transcribe(audio_path) -> ASRResult`. The synthetic backend does not implement that method. It returns prewritten hypotheses through `transcribe_id`. | The interface is specified. A waveform call is not. |
| Transcript input | `Hypothesis(text, provenance, rank)`. B0 uses one hypothesis. | Yes, for an existing string. |
| NLU input | The hypothesis text. Gold intent and slots are not inputs. | Yes. |
| NLU output | `intent` or null, and a slot dictionary. Prefix path and lexical path can disagree. Report which path was used. | Yes, on the synthetic grammar. |
| Semantic evaluation | Compare the frame with the synthetic gold frame. | Yes, transcript-only, synthetic. |
| LibriSpeech | Reference text exists. Intent and slot gold do not. | WER/CER only after a real hypothesis exists. Not intent or slots. |

B0 on synthetic text is already measured and frozen. B0 on speech has not been run.

## B1

B1 compares more than one transcript for the same utterance.

| Requirement | Current contract | Ready without a new dataset |
| --- | --- | --- |
| Candidate input | A tuple of `Hypothesis`, or a list of strings in the v3 reader. | Yes, when the strings already exist. |
| Provenance | `synthetic_edit` for injector output. `reference_passthrough` is oracle-only. `native_nbest` is reserved for a list a recognizer actually returned. The synthetic path rejects `native_nbest`. | The distinction is enforced in code. No `native_nbest` list exists. |
| Ranking | v1 `select_candidate` prefers confidence, then earlier rank. v3 `forced_selection` prefers one intent, then more filled critical slots, then earlier order. The selective layer commits only when one complete frame has enough agreement. | Yes, as separate reported conditions. |
| Disagreement | v3 records intent disagreement and slot-value disagreement. Confidence in the prefix path is 0, 0.5, or 1. The lexical path uses a support count. | Yes, on synthetic lists. |
| Proxy versus N-best | The 600 edits, paraphrases, slot-removed lists, and split lists are proxy candidates. | Proxy tests are done. Genuine N-best tests are not possible. |
| Evaluation | Frozen B1 exact frame on the v1 list is 1/200. v3 forced exact frame on that list is 145/200 and always answers. Those are not safety results. | Report them as frozen synthetic results. Do not rerun the writers. |

## B2

B2 chooses CONTINUE, RETRY, CLARIFY, or HOLD.

| Requirement | Frozen v1 controller | v3 layer |
| --- | --- | --- |
| Failure categories | `none`, `ambiguous`, `unknown`, `low_confidence` from the prefix score | Missing critical slot, multiple intents, slot disagreement, support below `min_support`, no intent evidence |
| Risk inputs | Confidence and the ambiguity flag. Gold is not an input. | Evidence from `assess()`. Gold is used only when scoring. |
| CONTINUE | Prefix failure is `none` | Selective action commits on the primary bundle |
| RETRY | One alternative with higher confidence and no failure. It is not a second decode. | Returned only when the caller supplies a second bundle that can commit. Label: `simulated_candidate_rescore`. |
| CLARIFY | The chosen parse is ambiguous | Intent without required slots, or slot values disagree |
| HOLD | No usable alternative | No intent evidence, or intent disagreement across complete frames |
| Safety | v2 records the frozen controller’s unsafe-commitment rate. Thresholds were not tuned. | Unsafe commits are frame mismatches among CONTINUE and RETRY. Abstention is not an unsafe commit. The v1 list has three unsafe reminder-time commits. |
| Expected action | Assigned by the evaluator from the gold frame and the strings, not from the decision | Same rule, documented in `expected_recovery` |

What can be tested now is this synthetic contract. What cannot be tested is whether those actions help a person in a spoken task. No dataset in the project, and none of the Phase 1D candidates, supplies gold labels for the four actions.

## Readiness summary

| Pipeline | Synthetic transcript path | Real task speech |
| --- | --- | --- |
| B0 | Implemented and frozen | Not run. LibriSpeech can support WER/CER later. It cannot support intent or slots. |
| B1 | Implemented for proxy candidates and frozen | Blocked. No recognizer N-best list exists. |
| B2 | Implemented as two separate contracts and frozen | Blocked. No task speech and no gold recovery labels. |

Phase 1D.2 does not add a third controller and does not retune either existing one.
