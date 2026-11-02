# Phase 5 pre-implementation audit

Stage 0 only. No Phase 5 controller, dataset, or experiment has been created. Phases 1–4 were not modified.

Repository: `/Users/shivanyaagrawal/cnn/CascadeGuard`. Branch `research/common-voice-phase1`, commit `f55b5bd`. `src/cascadeguard_phase5/`, `data/phase5/`, and `experiments/phase5/` do not exist.

## Repository findings

The frozen stack is the one Phase 4 called. Prefix strategies are `b0_prefix`, `b1_prefix`, and `b2_prefix_controller`. Lexical strategies are `b1_forced_lexical` and `b2_lexical_v3`. `b2_semantic_v4` is a separate identity. `assess()` and the five Phase 2 identities are unchanged. v4 detects the token `not`, the token `maybe`, the token `that`, missing critical slots, and cross-candidate disagreement. It does not detect `possibly`, `might`, or `if`. It does not return a committed candidate id. The Phase 4 harness reconstructed that id after the fact.

The closed grammar has 200 parent utterances, 10 intents, and fixed inventories of 20 dates, times, amounts, and the other slot types. `utt-020` and `utt-040` have no date. Every intent requires at least one slot. Currency is the word `rupees`. `cancel_appointment` is its own intent. `please` is not uncertainty. Weather `it` is not context. There is no "schedule the meeting" intent.

## Protected artifacts

These hashes match the Phase 4 audit record:

| File | SHA-256 |
| --- | --- |
| experiments/B0/summary.json | `3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee` |
| experiments/B1/summary.json | `597a2800c946018467865dfcf3d8e547bc51c10487596cc134ca2181fee695b2` |
| experiments/B2/summary.json | `34a40fdd233f5d4faa00af73c26f1afcc32c4d83922db8df57b7a7184dce0e5d` |
| experiments/sim-eval-v3/report.json | `7d1ca46400795908f6ffcd17091d4348e633493923fc030e5160e9f2ff8a8cd6` |
| experiments/sim-eval-v3b/report.json | `4c47b2b04e42b06972f7bd9e10da51d219d18a46e273d71fc50e78f2070631cf` |
| data/librispeech/annotations/phase_1c_pilot_30.csv | `56a4dc49b3a2f5add5c361c2b23edde923c8265a998de76c7e5b87462e5d6a5c` |
| data/synthetic/manifest.csv | `abc3cceec6a90e0953ac6614e1a6fee63b91c1401324798e0232ef1aa4f723e9` |
| docs/PHASE_3B_RESEARCH_AUDIT.md | `f025cb4bf387faea68a1e7cf574f15c47a3afc83c0a36c7264cb7399bec8560b` |

Phase 4 outputs under `experiments/phase4/` and `data/phase4/` stay read-only. LibriSpeech `test-clean` was not opened.

## Phase 4 findings checked against the saved test reports

`experiments/phase4/final_test/phase3_config/*/report.json`, unmodified Phase 3 weights, threshold 0.25:

| Strategy | Coverage | Selective risk | Unsafe commits | Path safety |
| --- | --- | --- | --- | --- |
| E0 | 99/120 | 61/99 | 79/99 | 20/99 |
| E1 | 99/120 | 61/99 | 79/99 | 20/99 |
| E2 | 96/120 | 58/96 | 76/96 | 20/96 |
| E3 | 0/120 | null | null | null |
| E4 | 69/120 | 10/69 | 49/69 | 20/69 |
| E5 | 69/120 | 10/69 | 49/69 | 20/69 |
| E6 | 47/120 | 10/47 | 27/47 | 20/47 |
| E7 | 56/120 | 10/56 | 27/56 | 29/56 |

E3 forced exact-frame accuracy is 79/120 and is not coverage. The Phase 4 E5 is diagnosis plus the frozen lexical action. The Phase 4 E6 is the v4 gates with retry disabled. The Phase 4 E7 is `b2_semantic_v4`.

Saved E7 test outcomes: all 10 critical-slot mutations were `UNSAFE_COMMIT`; all 10 function-word hedges were `CORRECT_FRAME_UNSAFE_PATH`; 3 `Maybe` cases were held and 7 `Possibly` / `might` / `If needed` cases were committed; all 20 clean controls were safe commits. The validation rule selected threshold 0, which kept 9 retries and held the clean controls. Those findings match the repository.

The Phase 5 prompt renumbers E5 as v4 and E6 as v5. Phase 5 experiment ids must not be written into `experiments/phase4/`. A mapping table has to say that Phase 5 E5 means `b2_semantic_v4` and Phase 5 E6 means `b2_semantic_v5`.

## Dataset feasibility

A new `synthetic-semantic-integrity-v1` can be built by editing copies of the frozen parents. The frozen files themselves do not need to change.

The prompt's examples are not all in the grammar.

| Prompt example | Feasible form |
| --- | --- |
| April 2 versus April 3 | April 2 is in the inventory. April 3 is not. A new-dataset edit can still write "April 3". It must not be added to the frozen inventory. |
| 180 versus 181 rupees | 180 is in the inventory. 181 is not. Same treatment as April 3. |
| 7 AM versus 8 AM | Both are in the inventory. Only the 20 `set_reminder` parents have a time. |
| Schedule the meeting | Not an intent. Use `Book an appointment for April 2`. |
| Don't, Could you, Can you | Unit fixtures for the analyzer. Not dataset rows. Prefix and lexical cues will not treat them as the frozen templates. |
| Cancel the reminder, as negation | `cancel_appointment` is an affirmative intent. Negation remains the token `not` or the contraction `don't` on a fixture. A cancel utterance is not a negated booking. |
| Please book an appointment | Feasible. Phase 4 already treated `Please` plus a frozen template as execution-ready. |

Thirty time-mutation cases and thirty amount-mutation cases cannot be built from distinct parents. There are 20 reminder parents and 20 transfer parents. The honest target is 20 cases in those two categories and 30 in the others, or 20 in every category. Parent-level separation still overrides category balance. Reminder and transfer parents should be stratified into the three splits before the remaining parents are shuffled, with seed `20261105`, so a split is not left without a time or an amount. No parent id may appear in two splits.

## Design constraint that blocks a false fix

The verifier is specified to compare the intended referent, the selected candidate, and the committed frame. The referent is an oracle field. If `b2_semantic_v5` receives it, the controller has read the label.

A single candidate that says "Transfer 1000 rupees" is a well-formed transfer of 1000. The oracle can still call that unsafe because the parent referent was 500. A controller that cannot see 500 cannot detect that conflict. Blocking every in-lexicon value would also block the clean controls.

Phase 5 can honestly do four things without that leak:

1. Emit the candidate id itself, so the evaluator does not reconstruct it.
2. Hold on negation, uncertainty, conditionality, mixed modality, missing slots, and two-candidate disagreements.
3. Continue on clean templates and on `Please` plus a clean template.
4. Refuse to write a parent value into a frame when the selected candidate text does not contain it. Committing April 3 from a candidate that says April 3 is a surface-faithful commit. The oracle may still mark it unsafe relative to an April 2 referent. That remaining gap has to be reported, not closed by passing the referent in.

Out-of-inventory values (April 3, 181) can be a separate gate: a critical span that is not in the closed inventory blocks commitment. That gate does not need the referent. In-inventory swaps (7 AM to 8 AM, 500 to 1000) remain undetectable from one candidate.

## Proposed architecture

New package `src/cascadeguard_phase5/`. v4 is not edited.

The controller sees only the bundle. The modality analyzer returns modality, polarity, conditionality, matched evidence, and `is_execution_ready`. Polite `please` is execution-ready. `maybe`, `possibly`, `might`, and `if` are not. Mixed cues are `AMBIGUOUS_OR_MIXED` and not execution-ready. `cancel` is not negation.

Slot reading may call the frozen `assess()` for inventory values. Values outside the inventory are recorded by a Phase 5 reader and block commitment. The commit gate is one function. `CONTINUE` and `RETRY` commit only when that function passes. `HOLD` and `CLARIFY` commit nothing. `RETRY` selects an id that is already in the bundle. Raw output and the normalized decision are separate objects.

The oracle lives in its own module, does not import the controller, and does not see controller output. Risk is a report of the same gate failures. It cannot override a failed gate. There is no 350-cell weight search. Validation may only confirm that the predeclared gates match the validation labels. The test split is read after that confirmation is written.

Phase 5 experiment ids, stored only under `experiments/phase5/<run-id>/`:

| Id | Strategy |
| --- | --- |
| E0 | `b0_prefix` |
| E1 | `b1_prefix` |
| E2 | `b2_prefix_controller` |
| E3 | `b1_forced_lexical` |
| E4 | `b2_lexical_v3` |
| E5 | `b2_semantic_v4` |
| E6 | `b2_semantic_v5` |

## Risks

- Feeding the referent to v5 would make the mutation result circular.
- A controller that holds on every non-clean string will look safe and fail the coverage question. Clean and `Please` cases are the check.
- Reusing the names E5 and E6 without a mapping table will be read as the Phase 4 runs.
- Twenty time parents and twenty amount parents limit those categories.
- The oracle will again be written in the same session. Reports have to say that this is not human gold.
- Ablation A6, "gate disabled," can reintroduce unsafe commits. It must be a configuration flag, not an edit to the gate's source during the run.

## Files proposed after authorization

`src/cascadeguard_phase5/` for the analyzer, verifier, provenance record, gate, controller, oracle, metrics, and registry. `data/phase5/` for the new challenge set, oracle labels, and split manifest. `experiments/phase5/<run-id>/` for validation, test, and ablations. `tests/phase5/` for the modality, slot, provenance, empty-bundle, and gate tests. `docs/PHASE_5_DESIGN.md`, `PHASE_5_METHODOLOGY.md`, and, after a later test run, the results, ablations, limitations, and audit.

## Not implemented

No v5 code, no Phase 5 dataset, no oracle, no runner, and no Phase 5 experiment output exist. Implementation waits for an explicit authorization of Stage 1 and Stage 2.
