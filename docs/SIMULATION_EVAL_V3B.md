# Simulation Evaluation v3b

**Experiment ID:** `sim-eval-v3b`  
**Role:** Audit and reporting extension of `sim-eval-v3`  
**Date:** 2026-11-02T11:38:41Z  
**Seed:** 17  
**Utterances:** `utt-000` through `utt-199` (200)  
**Authoritative results:** `experiments/sim-eval-v3/report.json`  
**This run writes:** `experiments/sim-eval-v3b/report.json` and `experiments/sim-eval-v3b/decision_log.jsonl`  
**Real-speech validation:** none  
**Phase 1C:** blocked

v3b calls the existing v3 functions on the same v1 injector lists. It does not add a selector, a threshold, or a negation reader. The recomputed v1 section matched the frozen report before anything was written. Where an existing function cannot supply a field, the record says the field is unavailable.

## 1. Candidate evidence

Each candidate in `decision_log.jsonl` stores the transcript, the intent cues from `assess()`, and the lexicon slot values from `assess()`.

Negation evidence is unavailable. Uncertainty evidence is unavailable. `assess()` returns intent cues and slot values only. The transcript is still stored, so a word such as "not" remains visible in the string. On `utt-000`, the third v1 candidate is `Book not an appointment for tomorrow`, and `negation_evidence.available` is false. The audit does not turn that word into a negation label.

## 2. Decision log

The log has 200 rows, one per utterance. SHA-256 `9c486601dcac141ccf7453f84b144fbd5d5c491da1b1a32542e7a14a796a4e75`.

Each row records the triggering reason, support count, selected action, expected action, and safety outcome. The expected action is assigned before the decision is read. A committed frame that differs from the reference is an unsafe decision. CLARIFY and HOLD are not unsafe decisions, and their frame match is null. Whether a retry improved frame correctness is unavailable: this condition passes no second candidate bundle, and a retry is not treated as correct.

The row counts match the frozen v1 aggregate: CONTINUE 145, RETRY 0, CLARIFY 48, HOLD 7. Coverage is 145/200. Selective risk is 3/145. Action accuracy is 192/200. Exact frame, with abstention counted incorrect, is 142/200.

## 3. Slot precision, recall, and F1

These are the `slot_scores()` values already inside the frozen v1 section. Precision uses `predicted_pairs` as its denominator. Recall uses `reference_pairs`.

| Condition | Precision | Recall | F1 | Matched | Predicted | Reference |
| --- | --- | --- | --- | --- | --- | --- |
| B1 prefix selector, all 200 | 18/125 | 18/220 | 0.10434782608695653 | 18 | 125 | 220 |
| Forced slot-aware selector, all 200 | 165/169 | 165/220 | 0.8483290488431877 | 165 | 169 | 220 |
| Selective layer, abstention is an empty prediction | 154/157 | 154/220 | 0.8169761273209549 | 154 | 157 | 220 |
| Selective layer, 145 committed decisions only | 152/155 | 152/155 | 0.9806451612903225 | 152 | 155 | 155 |

The committed-only row does not include the 55 utterances that were not committed.

## 4. Lexical timing

The measured quantity is wall time of `assess()` on one utterance's v1 strings, then wall time of `recovery_action()` on that list. No waveform was decoded. This is not ASR latency. The samples below are from this run on this machine. They are not a benchmark.

| Call | n | Mean seconds | Median seconds | p95 seconds |
| --- | --- | --- | --- | --- |
| `assess()` | 200 | 9.299788798671216e-05 | 9.247899288311601e-05 | 0.00010704202577471733 |
| `recovery_action()` | 200 | 8.85664444649592e-05 | 8.925001020543277e-05 | 9.883299935609102e-05 |

## 5. Ablation map

The six requested names are mapped onto existing functions. Three of them are not separate runs.

| Requested condition | Existing implementation | Distinct run |
| --- | --- | --- |
| Existing baseline candidate selection | `select_candidate` through `b1_frames` | Yes. Exact frame 1/200. |
| Semantic evidence preservation disabled | Same prefix selector. It never calls `assess()`. | No. Same as the baseline. |
| Slot-aware selection disabled | Same prefix selector. Slot-aware selection is `forced_selection`. | No. Same as the baseline. |
| Selective prediction disabled | `forced_selection` | Yes. Always returns one frame. Exact frame 145/200. This is not a safety result. |
| Recovery disabled | `recovery_action` with no retry bundle | Same call as full v3 on the v1 list. |
| Full Synthetic v3 | Same `recovery_action` call on the v1 list | Same recomputation as recovery disabled. |

The frozen recovery condition, slot-removed candidates with the paraphrase list as a second bundle, is cited from `experiments/sim-eval-v3/report.json` under `recovery_with_simulated_retry`. It was not recomputed. That citation records CONTINUE 0, RETRY 198, CLARIFY 2, HOLD 0, coverage 198/200, and selective risk 0/198.

## 6. Preserved files

Hashes matched before and after the write.

| File | SHA-256 |
| --- | --- |
| `experiments/B0/summary.json` | `3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee` |
| `experiments/B1/summary.json` | `597a2800c946018467865dfcf3d8e547bc51c10487596cc134ca2181fee695b2` |
| `experiments/B2/summary.json` | `34a40fdd233f5d4faa00af73c26f1afcc32c4d83922db8df57b7a7184dce0e5d` |
| `artifacts/reports/simulation_report.json` | `7adf69ee6ac344e7ef205099af3686ddf7cceaffa111a8789f03b83ed8319856` |
| `experiments/sim-eval-v2/report.json` | `74499b716103e26ef829cb56816bf738d67d3d3e5961848c4cfe37f2e8f4f77d` |
| `experiments/sim-eval-v3/report.json` | `7d1ca46400795908f6ffcd17091d4348e633493923fc030e5160e9f2ff8a8cd6` |
| `artifacts/reports/simulation_v3/report.json` | `7d1ca46400795908f6ffcd17091d4348e633493923fc030e5160e9f2ff8a8cd6` |
| `configs/evaluation_v3.yaml` | `ac4bb7ea743195e6ea860a4f2c34dc546437321f28c811055782fe4b1c5ed842` |
| `data/librispeech/annotations/phase_1c_pilot_30.csv` | `56a4dc49b3a2f5add5c361c2b23edde923c8265a998de76c7e5b87462e5d6a5c` |

## 7. Reproduce

From the CascadeGuard root:

```bash
python3 experiments/run_simulation_v3b.py
python3 -m pytest -q
```

The writer exits if the recomputed v1 section differs from the frozen report, if the decision log does not add up to that aggregate, or if a preserved file changes. It can write only to a directory named `sim-eval-v3b`. Configuration is `configs/evaluation_v3b.yaml`.

`python3 -m pytest -q` passed 71 tests after this run.

## 8. Limitations

The candidate lists are written variants, not recognizer hypotheses. Agreement is not correctness. The three unsafe commits in the new log are the same reminder-time cases: `utt-121` commits 8 AM against 7 AM, `utt-124` commits 6 PM against 5 PM, and `utt-129` commits 3 PM against 2 PM. Negation in a candidate string is not a finding of the current reader. This audit does not show that the method works on real speech. LibriSpeech Phase 1C stays blocked. `test-clean` was not read. SLURP and Fluent Speech Commands were not downloaded.
