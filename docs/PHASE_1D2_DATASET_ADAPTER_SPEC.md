# Phase 1D.2 dataset adapter specification

**Date:** 2026-11-02  
**Status:** specification. No adapter code was added. SLURP was not downloaded.

The adapter runs only after the owner names a release, accepts its licence, and records a storage decision. This specification uses the SLURP facts already established in the Phase 1D documents. Fields that those documents mark `not_verified` stay unspecified.

## Audio ingestion

| Item | Rule |
| --- | --- |
| Authorized files | Only files named in the acquisition decision. The conditional SLURP target is `slurp_real.tar.gz`. `slurp_synth.tar.gz` stays out unless that decision names it. |
| Identity | Join a recording `file` name to one row. A headset file and a distant file are separate audio items. They are not two hypotheses of one decode. |
| Format | The pinned README says FLAC. Sample rate was `not_verified`. The adapter records the measured rate. It does not assume 16 kHz. |
| Check | MD5 of `slurp_real.tar.gz` must equal `9efc0f058ced47bf5131c7cb2cade513` and the size must equal 3,918,185,662 bytes before extraction. |
| Failure | A checksum mismatch, a path that escapes the extract directory, or a missing file stops the run. |

## Reference transcript

The text field established by the README example and the paper is `sentence`. The adapter copies it. It does not edit it to match a hypothesis. The automatic `wer` and `ent_wer` fields on a recording are the dataset’s earlier scores. They are not this project’s ASR output.

## Intent mapping

The established labels are `scenario`, `action`, and the example `intent` string `alarm_set`. The paper’s Table 4 reports 18 scenarios and 46 actions. The adapter stores scenario and action as the gold intent pair. It does not collapse them into the synthetic intent list in `data/schemas/intent_schema.json`. That list belongs to the local simulation.

## Entity and slot mapping

The README example has `entities` with a token `span` and a `type`. The example type is `time`. The paper’s introduction says 55 entity types and Table 4 says 56. The adapter keeps the type string from the file and does not choose between 55 and 56. A slot pair is the type plus the surface tokens in the span. Missing spans stay an empty list. An empty list means the file had no entities. It is not a project annotation.

## Splits

Use the official files `train.jsonl`, `devel.jsonl`, and `test.jsonl` at commit `8eb16545762be97ace75334109d73824217311f1`. Do not invent a split. Development and threshold checks read `train` and `devel` only. `test.jsonl` is hashed and then left unread until the final evaluation. Paper Table 6 and Table 2 disagree on the audio-file total, 72,396 against 72,277. The adapter reports the count it actually joins. It does not average the two figures.

## Speaker leakage

`usrid` exists. Whether the official splits are speaker-disjoint was `not_verified`. Before any speaker-independent claim, the adapter counts speakers that appear in more than one of train, devel, and test. `usrid` encodes gender and native-English status. Those attributes are not copied into reports, logs, or git.

## Licence and provenance

Each output record carries the release name, the Zenodo version 1.0 DOI for audio, the text commit, the audio licence CC BY-NC 4.0, and the text licence CC BY 4.0. Provenance of a hypothesis is `primary_asr`, `beam_hypothesis`, `independent_decode`, or `retry_decode` only when a recognizer produced it. Written edits stay `synthetic_edit`. The gold sentence is not inserted into the candidate list.

## Evaluation records

The adapter emits records that match `docs/PHASE_1D2_EVALUATION_CONTRACT.md`. `audio_decoded` is false until a decode runs. `reference_intent` and `reference_slots` come from the dataset file, not from a model. `uncertainty` and `negation` stay unavailable unless a later, separate annotation layer listens and records them. Recovery actions are system outputs. The dataset does not supply gold CONTINUE, RETRY, CLARIFY, or HOLD labels.

## Validation before any training or tuning

| Check | Stop if |
| --- | --- |
| Authorization | The decision record does not name this release and licence. |
| Storage | The projected archive, extraction, and working files exceed the cap then in force. |
| Join | An audio file has no sentence, or a sentence in the chosen split has no acquired audio. |
| Split isolation | A development routine reads `test.jsonl` or `test-clean`. |
| Synthetic pool | A SLURP row is scored as if it were `utt-000` through `utt-199`. |

LibriSpeech can use the same transcript and provenance fields for WER and CER. Its intent and slot fields remain unavailable. It does not enter the SLURP adapter.
