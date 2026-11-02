# LLM audit disagreements

These are disagreements between provisional labels and the existing synthetic gold labels. Matching gold is a consistency check. It does not make the provisional file a human-validated dataset.

The human sheet is still blank. Do not copy these labels into `annotations.csv`.

## Agreement with synthetic gold

| Slice | Rows | Intent | Slots | Exact frame |
| --- | ---: | ---: | ---: | ---: |
| All rows | 120 | 87/120 | 73/120 | 73/120 |
| Unedited gold transcripts | 30 | 30/30 | 30/30 | 30/30 |
| Edited variants | 90 | 57/90 | 43/90 | 43/90 |

The 30 unedited transcripts use the closed grammar. Agreement there shows that the provisional labels follow that grammar. It is not evidence of human agreement.

Edited rows are supposed to differ from the parent gold label when the edit changes or removes meaning. A lower frame rate on those rows is not a model failure by itself.

| Edit category | Exact frame vs parent gold |
| --- | ---: |
| `insertion` (`please`) | 13/13 |
| `negation_corruption` | 12/12 |
| `substitution` | 9/14 |
| `number_corruption` | 6/12 |
| `deletion` | 3/7 |
| `ambiguous_transcript` | 0/11 |
| `entity_corruption` | 0/6 |
| `incorrect_transcript` | 0/15 |

`insertion` keeps the parent frame. That matches the coding rule that `please` does not change the task.

`negation_corruption` also keeps the parent frame, and every one of those 12 rows is `negation_present=yes` and `commit_safety=unsafe`. Gold has no negation field, so frame agreement does not mean the negated meaning matches gold. No row outside that edit category was marked as negation. This tag check is not a gold semantic score.

## Fields gold does not define

| Field | Result |
| --- | --- |
| Uncertainty | 0/120 `yes`. No transcript says "maybe". `please` was not treated as a hedge. |
| Ambiguity | 16/120 `yes`. |
| Coreference | 0/120 `yes`. Weather `it` was coded as a dummy subject. |
| Commit safety | 47 safe, 59 unsafe, 14 uncertain. None of the 30 gold transcripts were unsafe or uncertain. |
| Confidence | 94 high, 26 medium, 0 low. |

Temporal agreement where gold has a date or time is 49/60 overall and 15/15 on gold transcripts. The misses are edited lines whose visible time expression is not the parent gold value, including "The warehouse is closed today" and placeholder values such as `other`.

Numerical agreement where gold has an amount is 10/12. The two misses are:

- `utt-097-v1`, "Transfer 181 rupees": provisional amount 181, gold amount 180.
- `utt-099-v2`, "Transfer rupees": amount missing, gold amount 650.

## Rows that need a human decision

No gold-transcript frame disagreed. The review queue is the edited text and the coding policy.

1. Grammatical changes a committer might accept as a real frame. The provisional label followed the edited text and therefore disagrees with the parent gold value: "Cancel my appointment for April 3" against gold April 2 (`utt-033-v1`); "Will it rain July 2?" against gold July 1 (`utt-156-v0`); "Transfer 181 rupees" against gold 180 (`utt-097-v1`). Placeholder values were also committed as the visible slot and marked unsafe: `other` as genre, time, date, currency, or recency, and "July banana" (`utt-156-v2`).

2. Sixteen ambiguous lines. Eleven append a second balance question, for example `utt-041-v2`, "When is my Friday appointment? What is my account balance?" Five replace the appointment verb with `banana` or `9`, so booking, cancelling, and checking all remain possible. Those five are `utt-012-v0`, `utt-025-v0`, `utt-023-v2`, `utt-033-v0`, and `utt-025-v1`.

3. Fourteen uncertain commits. The task is still recoverable, but a function word is damaged. Examples: "9 is my Friday appointment?" (`utt-041-v1`), "banana me at 10 AM" (`utt-126-v1`), and "it rain August 12?" (`utt-157-v1`). The full list is `uncertain_commit_rows` in `data/manual_audit/llm_disagreement_examples.json`.

4. The negation coding itself. Twelve rows keep the affirmative gold frame, record `negation_present=yes`, and refuse the commit. A reviewer should decide whether that split is the coding the project wants. The provisional file does not treat a negated sentence as an affirmative safe commit.

Full row-level examples are in `data/manual_audit/llm_disagreement_examples.json`. Counts are in `data/manual_audit/llm_comparison_report.json`.
