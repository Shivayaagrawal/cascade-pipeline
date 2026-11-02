# Phase 1 sampling protocol

**Status:** IDs for the 200-utterance samples are now written. The ordering rule is unchanged.  
**Acquisition:** D-LS-001 authorizes `dev-clean` and `test-clean`. The held-out file exists so the sample is fixed. It is not available for tuning.

## Populations

| Sample | Split | Size | When the IDs may be written |
|--------|-------|------|-----------------------------|
| Development pilot | `dev-clean` | 200 | After acquisition approval, from that split’s official transcripts |
| Development maximum | `dev-clean` | 500 | Same ordering as the pilot. The 200 IDs are a prefix of these 500. |
| Held-out evaluation | `test-clean` | 200 | After the evaluation configuration is frozen. Not used to debug or tune. |

The first real-audio pilot uses the 200 development utterances. Moving from 200 to 500 is a written development decision made before any `test-clean` result is computed. The size is not chosen by looking at error rates.

## Ordering

1. Parse utterance IDs only from `*.trans.txt` files inside the named split.
2. Reject the run if any utterance ID is repeated or lacks a matching FLAC in that split.
3. Sort the unique IDs with SHA-256 of `17:{split}:{utterance_id}`, hex digest ascending. If two digests match, break the tie by the utterance ID ascending.
4. Take the first 200 IDs for the development pilot, the first 500 for the development maximum, and the first 200 of the `test-clean` ordering for the held-out sample.

The seed is 17, the same integer used by the synthetic simulation. The split name is inside the hash, so the two splits do not share one shuffled list. File size, duration, and Kaggle chapter order are not keys.

`order_utterances` in `src/cascadeguard/dataset/sampling.py` implements this order. It does not open audio.

The LibriSpeech ID form is `speaker-chapter-utterance`. The manifest keeps `speaker_id` and `chapter_id` from those fields. Sampling must not drop them.

## Separation

- Preprocessing, ASR settings, and later thresholds may be inspected on the development sample only.
- The held-out sample file is fixed. Its transcripts were read once to build that file. They are not an input to tuning, threshold selection, or model choice.
- After both ID lists exist, the speaker-id sets are compared. A speaker in both samples fails the run. Official documentation is not a substitute for that check.
- Development and test utterances are never pooled in one score.

## Selection manifest

After the approved preparation run, `data/librispeech/metadata/sampling_manifest.json` stores the seed, the expression `17:{split}:{utterance_id}`, and the selected IDs. The development sample is the first 200 IDs of the dev-clean order. That 200 is the prefix of the first 500 under the same order. The 500-row file was not written. The held-out sample is the first 200 IDs of the separate test-clean order. The two samples share no utterance ID and no speaker ID. The full splits also share no speaker ID.
