# Phase 3 safe-commit policy

Policy version `phase3-policy-v1`. Critical gates do not consult the risk score.

| Order | Condition | Action | Reason |
| --- | --- | --- | --- |
| 1 | No candidates. | `HOLD` | `EMPTY_BUNDLE` |
| 2 | Negation, and exactly one other candidate is a complete affirmative frame, and retry is allowed. | `RETRY` | `ALTERNATE_CANDIDATE_AVAILABLE` |
| 3 | Negation otherwise. | `HOLD` | `POLARITY_CONFLICT` |
| 4 | Placeholder `other`, or candidates disagree on a critical value. | `HOLD` | `CRITICAL_SLOT_CONFLICT` |
| 5 | Incompatible intents or an unresolved within-string contradiction. | `HOLD` | `CONTRADICTORY_EVIDENCE` |
| 6 | Two intents in the string and no single safe frame. | `CLARIFY` | `AMBIGUOUS_INTENT` |
| 7 | `maybe`. | `HOLD` | `INSUFFICIENT_EVIDENCE` |
| 8 | `that`, or a non-weather `it`. | `HOLD` | `INSUFFICIENT_EVIDENCE` |
| 9 | One intent and a missing critical slot. | `HOLD` | `INCOMPLETE_FRAME` |
| 10 | One complete affirmative frame and the risk score is below the threshold. | `CONTINUE` | `SAFE_COMPLETE_FRAME` |
| 11 | Anything else. | `HOLD` | `INSUFFICIENT_EVIDENCE` |

`CLARIFY` does not generate a question. `HOLD` and `CLARIFY` do not commit a frame. `RETRY` commits the one safe alternate and is a simulated rescore of a candidate that was already in the bundle. It is not a second recognition pass.

E6 uses the same gates with retry disabled, so a resolvable negation is `HOLD` instead of `RETRY`. E5 and ablation A8 do not use this policy. Their action comes from frozen `recovery_action`.

## Risk score

`R` is the sum of five binary indicators times weights that sum to 1. The indicators are intent uncertainty, slot uncertainty, polarity, ambiguity, and contradiction. Function-word damage sets the intent indicator even when the frame is still complete, so the score can hold a recoverable `banana` sentence.

The grid is every assignment of quarter-units that sums to 1, crossed with thresholds `0, 0.25, 0.5, 0.75, 1`. That is 70 weight rows and 350 configurations. It was written down before the validation split was scored.

Selection on the 32 validation cases, in order: fewest unsafe commits, highest safe-commit accuracy, lowest selective risk, highest coverage, then lexicographic weights and the lowest threshold. A missing selective risk sorts as 1 inside the tuner only. The published rate stays null.

The selected configuration is intent `0`, slot `0`, polarity `0`, ambiguity `0`, contradiction `1`, threshold `0.25`. Validation had 0 unsafe commits, safe-commit accuracy 4/4, selective risk 0/4, and coverage 4/32. Many configurations tied on those four priorities. The lexicographic rule selected this one. The test split was not an input to that choice.

A polarity conflict still holds when every weight is 0 and the threshold is 1. The score cannot open a gate the rules have closed.
