# Storage decision

**Date:** 2026-11-02.  
**Phase 1:** not approved. This decision does not accept Mozilla terms.

| Data | Storage | Policy |
|------|---------|--------|
| Synthetic simulation text | This repository | Manifests, annotations, and schemas may be committed. |
| Synthetic audio | Local Mac, `data/synthetic/audio/` | Gitignored. Produced by macOS `say`. |
| Small Common Voice subset | Local Mac, maximum 5 GB | Not downloaded. Obtain it later only through Mozilla Data Collective, after the owner accepts the terms and confirms the file. |
| Proposed LibriSpeech archives | Local Mac, maximum 5 GB, `data/librispeech/raw/` | Not downloaded. Official OpenSLR `dev-clean` and `test-clean` only, and only after D-LS-001 acquisition approval. See `docs/PHASE_1_STORAGE_BUDGET.md`. |
| Full Common Voice archive | Mozilla Data Collective | Do not download the 88.43 GB archive onto this Mac. Do not upload it to Google Drive, Dropbox, Hugging Face, S3, or any other host. |

A 1 TB APFS external SSD may be used later for a full-corpus experiment. Extra disk does not change the access rules. The official dataset stays inside the access path Mozilla permits.

Free space measured on 2026-11-02 was about 60 GiB. That is for simulation, inference, and evaluation, not for the full corpus.
