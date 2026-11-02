# Phase 3 implementation blueprint

Status: the six decisions are accepted and the implementation described here has been run. Results are in `docs/PHASE_3_RESULTS.md`. This file is not a speech-robustness claim.

This blueprint reconciles the proposed Phase 3 plan with the repository as it stands. Where the proposal and the frozen code disagree, the blueprint keeps the stricter existing constraint and records the difference.

Companion document: `docs/PHASE_3_RESEARCH_PROTOCOL.md`.

## 1. Repository constraints

`assess()` in `src/cascadeguard/evaluation/semantic_evidence.py` returns `Evidence(intents, slots)`. Historical comparisons keep calling it. A new function, proposed as `assess_v4()`, lives beside it. It must not change `Evidence` or `assess()`.

The facade router accepts only the five identities in `STRATEGIES`. `b2_semantic_v4` is not one of them. Adding it by editing that set would make a new experiment look like an existing identity. The proposed design is a separate registration path. The five adapters, their normalization rules, and the empty-bundle short circuit stay in place.

Prefix `run_b2` still attaches one-best text on `CLARIFY` and `HOLD`. That text is raw output, not a committed frame. Lexical `RETRY` remains `simulated_candidate_rescore`. Prefix `RETRY` is not given that label. `select_candidate(())` and `forced_selection([])` still raise. `decide_selective([])` still returns `HOLD` / `no_intent_evidence`. `EMPTY_BUNDLE` is not that reason.

`forced_selection` is not a safety commit. An experiment that reports its exact-frame count must not put that count in the coverage field.

New outputs go under `experiments/phase3/`. They must not be written into `experiments/B0`, `experiments/B1`, `experiments/B2`, `experiments/sim-eval-v2`, `experiments/sim-eval-v3`, or `experiments/sim-eval-v3b`.

The currency unit in this grammar is the word `rupees`. The blueprint does not add a rupee symbol or a new slot. Challenge examples that do not match the ten intents are illustrations only. Construction has to use the existing intent and slot schema. "Schedule it" and "Move it" are not intents in this repository.

## 2. Proposed architecture

```
synthetic candidate bundle
        |
        v
existing candidate assessment (frozen assess / prefix parser)
        |
        v
assess_v4          extraction, interpretation, commit eligibility kept apart
        |
        v
diagnose_failure   one or more taxonomy labels, each with a span and a severity
        |
        v
risk and commit policy
        |
        v
b2_semantic_v4     CONTINUE, RETRY, CLARIFY, HOLD, with a reason code
        |
        v
new experiment directory and decision log
```

E0 through E4 call the frozen functions and write only to the new directory. They are comparison runs on the new challenge set, not reproductions of the seed-17 scores.

Three representations stay distinct:

| Layer | Question | Example |
| --- | --- | --- |
| Extraction | What string is present? | The characters `181` are in the text. |
| Interpretation | What frame does that string support? | A transfer of 181 rupees, if the verb supports it. |
| Commit eligibility | Is that frame safe to act on? | Not if another candidate says 180, or if the polarity is negative. |

A correct extraction can still be an unsafe commit.

## 3. Failure taxonomy

A label describes the evidence. It is not a recovery action. One text can carry more than one label. `NO_FAILURE_DETECTED` is legal only after the checks for the implemented detectors have run.

| Label | Include | Exclude | Proposed severity |
| --- | --- | --- | --- |
| `NEGATION_SHIFT` | A polarity marker changes the request, as in "book not". | The intent `cancel_appointment`. Cancel is its own task, not a negated booking. The word "closed" in an out-of-grammar sentence. | `CRITICAL` |
| `SLOT_VALUE_CORRUPTION` | A critical slot value differs from the parent gold value, or a placeholder such as `other` occupies the slot. | A missing slot. That is `INCOMPLETE_EVIDENCE`. | `HIGH` if the value is critical. `CRITICAL` if the two readings name different actions. |
| `TEMPORAL_CORRUPTION` | The corrupted critical value is a date or a time. | A topic name that merely contains the word "time", such as "opening time". | `HIGH` |
| `NUMERICAL_CORRUPTION` | The corrupted critical value is an amount. | A digit that replaced a function word, such as a leading `9` where the question word was. That is `FUNCTION_WORD_DAMAGE`. | `HIGH` |
| `SEMANTIC_AMBIGUITY` | More than one of the ten intents is supported, including two tasks joined in one line. | A single unreadable sentence with no supported intent. | `HIGH` |
| `CONTRADICTORY_EVIDENCE` | Candidates in one bundle support incompatible intents, polarities, or critical values. | A conflict inside one string. That is ambiguity or corruption of that string. | `HIGH`, or `CRITICAL` when the conflict is polarity or the action itself. |
| `INCOMPLETE_EVIDENCE` | The task is supported and a required schema slot is absent. | An empty bundle. That remains `EMPTY_BUNDLE`. | `HIGH` |
| `UNCERTAINTY_OR_MODALITY` | A declared hedge, such as "maybe", or a declared conditional. | The word "please". The audit coded "please" as politeness. | `MEDIUM` until the validation split says otherwise. A commit of an uncertain frame is still blocked. |
| `COREFERENCE_DEPENDENCY` | A referring expression has no resolvent in the supplied text. | Weather "it" in "will it rain". | `HIGH` when the missing resolvent is required for the frame. Otherwise `MEDIUM`. |
| `FUNCTION_WORD_DAMAGE` | A small grammatical break leaves one task recoverable, or leaves the task unclear without adding a second intent. | A full substitution by an unrelated sentence. | `MEDIUM` when one task remains recoverable. `HIGH` when it does not. |

`TEMPORAL_CORRUPTION` and `NUMERICAL_CORRUPTION` are specializations of `SLOT_VALUE_CORRUPTION`. Reports may count the specialization and must not also count the parent for the same span.

The eight edit categories in `variants.csv` are not this taxonomy. One `negation_corruption` row can be `NEGATION_SHIFT` and still contain the original slot values. One `number_corruption` row can be either a changed amount or a function word replaced by a digit. The challenge set records the semantic effect. It does not copy the injector category in as a diagnosis.

Severity is a rule on the label and the critical-slot table. It is not a model confidence score.

Priority, if implementation is later staged: polarity, critical slot values, ambiguity, completeness, and the safe-commit rules come first. Cross-candidate contradiction and the recovery matrix come next. Modality and coreference can follow. The audit sample contained no "maybe", so modality has no empirical base in that sample until the challenge set creates some.

## 4. Semantic evidence contract

Proposed module: `src/cascadeguard_facade/semantic_evidence_v4.py`. Proposed function: `assess_v4(text, lexicon, provenance)`. It may call `assess()` and then add fields. It must not write back into `Evidence`.

| Field | Allowed states | Rule |
| --- | --- | --- |
| `candidate_id` | string | Copied from the bundle. |
| `intent_hypotheses` | zero or more of the ten intents, each with a span | No eleventh intent. Zero intents is an empty list, not a guessed intent. |
| `slot_hypotheses` | schema slots only, each with a value and a span | A value is recorded only if the span supports it. Missing is not filled from the parent gold. |
| `polarity` | `affirmative`, `negative`, `unknown` | `unknown` when no polarity cue was found. `negative` is not the default. |
| `modality` | `certain`, `uncertain`, `conditional`, `unknown` | `unknown` when the detector was not run or the cue set does not apply. `please` does not mean `uncertain`. |
| `temporal_values` | extracted spans, or empty | Empty means none found, not "no time exists in the world". |
| `numerical_values` | extracted spans, or empty | A digit inside a date is a numeric span. It is not automatically an amount. |
| `completeness` | `complete`, `incomplete`, `unknown` | `complete` only when one intent has each of its critical slots once. |
| `ambiguity` | `none`, `competing`, `unknown` | `competing` when two intents are supported. `unknown` when the check did not run. |
| `contradictions` | list of conflicts, possibly empty | A conflict names the two spans or the two candidate ids. |
| `context_dependencies` | list, possibly empty | Weather "it" is not an entry. |
| `evidence_spans` | start, end, and the field that span supports | Offsets refer to the candidate string as stored, without text normalization. |
| `provenance` | `synthetic_edit` or `reference_passthrough` | `native_nbest` is rejected, as in the Phase 2 contract. |

Gold intent and gold slots are not arguments.

## 5. Diagnosis and commit policy

Proposed functions: `diagnose_failure`, then a policy module that returns an action, a reason, and a commit bit.

Diagnosis returns every label whose check fired, the spans, the affected intent and slots, the severity, whether the bundle agrees, and whether a critical value is involved. Absence of a span is not evidence that the meaning is affirmative.

Proposed action rules, applied in order:

| Order | Condition | Action | Reason |
| --- | --- | --- | --- |
| 1 | The bundle has no candidates. | `HOLD` | `EMPTY_BUNDLE` |
| 2 | Polarity is negative or candidates disagree on polarity. | `RETRY` only if another synthetic bundle resolves it. Otherwise `HOLD`. `CLARIFY` only if the metadata says a user choice is the declared resolution and none is available. | `POLARITY_CONFLICT` |
| 3 | Critical slot values disagree, or a critical value is a placeholder. | Same shape as polarity. | `CRITICAL_SLOT_CONFLICT` |
| 4 | Two intents are supported. | `RETRY` only if another bundle supports exactly one. Otherwise `CLARIFY`. | `AMBIGUOUS_INTENT` |
| 5 | One intent, missing critical slot. | `RETRY` if another bundle supplies it. Otherwise `HOLD`. | `INCOMPLETE_FRAME` |
| 6 | Modality is `uncertain` or `conditional`. | Do not `CONTINUE`. `HOLD` unless a declared alternative is affirmative and certain. | `INSUFFICIENT_EVIDENCE` |
| 7 | One complete affirmative frame, no critical conflict, checks actually run. | `CONTINUE` | `SAFE_COMPLETE_FRAME` |
| 8 | Anything else unresolved. | `HOLD` | `CONTRADICTORY_EVIDENCE` or `INSUFFICIENT_EVIDENCE` |

`RETRY` requires a second bundle that the caller supplied. A high risk score is not that bundle. `CLARIFY` is a label. The controller does not write a question. `HOLD` and `CLARIFY` commit no frame.

An optional score `R = w_i I + w_s S + w_p P + w_a A + w_c C` may be logged. The terms are binary indicators of intent disagreement, critical-slot disagreement, polarity conflict, ambiguity, and contradiction. The weights are D-P3-5 and are unset. A polarity conflict or an incompatible action blocks commitment even when `R` is low. The score does not choose `RETRY`.

`b2_semantic_v4` returns the raw diagnosis and the normalized decision in separate fields, following the Phase 2 audit record. It does not mutate the frozen controllers' objects.

## 6. Challenge dataset

Proposed identity: `synthetic-semantic-challenge-v1`. Proposed path: `data/phase3/`. It does not exist. Creating it waits on D-P3-1, D-P3-2, D-P3-4, and D-P3-6.

Proposed size: 8 categories times 30 cases, 240 cases. Each case stores the parent id, the parent text, the transformed text, the operator, the expected semantic effect, the expected polarity and modality, the expected safety outcome, whether a resolving alternate bundle exists, and the expected recovery action.

The expected action is assigned by the transformation rule before any controller runs. It is circular to label the expected action with `b2_semantic_v4` and then score that controller against the label.

Parents come from `synthetic-seed17-v1` by read-only copy. The frozen manifest and `variants.csv` are not edited. The existing 600 edits are not the challenge set. Their categories do not match this taxonomy one to one.

Split unit is the parent utterance id. Every case derived from one parent is in the same split, so a negation case and a slot case from the same sentence cannot land in both validation and test. The test split is not used to choose weights, thresholds, or rules. The seed and fractions are D-P3-4.

D-P3-6 matters because some frozen cancel and check-appointment gold rows have an empty slot map, while `CRITICAL_SLOTS` still lists `date`. Using those parents without a recorded decision would mix "gold has no date" with "the transformation deleted a date".

The files were built under `data/phase3/`. Parent leakage checks passed. `utt-020` and `utt-040` were excluded. Frozen manifest bytes were unchanged. See `docs/PHASE_3_DATASET_SPECIFICATION.md`.

## 7. Experiments and metrics

| ID | Condition | Implementation |
| --- | --- | --- |
| E0 | B0 prefix | Frozen `run_b0`. |
| E1 | B1 prefix | Frozen `run_b1`. |
| E2 | B2 prefix controller | Frozen `run_b2`. |
| E3 | Forced lexical selection | Frozen `forced_selection`. Scored as an answer, not as coverage. |
| E4 | Lexical recovery | Frozen `recovery_action`. |
| E5 | Diagnosis without the v4 policy | `assess_v4` and `diagnose_failure`. The action comes from a named frozen policy, declared before the run. |
| E6 | Diagnosis plus the safe-commit rules, without the full recovery matrix | New policy. |
| E7 | `b2_semantic_v4` | Diagnosis, overrides, and recovery. |

E5 compared with E7 is H7. Ablation A8 is that same comparison, not an extra undeclared system.

Ablations A1 through A7 turn one declared signal off. The signal becomes `unknown` and the rest of the policy stays fixed. The ablation list is fixed before the test split is read. A component is not dropped after the test numbers are known.

Metrics use the existing `rate()` helper: a zero denominator is null, not zero.

| Metric | Denominator |
| --- | --- |
| Intent accuracy, slot precision, slot recall, slot F1, exact frame | The evaluated cases, using the existing slot-metric definitions. |
| Coverage | Commits divided by all cases. |
| Selective risk | Committed frames whose intent and slots differ from gold, divided by commits. |
| Unsafe-commit rate | Commits that violate the safety label in the challenge metadata, divided by commits. |
| Action accuracy | Match to the predeclared expected action. |
| RETRY success | Retries that the metadata marked as resolvable and that the alternate bundle resolved, divided by retry attempts. |
| CLARIFY rate and HOLD rate | Those actions divided by all cases. |

Selective risk and unsafe-commit rate are different. A commit can match the parent intent and slots and still be unsafe because the polarity changed. Historical v3 used one ratio for both names. Phase 3 must not collapse them again.

Additional reported checks: polarity accuracy, critical-slot safety, ambiguity precision and recall, contradiction recall, safe-commit accuracy across intent, slots, polarity, and modality, the risk-coverage curve, and recovery utility when a resolving alternate exists.

Coverage is never quoted without selective risk. Neither number alone is a result.

## 8. Tests

`tests/phase3/` covers evidence, negation, modality, context, contradiction, ambiguity, empty bundles, the separate registry, the weight grid, and protected hashes. The full suite result is in `docs/PHASE_3_VALIDATION_REPORT.md`.

## 9. Sequence

Stages 3A through 3G were executed in that order. The validation split selected the policy. The test split was scored after `experiments/phase3/frozen_policy.json` existed. A second test scoring pass corrected forced-selection so it is not counted as coverage. Weights were not changed between those passes.

## 10. Acceptance

The implementation gate is recorded in `docs/PHASE_3_VALIDATION_REPORT.md`. The scientific reading of the test numbers, including hypotheses that this set does not separate, is in `docs/PHASE_3_RESULTS.md` and `docs/PHASE_3_LIMITATIONS.md`. Matching the rule-derived labels is not independent confirmation of those rules.
