# LLM annotation methodology

This is an automated exploratory annotation audit of the Phase 2 text sample. The labels are LLM-generated provisional annotations. They are not human annotations, not inter-annotator agreement, and not independently validated ground truth.

The pending sheet `data/manual_audit/annotations.csv` was not filled in. Gold was not read until the provisional file had been written.

## What was labeled

The existing sample is unchanged: seed `20261102`, 30 utterance ids, 90 edited variants, 120 rows. Row order is the order already stored in `annotations.csv`. That order is the shuffle produced by `random.Random(20261102)` after the stratified draw. No second shuffle was applied. The recorded annotation-order seed is `20261102`.

During labeling, the inputs were the transcript, the candidate id, and the closed schema in `annotation_guidelines.md` and `utterance_generator.py`. Gold intent, gold slots, strategy names, and system predictions were not inputs. `sealed_gold.json` and `sampling_manifest.json` were not opened for this step.

## Coding rules

Only the ten existing intents were used. Text that did not support exactly one of them was labeled `unknown`. The prompt's `UNKNOWN` is stored as `unknown`, and its `UNCERTAIN` is stored as `uncertain`, matching the guideline vocabulary.

| Decision | Rule applied |
| --- | --- |
| Slots | Only schema slots for the chosen intent. Values are copied from the text. A missing required slot is `uncertain`. `not_applicable` means no task slot applies. |
| `please` | Politeness. Not uncertainty. A complete polite request can still be commit-safe. |
| `not` | Negation that reverses the request. The recognizable frame is kept, and commit safety is `unsafe`. |
| `other` or `banana` in a slot position | The placeholder is the slot value. Commit safety is `unsafe`. |
| A second task in the same line | `unknown`, ambiguity `yes`, commit `unsafe`. |
| `The warehouse is closed today` | `unknown`. It is not one of the ten tasks. |
| Weather `it` | Not discourse coreference. |
| Broken function word with one recoverable task | Intent is kept, commit safety is `uncertain`, confidence is `medium`. |
| Digit or `banana` replacing the verb of an appointment sentence | `unknown` and ambiguity `yes`, because booking, cancelling, and checking are all possible. |

No row contained "maybe". Uncertainty was not invented to fill the column: all 120 rows are `uncertainty_present=no`.

## Files

| File | Role |
| --- | --- |
| `data/manual_audit/llm_provisional_annotations.csv` | 120 provisional rows. |
| `scripts/write_llm_provisional_annotations.py` | Writes those stored judgments. It does not infer them and does not read gold. |
| `scripts/compare_llm_audit.py` | Reads gold only after the provisional file exists. |
| `data/manual_audit/llm_comparison_report.json` | Agreement counts. |
| `data/manual_audit/llm_disagreement_examples.json` | Rows for review. |
| `data/manual_audit/comparison_report.json` | Unchanged human-audit placeholder. `comparison_performed` remains false. |

## Comparison, after labeling

Gold intent and gold slots come from `sealed_gold.json` for the parent utterance. They are the original synthetic labels, including on edited rows. Variant category comes from `variants.csv` and is an edit tag, not a gold semantic field.

Intent agreement is exact string match. Slot agreement is exact map match. `not_applicable` matches only an empty gold slot map. `uncertain` does not match. Frame agreement requires both. There is no gold field for negation, uncertainty, ambiguity, coreference, or commit safety, so those sections are counts and edit-tag checks, not agreement rates.

## Recorded run

| Item | Value |
| --- | --- |
| Model name | Cursor Auto. The underlying model id was not exposed in this session. |
| Prompt version | `llm-audit-v1` |
| Annotation-order seed | `20261102` |
| Generated at | `2026-11-02T13:11:57+00:00` |
| Annotator id | `cursor-auto-llm-provisional` |
| Label status | `llm_provisional` |
