# CascadeGuard final research report

CascadeGuard is a synthetic, text-only study of how controlled transcript changes affect intent, slots, candidate choice, and the decision to commit a semantic frame. It does not run a speech recognizer and it does not read audio. No waveform decoding was performed. No real word-error-rate or character-error-rate evaluation was conducted. CascadeGuard is not a production spoken-language-understanding system. It does not reproduce a published spoken-language-understanding paper.

Oracle labels are same-session specifications rather than independent human annotations. They are not human gold. Phase 5 and Phase 6 reuse the same eligible parent pool. Phase 6 does not represent an independent population evaluation.

## Question

The project asked how transcript edits propagate into a downstream semantic decision, and what a controller can refuse when the only evidence is the candidate text. Phase 6 asked a narrower follow-up: which of the remaining unsafe commits are missing information rather than a missed cue in the candidate.

## What was built

The stack is a closed grammar of ten intents and fixed slot inventories. Prefix, lexical, and semantic controllers read those strings. Later controllers add gates for negation, uncertainty, conditionality, conflicting candidates, and candidate identity. Phase 6 adds an explicit reference object and does not change the candidate-only controller.

Controller identities that matter for the final comparison:

| Identity | Role |
| --- | --- |
| `b0_prefix`, `b1_prefix`, `b2_prefix_controller` | Always-or-nearly-always answer from template cues |
| `b1_forced_lexical` | Selects a frame and does not count as a safety commit |
| `b2_lexical_v3` | Lexical evidence and selective recovery |
| `b2_semantic_v4` | Diagnosis and commitment gates, evaluated without being given the referent |
| `b2_semantic_v5` | Stricter gates, emits a candidate id, still candidate-only |
| `b2_reference_aware_v1` | Calls v5 unchanged, then checks an explicit reference |

## Results by phase

Phase 1 and the early simulations established the synthetic baseline and the metric definitions. Lower word error is not the same claim as a correct frame. Those runs stay frozen. The protected hashes still match.

Phase 2 wrapped the existing strategies behind one facade and kept an unfinished human annotation sheet separate from an exploratory language-model labeling pass. The model labels are not gold. The LibriSpeech pilot remains `not_annotated`.

Phase 3, on a 40-case synthetic test, found a safety–coverage tradeoff. The semantic controller committed 4/40 with 0 unsafe commits among those 4. The prefix and lexical baselines covered more cases and committed frames the specification marked unsafe. Action agreement with labels that were generated from the same rules is not independent validation. The weight cell was one of many validation ties. That result is a description of the slice, not a general safety guarantee.

Phase 4 repeated the evaluation on a 120-case set whose labels were written beside the controller rather than copied out of it. The same controller, at the Phase 3 weights, committed 56/120. Unsafe commits were 27/56. Path safety among commits was 29/56. It held negation and `Maybe`. It committed in-lexicon slot substitutions, and it committed `Possibly`, `might`, and `If needed` when the frame still matched the parent. The hypothesis that critical-slot substitutions would be blocked was contradicted on that set. Native candidate ids were reconstructed by the harness for the older strategies. v4 did not emit them.

Phase 5 kept v4 and added v5, still without the referent. On 56 test cases sitting on 14 of 40 test parents, v5 committed 23/56, with 14/23 unsafe and 9/23 native path-safe commits. The 14 unsafe commits were every in-inventory critical substitution in the split. Negation, maybe, possibly, might, and if-needed were held. Both polite controls were committed. Clean-control false rejections were 0/6. The test split did not contain `April 3` or `181`. The oracle was a same-session specification.

Phase 6 asked whether an explicit critical-slot reference detects the substitutions v5 cannot see. It reuses the same 198 eligible synthetic parents as Phase 5. The Phase 6 cases are a new construction on that pool, not an independent population evaluation. The set has 184 cases, seed `20261106`. Three parents were assigned to test before scoring: `utt-097`, `utt-013`, and `utt-121`. The scored test has 36 cases on 14 of 42 test parents.

| Condition | Coverage | Unsafe commits | In-inventory substitutions | Clean false rejections |
| --- | ---: | ---: | ---: | ---: |
| Candidate-only v5 | 19/36 | 9/19 | 9 committed | 0/7 |
| Critical-slot reference | 11/36 | 0/11 | 9 held | 0/7 |
| Full parent transcript | 10/36 | 0/10 | 9 held | 0/7 |

`April 3` and `181` were held by both candidate-only and reference-aware runs, because those strings are outside the lexicon. The parent-cluster interval for unsafe commits, reference minus candidate-only, is −0.518 with CI −0.741 to −0.277 on 14 clusters. The coverage interval is −0.500 with CI −0.750 to −0.205. The full transcript matched the slot reference on every substitution and held one extra row whose transcript was prefixed with `Maybe`.

Turning the reference check off restored the nine unsafe commits. Removing the reference entirely held every row, including the clean controls. A perfect detection rate with a 7/7 false-rejection rate is not a useful controller.

## What is supported

On these synthetic sets, the following was observed.

Candidate text can support a decision about modality, lexicon membership, whether the frame's values occur in the selected candidate, and whether two candidates disagree. v5 uses that information. It emits the candidate id it selected.

A complete in-inventory value that differs from an authorized value is not visible in the candidate alone. Detecting it requires the other value. An explicit critical-slot reference supplied that value in Phase 6 and the checker held the substituted candidates. It did not reject the clean or polite controls in the 36-case test.

A full parent transcript was not required for those slot substitutions. It mattered for one constructed case in which the transcript carried `Maybe` and the slot record did not.

Coverage falls when unsafe substitution commits become abstentions. That cost is part of the result. Holding every row removes the unsafe commits and also rejects commands the specification says to commit.

## What is not supported

Nothing here shows speech robustness, recognizer N-best behavior, or a latency claim. Nothing here is inter-annotator agreement. The same-session specifications can be satisfied by a checker that implements those specifications. Small parent clusters make the intervals wide. Zero unsafe commits in a double-digit commit count is not a general guarantee. `181` is not in the parent pool. A balanced multiple-slot attack cannot be built from this grammar, because the only second slot is the word `rupees`.

## Reproducibility

Frozen Phase 5 run: `experiments/phase5/run-20261102-stage4-scored`, policy `0840ee89f84553b2d345d56c141056f57428950320904b23abd11f91ac7393b9`.

Phase 6 run: `experiments/phase6/run-20261102-phase6`, policy `6f976bb1f01d4ba005ac1dbdb0dae1fe2ff2a02f38169d9a218d6514073e6b22`.

Git HEAD at both runs: `f55b5bd5b74d760e00f3178a35cd9b9512fd1ccf`. The historical protected hashes were rechecked and matched. `b2_semantic_v5` was not edited for Phase 6.

## What remains

A reference that is authorized, scoped, and absent from the candidate channel is a research instrument here. How such a signal would be produced in a real dialogue system is not answered. The grammar's inventories are small, the parent clusters are few, and the labels are not independent of the people who wrote the rules. Those are reasons to stop adding controllers and to write up the boundary that the experiments actually isolated.
