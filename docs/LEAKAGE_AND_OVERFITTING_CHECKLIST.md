# Leakage and Overfitting Checklist

Use this list before any training or threshold fit. Items that need files are PENDING until Phase 1 loads an approved dataset.

## Split policy

- [ ] Train rows are the only rows used to fit a lexicon, vocabulary, scaler, or model.
- [ ] Validation rows are the only rows used to pick checkpoints and thresholds.
- [ ] Test rows are scored once by a frozen config.
- [ ] Test labels are not used to edit features, prompts, or rules.
- [ ] Official split files are kept. Speakers are not reshuffled.

## Leakage checks (PENDING data)

- [ ] No sample ID appears in more than one split.
- [ ] No speaker ID appears in more than one split.
- [ ] Duplicate audio paths and duplicate file hashes are listed.
- [ ] The same waveform is not stored under two IDs across splits. Hash check PENDING.
- [ ] Feature normalization, if any, is fit on train and applied to valid and test.
- [ ] Augmented files are created inside a split after the split is assigned, and they point at a source ID from that same split.
- [ ] A test transcript is not added to the train lexicon because it was “useful.”
- [ ] Predictions from an older model are not mixed into a new run’s score file.

## Overfitting controls

- [ ] First NLU is the lexicon baseline, not the largest network that fits in memory.
- [ ] Any later neural training uses validation loss or validation F1 for early stopping, with the metric named before training.
- [ ] Learning curves are saved when a model is trained.
- [ ] Per-intent counts are reported so a frequent command cannot hide rare-command failures.
- [ ] More than one seed is used when training is stochastic and affordable. If one seed is used, the report says so.
- [ ] Clean-condition false positives are reported for every detector threshold.
- [ ] Difficult utterances stay in the denominator. Exclusions have a reason.

## Scoring manipulation

- [ ] Test conditions are not narrowed after the scores are known.
- [ ] The favorable seed is not the only seed in the paper table.
- [ ] Validation F1 is not labelled as test F1.
- [ ] Ruan et al.’s matched-entity slot score is not silently substituted for the primary slot F1 in `docs/METRIC_DEFINITIONS.md`.

## Dataset-specific controls

Fluent Speech Commands, when a release is accepted:

- [ ] Official train, valid, and test files are unchanged.
- [ ] Speaker IDs do not cross splits.
- [ ] Repeated command templates are counted. Phrase overlap across splits is reported before any unseen-phrase claim.
- [ ] Test phrases are not added to the training lexicon.

SLURP, when a release is accepted:

- [ ] Real and synthetic audio are separate conditions.
- [ ] Headset and non-headset files that share a `slurp_id` are grouped before any split is invented.
- [ ] The same utterance is not treated as independent train and test items because two microphones recorded it.
- [ ] `wer` stored in the JSON is not used as a training label.
- [ ] No claim of unseen-speaker generalization unless the official split, once read, actually holds speakers out.

## Current status

No dataset, no model, and no threshold have been fit. The unchecked boxes are later gates, not failures of a run. FSC and SLURP are selected and not licensed for acquisition.
