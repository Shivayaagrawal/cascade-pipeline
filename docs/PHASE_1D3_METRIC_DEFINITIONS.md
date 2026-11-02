# Phase 1D.3 metric definitions

**Date:** 2026-11-02  
**Status:** the scoring rules for this protocol.  
**Source of the formulas:** the functions already used by the frozen reports. A formula is not changed to improve a published number.

`docs/METRIC_DEFINITIONS.md` remains the older general note. Where this file is more specific about a denominator, this file is the Phase 1D.3 rule. Counts already published in `docs/SIMULATION_RESULTS.md` and `docs/SIMULATION_EVAL_V3.md` keep the denominators those reports used.

Normalization for WER and CER is `normalize()` in `textnorm.py`: Unicode NFC, casefold, collapsed whitespace, punctuation kept on both sides. Intent equality is exact string equality. Slot names and values are casefolded, and values are stripped, before they are compared.

If a denominator is zero, the rate is undefined. It is not stored as zero.

## Intent accuracy

| Item | Rule |
| --- | --- |
| Formula | Correct utterances / scored utterances. |
| Numerator | Utterances whose predicted intent string equals the reference intent string. |
| Denominator | Scored utterances in the named condition. |
| Unit | Utterance. |
| Abstention | A null prediction is incorrect. It is not dropped. |
| Aggregation | Micro, one utterance one vote. Macro-F1 across intents is optional and is not the frozen headline. |
| Measurable now | Yes, on synthetic gold. Frozen prefix B0 0.310, B1 0.685, B2 0.565. |
| Real-speech evidence | A task-corpus gold intent and a hypothesis. LibriSpeech does not supply the gold intent. |

## Slot precision, recall, and F1

A slot instance is the pair `(name, value)` after casefolding.

| Item | Rule |
| --- | --- |
| Precision | Matched pairs / predicted pairs. |
| Recall | Matched pairs / reference pairs. |
| F1 | Harmonic mean. If precision and recall are both zero, F1 is 0. If either denominator is zero, that rate and F1 are undefined. |
| Empty both sides | Micro `slot_scores` adds one matched pair, one predicted pair, and one reference pair for that utterance. |
| Unit | Pair, pooled across utterances. This is micro-average. |
| Abstention | The published selective column that counts abstention as an empty prediction uses an empty slot dict for CLARIFY and HOLD. Committed-only slot scores use only CONTINUE and RETRY rows and are a different denominator. Both may be printed. They are not substitutes. |
| Macro | `per_slot_scores` can report each name. An utterance that has the slot on neither side is not a true positive for that name. Macro-F1 is the unweighted mean of those per-name F1 values when a report chooses to add it. The frozen comparison number is micro-F1, with pair counts. |
| Measurable now | Yes, synthetic. v3 publishes precision, recall, and F1, not F1 alone. |
| Real-speech evidence | Gold spans or gold pairs from the task release. The primary score does not drop a pair because an ASR error damaged the span. A matched-entity score would need its own name. |

Unsupported values sit in the predicted set and lower precision. Missing gold values sit in the reference set and lower recall.

## Exact semantic-frame accuracy

| Item | Rule |
| --- | --- |
| Formula | Utterances for which `frames_equal` is true / scored utterances. |
| Numerator | Intent matches and the slot pair sets match. Partial slot credit is not a match. |
| Denominator | Scored utterances. |
| Unit | Utterance. |
| Abstention | Incorrect in this rate. The selective report’s column is named `accuracy_counting_abstention_as_incorrect`. Exact frame among commits uses only committed rows and is a second rate. |
| Aggregation | Micro. |
| Measurable now | Yes, synthetic. Prefix B0 on the v1 first candidates is 0/200. Prefix B1 is 1/200. Forced lexical on that list is 145/200. Selective with abstention counted wrong is 142/200. |
| Real-speech evidence | Gold intent and gold slots for every scored utterance, plus a statement of which exact-frame column is used. |

## Candidate coverage

| Item | Rule |
| --- | --- |
| Formula | Utterances whose named list meets the stated containment test / utterances. |
| Numerator | For the v3 complete-frame oracle: at least one candidate for which the lexical reader preserves the gold intent and every gold slot value. Intent-cue coverage and slot-value coverage are separate numerators. |
| Denominator | Utterances in the condition. |
| Unit | Utterance. |
| Abstention | Not applicable. This metric does not read the decision. |
| Aggregation | Micro. |
| Measurable now | Yes, as a property of written lists. v1 lexical complete frame in one candidate: 147/200. |
| Real-speech evidence | A recognizer’s list. Coverage of written edits is string containment. |

The gold sentence is not added before this count.

## Selective coverage

| Item | Rule |
| --- | --- |
| Formula | Committed utterances / utterances. |
| Numerator | CONTINUE plus RETRY. CLARIFY and HOLD are outside the numerator. |
| Denominator | Utterances in the condition. |
| Unit | Utterance. |
| Abstention | The complement of coverage. It is not removed from the denominator. |
| Aggregation | Micro. |
| Measurable now | Yes, synthetic. v1 list, `min_support` 1: 145/200. |
| Real-speech evidence | The same commit rule, fixed before the test split is scored, on real hypotheses. |

## Selective risk

| Item | Rule |
| --- | --- |
| Formula | Unsafe commits / committed utterances. |
| Numerator | CONTINUE or RETRY decisions whose frame fails `frames_equal`. |
| Denominator | CONTINUE plus RETRY. When this count is zero, the rate is undefined. Refusing every input has no risk score. |
| Unit | Committed utterance. |
| Abstention | Excluded from both numerator and denominator. Abstention is not an error in this rate and is not a success. |
| Aggregation | Micro. |
| Measurable now | Yes, synthetic. v1 list: 3/145. The three ids are `utt-121`, `utt-124`, and `utt-129`. |
| Real-speech evidence | Gold frames on the committed speech utterances. |

The frozen v3 field `unsafe_commitment` uses this same numerator and this same denominator. A rate of unsafe commits over all utterances would be a new name. It is not the published 3/145.

## Unsafe commit rate

For the v3 lexical layer, unsafe commit rate is selective risk. Report the fraction and the counts.

The frozen v2 prefix-controller record uses its own published fraction, 112/113. That denominator is the commitment count in that report. It is not recomputed here and it is not pooled with 3/145.

| Item | Rule |
| --- | --- |
| Abstention | Not an unsafe commit. |
| Measurable now | Yes, inside each published system. |
| Real-speech evidence | Gold frames. A system that holds every utterance is not safe under this metric. Its risk is undefined and its HOLD rate is reported. |

## Recovery action accuracy

| Item | Rule |
| --- | --- |
| Formula | Utterances whose system action equals `expected_recovery` / utterances. |
| Numerator | Matches to the derived label. |
| Denominator | All utterances in the condition. |
| Unit | Utterance. |
| Abstention | CLARIFY and HOLD can match a derived CLARIFY or HOLD. They are not dropped. |
| Aggregation | Micro. |
| Measurable now | Yes, against the derived label. v3 v1 list: 192/200. v2 prefix controller: 88/200. |
| Real-speech evidence | Independently assigned human actions. The derived label does not become that evidence. |

`expected_recovery` does not read the decision. The order is: a primary candidate that preserves the gold frame expects CONTINUE; otherwise a supplied second list that preserves it expects RETRY; otherwise a missing gold slot, a split, or more than one intent cue expects CLARIFY; otherwise HOLD.

## Recovery gain

| Item | Rule |
| --- | --- |
| Formula | (Correct commits / all utterances) minus (B0 exact frames / all utterances). |
| Numerator | Not a single count. The value is a difference of two rates. |
| Denominator | Both rates use all utterances. Abstention counts as not correct in the achieved rate. |
| Unit | Utterance, paired. |
| Measurable now | Yes, synthetic, when the report names which B0 count it subtracts. v1-list gain uses prefix B0 exact frame 0/200. |
| Real-speech evidence | A speech B0 scored with the same exact-frame rule on the same ids. |

The v3 report states the v1-list gain as 0.710. That figure is 142/200 minus 0. It is not recomputed in this phase.

## WER

| Item | Rule |
| --- | --- |
| Formula | Word edits / reference words, after `normalize`, tokens split on whitespace. |
| Numerator | Sum of Levenshtein edit counts. |
| Denominator | Sum of reference-word lengths. An empty reference is counted in `excluded_empty_reference` and omitted from both sums. |
| Unit | Word, micro-averaged. Also report utterance count and reference-word count. |
| Abstention | Not applicable. |
| Measurable now | The function exists. Frozen synthetic prefix WER is published: B0 419/935, B1 289/935, B2 369/935. No LibriSpeech hypothesis has been scored. |
| Real-speech evidence | A decode and the official reference. Dataset fields named `wer` in an external release are that release’s earlier scores. |

## CER

| Item | Rule |
| --- | --- |
| Formula | Character edits / reference characters on the same normalized string. Spaces that survive normalization count as characters. |
| Numerator | Sum of character Levenshtein counts. |
| Denominator | Sum of reference character lengths. Empty references are excluded and counted. |
| Unit | Character, micro-averaged. |
| Abstention | Not applicable. |
| Measurable now | Frozen synthetic prefix CER uses 5,159 reference characters. No speech CER has been scored. |
| Real-speech evidence | Same as WER. CER stays secondary. |

## Processing latency

| Item | Rule |
| --- | --- |
| Formula | Elapsed seconds from `perf_counter` around the named calls. |
| Unit | One call, then mean, median, and p95 with the sample size. |
| Abstention | Not applicable. |
| Aggregation | The published v3b summary is lexical `assess` and `recovery_action` only. |
| Measurable now | Yes, as lexical wall time. `asr_latency` is false. v1 text-pipeline means exclude `say`. The 437.66 s v1 wall time is dominated by `say` and is not ASR latency. |
| Real-speech evidence | Timed decodes on the evaluation audio, with hardware, batch size, whether the first call is included, and the clock. |

## Clarification precision and recall

These sit beside the action metrics. Precision is CLARIFY decisions whose derived label is CLARIFY, divided by CLARIFY decisions. Recall is those matches divided by utterances whose derived label is CLARIFY. Either rate is undefined when its denominator is zero. On the v1 list the published values are precision 43/48 and recall 43/46. On the second-bundle condition precision is 0/2 and recall is undefined.

Human gold actions would replace the derived label. Until then the name of the metric stays “derived clarification precision” in any new prose.
