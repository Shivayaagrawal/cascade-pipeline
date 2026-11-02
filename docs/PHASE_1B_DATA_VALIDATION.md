# Phase 1B data validation

**Status:** PASS for dataset preparation. Phase 1C was not started.

## Storage

Measured after copy and extraction, from `data/librispeech/metadata/phase1b_run.json`:

| Item | Bytes |
|------|------:|
| Both archives | 684,590,270 |
| dev-clean extracted files | 360,289,905 |
| test-clean extracted files | 368,431,293 |
| Entire `data/` directory, including the older synthetic audio | 1,430,248,587 |
| Cap | 5,000,000,000 |
| Cap remaining | 3,569,751,413 |

Free space on the volume at the start of the successful run was about 62.9 GB. No file was deleted to make room. The Downloads originals are still there, outside `data/`.

## Audio and transcripts

Transcript lines were parsed from the extracted `.trans.txt` files. Reference text after the utterance ID was not rewritten. Every FLAC was decoded with macOS `afconvert`.

| Split | FLAC files matched | Transcript files | Utterance lines | Sample rate | Channels | Decode failures | Missing or duplicate IDs | Empty text |
|-------|-------------------:|-----------------:|----------------:|-------------|----------|----------------:|---------------------------|------------|
| dev-clean | 2,703 | 97 | 2,703 | 16,000 Hz | 1 | 0 | 0 | 0 |
| test-clean | 2,620 | 87 | 2,620 | 16,000 Hz | 1 | 0 | 0 | 0 |

Duration is positive for every matched utterance. The shortest and longest measured durations are 1.445 s and 32.645 s in dev-clean, and 1.285 s and 34.955 s in test-clean. dev-clean has 40 speakers and 97 chapters. test-clean has 40 speakers and 87 chapters. The full splits share no speaker ID.

Manifests:

- `data/librispeech/processed/dev-clean/manifest.csv`
- `data/librispeech/processed/test-clean/manifest.csv`

No semantic labels were added.

## What this does not show

These checks do not measure ASR accuracy. LibriSpeech here is read audiobook speech, not spontaneous conversation.
