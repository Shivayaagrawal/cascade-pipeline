# Phase 1B reproducibility

**Run:** 2026-11-02T10:44:17Z through 2026-11-02T10:45:23Z  
**Result:** Phase 1B dataset preparation passed. Phase 1C was not started.

## Environment

| Item | Value |
|------|-------|
| Operating system | macOS 26.4, build 25E5218f |
| Python | 3.13.7 |
| Branch | `research/common-voice-phase1` |
| HEAD | `f55b5bd5b74d760e00f3178a35cd9b9512fd1ccf` |
| Audio tool | `/usr/bin/afconvert` |
| Script | `python3 scripts/prepare_librispeech.py` |

No ASR package was installed. The first preparation attempt failed on Python's certificate store while fetching `md5sum.txt`. The successful run used `curl`, which could verify the TLS certificate. An intermediate run decoded every FLAC with zero failures and then stopped before writing manifests because the script mutated a dictionary while iterating. That bug was fixed and the successful run repeated the decode.

## Commands

- `curl -fsSL https://openslr.trmal.net/resources/12/md5sum.txt`
- Local MD5 and SHA-256 of both Downloads archives, then of the project copies
- In-memory tar member checks, then `safe_extract` into `data/librispeech/raw/<split>/`
- `afconvert -f WAVE -d LEI16` for every matched FLAC, with the temporary WAV removed
- `python3 -m pytest -q` after the manifests existed. Result: 51 passed, 0 failed.

## Sampling

Seed 17. Expression `17:{split}:{utterance_id}`. SHA-256 hex digest ascending, then utterance ID ascending. Development sample: first 200 dev-clean IDs, also the prefix of the first 500. Held-out sample: first 200 test-clean IDs. The samples share no utterance and no speaker. The canonical write-up is `docs/PHASE_1_SAMPLING_PROTOCOL.md`. The ID list is `data/librispeech/metadata/sampling_manifest.json`.

## Frozen outputs

| File | SHA-256 |
|------|---------|
| `experiments/B0/summary.json` | `3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee` |
| `experiments/B1/summary.json` | `597a2800c946018467865dfcf3d8e547bc51c10487596cc134ca2181fee695b2` |
| `experiments/B2/summary.json` | `34a40fdd233f5d4faa00af73c26f1afcc32c4d83922db8df57b7a7184dce0e5d` |
| `artifacts/reports/simulation_report.json` | `7adf69ee6ac344e7ef205099af3686ddf7cceaffa111a8789f03b83ed8319856` |
| `experiments/sim-eval-v2/report.json` | `74499b716103e26ef829cb56816bf738d67d3d3e5961848c4cfe37f2e8f4f77d` |

The test suite checks these digests. This preparation did not rewrite the files.

## Not run

ASR inference, synthetic transcript generation, NLU training, B0, B1, B2, threshold tuning, and semantic annotation were not run.
