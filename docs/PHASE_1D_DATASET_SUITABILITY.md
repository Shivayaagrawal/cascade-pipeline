# Phase 1D dataset suitability

**Date:** 2026-11-02  
**Recommendation:** do not acquire a new dataset.  
**Conditional technical preference, if a later owner decision and a storage decision allow it:** SLURP real audio plus the pinned textual release. That preference is not authorization.

The scores are in `docs/PHASE_1D_DATASET_COMPARISON.md`. Legal status is in `docs/PHASE_1D_LICENSING_REGISTER.md`. A higher technical score does not override a licence that the owner has not accepted.

## What the research needs

B0 needs audio, a reference transcript, and a semantic frame. B1 needs the same frame so that more than one transcript hypothesis can be scored against one gold meaning. B2 needs that frame in order to decide whether CONTINUE was safe. RETRY, CLARIFY, and HOLD are controller actions. None of the candidate releases contains gold labels for those four actions.

A correct CONTINUE can be checked when the committed intent and slots match the dataset’s gold frame. A correct HOLD or CLARIFY cannot be checked against a follow-up turn, because these releases are single-turn. A correct RETRY cannot be checked against a second official recording of the same request. Any later protocol for CLARIFY or RETRY has to be written and labelled on development data. It cannot be inferred from the fact that an utterance is short or ambiguous.

## B0

| Dataset | Single-best ASR against a reference | Intent and slot scoring |
| --- | --- | --- |
| LibriSpeech prepared splits | Supported for WER and CER | Not supported. No intent or slot gold. |
| SLURP | Supported if the real audio and the `sentence` field are both acquired | Supported by scenario, action, and entity spans |
| Fluent Speech Commands | Supported by the paper’s transcription column | Supported only for the three slots whose combination the paper calls an intent |
| Timers and Such | Supported for the 2,151 real utterances | Supported for four numeric intents |
| Sonos / Snips | Supported only for queries that have recordings. SmartSpeaker training audio is absent. | Supported for the listed intents and slots |
| STOP | Supported by the spoken-form transcript | Supported by the semantic parse, as exact match |

## B1

Every candidate that has one gold frame can score several ASR hypotheses for that utterance. None of them publishes an official N-best list from a recognizer. A multi-candidate experiment would have to come from a decoder run after acquisition. Manufacturing extra transcripts, as the synthetic track does, would remain a synthetic condition and would have to keep the `synthetic_edit` provenance.

SLURP is the strongest B1 candidate because one sentence can contain several entity spans, and the paper’s own SLU-F1 metric is defined for entity errors after transcription mismatch. Fluent Speech Commands can score three slots, but the paper treats the task as classification over 31 combinations of a small phrase list. That is a weaker test of whether a wrong hypothesis preserves a slot value.

## B2

| Action | What the datasets support | What they do not support |
| --- | --- | --- |
| CONTINUE | A commit can be marked correct when its frame matches dataset gold. | They do not say whether the speaker wanted the system to act. |
| RETRY | A second decode can be compared with the same gold frame. | There is no gold label that the proper action was RETRY, and no second conversational recording. |
| CLARIFY | A missing or disputed slot can be detected from the gold frame. | There is no follow-up answer to score. |
| HOLD | Abstention can be reported with coverage, as in the synthetic track. | Abstention is not a published label. Selective risk still has to be defined as error among commits. |

SLURP can support that B2 protocol because the gold frame is scenario, action, and entities. Timers and Such can support it for numbers, which is the failure mode the synthetic v3 log already shows on reminder times. Fluent Speech Commands can support a three-slot frame and little else. STOP could support a stricter exact-parse frame, but its licence text was not found. LibriSpeech cannot support B2 semantic recovery.

## Why SLURP is the conditional preference

The EMNLP 2020 paper and the pinned repository show real speech, gold sentences, 18 scenarios, 46 actions, and entity spans. The Zenodo record pins version 1.0, the two archive names, and their MD5 values. The repository separates official `train`, `devel`, and `test` files. The published README example, “wake me up at eight o'clock”, has entity type `time`, so temporal entity labels exist in the schema.

That is the best match to B0, B1, and B2 among the sources read in this pass. It is still blocked. The owner has not accepted CC BY-NC 4.0 for the audio or CC BY 4.0 for the text. The real archive does not fit in the remaining 3,569,732,592 bytes. Synthetic audio should stay a separate condition if a later plan acquires anything at all.

## Why the others are not the preference

Fluent Speech Commands has speaker-disjoint splits and clear transcript and slot columns. The publisher page and the Public License PDF do not grant the same rights. Until the bundle’s own licence file is read, it cannot be selected.

Timers and Such is the right stress test for numbers, and its real subset is small enough to annotate by listening. The published zip is 13,133,746,587 bytes. The paper calls the licence CC0, and the Zenodo record’s licence id is `other-open`, with no licence file. Those two statements are not the same instrument.

The Sonos sets have an official audio description and a licence that was read. The large English assistant does not include training recordings. Access depends on a form. No checksum was published on the page that was read.

STOP is the largest spoken semantic-parsing set in this comparison, and the paper says speakers do not cross splits. The repository licence is `Other`, and no grant was read. Its 218 hours were not paired with an archive size. It cannot be recommended.

LibriSpeech remains the transcription resource already in the project. It is not a substitute for a task-oriented set. The 30-row Phase 1C pilot is still `not_annotated`.

## Annotation that would still be required

SLURP already has scenario, action, entity, and sentence labels. Those are dataset labels, not labels created by this project. A later development pilot would still listen to audio. The paper’s filter used ASR word error, which is not human listening.

This pass does not set a completed annotation count. A defensible first pilot, after authorization, is the same shape as Phase 1C: a small development sample, two independent listeners, and adjudication. The hours required are unknown until that trial is timed. No agreement statistic exists.

Negation and uncertainty are not dataset fields in the sources read here. If they are required, they need a new annotation layer on development audio. They must not be filled from the sentence text without listening, and they must not be counted as present merely because a command could in principle contain “not”.

## Mandatory checks that fail today

| Check | Result |
| --- | --- |
| Audio and reference transcript for WER and CER | Met by LibriSpeech now. Met by SLURP only on paper. |
| Intent and slot gold | Absent for LibriSpeech. Present in the SLURP, FSC, Timers and Such, Sonos, and STOP descriptions. |
| Exact frame comparison | Possible for those task sets. Not possible for LibriSpeech. |
| Multi-hypothesis transcripts | Not supplied by any candidate. |
| Recovery-action gold | Not supplied by any candidate. |
| Licence accepted for a new dataset | Not met. |
| Fits the remaining cap | Not met for any verified task-oriented audio archive. |
