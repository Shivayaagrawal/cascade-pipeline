# Model and Compute Decisions

**Status:** Provisional. No model is downloaded. No package was installed in the amended Phase 0 pass. No accuracy number below is a CascadeGuard measurement.

The current candidate is Common Voice Scripted Speech v27.0 English, accessed later through Mozilla Data Collective only. FSC and SLURP are superseded and are not downloaded. ATIS is out of implementation scope. A CNN keyword model is optional and is not downloaded. The first model milestone is ASR evaluation on CPU, not NLU training.

**Date:** 2026-11-02.

## Hardware observed on this machine

| Item | Observation | Evidence |
|------|-------------|----------|
| OS | Darwin, arm64 | `uname -sm` |
| CPU | Apple M1 | `sysctl machdep.cpu.brand_string` |
| RAM | 17,179,869,184 bytes (16 GiB) | `sysctl hw.memsize` |
| Disk free | about 60 GiB available on `/System/Volumes/Data` on 2026-11-02 | `df -h` the same day. The public English v27.0 archive is listed as 88.43 GB, so the full file does not fit. |
| NVIDIA GPU | Not available | `nvidia-smi` missing |
| CUDA | Not applicable on this host | No NVIDIA device |

CPU execution is the only path verified as available. A CUDA path is not assumed.

## ASR

| Option | Decision | Why |
|--------|----------|-----|
| Amazon Transcribe | Not selected | Ruan et al., Section 5.1, use it for ATIS. It is a paid service. Project rules require owner approval before a paid API. |
| faster-whisper | Provisional local candidate for a later phase | README already names it. The public README example returns one text string per segment. `beam_size` is a search setting, not a returned N-best list. The package is **not installed**. Whether any object in the installed version exposes alternative hypotheses is PENDING a read of that version’s `transcribe` return value. |
| Transcript-input adapter | Required for tests | Downstream NLU and metrics must run without a recognizer. This is not an ASR model. |

**Provisional ASR choice for a later Phase 1C evaluation, not for this documentation pass:** a small faster-whisper checkpoint on CPU (`tiny` or `base`), exact checkpoint name recorded at download time. Do not download it until Phase 1C is approved. Compare license, English support, memory, and the actual hypothesis return value before that choice is frozen. One baseline is enough. A returned alternative from one decoding run is `beam_hypothesis`. A second decode is `retry_decode` or `independent_decode`, depending on why it was run. Those labels are not pooled. See `docs/PHASE_1_IMPLEMENTATION_PLAN.md`.

License of the Whisper weights and of faster-whisper was **not** re-read in this phase. PENDING before download.

Native N-best: **PENDING / not claimed.**

## NLU

**Provisional choice:** a transparent baseline before any neural tagger.

1. Intent: map normalized transcript text to the intent string using a table built from the **training** split only. Unknown text yields an explicit unknown intent, not the majority class, unless a later ablation says otherwise.
2. Slots: a training-split lexicon or pattern baseline that fills only the slot names in the annotation guide. Common Voice has no native slot list. Missing slots stay missing. This NLU is not Phase 1.

Ruan et al.’s CNN-BiLSTM-CRF is the reference architecture, not the first implementation. It needs frozen fastText embeddings, character CNNs, and a CRF. Those dependencies are not justified until the lexicon baseline and the metrics both run. Optimizer, learning rate, and epoch count are not in the paper, so that architecture cannot be reproduced exactly even later.

No large language model is selected.

## What is installed now

System Python 3.13.7, pip 26.0.1. There is no project virtualenv and no lockfile.

| Package | Import version | Required for Phase 1 |
|---------|----------------|----------------------|
| numpy | 2.3.5 | Yes, when the package exists |
| pandas | 3.0.2 | Yes |
| scikit-learn | 1.8.0 | Later, for metric helpers if used |
| pytest | 9.1.0 | Yes |
| torch | not installed | Not in Phase 1 |
| torchaudio | not installed | Phase 1 audio path must choose torchaudio or soundfile plus a feature library. Not installed yet. |
| librosa | not installed | Candidate for features. Not installed yet. |
| soundfile | not installed | Candidate for WAV reads. Not installed yet. |
| matplotlib | not installed | Inspection plots. Not required to pass loader tests. |

These versions are the system interpreter’s packages. They are not a project environment. Phase 1 should create a virtualenv and pin what it installs. README asks for Python 3.11. This machine has 3.13.7. Compatibility of a 3.11 environment was not tested.

## Training cost

No training is planned in Phase 1. Phase 1C, when approved, is inference on a small CPU ASR model against reference transcripts. A later BiLSTM-CRF is not scheduled on Common Voice. The Alexa-scale experiment in the reference paper is not feasible here: the data are private. The full Common Voice English archive listed at 88.43 GB does not fit in the 60 GiB free on this disk.
