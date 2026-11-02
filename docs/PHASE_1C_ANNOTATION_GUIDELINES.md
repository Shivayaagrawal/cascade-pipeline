# Phase 1C annotation guidelines

**Version:** phase1c-0  
**Date:** 2026-11-02  
**Unit:** one LibriSpeech utterance.  
**Attribution:** examples below are short excerpts from LibriSpeech dev-clean, OpenSLR SLR12, CC BY 4.0, prepared by Vassil Panayotov with Daniel Povey. They illustrate the rules. They are not completed pilot labels.

## 1. Purpose

Record sentence-level meaning that a reader can point to in the reference text, and record whether the utterance is a genuine task request. The record is for studying how transcript errors could change that meaning. It is not a command label set.

## 2. Research questions

The labels support two questions. First: which sentence-level properties of a LibriSpeech utterance can be named without guessing. Second: which of those properties could later be compared between a reference transcript and an ASR transcript. They do not support a claim that LibriSpeech contains intent and slot gold for B0, B1, or B2.

## 3. Scope and non-goals

Annotate the reference text after listening to the matching FLAC. Do not change the reference text. Do not add speaker traits, emotion, dialect, or demographics. Do not assign `book_flight`, `check_balance`, `transfer_money`, `weather_query`, or `restaurant_booking` unless the decision rule in section 16 is met. Do not annotate `test-clean` in this phase.

## 4. Unit of annotation

One row is one `utterance_id`. The split, speaker id, and reference text are copied from the development manifest. Copying is not an annotation.

## 5. Field definitions

| Field | Definition |
|-------|------------|
| `sentence_type` | The grammatical form of the reference text, using the rules in section 6. |
| `utterance_completeness` | Whether the reference text is a finished sentence, a sentence that stops early, or a piece that is not a sentence. |
| `proposition_summary` | One clause stating what the reference text asserts, asks, or requests. Use the reference words. Do not add events that are not written. |
| `semantic_coherence` | `coherent` if the reference text does not contradict itself. `internally_inconsistent` only if two parts of the same text cannot both be true. |
| `entities_explicitly_mentioned` | A JSON list of names, places, numbers, and other referring expressions that appear as words in the reference. |
| Presence fields | `present` only if the reference text contains the relevant words. `absent` only after the annotator has looked and not found them. |
| `coreference_or_context_dependency` | `context_dependent` if a pronoun or other expression needs an earlier sentence, which this file does not contain, to identify its referent. |
| `semantic_ambiguity` | The first applicable ambiguity type. Use `none_observed` only after checking the list. |
| `task_intent_status` | Whether the utterance is a real task request. Default for narrative is `not_applicable`. |
| `task_intent` and `task_slots` | Filled only when `task_intent_status` is `genuinely_present`. |
| `annotation_confidence` | `high`, `medium`, or `low`, from section 18. |
| `annotator_id` | The person who listened and labeled. `not_annotated` means nobody has labeled the row. |
| `audio_reviewed` | `yes` only if that person listened to the whole FLAC. |

## 6. Allowed values

Use only the enumerations in `data/librispeech/annotations/phase_1c_annotation_schema.json`. `not_annotated` means the field was not judged. It is not a finding of absence. `not_applicable` is allowed for task intent when the utterance is not a task request.

Sentence type, in this order: if the text is only a phrase with no finite verb, `fragment`. Else if it asks a question, `interrogative`. Else if it directs someone to act, `imperative`. Else if it is only an exclamation, `exclamatory`. Else if it states something, `declarative`. Else `unclear`.

## 7. Positive examples

`6313-66129-0028`, "TAD IS AN EXPERIENCED RIDER", is a declarative statement if the annotator hears the same sentence. The name "TAD" is an explicit entity. Task intent is `not_applicable`.

`3752-4943-0019`, "WHAT DOES HE CARE CARE", is interrogative. "HE" is context-dependent. Task intent is `not_applicable`.

## 8. Negative examples

Do not mark `7976-105575-0005`, "NO BATTERY IN THE WHOLE FOUR YEARS WAR...", as a device-battery command. "BATTERY" here is in a war narrative. Task intent is `not_applicable`. Negation is `present` because of "NO", not because a slot was cancelled.

Do not mark a mentioned place in `1462-170142-0001` ("EUSTON", "SAVOY", "BEDFORD SQUARE") as a destination slot.

## 9. Ambiguous examples

`3081-166546-0009`, "HAVE YOU EVER THOUGHT THAT SHE MIGHT HAVE BEEN A SUICIDE", is an in-story question. It is not a help-desk intent. Mark the sentence type `interrogative`, uncertainty `present` because of "MIGHT", and task intent `not_applicable`. If the audio makes the wording doubtful, record the discrepancy in `annotation_notes` and do not edit the reference.

## 10. Incomplete utterances

Use `incomplete` when the text begins a sentence and stops before its main clause finishes. Use `fragment` when there is no finite clause. A short complete sentence, such as "HE'S A GREAT SCIENTIST" (`251-137823-0023`), is `complete`.

## 11. Fragments

A fragment gets `sentence_type` `fragment` and `utterance_completeness` `fragment`. Do not invent the missing clause in `proposition_summary`. Summarize only the words that are present, or write `unclear` in the summary field's companion note if a summary would add content. The summary itself stays a description of the visible words.

## 12. Entities

Copy the expression as written. Do not normalize "FOUR YEARS" into a date. Do not add a type unless the words say it. An empty JSON list is allowed only after the annotator decides there is no explicit entity. An unannotated row uses the token `not_annotated`, not `[]`.

## 13. Negation

`present` if the reference contains a negative word that changes the claim, including "NO", "NOT", "NEVER", or "N'T". A name or place that merely contains those letters does not count. If the scope is unclear inside the sentence, use `ambiguous`.

## 14. Uncertainty

`present` for words such as "MIGHT", "THINK", "PERHAPS", or "SHOULDN'T BE AT ALL SURPRISED" when they weaken a claim. `2428-83705-0002` contains that kind of wording. Do not mark uncertainty because the story world is fictional.

## 15. Context-dependent meaning

If the sentence uses "HE", "SHE", "IT", "THIS", or "THE OTHER" and the referent is not named in the same utterance, set `coreference_or_context_dependency` to `context_dependent`. Do not look up the book to resolve it. Do not guess the referent in the summary.

## 16. Genuinely task-oriented expressions

Set `task_intent_status` to `genuinely_present` only when all three are true: the speaker is asking a listener to do a practical task now, the task can be named with a verb in the sentence, and the sentence is not narration about someone else doing or discussing a task. Dialogue inside a novel usually fails the third test. "YOU SAID YES YES" in `3752-4944-0034` is reported dialogue, so the status is `not_applicable`. If the three tests disagree, use `ambiguous` and leave `task_intent` as `not_annotated`.

## 17. Unclassifiable examples

If none of the sentence-type rules apply, use `unclear` and `annotation_confidence` `low`. Do not force a task intent. `not_annotated` is reserved for rows nobody has judged.

## 18. Confidence

`high`: the rule picks one value and the audio matches the reference. `medium`: the rule picks one value, but a second value was considered. `low`: the rule ends in `unclear` or `ambiguous`. Do not use a number. Do not assign confidence on a row with `annotator_id` `not_annotated`.

## 19. Adjudication

One annotator cannot produce agreement. The future check is: a second person labels the same 30 rows without seeing the first labels; disagreements are listed by field; a third pass keeps the value both annotators chose, and records `unclear` or `ambiguous` when they do not agree. No agreement coefficient is computed until that second labeling exists.

## 20. Versioning

This file is `phase1c-0`. A schema change raises the version, states which field changed, and does not rewrite older rows in place. Older rows stay readable under the version named on them. The pilot file for this version has no completed labels.

The validator is `src/annotation/validate_annotations.py`.
