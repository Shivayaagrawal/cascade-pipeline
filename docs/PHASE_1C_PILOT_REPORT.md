# Phase 1C pilot report

**Status:** The 30 utterances were selected. They were not annotated. Audio was not reviewed by a person.

## Selection

The pilot is the first 30 rows of `data/librispeech/processed/dev-clean/sample-200.csv`. That file is already in the seed-17 SHA-256 order. The IDs were not chosen by duration or file size. No `test-clean` ID is included. The 200-utterance sample was not changed.

## Counts from the pilot CSV

| Measure | Count |
|---------|------:|
| Rows | 30 |
| Rows with a completed annotation | 0 |
| Rows awaiting a person | 30 |
| Rows requiring adjudication | 0, because there are no labels to disagree about |
| Incomplete, fragment, ambiguous, entity, negation, or number labels | Not calculated. Those fields are `not_annotated`, which is not a count of the phenomenon. |
| Task intent `genuinely_present` | 0 completed labels. The status is `not_annotated`, not `not_applicable`. |
| Task intent `not_applicable` | 0. That value was not assigned. |
| Schema changes made while labeling | 0. No labeling pass occurred. |
| Annotation time | Not measured. |
| Audio versus transcript discrepancies | Not observed, because nobody compared the sound with the text. |

`audio_reviewed` is `not_performed` on every row. `annotator_id` is `not_annotated`. The reference text matches the development manifest. Decoding with `afconvert` was already shown in Phase 1B. That decode is not a listening review.

## Agreement

Inter-annotator agreement is unavailable. One annotator did not label the rows, so Cohen's kappa is not defined and is not reported. A 30-utterance set would not establish reliability even after a real labeling pass. It can only test whether the guidelines can be applied.

## What remains useful

The guidelines and the validator can reject a malformed row and can keep the reference text unchanged. They do not yet show which fields a person can apply consistently. Sentence type, negation, numbers, and explicit names are the fields most likely to be checkable from the text. Task intent is the field least likely to support SLU evaluation on this corpus. That expectation is not a pilot result.

## Manual step required

A person listens to each of the 30 FLAC files, compares it with the reference, and replaces `not_annotated` using `docs/PHASE_1C_ANNOTATION_GUIDELINES.md`. Until that file changes, Phase 1C is not complete.
