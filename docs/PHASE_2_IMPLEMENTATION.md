# Phase 2 implementation

Cascade Pipeline is a synthetic, text-only simulation. This phase adds an evaluation facade beside the existing experiment code. It does not decode audio, and it does not replace the frozen seed-17 dataset.

The name "Phase 2" in this document means the facade and the separate text audit authorized on 2026-11-02. It is not the older speech NLU Phase 2. Phase 1D.7 had recorded that facade as not authorized and that speech Phase 2 as stopped. This implementation follows the later authorization. Speech recognition, real N-best lists, and Phase 3 were not started.

## Architecture

`src/cascadeguard_facade/` calls the existing functions. It does not reimplement them.

| Module | Responsibility |
| --- | --- |
| `contracts.py` | Candidate, raw output, normalized decision, evaluation, and audit types. |
| `adapters/` | One module per identity. Each calls one existing function. |
| `normalization.py` | Copies a raw result into a commit decision. The raw object is not edited. |
| `recovery.py` | Empty-bundle `HOLD` / `EMPTY_BUNDLE`. It imports no processor. |
| `router.py` | Accepts the five identities and rejects every other name. |
| `audit.py` | Places raw output and the normalized decision on one record. |
| `evaluation.py` | Scores a finished decision with the existing metric functions. Gold is applied after the adapter returns. |
| `manual_audit.py` | Reads the frozen tables and writes a separate audit sample. |

## Data contracts

`CandidateRecord` accepts provenance `synthetic_edit` and `reference_passthrough`. `native_nbest` is rejected at construction. Bundle sources are `SINGLE_TRANSCRIPT` and `SYNTHETIC_PROXY`.

`RawControllerOutput` stores the existing function's text, intent, slots, action, reason, retry mechanism, support, retries, and elapsed time, plus `invoked`. `NormalizedDecision` stores the facade action, reason, committed frame, and answered frame. They are separate objects.

## Adapter mappings

| Identity | Existing function |
| --- | --- |
| `b0_prefix` | `run_b0` on the lowest rank |
| `b1_prefix` | `run_b1` on the rank-ordered bundle |
| `b2_prefix_controller` | `run_b2` with the lowest rank as one-best and the rest as alternatives |
| `b1_forced_lexical` | `forced_selection` |
| `b2_lexical_v3` | `recovery_action` |

There is no sixth identity. Lexical calls use `lexicon_from_utterances()` unless the caller passes a lexicon. `min_support` stays at its existing default of 1 unless the caller sets it. Gold is not an adapter argument.

## Normalization

| Existing result | Facade treatment |
| --- | --- |
| `b0_prefix`, `b1_prefix` | The parse is both the answered frame and the committed frame. These paths always answer. The action field stays empty, with reason `always_answers`. |
| `b1_forced_lexical` | The parse is the answered frame only. `committed_frame` is empty. Reason: `forced_selection_is_not_a_safety_commit`. |
| `CONTINUE` | Commit the selected frame. |
| `RETRY` | Commit the frame produced by the existing retry path. |
| `CLARIFY`, `HOLD` | Commit nothing. Prefix one-best text remains on the raw object only. |

Prefix `RETRY` does not receive the label `simulated_candidate_rescore`. Lexical `RETRY` keeps that label. Lexical `CLARIFY` does not add a question string.

## Recovery

An empty bundle returns `HOLD` and reason `EMPTY_BUNDLE` from `recovery.py`. The router returns that record without calling an adapter. Each adapter also returns before calling its processor if it is invoked with an empty bundle. `select_candidate([])`, `forced_selection([])`, and `decide_selective([])` are unchanged. `EMPTY_BUNDLE` is not the same reason as `no_intent_evidence`.

## Evaluation

`evaluation.py` calls `frames_equal`, `slot_scores`, and `rate`. It does not redefine them.

Controller coverage counts `CONTINUE` and `RETRY` commits. Selective risk counts unsafe commits among those commits. Forced-selection exact frame is scored from `answered_frame` and is not written into the coverage field. An equal count on two measures is not evidence that they describe the same utterances.

## Manual audit

`manual_audit.write_audit` reads `data/synthetic/manifest.csv` and `data/synthetic/transcripts/variants.csv` and writes under `data/manual_audit/`.

Sampling uses one `random.Random(20261102)`. Intents follow `utterance_generator.INTENTS`. Within each intent, ids are sorted and three are drawn with `sample`. The same generator then shuffles presentation order. Each selected id contributes its gold transcript and every `variants.csv` row for that id. `data/synthetic/annotations/annotations.jsonl` is a gold copy, not an edit list, and is not sampled.

`annotations.csv` has the transcript and blank judgement fields. It does not have gold intent, gold slots, strategy, expected action, or system outcome. `annotation_status` is `pending`. `sealed_gold.json` and `sampling_manifest.json` hold labels for a later comparison. The guidelines tell the annotator not to open them while labelling.

## Reproducibility

From the Cascade Pipeline root:

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -c "from pathlib import Path; from cascadeguard_facade.manual_audit import write_audit; write_audit(Path('data/manual_audit'), Path('data/synthetic/manifest.csv'), Path('data/synthetic/transcripts/variants.csv'))"
```

The second command rewrites the derived audit files. It does not rewrite the source tables. Do not run `experiments/run_simulation.py` or the v3 writers.
