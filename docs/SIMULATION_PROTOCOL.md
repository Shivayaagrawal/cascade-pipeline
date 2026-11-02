# Synthetic simulation protocol

**Status:** Local simulation track. Not a Common Voice benchmark. Phase 1 is not approved.

## What is generated

- 10 intents, 20 utterances each, 200 originals.
- Three synthetic transcript variants per utterance, 600 variants.
- Provenance of every variant is `synthetic_edit`. None are `native_nbest`.
- Audio is macOS `say` output, AIFF, under `data/synthetic/audio/`. Those files are not committed.
- Gold intent and slots are written by the generator. They are not Common Voice labels.

The canonical examples are the first utterance of each intent, including "Book an appointment for tomorrow", "Cancel my appointment", "When is my appointment?", "What is my account balance?", "Transfer 500 rupees", "Show my latest transaction", "Remind me at 6 PM", "Will it rain tomorrow?", "Play jazz music", and "What are your working hours?".

## Error categories

deletion, substitution, insertion, entity corruption, number corruption, negation corruption, ambiguous transcript, incorrect transcript.

Each utterance receives three of those categories. The assignment is a function of the utterance index. Token choice inside deletion, substitution, and similar edits uses `random.Random` seeded by `17`, the utterance id, and the category.

The injected category is stored for analysis. B0, B1, and B2 do not read it.

## Systems

- **B0:** variant 0 is the single hypothesis. A template NLU reads that text.
- **B1:** all three variants are compared. Selection uses parse confidence only. It does not look at the gold intent.
- **B2:** CONTINUE when the 1-best parse is confident, CLARIFY when two intents match, RETRY once when another synthetic candidate parses cleanly, otherwise HOLD.

The ASR backend name is `synthetic_hypothesis`. It does not decode the waveform. `faster-whisper` is not installed and was not run. `beam_size` is not treated as N-best.

## Scores

WER and CER use NFC, casefold, collapsed whitespace, and kept punctuation, applied to both sides. They compare the hypothesis text with the original synthetic sentence.

Intent accuracy, slot precision, recall, F1, exact frame match, and semantic error rate use the generator's labels. Semantic error rate is one minus exact frame match, on this track only.

Recovery success rate is the fraction of B0 frame failures that B2 gets right. False recovery rate is the fraction of B0 frame successes that B2 gets wrong. Latency is process time around the text pipeline, not audio playback.

## Reproduce

```text
PYTHONPATH=src python3 experiments/run_simulation.py --seed 17
python3 -m pytest -q
```

`--skip-audio` rebuilds the text reports without calling `say`.

## Separation

`data/common_voice/manifest.csv` contains one project status row, `not_acquired`. It is not a Common Voice schema and not a sample list. Do not pool these scores with any later Common Voice run.
