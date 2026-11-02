# Manual text annotation

CascadeGuard is a synthetic, text-only simulation. This audit labels transcript text. It is not an audio review, and it is not a speech-recognition annotation.

One person annotates. Do not report inter-annotator agreement.

## What to open

Use `annotations.csv` and this file. Do not open `sealed_gold.json`, `sampling_manifest.json`, or the source files under `data/synthetic/` while labelling. Those files contain the existing gold intent and gold slots. Comparison happens only after the sheet is filled.

Blank cells mean the row is still pending. A blank is not a negative label. Do not change `utterance_id`, `candidate_id`, or `transcript`.

## Closed intent set

Use only these intents. Do not add a new intent name.

| Intent | Required slots | A complete request mentions |
| --- | --- | --- |
| `book_appointment` | `date` | booking an appointment and a date |
| `cancel_appointment` | `date` | cancelling an appointment and a date |
| `check_appointment` | `date` | asking when an appointment is, and a date when one is stated |
| `check_balance` | `account` | asking for a balance and naming the account |
| `transfer_money` | `amount`, `currency` | transferring an amount in a currency |
| `check_transaction` | `recency` | asking about a transaction and how recent it is |
| `set_reminder` | `time` | setting a reminder and a time |
| `weather_query` | `date` | asking about weather and a date |
| `play_music` | `genre` | playing music and a genre |
| `general_information` | `topic` | asking for information and a topic |

If the text does not support exactly one of these intents, write `unknown` in `human_intent`. If a slot does not apply, write `not_applicable` for that slot rather than guessing a value. If you cannot tell, write `uncertain`.

`human_slots` uses `name=value` pairs separated by `|`. Example: `date=tomorrow`. An empty slot map is written as an empty cell only when you have decided there are no slots. Until you decide, leave the cell blank.

## Other fields

Allowed values for the yes/no fields are `yes`, `no`, `uncertain`, and `not_applicable`.

| Field | Record |
| --- | --- |
| `negation_present` | Whether a negation changes the request, as in a request not to do the task. |
| `uncertainty_present` | Whether the speaker hedges, for example with "maybe". |
| `temporal_expression` | A date, time, or relative time copied from the text, or `not_applicable`. |
| `numerical_expression` | An amount, quantity, or number copied from the text, or `not_applicable`. |
| `semantic_completeness` | `complete` when the intent and its required slots are present. `incomplete` when a required piece is missing. `uncertain` when you cannot tell. |
| `semantic_ambiguity` | `yes` when more than one of the ten intents is plausible. |
| `coreference_dependency` | `yes` when a pronoun or "it" / "that" needs earlier context. These rows are single sentences, so `no` is expected unless the sentence itself points outside itself. |
| `commit_safety` | `safe` when you would accept a semantic frame for this text. `unsafe` when committing would lock in a wrong or incomplete request. `uncertain` when you would not decide. |
| `annotation_confidence` | `high`, `medium`, or `low`. |
| `annotator_id` | Your identifier, the same value on every row you label. |
| `annotation_notes` | Short text for hard rows. Leave blank when you have nothing to add. |
| `annotation_status` | Change `pending` to `complete` only after you have filled the judgement fields on that row. |

## Examples of the judgement, not of the sample

These examples are the task grammar. They are not the rows assigned to you, and they are not a key for the sheet.

- "Book an appointment for tomorrow" supports `book_appointment` and `date=tomorrow`. Negation is `no`. The date is a temporal expression. Completeness is `complete`.
- "Book an appointment" supports `book_appointment` but has no date. Completeness is `incomplete`. Commit safety is `unsafe`.
- "Book not an appointment for tomorrow" has negation that changes the request. Do not copy an affirmative booking frame without a note.
- "What is my savings account balance?" supports `check_balance` and an account. A sentence that also asks to book an appointment is ambiguous.

## After annotation

Leave disagreements in place. Do not edit `data/synthetic/manifest.csv`, `data/synthetic/transcripts/variants.csv`, or any experiment output to match your labels.
