# Phase 1D research design

**Date:** 2026-11-02  
**Dataset selected for acquisition:** none.  
**Conditional design, if SLURP real audio and the pinned text are later authorized and a storage decision makes the archive fit:** the notes below. They are not permission to train or decode.

Synthetic v3 and v3b stay closed-grammar text experiments. Their 145/200 coverage and 3/145 selective risk are not real-speech results. v3b’s timing is lexical processing, not ASR latency. LibriSpeech remains the read-speech transcription resource. It does not supply the frames this design needs.

## B0

B0 is one ASR hypothesis, then NLU, then the predicted scenario, action, and entities. The reference transcript supports WER and CER. The gold scenario, action, and entity spans support intent accuracy, slot precision, recall, and F1, and exact frame match. The dataset `wer` field in SLURP is an earlier automatic score. It is not this project’s ASR output and must not be reported as one.

LibriSpeech can host a transcript-only B0 for WER and CER. That experiment must not be labelled intent or slot evaluation.

## B1

B1 runs NLU on each hypothesis and compares the resulting frames. The gold frame is the comparison target. Candidates produced by a recognizer need a provenance label such as `primary_asr`, `beam_hypothesis`, or `independent_decode`. Edited strings remain `synthetic_edit` and are not pooled with decoder hypotheses. The gold sentence stays out of the candidate list, as in the synthetic protocol.

SLURP’s entity spans make a wrong hypothesis visible when a time, name, or quantity changes. Fluent Speech Commands can support the same diagram only for `action`, `object`, and `location`. That narrower frame should not be described as the same semantic task.

## B2

The controller can CONTINUE when one complete frame is supported, CLARIFY when a required entity is missing or disputed, and HOLD when the intent evidence is absent. RETRY is a new decode or a supplied second bundle, and it is correct only when the frame it commits matches gold. A completed RETRY is not automatically correct. That rule is already required by the synthetic track.

No dataset in this review labels the four actions. Action accuracy against a gold action is therefore not available. What can be reported, after a real decode, is:

| Quantity | Denominator |
| --- | --- |
| Frame match on CONTINUE and successful RETRY commits | Committed utterances |
| Selective risk | Errors among those commits. Zero commits make the rate undefined, not zero. |
| Exact frame over all utterances | All utterances in the split. Abstention counts as not an exact frame. |
| Coverage | Utterances that received CONTINUE or RETRY, over all utterances |
| Slot precision | Matched slot pairs over predicted slot pairs |
| Slot recall | Matched slot pairs over reference slot pairs |

CLARIFY precision can be reported only after a development protocol defines when gold says clarification was required. That protocol is not in the dataset.

## Negation and uncertainty

The v3 reader does not return negation or uncertainty. v3b recorded both as unavailable. SLURP’s published example shows a `time` entity, and Timers and Such is built from numeric slots. Neither source was counted for negation, uncertainty, contradiction, or context-dependent reference. A later annotation layer has to listen. Text inspection is not that layer.

Publishing `usrid` gender or native-language codes is out of scope even if the text licence is later accepted.

## Splits and statistics

Official SLURP `train`, `devel`, and `test` files are the splits. `test` is sealed before threshold or model choices. Speaker overlap is measured before any speaker-independent claim. The paper’s 72,277 and the Table 6 sum of 72,396 are both recorded and not averaged.

Development estimates use `devel` only. A single pilot does not support a confidence interval for the full corpus. Agreement requires two independent annotators and is not computed from one reviewer’s notes.

## What this design cannot claim

It cannot claim that selective recovery improves real-world semantic reliability. That claim waits for an authorized real-speech set, an actual decode, and a held-out test that was not used to choose the system. Phase 1D does not start Phase 1E, Phase 2, or the B0/B1/B2 implementation.
