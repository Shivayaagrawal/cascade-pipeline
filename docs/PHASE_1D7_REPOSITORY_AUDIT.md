# Phase 1D.7 repository audit

**Date:** 2026-11-02  
**Method:** source and file inspection. Filenames were not treated as features.  
**Code changes:** none.

Classes: `EXISTING_AND_REUSABLE`, `EXISTING_BUT_REQUIRES_ADAPTER`, `DOCUMENTATION_ONLY`, `MISSING`, `OUT_OF_SCOPE`.

| Item | Where | Class |
| --- | --- | --- |
| Gold rows, 200 | `data/synthetic/manifest.csv`. Intents 20 each. Ids `utt-000`–`utt-199`. | EXISTING_AND_REUSABLE |
| 600 edits | `data/synthetic/transcripts/variants.csv`. Provenance `synthetic_edit` on every row. Eight categories, 75 rows each. Three rows per id, ids `v0`, `v1`, `v2`. | EXISTING_AND_REUSABLE |
| Category rule | `error_injector.categories_for_index` and `generate_variants` | EXISTING_AND_REUSABLE |
| Paraphrase, slot-removed, split lists | `candidate_diversity.py`. Not a fourth variant inside the 600. | EXISTING_AND_REUSABLE |
| `Hypothesis`, `ASRResult`, `SyntheticHypothesisASR.transcribe_id` | `asr/base.py`. `transcribe(path)` raises. | EXISTING_AND_REUSABLE for written text. Waveform decode is OUT_OF_SCOPE. |
| Prefix intent and slots | `intent_classifier.py`, `slot_extractor.py` | EXISTING_AND_REUSABLE |
| Prefix score and select | `candidate_manager.py`. Empty input raises `ValueError`. | EXISTING_AND_REUSABLE |
| `run_b0`, `run_b1`, `run_b2` | `pipeline.py`. Gold is not an argument. `run_b2` still copies a selected frame onto CLARIFY and HOLD. | EXISTING_BUT_REQUIRES_ADAPTER so a record does not treat that copy as a commit. |
| Prefix controller | `failure_detector.py`, `recovery_controller.py` | EXISTING_AND_REUSABLE |
| Lexical evidence, `forced_selection`, `decide_selective`, `recovery_action` | `semantic_evidence.py`, `selective.py` | EXISTING_AND_REUSABLE |
| Metrics | `intent_metrics.py`, `slot_metrics.py`, `v3_metrics.py`, `wer.py`, `cer.py`, `rates.py` | EXISTING_AND_REUSABLE. Speech WER is OUT_OF_SCOPE. Text-edit distance may be reported as text. |
| Frozen reports | `experiments/B0`, `B1`, `B2`, `sim-eval-v2`, `sim-eval-v3`, `sim-eval-v3b` | EXISTING_AND_REUSABLE as evidence. Not to be rewritten. |
| Tests | 11 files under `tests/`. This phase did not run them. | EXISTING_AND_REUSABLE |
| Facade types and router | Not in the tree. | MISSING. Proposed only. |
| `EMPTY_BUNDLE` | Not in code. | MISSING. Facade contract only. |
| Clarification question text | Not in code. | OUT_OF_SCOPE for this project. |
| Whisper adapter, LibriSpeech tree, Phase 1C UI, SLURP notes | Present on disk. | OUT_OF_SCOPE as simulation inputs. |

## Documentation gaps this phase closes

Phase 1D.6 left implementation authorization open under S11 and pointed at Phase 1D.7. This phase records that decision as not granted. It also records the category counts from the CSV, which the earlier spec did not count. The two uses of 145/200 stay distinguished.

## What was not inferred

`audio_path` on the manifest is a stored path. No scoring function in the frozen B0/B1/B2 path reads those AIFF files. `WhisperAdapter` is not on the simulation path.
