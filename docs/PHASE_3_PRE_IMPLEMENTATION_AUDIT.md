# Phase 3 pre-implementation audit

Status: recorded before Phase 3 code, data, or experiments were added. This file does not replace any earlier report.

Repository: CascadeGuard. HEAD `f55b5bd`. The working tree already had 13 tracked documentation files modified from earlier phases, and the rest of `src/`, `tests/`, `data/`, `experiments/`, and `configs/` was untracked. Those tracked documentation edits were not made for Phase 3 and were not reverted.

Test baseline before Phase 3 changes: `python3 -m pytest -q` reported `98 passed in 5.89s`.

## Architecture the code actually implements

`assess()` in `src/cascadeguard/evaluation/semantic_evidence.py` returns `Evidence(intents, slots)` only. `frame_is_complete()` requires one intent and exactly one value for every name in `CRITICAL_SLOTS`. Every intent in that table requires at least one slot. There is no intent whose required-slot list is empty.

The facade router accepts only:

- `b0_prefix` → `run_b0`
- `b1_prefix` → `run_b1`
- `b2_prefix_controller` → `run_b2`
- `b1_forced_lexical` → `forced_selection`
- `b2_lexical_v3` → `recovery_action`

`route()` raises `UnknownStrategyError` for any other name. An empty bundle returns `HOLD` / `EMPTY_BUNDLE` and does not call those functions. `CLARIFY` and `HOLD` do not commit a frame. Lexical `RETRY` is `simulated_candidate_rescore`.

Prefix intent cues and lexical `intent_hits()` are different matchers. The lexical general-information cue includes the substring ` your `.

## Frozen hashes at the start of Phase 3

All 12 stored baselines matched:

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

Additional files hashed so later edits can be detected. These hashes were not in the older baseline list:

| File | SHA-256 |
| --- | --- |
| `configs/evaluation_v3b.yaml` | `01df50b78117fa08acec59bcb4c977def27e719306d141743b91f9a760dee0ed` |
| `data/synthetic/annotations/annotations.jsonl` | `f27d9f2b01e2ccac310f08d92c505524ec86070184bce475c054f3b8cadac06c` |
| `data/manual_audit/annotations.csv` | `f5ea4fb5c98215dcb80650404091ea6ca31de9da20228f1ce3a0dffba251dd76` |
| `data/manual_audit/llm_comparison_report.json` | `a6986f52bc1fc76fcdf553b06b663d045173714be6cc8d7c8dd8942d2d720e58` |
| `data/manual_audit/comparison_report.json` | `002709d9e2bd77c672d9bc2adc4477f59010108527b3fee90cc67015d155dc15` |
| `data/manual_audit/sampling_manifest.json` | `72ca484c30b3eab3694ca794661a33a0acfada6016655741d51f61298ca363fd` |
| `data/manual_audit/sealed_gold.json` | `7482db137736b8c74ddfda8b754b586bc246be494d47ccecaf7825b1f02a9f15` |

## Blueprint differences that bind the implementation

The approved challenge list has eight categories, not a separate 30-case bucket for temporal corruption and numerical corruption. A single fluent candidate whose date was swapped for another real date cannot be rejected without the parent gold or a second candidate. Those swaps are therefore two-candidate `CONTRADICTORY_EVIDENCE` cases. `SLOT_VALUE_CORRUPTION` uses the placeholder `other`, which the text itself shows is not a lexicon value.

`synthetic-seed17-v1` has two empty slot maps: `utt-020` (`Cancel my appointment`) and `utt-040` (`When is my appointment?`). Both intents require `date` in `CRITICAL_SLOTS`. Decision 6 admits an empty map only when the intent requires no slots. No intent meets that condition, so both parents are excluded. They are not treated as valid intent-only requests.

The LLM audit figures 30/30, 57/90, and 43/90 stay exploratory. They are not labels for this challenge set.
