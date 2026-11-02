# Phase 3 failure taxonomy

Labels describe evidence. They are not recovery actions. One candidate can carry more than one label. `NO_FAILURE_DETECTED` is used only after the checks have run and none fired.

| Label | Include | Exclude | Severity in this implementation |
| --- | --- | --- | --- |
| `NEGATION_SHIFT` | A bounded token `not`. | `cancel_appointment`. The word "closed" in an out-of-grammar sentence. | `CRITICAL` |
| `SLOT_VALUE_CORRUPTION` | The placeholder `other`, or two candidates with different critical values. | A missing span with no placeholder. That is `INCOMPLETE_EVIDENCE`. | `HIGH` |
| `SEMANTIC_AMBIGUITY` | Two of the ten lexical intents in one string. | A string with no supported intent. | `HIGH` |
| `CONTRADICTORY_EVIDENCE` | Complete candidates that disagree on intent, or more than one value for one slot inside a string. Slot-value disagreement is also `SLOT_VALUE_CORRUPTION`. | A second task inside one string. That is ambiguity. | `HIGH`, or `CRITICAL` when the intents themselves disagree. |
| `INCOMPLETE_EVIDENCE` | One intent and a missing critical slot, and the string is not a placeholder or a context reference. | An empty bundle. That is `EMPTY_BUNDLE`. | `HIGH` |
| `UNCERTAINTY_OR_MODALITY` | A bounded token `maybe`. | `please`. | `MEDIUM` |
| `CONTEXT_DEPENDENCY` | A bounded `that`, or a bounded `it` when the string is not a weather question. | Weather `it` in "will it rain". | `HIGH` |
| `FUNCTION_WORD_DAMAGE` | A bounded token `banana`. | A fluent paraphrase that the grammar still accepts as the same frame and that contains no `banana`. | `MEDIUM` if the frame is still complete, otherwise `HIGH`. |

`TEMPORAL_CORRUPTION` and `NUMERICAL_CORRUPTION` are not separate challenge buckets. A changed date or amount appears as `CONTRADICTORY_EVIDENCE` when a second candidate carries the other lexicon value. A single fluent swap cannot be detected without the parent gold, so it is not labeled as something the text-only controller should reject on its own.

Severity is the maximum rank among the labels that fired. It is not a model confidence score.
