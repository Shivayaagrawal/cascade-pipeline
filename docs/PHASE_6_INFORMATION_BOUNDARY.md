# Phase 6 information boundary

The question is what the candidate text can establish, and what remains unavailable until an authorized reference is supplied. The comparison uses the same 36 test bundles. E3 never sees the reference. E4 sees intent and critical values. E5 also sees a parent transcript. The reference is not a candidate.

## What candidate-only evidence establishes

On this grammar, v5 can tell whether a candidate is affirmative, uncertain, conditional, or negated; whether its slots are inside the closed lexicon; whether the frame's values occur in that candidate; and whether two candidates disagree. It held negation, uncertainty, conditionality, ambiguity, `April 3`, and `181`. It committed both polite controls and the clean controls. It retried the clean candidate when a negated candidate was paired with it. It held the two-value bundle, because both frames are complete and the bundle does not say which value was intended.

## What it cannot establish

An in-inventory substitution is a complete frame. "Remind me at 8 AM" supports a reminder at 8 AM. Nothing in that string says the parent said 7 AM. E3 committed all 9 of those test rows: 2 dates, 4 times, and 3 amounts. Calling that a controller bug would require the controller to know a value it was not given.

## What the critical-slot reference adds

E4 held all 9. It also held `April 3` and `181`, which E3 already held for a different reason: those values are not in the lexicon. The reference is necessary for the in-inventory rows. It is not what makes the out-of-inventory rows incomplete.

On the two-value bundle, E4 commits the candidate that matches the reference. E3 holds. That is a coverage gain on one row, bought with the reference, and it is not a candidate-only improvement.

No clean or polite control was rejected. Unnecessary abstention for E4 is 0.

## What the full transcript adds

E5 matches E4 on every substitution. The one difference is `p6-parent_transcript_cue-tes-00`. The candidate is a clean play-music line. The slot reference matches it, so E3 and E4 commit. The transcript is that line prefixed with `Maybe`, so E5 holds. Slot values and a transcript are not the same information. On the other 35 test rows, the frozen parent sentence restates the slots and does not add a blocking cue.

## How the failures are classified

| Rows | Classification |
| --- | --- |
| 9 in-inventory substitutions | Missing information under candidate-only evidence. The reference supplies it. |
| `April 3`, `181` | Detectable from the candidate because the value is outside the lexicon. |
| Two-value bundle | Ambiguous without a reference. The reference selects the matching candidate. |
| `Maybe` on the parent transcript | Invisible to Mode 1. Mode 2 holds. One constructed row, not a population rate. |
| Clean and polite controls | No incorrect rejection under E4 or E5. |

None of the nine substitution misses is an implementation defect in v5. The same function, called unchanged, commits them. The reference-aware checker holds them only after it is given the other value.
