# Phase 3 validation report

Checked after the challenge set, the v4 modules, the frozen policy, and the second test scoring pass were in place.

## Tests

`python3 -m pytest -q` reported `113 passed in 6.05s`. That includes the 15 Phase 3 tests and the previous suite. No test failed.

Before any Phase 3 code was added, the same command reported `98 passed in 5.89s`.

## Dataset

`synthetic-semantic-challenge-v1` has 240 cases, 30 in each of the eight categories. Eligible parents: 198. Excluded: `utt-020`, `utt-040`. Parent splits at seed `20261103`: development 138, validation 30, test 30. Case counts: development 168, validation 32, test 40. No parent is in more than one split.

Expected labels were written by the operators in `src/cascadeguard_facade/phase3_dataset.py`. The LLM annotation files were not inputs.

## Policy freeze

`experiments/phase3/frozen_policy.json` records weights intent 0, slot 0, polarity 0, ambiguity 0, contradiction 1, and threshold 0.25. The file's `test_cases_read` field was false at selection time. The selector saw 32 validation cases. The 350-configuration table is `validation_search.json`.

The test command was then run. It was run a second time after forced selection was removed from coverage. Weights were the same file both times.

## Hashes

SHA-256 matched the pre-implementation baselines for the B0, B1, and B2 summaries, `simulation_report.json`, the v2, v3, and v3b reports, the v3b decision log, `configs/evaluation_v3.yaml`, the LibriSpeech pilot CSV, `data/synthetic/manifest.csv`, `data/synthetic/transcripts/variants.csv`, `data/manual_audit/annotations.csv`, and `data/manual_audit/llm_comparison_report.json`.

## Acceptance

The protocol decisions are recorded as accepted. The challenge set exists and is leakage-free. The v4 modules exist. `b2_semantic_v4` is outside the five-identity set. E0 through E7 and A1 through A8 have test reports. Coverage is paired with selective risk. The unsafe-commit rate uses a different numerator. The test pass used the frozen policy.

What this does not accept: E7's perfect action accuracy is not independent evidence for the policy, because the labels and the controller share the operators. H4 and H5 are not supported as separate effects on this test split. The result is not a real-speech result.
