# Phase 1C reproducibility

**Date:** 2026-11-02  
**Branch:** `research/common-voice-phase1`  
**HEAD:** `f55b5bd5b74d760e00f3178a35cd9b9512fd1ccf`  
**Python:** 3.13.7  
**Status:** Methodology recorded. Human annotation was not done.

## What was inspected

Phase 1B reports, both sample manifests, and the FLAC paths for the first 30 development utterances. All 30 files were present. Their reference texts were copied into the pilot CSV and were not edited.

## Selection

Seed 17. Order: SHA-256 of `17:dev-clean:{utterance_id}`, hex ascending. The pilot is the first 30 IDs of `data/librispeech/processed/dev-clean/sample-200.csv`. The first ID is `7976-105575-0005`. The held-out file was used only to prove that none of its IDs entered the pilot.

## What was not done

No person listened to the audio. No semantic label was assigned. No second dataset was downloaded. No licence was accepted. ASR, NLU training, and B0/B1/B2 were not run. Annotation time was not measured. Agreement was not calculated.

## Checks

`python3 -m pytest -q` returned 57 passed and 0 failed. The Phase 1C tests check the 30-row selection, transcript immutability, rejected judgments on unannotated rows, held-out exclusion, and the five simulation hashes.

## Files

- `docs/PHASE_1C_DATASET_SUITABILITY.md`
- `docs/PHASE_1C_ANNOTATION_GUIDELINES.md`
- `docs/PHASE_1C_PILOT_REPORT.md`
- `docs/PHASE_1C_TASK_ORIENTED_DATASET_REVIEW.md`
- `docs/PHASE_1C_RESEARCH_DESIGN_IMPLICATIONS.md`
- `data/librispeech/annotations/phase_1c_annotation_schema.json`
- `data/librispeech/annotations/phase_1c_pilot_30.csv`
- `src/annotation/validate_annotations.py`
