# Phase 1C blockers

**PHASE 1C BLOCKED.**

The suitability assessment, guidelines, schema, validator, and dataset review are written. The pilot was not annotated.

## Failed exit conditions

| Condition | Evidence |
|-----------|----------|
| Pilot annotated to the stated standard | 0 of 30 rows have an annotator. Every judgment is `not_annotated`. |
| Audio review | `audio_reviewed` is `not_performed`. Decode support from Phase 1B is not listening. |
| Pilot statistics of linguistic phenomena | Not calculated. `not_annotated` is not a count of negation, entities, or intent. |

## What did pass

The 30 IDs are the deterministic prefix of the development sample. No test ID is included. Reference text matches the manifest. The five simulation hashes are covered by the test suite. No ASR, NLU, or B0/B1/B2 run was added.

## Manual actions

The review screen is `python3 scripts/annotate_librispeech_pilot.py`, documented in `docs/PHASE_1C_HUMAN_ANNOTATION_WORKFLOW.md`. It does not fill labels. These steps are still required:

1. Start the screen from the repository root and open the printed local address.
2. For each of the 30 development utterances, play the FLAC through, then choose the values yourself. Do not open `test-clean`.
3. Save that utterance. Previous and Next do not save. Unsaved edits prompt before you leave the page.
4. Stop when the page shows 30/30 completed, or leave the remaining rows `not_annotated` if the session stops early.
5. Re-run `python3 -m pytest -q`.
6. A second person repeats the same 30 rows before any agreement number is reported.

Phase 1C can be marked PASS only after a person has completed steps 2–5. A second dataset still needs a separate owner decision. Phase 2 does not start from this file.
