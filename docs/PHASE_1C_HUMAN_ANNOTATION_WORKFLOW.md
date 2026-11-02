# Phase 1C human annotation workflow

**Status:** The screen is ready. No row has been annotated. Phase 1C stays blocked.

## Launch

From the repository root:

```bash
python3 scripts/annotate_librispeech_pilot.py
```

The process prints a local address, `http://127.0.0.1:8765/`. Open that address in a browser on this machine. Leave the process running while you review. Stop it with Control-C. Closing the browser does not annotate anything.

## Listen

Each page shows one development utterance: its ID, speaker ID, and reference text. Use the audio control and play the recording through to the end. The page then says that the recording was played through. The reference text is not treated as proof of what was spoken. If the sound and the text disagree, write that in Notes and do not edit the transcript.

The held-out split is not linked from this screen. A request for a `test-clean` file is refused.

## Annotate

Every judgment starts as `not_annotated` or, for audio review, `not_performed`. Those values mean the row has not been judged. They do not mean the phenomenon is absent. Absence is the choice `absent`, and only after you have listened.

Choose one allowed value for each menu. Use `unclear` or `ambiguous` when the guideline does not pick a single value. Use `not_applicable` for task intent when the utterance is not a task request, and type `not_applicable` in the task-intent box. Type your reviewer id. The screen does not invent one.

Entities are a JSON list of strings you copy from the reference, such as `[]` if you decide there are none. Do not leave the token `not_annotated` in that box once you are submitting a review.

## Save and resume

Save writes the current utterance into `data/librispeech/annotations/phase_1c_pilot_30.csv`. Previous and Next do not save. If you move away with unsaved edits, the page asks first, including when the browser tab is closing. Progress shows how many of the 30 rows have a reviewer id.

Start the same command later. Saved rows are loaded again. Rows you did not save stay `not_annotated`.

## Validate

After a review session:

```bash
python3 -m pytest -q
```

The existing annotation validator checks the pilot file. A row that was not saved still has to say `not_annotated` rather than a guessed label.

The guidelines remain `docs/PHASE_1C_ANNOTATION_GUIDELINES.md`.
