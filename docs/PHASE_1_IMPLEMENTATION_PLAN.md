# Phase 1 implementation plan

**Status:** Written 2026-11-02. **Not approved. Do not start.**  
**Blocked by:** Owner confirmation of the MDC record, personal acceptance of the applicable terms, a download that fits on disk, and an explicit Phase 1 approval in `docs/PHASE_0_DECISION_LOG.md`.

Phase 1 is dataset acquisition verification, manifest generation, audio validation, split integrity, reproducible preprocessing, and ASR baseline preparation. It does not train a model and it does not implement the recovery controller.

No empty source files are created with this plan.

## Milestone 1A — ingestion

Starts only after the dataset card names the archive that was actually downloaded.

- Read the metadata files that are inside that archive. Do not assume column names from the public datasheet.
- Map audio paths to reference transcripts.
- Keep sample IDs and the source split.
- Report missing audio, empty transcripts, and malformed rows. Do not drop them silently.
- Write a manifest under `data/manifests/common_voice/`. Keep audio under `data/raw/common_voice/`, which is gitignored.

## Milestone 1B — integrity

- Check that audio opens, and record format, duration, and sample rate.
- Record empty or corrupt files and the reason for every exclusion.
- Detect duplicate recordings where the bytes or hashes show a duplicate.
- Keep the source split design. Do not invent a train/dev/test cut.
- Check sample-ID overlap across splits.
- Check speaker overlap only if the downloaded metadata has a speaker key and the protocol allows its use. `client_id` is not permission to identify a person.
- Do not use the test split to choose models or thresholds.
- Write a data-quality report.

## Milestone 1C — ASR baseline

Starts only after 1A and 1B have a passing report.

- Compare CPU-feasible ASR candidates for an Apple M1 with 16 GB RAM, including license, language support, and memory, before selecting one.
- Record the exact model name, version, and decode settings.
- Save predictions apart from references. Keep failures and empty predictions in the accounting.
- Compute WER and CER with the normalizer in `docs/METRIC_DEFINITIONS.md`.
- Record latency and memory. Do not publish numbers that were not measured.
- Do not claim genuine N-best unless that build’s return value contains an ordered hypothesis list.

## Milestone 1D — candidate and annotation readiness

- Define how candidates are stored and how provenance is labelled: `native_nbest`, `independent_decode`, or `synthetic_edit`.
- Write the annotation guide for intent, slots, transcript correctness, and ambiguity before any labels are treated as gold.
- Pilot size target: about 200–300 utterances after the ASR baseline exists. Not a final sample-size claim.
- Freeze the B0/B1/B2 interfaces in documentation. Do not implement B2.

## Out of scope for Phase 1

NLU training, B0/B1/B2 execution, synthetic corruption runs, a recovery controller, a UI, SLURP, FSC, ATIS, and a second dataset download.

## Exit

Phase 1A/1B exit requires a manifest built from the downloaded files, a quality report, and tests on synthetic fixtures. Phase 1C exit requires measured WER, CER, latency, and sample counts, or an explicit statement that a metric was not run. Phase 1 does not exit into semantic scores.
