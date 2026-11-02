# Phase 1 storage budget

**Date:** 2026-11-02  
**Cap:** 5,000,000,000 bytes (5 GB). This is a hard project limit for the LibriSpeech acquisition.  
**Acquisition:** not approved. Nothing in this budget was measured on a local archive.

## Proposed download

The OpenSLR catalog printed these compressed sizes on 2026-11-02. They are not local file sizes.

| Item | Printed size | Local measurement |
|------|----------------|-------------------|
| `dev-clean.tar.gz` | 337M | Unknown |
| `test-clean.tar.gz` | 346M | Unknown |
| Printed compressed total | 683M | Unknown |

683M is below 5 GB. That comparison uses the catalog labels only.

## Not yet known

Extracted FLAC size, resampled or converted audio, and the space used by predictions are unmeasured. This document does not estimate them. The Kaggle file listing is not an OpenSLR extracted-size measurement.

Processed manifests, checksums, and prediction JSON are text. Their allowance is whatever remains under the cap after the audio is measured. They do not get a guessed quota.

## Cap rule

Before a download starts, and again after extraction, sum the bytes under `data/librispeech/` plus any temporary archive. If that sum would exceed 5,000,000,000 bytes, stop. Do not delete an unrelated project to make room, and do not add `train-clean-100`, `train-clean-360`, or `train-other-500`.

## Temporary archives

Keep a `.tar.gz` only while the cap still holds after extraction. Once the archive checksum has been recorded, extraction has been checked, and keeping both copies would pass the cap, delete the temporary archive and record that deletion. Do not delete the extracted split to hide a failed checksum.

Raw audio and extracted audio stay gitignored under `data/librispeech/raw/`. Metadata JSON may be committed. Audio may not.
