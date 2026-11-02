# Phase 1D.3 reproducibility protocol

**Date:** 2026-11-02  
**Status:** rules for citing frozen artifacts and for any later run. No run is started here.

## Identifiers that stay fixed

| Item | Identifier |
| --- | --- |
| Synthetic set | Seed 17. Ids `utt-000` through `utt-199`. Config `configs/simulation.yaml`. |
| v1 cascade | Directories `experiments/B0`, `experiments/B1`, `experiments/B2`, and `artifacts/reports/simulation_report.json`. |
| v2 | `experiments/sim-eval-v2`. |
| v3 | `experiments/sim-eval-v3`. Config `configs/evaluation_v3.yaml`. |
| v3b | `experiments/sim-eval-v3b`. Role: audit. Config `configs/evaluation_v3b.yaml`. |
| LibriSpeech | Official OpenSLR SLR12 archives already authorized: `dev-clean` and `test-clean` only. |
| Pilot | `data/librispeech/annotations/phase_1c_pilot_30.csv`. Schema `phase1c-0`. |
| Code revision recorded with v3 | Git HEAD `f55b5bd5b74d760e00f3178a35cd9b9512fd1ccf`. The v3 report states that the working tree was dirty and that the experiment is not in that commit. |

A new synthetic draw uses a new seed and new ids. It does not rewrite `utt-000` through `utt-199`.

## Seeds

Seed 17 is the frozen synthetic sample. Reports that cite it say “one seed.” A later stochastic training run uses more than one seed when the run is cheap enough, and it reports the mean and the standard deviation. A single seed stays labelled as a single seed. Seeds do not make a future beam search deterministic. Library versions are recorded anyway.

The bootstrap seed in `docs/PHASE_1D3_STATISTICAL_ANALYSIS.md`, if a later phase draws it, is a different seed and is stored in that run’s config.

## Configuration versioning

Each new run directory contains the config file and the SHA-256 of that file. The v3 config hash already published is `ac4bb7ea743195e6ea860a4f2c34dc546437321f28c811055782fe4b1c5ed842`. Changing a threshold, a `min_support` default, or a metric denominator after seeing a score is a protocol change. It is logged before any new number is compared with an old number. The frozen directories are not edited to match the new rule.

## Model and decoder versioning

Current results record `asr_backend: synthetic_hypothesis` and `audio_decoded: false`. A later decode records the package version, the model id, the device, and every decoder flag. `beam_size=1` is recorded as one segment. It is not recorded as `native_nbest`.

`faster-whisper` is not an environment fact of the frozen results. It is not installed for this protocol.

## Hash record

A run that claims to preserve frozen artifacts hashes them before and after. The hashes that Phase 1D.3 treats as the preservation set are:

| File | SHA-256 |
| --- | --- |
| `experiments/B0/summary.json` | `3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee` |
| `experiments/B1/summary.json` | `597a2800c946018467865dfcf3d8e547bc51c10487596cc134ca2181fee695b2` |
| `experiments/B2/summary.json` | `34a40fdd233f5d4faa00af73c26f1afcc32c4d83922db8df57b7a7184dce0e5d` |
| `artifacts/reports/simulation_report.json` | `7adf69ee6ac344e7ef205099af3686ddf7cceaffa111a8789f03b83ed8319856` |
| `experiments/sim-eval-v2/report.json` | `74499b716103e26ef829cb56816bf738d67d3d3e5961848c4cfe37f2e8f4f77d` |
| `experiments/sim-eval-v3/report.json` | `7d1ca46400795908f6ffcd17091d4348e633493923fc030e5160e9f2ff8a8cd6` |
| `experiments/sim-eval-v3b/report.json` | `4c47b2b04e42b06972f7bd9e10da51d219d18a46e273d71fc50e78f2070631cf` |
| `experiments/sim-eval-v3b/decision_log.jsonl` | `9c486601dcac141ccf7453f84b144fbd5d5c491da1b1a32542e7a14a796a4e75` |
| `configs/evaluation_v3.yaml` | `ac4bb7ea743195e6ea860a4f2c34dc546437321f28c811055782fe4b1c5ed842` |
| `data/librispeech/annotations/phase_1c_pilot_30.csv` | `56a4dc49b3a2f5add5c361c2b23edde923c8265a998de76c7e5b87462e5d6a5c` |

A mismatch stops the run. The pilot hash changes only after a person saves a real annotation. The expected test hash is then updated to that save. The labels are not rewritten to restore the old hash.

## Experiment naming and immutable directories

A new experiment receives a new directory name. These names are immutable:

- `experiments/B0`
- `experiments/B1`
- `experiments/B2`
- `experiments/sim-eval-v2`
- `experiments/sim-eval-v3`
- `experiments/sim-eval-v3b`
- `artifacts/reports/simulation_report.json`
- `artifacts/reports/simulation_v3/report.json` when that copy is present

`experiments/run_simulation.py` writes the v1 summaries. It is not the command for a new condition. A later script refuses a destination that is one of the immutable names. v3b already refuses a destination other than `sim-eval-v3b`.

The run directory stores the config, the seed, the dataset version, the model identifier, the package versions, the hardware, the predictions, the exclusion list, and the clock method.

## Test-set isolation

| Split | Rule |
| --- | --- |
| Synthetic `utt-000`–`utt-199` | The evaluation set for Track A. Thresholds are not fit to it again. The v3 report states that B2 thresholds were not tuned. |
| LibriSpeech development sample | The first 200 of the seed-17 `dev-clean` order, and the 30-row pilot inside it, may be used for transcription development after a decode is separately approved. |
| LibriSpeech `test-clean` | Hashed sample file stays in place. It is not opened for prompts, lexicons, thresholds, or error analysis. |
| Future task corpus | Official development split for choices. Official test file is hashed, then left unread until the config is frozen. |

Reading a test split to decide the next code change breaks the protocol. Speaker overlap is measured and reported before any speaker-independent sentence. `usrid` attributes are not copied into reports.

## Environment

The frozen text results used the project interpreter, `PYTHONPATH=src` or `pytest.ini` with `pythonpath = src`, and no GPU. They did not import a speech model. A later environment record includes the Python version and the package list actually imported. The current protocol check may run `python3 -m pytest -q` as an integrity check. That command is not an experiment.

## Preservation command

Before and after a documentation-only phase, hash the preservation set and compare it with the table above. Do not download an archive as part of that check.
