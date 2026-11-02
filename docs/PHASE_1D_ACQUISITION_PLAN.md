# Phase 1D acquisition plan

**Date:** 2026-11-02  
**Status:** not executable.  
**This document does not authorize a download, an extraction, or a request form.**

No new dataset is recommended for acquisition. The conditional target, after a separate owner decision and a separate storage decision, is SLURP real audio plus the pinned text. The checks below are the gate for that later phase. They are not instructions to run now.

## Recommended dataset

None.

## Conditional target

| Item | Value |
| --- | --- |
| Corpus | SLURP version 1.0 |
| Audio | `slurp_real.tar.gz` only, unless a later decision explicitly adds `slurp_synth.tar.gz` |
| Text | GitHub commit `8eb16545762be97ace75334109d73824217311f1`, files under `dataset/slurp/` |
| Official audio page | https://zenodo.org/records/4274930 |
| Official text page | https://github.com/pswietojanski/slurp/tree/8eb16545762be97ace75334109d73824217311f1/dataset/slurp |
| Paper | Bastianelli et al., EMNLP 2020, https://aclanthology.org/2020.emnlp-main.588/ |

## Why it cannot run

1. Audio authorization is `authorization_required`. The owner has not accepted CC BY-NC 4.0.
2. Text authorization is `authorization_required`. The owner has not accepted CC BY 4.0 for that commit.
3. `slurp_real.tar.gz` is 3,918,185,662 bytes. Remaining cap after the measured `data/` directory is 3,569,732,592 bytes. The compressed archive alone exceeds the cap by 348,453,070 bytes. Extracted size is `not_verified`.
4. The cap rule forbids deleting existing files to make room.

A storage decision that raises the cap, or explicitly retires named existing files, has to be recorded before any download. This plan does not make that decision.

## Expected files, if a later phase is authorized

| File | Expected size | Expected MD5 |
| --- | --- | --- |
| `slurp_real.tar.gz` | 3,918,185,662 bytes | `9efc0f058ced47bf5131c7cb2cade513` |
| Zenodo `LICENSE.txt` | 287 bytes | `eb6f866654ad4facb53b038dc24f9c6a` |
| `train.jsonl` | 12,745,012 bytes at the pinned commit | Git blob `c7568b5661ea802c9e41204af3d30ef892dcd5c9` |
| `devel.jsonl` | 2,221,203 bytes | Git blob `de034fadea8caa5a3c08c387b2a750f37737729d` |
| `test.jsonl` | 3,267,569 bytes | Git blob `d98a6962767dd6a03cae20c31d03c7bf7e4c36af` |
| `metadata.json` | 18,473,896 bytes | Git blob `7e5cdbe5f7dcc900fad8ca22aca1a0c249bb01fc` |

`train_synthetic.jsonl` and `slurp_synth.tar.gz` stay out unless the later decision names them. The README says acoustic files land in `audio/slurp_real` as FLAC. That layout was not observed locally.

## Validation that would be required later

| Check | Pass condition |
| --- | --- |
| Checksum | Local MD5 equals the Zenodo API value. A mismatch stops the phase. |
| Extraction | Reject absolute paths, `..`, links, and unexpected member types, using the same class of checks as the LibriSpeech extractor. |
| Audio | Every FLAC named by the acquired split opens, has a positive duration, and has a documented sample rate. The sample rate is `not_verified` now, so the later check has to record the measured rate rather than assume 16 kHz. |
| Transcript | Every acquired audio id joins to one `sentence`. The sentence is copied, not rewritten. |
| Annotation | `scenario`, `action`, and entity spans are present or explicitly empty. Empty is a dataset fact, not a project label. |
| Held-out | `test.jsonl` is hashed and then left unread during development, threshold design, and model selection. |
| Speakers | Speaker overlap across train, devel, and test is measured before any speaker-independent claim. It is `not_verified` now. |
| Privacy | `usrid` gender and native-language codes are not copied into reports. |

## Sampling

Do not create a new split. Use the official `train`, `devel`, and `test` files. A development pilot, if later authorized, is a deterministic subset of `devel` only. The algorithm, seed, ids, and file hashes have to be written before the sample is used. `test` is not the source of that sample.

No seed is chosen here, because no sample is drawn.

## Rollback

A failed checksum or a failed path check removes only the file that the later phase itself wrote. It does not delete LibriSpeech, synthetic audio, or the Phase 1C CSV. The download original, if the owner placed one in `~/Downloads`, is not deleted by the project.

## Datasets that are not planned

| Dataset | Reason this plan does not name an archive |
| --- | --- |
| Fluent Speech Commands | Licence conflict. No pinned archive or checksum. |
| Timers and Such | 13,133,746,587 byte zip. Licence id on Zenodo is not the paper’s CC0 sentence. |
| Sonos / Snips | Form-gated. No checksum. SmartSpeaker training audio is absent. |
| STOP | Licence text not found. Archive size not found. 218 hours is not a byte budget. |
| Further LibriSpeech archives | Outside D-LS-001. |
| SLURP synthetic audio | Separate condition. Not included by silence. |
