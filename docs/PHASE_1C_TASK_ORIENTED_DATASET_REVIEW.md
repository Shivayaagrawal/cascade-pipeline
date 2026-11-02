# Phase 1C task-oriented dataset review

**Date:** 2026-11-02  
**No dataset was downloaded. No licence was accepted. D-LS-001 was not changed.**

Facts below are taken from `docs/DATASET_LICENSE_REGISTER.md` unless a cell says the count was not re-verified. Utterance and speaker totals are omitted where this pass did not recount them.

## LibriSpeech

Audio and reference transcripts exist locally for the two prepared splits. Intent and slot labels do not. Speech is read. CC BY 4.0 is accepted for those two archives only. It can support WER and CER. It cannot by itself support intent, slot, or recovery metrics.

## Fluent Speech Commands

| Dimension | Evidence |
|-----------|----------|
| Audio | The publisher describes a spoken-command corpus. No archive is local. The author data link timed out on 2026-11-02. |
| Transcripts, intents, slots | The corpus is built as command utterances with slot structure. This pass did not open a bundle, so the column names are not re-copied here. |
| Speakers and splits | Not re-counted. The release identity and checksum are unknown. |
| Style and domain | Prompted smart-home commands, not audiobook reading. |
| Licence | The publisher page says CC BY-NC-ND 4.0. The linked PDF is the Fluent Speech Commands Public License. Both were read on 2026-11-02. They disagree on sharing and on whether training and testing are allowed. |
| Access | A Google Group, not a pinned archive URL. |
| Owner decision | Pending. Not Refused. Acquisition stays blocked. |
| B0/B1/B2 | The task design could support them if a governed bundle were obtained. The licence conflict means it cannot be selected now. |

## SLURP

| Dimension | Evidence |
|-----------|----------|
| Audio | Zenodo version 1.0, DOI 10.5281/zenodo.4274930, has `slurp_real.tar.gz` and `slurp_synth.tar.gz`. Neither was downloaded. The record prints their MD5 values and sizes. |
| Text | GitHub commit `8eb16545762be97ace75334109d73824217311f1` states CC BY 4.0 for the textual part. That commit was not cloned. |
| Intent and slots | The resource is a spoken-language-understanding corpus with scenario labels. The files that hold the labels were not opened in this pass. |
| Speakers | The README describes a `usrid` field that encodes gender and whether English is native. Those attributes are not to be published. The metadata file was not downloaded. |
| Style and domain | Prompted assistant commands, including close and distant recording conditions named in the project record. Not read audiobook speech. |
| Licence | Audio: CC BY-NC 4.0, from Zenodo `LICENSE.txt` fetched 2026-11-02. Text: CC BY 4.0 at the pinned commit. The owner has not accepted either. |
| Scale | Not re-counted here. |
| B0/B1/B2 | The label design matches task-oriented SLU. Use is blocked until the owner accepts the audio licence and decides whether synthetic audio is in scope. |

## SNIPS

This pass did not re-fetch a SNIPS release. The widely cited SNIPS benchmark is a text intent-and-slot corpus. An official audio release was not verified. It is not a candidate for acquisition in this phase. No licence conclusion is drawn.

## Common Voice

The pending English scripted-speech record has read prompts, not task intents or slots. It would not fill the SLU gap. Its owner decision remains Pending.

## Recommendation

Pause before adding a second dataset. Keep LibriSpeech for the transcription track. Do not replace it, and do not treat it as the SLU corpus.

The research design still wants a task-oriented track. SLURP is the clearer candidate of the two reviewed audio corpora because the audio licence is a single CC BY-NC 4.0 text rather than two conflicting instruments. That is not authorization to download it. Fluent Speech Commands stays blocked until the page licence and the PDF are reconciled against an actual bundle. The owner would have to accept the applicable licence, choose real audio rather than synthetic audio, and approve a storage plan before any acquisition.
