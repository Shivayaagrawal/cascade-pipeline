# LLM audit validation

This report covers the automated annotation audit only. Phase 2 facade implementation was already complete and was not changed. The checks below were run after the provisional labels and comparison files were written.

## Deliverables

- `data/manual_audit/llm_provisional_annotations.csv`: 120 rows, status `llm_provisional`.
- `data/manual_audit/llm_comparison_report.json`: comparison with synthetic gold after labeling.
- `data/manual_audit/llm_disagreement_examples.json`: review examples.
- `docs/LLM_AUDIT_METHODOLOGY.md`
- `docs/LLM_AUDIT_DISAGREEMENTS.md`
- `scripts/write_llm_provisional_annotations.py`
- `scripts/compare_llm_audit.py`
- `tests/test_llm_audit.py`

`data/manual_audit/annotations.csv` still has 120 pending rows and blank judgement fields. `data/manual_audit/comparison_report.json` still has `comparison_performed: false`. The human comparison file was left in place so provisional labels would not be stored as human labels.

## Run record

| Item | Value |
| --- | --- |
| Model | Cursor Auto. Underlying model id was not exposed. |
| Prompt version | `llm-audit-v1` |
| Order seed | `20261102` |
| Generated at | `2026-11-02T13:11:57+00:00` |
| Rows | 120 |
| Gold-transcript frame agreement | 30/30 |
| All-row frame agreement | 73/120 |

Those rates are consistency with synthetic gold, not a new benchmark and not human validation.

## Tests

`python3 -m pytest -q` from the CascadeGuard root reported `98 passed in 6.11s`. That includes the three new audit integrity tests and the existing suite. No test failed.

## Protected hashes

SHA-256 matched the stored baselines for all 12 frozen files: B0, B1, and B2 summaries; `simulation_report.json`; sim-eval v2, v3, and v3b reports; the v3b decision log; `configs/evaluation_v3.yaml`; the LibriSpeech pilot CSV; `data/synthetic/manifest.csv`; and `data/synthetic/transcripts/variants.csv`. No experiment runner was executed.

The pending human sheet is not one of those frozen files. Its check is the test result: 120 rows, every judgement cell blank, every `annotation_status` still `pending`.

## What this audit does not close

Phase 3 was not started. No real ASR, audio decoding, or human audio annotation was added. The manual audit analysis remains incomplete as a human analysis because the human fields are blank. The automated consistency audit is complete and ready for review of the disagreements in `docs/LLM_AUDIT_DISAGREEMENTS.md`.
