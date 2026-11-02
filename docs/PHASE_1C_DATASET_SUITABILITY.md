# Phase 1C dataset suitability

**Date:** 2026-11-02  
**Evidence:** Phase 1B validation, the development and held-out manifests, and the LibriSpeech reference texts. No ASR was run.

## What the repository shows

`dev-clean` and `test-clean` each have a reference transcript for every FLAC. The prepared samples have 200 development utterances and 200 held-out utterances. Audio is 16 kHz, mono, and decodable. Speaker and chapter identifiers are the official ID fields. The two samples share no speaker. None of the manifest columns is an intent or a slot.

The speech is read audiobook speech. A sentence can mention a person, a place, a number, or a negation without being a user request.

## Dimensions

| Dimension | Result | Basis |
|-----------|--------|-------|
| Audio availability | Directly supported for the prepared files. Every pilot candidate's FLAC is on disk. | Repository inspection. |
| Reference transcript | Directly supported. The text is the LibriSpeech transcript, not an ASR output. | Phase 1B manifests. |
| Speaker metadata | A speaker number is available. A name, role, or demographic attribute is not, and must not be inferred. | Utterance IDs. |
| Intent labels | Not available. | No such column exists. |
| Slot labels | Not available. | No such column exists. |
| Dialogue context | Not available. Each utterance is a separate read span. A pronoun often needs the book. | Corpus design and the sample text. |
| Speech style | Read speech. Not spontaneous conversation. | OpenSLR description and the recordings' source. |
| ASR evaluation | Supported after an ASR system is run. The reference text is the right gold for WER and CER. | Reference transcripts exist. ASR was not run. |
| SLU evaluation | Cannot be done directly for task intent or slots. Sentence-level properties can be annotated, and that annotation has not been done. | No gold intents or slots. |
| Recovery evaluation | CONTINUE, RETRY, CLARIFY, and HOLD cannot be scored against task success. They could later be studied only against a defined sentence-level label, which this phase does not have. | No recovery gold. |

## Recommended role

**Role C.** Keep LibriSpeech for acoustic conditions and transcript-error analysis. Use a separate task-oriented dataset before claiming anything about intent, slots, or recovery.

Role A is not supported. The corpus does not contain task requests as its annotation unit. Role B is the part of role C that LibriSpeech itself can carry: WER, CER, and, after human annotation, a small set of sentence-level properties. Role D is too strong. The audio and references are valid for transcription measurement. The hypothesis that LibriSpeech should stay for transcript-error analysis, with another dataset for SLU, matches this evidence.

## Consequences

Transcription metrics can be computed later on the fixed samples. Intent accuracy, slot F1, frame accuracy, and recovery success cannot be computed from LibriSpeech until a task schema is independently true of the utterances. Painting command labels onto these sentences would make those metrics look defined when the gold is invented.

The held-out sample was not read for this assessment beyond confirming that its manifest exists and was not annotated.
