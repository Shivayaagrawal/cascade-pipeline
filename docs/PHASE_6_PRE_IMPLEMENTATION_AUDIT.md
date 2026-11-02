# Phase 6 pre-implementation audit

Stage 0 only. No Phase 6 dataset, controller, runner, or experiment has been created. Phases 1–5 were not modified by this audit.

Phase 6, if later authorized, would compare two evidence conditions on the same candidate bundles. It would not be another attempt to raise Phase 5's scores by editing `b2_semantic_v5`.

## Repository

Git HEAD is `f55b5bd5b74d760e00f3178a35cd9b9512fd1ccf`. That is the commit recorded in the Phase 5 scored summary. The worktree has older tracked documentation edits and a large set of untracked research files, including Phase 5. Those tracked edits were already present before this audit and were not reverted.

Existing experiment directories: `experiments/B0`, `B1`, `B2`, `sim-eval-v2`, `sim-eval-v3`, `sim-eval-v3b`, `phase3`, `phase4`, `phase5`. Existing data directories include `data/synthetic`, `data/phase3`, `data/phase4`, `data/phase5`, and `data/librispeech`. Source packages include `cascadeguard`, `cascadeguard_facade`, `cascadeguard_phase4`, and `cascadeguard_phase5`.

These paths do not exist: `src/cascadeguard_phase6`, `data/phase6`, `experiments/phase6`, `tests/phase6`, and any `docs/PHASE_6_*` file other than this audit. New Phase 6 work can be isolated there.

## Protected artifacts

All 13 protected hashes match. Nothing was rewritten.

| File | SHA-256 |
| --- | --- |
| `experiments/B0/summary.json` | `3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee` |
| `experiments/B1/summary.json` | `597a2800c946018467865dfcf3d8e547bc51c10487596cc134ca2181fee695b2` |
| `experiments/B2/summary.json` | `34a40fdd233f5d4faa00af73c26f1afcc32c4d83922db8df57b7a7184dce0e5d` |
| `artifacts/reports/simulation_report.json` | `7adf69ee6ac344e7ef205099af3686ddf7cceaffa111a8789f03b83ed8319856` |
| `experiments/sim-eval-v2/report.json` | `74499b716103e26ef829cb56816bf738d67d3d3e5961848c4cfe37f2e8f4f77d` |
| `experiments/sim-eval-v3/report.json` | `7d1ca46400795908f6ffcd17091d4348e633493923fc030e5160e9f2ff8a8cd6` |
| `experiments/sim-eval-v3b/report.json` | `4c47b2b04e42b06972f7bd9e10da51d219d18a46e273d71fc50e78f2070631cf` |
| `experiments/sim-eval-v3b/decision_log.jsonl` | `9c486601dcac141ccf7453f84b144fbd5d5c491da1b1a32542e7a14a796a4e75` |
| `configs/evaluation_v3.yaml` | `ac4bb7ea743195e6ea860a4f2c34dc546437321f28c811055782fe4b1c5ed842` |
| `data/librispeech/annotations/phase_1c_pilot_30.csv` | `56a4dc49b3a2f5add5c361c2b23edde923c8265a998de76c7e5b87462e5d6a5c` |
| `data/synthetic/manifest.csv` | `abc3cceec6a90e0953ac6614e1a6fee63b91c1401324798e0232ef1aa4f723e9` |
| `data/synthetic/transcripts/variants.csv` | `fd4d3d9a66e68dd8e687a8ab4d6c5484d32774c2d9c08f3c1ecb7a7e7fa89f68` |
| `docs/PHASE_3B_RESEARCH_AUDIT.md` | `f025cb4bf387faea68a1e7cf574f15c47a3afc83c0a36c7264cb7399bec8560b` |

Phase 5 files that must also stay frozen, checked by content rather than added to the historical hash list:

- `experiments/phase5/run-20261102-stage4-scored/validation/frozen_policy.json` SHA-256 `0840ee89f84553b2d345d56c141056f57428950320904b23abd11f91ac7393b9`
- `test_cases_read` is `false`
- `data/phase5/challenge_cases.jsonl` `8fcc2eabfc7f7d115059f0425fb56f27c4108cfe9f52a601201ff1fd61d45fae`
- `data/phase5/oracle_labels.jsonl` `7ac4aa1abe6f4ba94b80823aaa2c49580013bf1fafb155ff6ba90cf024cdd05b`
- `data/phase5/splits.json` `708cc65b8036b239bb26523f44f1db59b87dd3cf4f8fa12def2f50b3f848f6d0`

`experiments/phase5/run-20261102-stage4` is the earlier scoring directory. Cite `run-20261102-stage4-scored` only. The last full suite recorded with these hashes was 138 passed. This audit did not rerun pytest.

## Phase 5 results, read from the scored summary

Dataset `synthetic-semantic-integrity-v1`, seed `20261105`, 280 cases, validation 56, test 56. The test cases use 14 of 40 test parents. The oracle is a same-session specification, not human gold. The test split contains no `April 3` and no `181`.

| Phase 5 id | Strategy | Coverage | Unsafe commits | Native path safety | Safe commits |
| --- | --- | ---: | ---: | ---: | ---: |
| E0, E1, E2 | prefix | 48/56 | 42/48 | null, id not emitted | 4 |
| E3 | forced lexical | 0/56 | null | null | 0 |
| E4 | lexical v3 | 53/56 | 47/53 | null | 6 |
| E5 | `b2_semantic_v4` | 41/56 | 35/41 | null | 6 |
| E6 | `b2_semantic_v5` | 23/56 | 14/23 | 9/23 | 9 |

The category log in `docs/PHASE_5_RESULTS.md` matches those headlines: negation, maybe, possibly, might, and if-needed were held; both polite controls were committed; three clean retries were emitted; three two-value bundles were held; all 14 in-inventory substitutions were committed. Critical-slot safety on those commits is 0/14. Clean-control false rejects are 0/6. Unnecessary abstention is 0/9.

`run_semantic_v5` accepts `bundle`, `lexicon`, and `switches` only. It reads `candidates`, `bundle_id`, and `case_id`. It has no reference parameter. That is the candidate-only boundary. Phase 6 must not edit this function.

## Evidence-boundary design

Condition A calls the frozen function through a new adapter. The adapter builds a fresh bundle containing only candidate id, text, provenance, and rank. It does not forward a reference, a parent transcript, or an oracle field, even as an unused key.

Condition B is a new identity, `b2_reference_aware_v1`, in a new package. It may call the frozen Phase 5 function and then apply one extra check. It may not change Phase 5 source. The reference arrives as a second argument with provenance `EXPLICIT`. It is verification evidence. It is not inserted into candidate text and it is not a candidate that can be committed.

Proposed contract:

| Evidence | Candidate-only | Critical-slot reference | Full-transcript reference | Oracle only |
| --- | --- | --- | --- | --- |
| Candidate text, id, provenance | yes | yes | yes | yes |
| Slots read from that candidate | yes | yes | yes | yes |
| Intent and critical values as a separate signal | no | yes | yes | yes |
| Parent transcript | no | no | yes | yes |
| Expected action, commitment, or path | no | no | no | yes |

Mode 1 and mode 2 are not the same advantage. Mode 1 can show that 8 AM disagrees with an authorized 7 AM. It does not show wording that never entered the slot record. Mode 2 adds the parent transcript. On the frozen templates, that transcript usually restates the same slots. It adds something only when the sentence carries a cue the slot record omits, such as "Maybe" or "Please" on the parent. The primary comparison is mode 1. Mode 2 stays a separate sensitivity run. If they match, the report should say the transcript added no decision on this grammar.

Phase 6 ids must not be read as Phase 5 ids.

| Phase 6 id | Meaning | Not the same as |
| --- | --- | --- |
| E0 | one frozen prefix baseline | Phase 5 E0–E2, which were reported together because they matched |
| E1 | frozen lexical v3 | Phase 5 E4 |
| E2 | frozen `b2_semantic_v4` | Phase 5 E5 |
| E3 | unchanged `b2_semantic_v5` | Phase 5 E6 |
| E4 | reference-aware, critical slots only | no Phase 5 counterpart |
| E5 | reference-aware, full parent transcript | no Phase 5 counterpart |

The comparison that isolates the reference is E3 versus E4. E5 is not pooled with E4.

Recommended behavior, still unimplemented: if v5 holds for negation, uncertainty, conditionality, conflict, or provenance, the reference-aware wrapper also holds. The reference may block a commit or select another bundle candidate that matches it. It may not invent a candidate from the parent sentence. A missing reference is a hold, not a guess.

No validation weight search. The Phase 5 gates stay as they are. Validation would confirm the contract. It would not be used to retune after the test labels are read.

## Dataset feasibility

Read-only parents in `data/synthetic/annotations/annotations.jsonl`: 200 rows, 198 eligible. Excluded: `utt-020`, `utt-040`. Counts: 20 book, 19 cancel, 19 check-appointment, 20 weather, 20 reminder, 20 transfer, 20 balance, 20 transaction, 20 music, 20 general information.

A new set `synthetic-reference-integrity-v1` can be built without editing Phase 5 data. Suggested seed `20261106`. Do not force a round target.

Limits that are already visible:

- Reminder and transfer parents are 20 each. Time and amount categories cannot exceed 20 without reusing a parent inside a category.
- `April 2` occurs on 4 parents. `7 AM`, `8 AM`, `6 PM`, `5 PM`, and `180` each occur on 1 parent. `181` occurs on none. Each parent can enter only one split, so each of those substitutions can be scored in only one split. To avoid the Phase 5 outcome, where the test split received neither `April 3` nor `181`, the construction rule should place the `180` parent and at least one `April 2` parent and the `7 AM` parent into the test list before any score is computed. That is a predeclared allocation, not a fit to labels.
- Two critical slots exist only on `transfer_money`, and the second slot is always `rupees`. There is no second currency. A balanced "multiple critical-slot conflict" category cannot be built from this grammar. The honest version is a small amount-plus-unsupported-currency probe, or the category is dropped and the shortfall is recorded.
- Missing-reference cases should be the same bundles with the signal omitted, not a second candidate set.
- Out-of-inventory behavior cannot be imported from the Phase 5 test. Phase 6 has to build those rows itself, and the counts will be small.

## Proposed files, not created

- `src/cascadeguard_phase6/` with `evidence_contract.py`, `reference_signal.py`, `critical_slot_comparator.py`, `reference_verifier.py`, `candidate_only_adapter.py`, `reference_aware_controller.py`, `phase6_registry.py`, `phase6_metrics.py`, `phase6_oracle.py`
- `tests/phase6/`
- `data/phase6/`
- `scripts/run_phase6.py`, `scripts/audit_phase6.py`
- `experiments/phase6/<new-run-id>/`
- `docs/PHASE_6_DESIGN.md`, `PHASE_6_EVIDENCE_CONTRACT.md`, `PHASE_6_DATASET.md`, `PHASE_6_METHODOLOGY.md`, `PHASE_6_RESULTS.md`, `PHASE_6_ABLATIONS.md`, `PHASE_6_INFORMATION_BOUNDARY.md`, `PHASE_6_LIMITATIONS.md`, `PHASE_6_RESEARCH_AUDIT.md`, `CASCADE_PIPELINE_FINAL_RESEARCH_REPORT.md`

## Risks

The two conditions can be isolated, because v5 has no reference argument and the new package can pass a stripped bundle. Isolation fails if the reference is stored on the object that v5 receives, or if the new controller is described as candidate-only.

Reimplementing the modality gates would make H4 a new controller result. Calling the frozen function and only adding a reference check keeps the comparison on the information boundary.

The same session would again write both the specification and the checker. That remains a specification match, not human gold.

Parent clusters will be small. Intervals should carry the cluster count. A missing-information hold is not a controller bug. A reference-assisted hold is not a candidate-only improvement.

## Not implemented

No Phase 6 code, data, tests, runner, or scored run exists. Implementation waits for a separate authorization.
