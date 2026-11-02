# Phase 3 dataset specification

Identity: `synthetic-semantic-challenge-v1`. Path: `data/phase3/`. Parents are read from `data/synthetic/manifest.csv` and are not rewritten.

## Eligibility

A parent is eligible when every `CRITICAL_SLOTS` value for its intent is present in the text. An empty gold slot map would be eligible only if that intent required no slots. No intent does. The excluded parents are `utt-020` and `utt-040`. Eligible parents: 198.

## Split

Seed `20261103`. Eligible ids are shuffled with `random.Random(seed)`. Validation and test each receive `round(0.15 * 198) = 30` parents. Development receives the remaining 138. Cases inherit the parent split. No parent appears in two splits.

A second `random.Random(seed)` draws cases inside each split. The streams are independent and both are recorded. Targets per category are 21 development, 4 validation, and 5 test. All eight categories met those targets, so the set is 240 cases. There was no shortfall and no padding.

## Operators

| Category | Operator | Expected action |
| --- | --- | --- |
| `NEGATION_SHIFT` | Insert ` not` after the first token. Odd draws in each split also keep the parent text as an alternate. | `HOLD`, or `RETRY` when the alternate is present. 14 of 30 are retries. |
| `SLOT_VALUE_CORRUPTION` | Replace the primary critical span with `other`. | `HOLD` |
| `SEMANTIC_AMBIGUITY` | Append a second closed-grammar request. Balance requests get a transaction sentence. Every other intent gets a balance sentence. | `CLARIFY` |
| `CONTRADICTORY_EVIDENCE` | Pair the parent text with a copy whose primary critical value is the first other lexicon value in alphabetical order. | `HOLD` |
| `INCOMPLETE_EVIDENCE` | Delete the primary critical span. | `HOLD` |
| `UNCERTAINTY_OR_MODALITY` | Prefix `Maybe `. | `HOLD` |
| `CONTEXT_DEPENDENCY` | Replace the primary critical span with `that`. | `HOLD` |
| `FUNCTION_WORD_DAMAGE` | Replace the first token with `banana`. | `CONTINUE` when the frozen intent and slot checks still match the parent. Otherwise `HOLD`. 12 of 30 continue. |

The expected intent and slots are the parent frame. Expected polarity, modality, completeness, ambiguity, contradiction, commit safety, and action are assigned by the operator before any controller runs. The controller is not used to write those labels.

`please` is not an uncertainty operator. Weather `it` is not a context operator. Cancel is not produced by inserting `not` into a booking. Currency remains the word `rupees`.
