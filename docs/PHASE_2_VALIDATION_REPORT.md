# Phase 2 validation report

Checks below were run from `/Users/shivanyaagrawal/cnn/CascadeGuard` on 2026-11-02 after the facade and audit files were written. A check that is not listed here was not run.

## Files created

Facade package:

- `src/cascadeguard_facade/__init__.py`
- `src/cascadeguard_facade/contracts.py`
- `src/cascadeguard_facade/normalization.py`
- `src/cascadeguard_facade/recovery.py`
- `src/cascadeguard_facade/router.py`
- `src/cascadeguard_facade/audit.py`
- `src/cascadeguard_facade/evaluation.py`
- `src/cascadeguard_facade/manual_audit.py`
- `src/cascadeguard_facade/adapters/__init__.py`
- `src/cascadeguard_facade/adapters/b0_prefix.py`
- `src/cascadeguard_facade/adapters/b1_prefix.py`
- `src/cascadeguard_facade/adapters/b2_prefix_controller.py`
- `src/cascadeguard_facade/adapters/b1_forced_lexical.py`
- `src/cascadeguard_facade/adapters/b2_lexical_v3.py`

Tests:

- `tests/facade/__init__.py`
- `tests/facade/test_contracts.py`
- `tests/facade/test_adapters.py`
- `tests/facade/test_normalization.py`
- `tests/facade/test_recovery.py`
- `tests/facade/test_router.py`
- `tests/facade/test_audit.py`
- `tests/facade/test_regression.py`

Audit and documentation:

- `data/manual_audit/sampling_manifest.json`
- `data/manual_audit/annotation_guidelines.md`
- `data/manual_audit/annotations.csv`
- `data/manual_audit/sealed_gold.json`
- `data/manual_audit/comparison_report.json`
- `docs/PHASE_2_IMPLEMENTATION.md`
- `docs/PHASE_2_LIMITATIONS.md`
- `docs/PHASE_2_VALIDATION_REPORT.md`

## Files modified

No existing source, dataset, or experiment file was edited. `git diff --stat` shows 13 tracked documentation files that were already modified before this phase. This phase did not edit them. New files are untracked, together with the rest of the previously untracked tree (`src/`, `tests/`, `data/`, `experiments/`, `configs/`).

## Tests

`python3 -m pytest -q tests/facade` reported `24 passed in 0.15s`.

`python3 -m pytest -q` reported `95 passed in 6.24s`. That run includes the 24 facade tests and the existing suite. No test was skipped or failed.

## Hash verification

SHA-256 after implementation matched the preflight values:

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
| `data/synthetic/manifest.csv` | `abc3cceec6a90e0953ac6614e1a6fee63b91c1401324798e0232ef1aa4f723e9` |
| `data/synthetic/transcripts/variants.csv` | `fd4d3d9a66e68dd8e687a8ab4d6c5484d32774c2d9c08f3c1ecb7a7e7fa89f68` |

Two further files were hashed because they must stay untouched. They were not in the stored preflight list, so this is a current hash, not a comparison:

- `configs/evaluation_v3b.yaml` `01df50b78117fa08acec59bcb4c977def27e719306d141743b91f9a760dee0ed`
- `data/synthetic/annotations/annotations.jsonl` `f27d9f2b01e2ccac310f08d92c505524ec86070184bce475c054f3b8cadac06c`

No experiment runner was executed. No frozen output was regenerated.

## Manual audit counts

Measured from the source files, not assumed:

- Seed `20261102`.
- 10 intents, 3 utterance ids each, 30 ids.
- 30 gold rows.
- 90 variant rows. Every selected id has 3 rows in `variants.csv`.
- 120 annotation rows, 120 distinct candidate ids.
- Every judgement field is blank.
- Every `annotation_status` is `pending`.
- `comparison_report.json` has `comparison_performed: false` and `inter_annotator_agreement: not_claimed`.

## Deviations

`sealed_gold.json` is an extra derived file so a later comparison can run without opening the annotator sheet. The guidelines say not to open it during annotation.

`annotation_status` is an extra column so a blank judgement is explicit. Blank still means pending, not a negative label.

`b0_prefix` and `b1_prefix` commit their parse. `b1_forced_lexical` does not. See `docs/PHASE_2_LIMITATIONS.md`.

## Known limitations

See `docs/PHASE_2_LIMITATIONS.md`. The project is a synthetic, text-only simulation. The audit is a single-annotator text sample with labels still pending.
