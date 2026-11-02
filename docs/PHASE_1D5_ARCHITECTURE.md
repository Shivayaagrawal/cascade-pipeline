# Phase 1D.5 architecture

**Date:** 2026-11-02  
**Status:** conceptual. No module was added.  
**Metric authority:** `docs/PHASE_1D3_METRIC_DEFINITIONS.md`.  
**Comparison authority:** `docs/PHASE_1D3_EXPERIMENTAL_PROTOCOL.md`.

The current project starts at the written transcript. Audio, preprocessing, and ASR are future work, not layers this simulation has to finish.

The path that runs is:

`Written string or written bundle → prefix reader or lexical reader → optional controller → evaluation record`

Synthetic audio files from `say` exist on disk. No B0, B1, or B2 result decodes them, and the simulation does not need them.

## Layers

### Layer 1. Input and transcript interface

Owns utterance id, text, provenance, and rank. Existing type: `Hypothesis` plus `ASRResult`.

| Mode | Provenance allowed now | Owner |
| --- | --- | --- |
| One transcript | `synthetic_edit` for B0 on an edit. `reference_passthrough` only for the gold-transcript oracle. | `run_b0` |
| Proxy bundle | `synthetic_edit` | `run_b1`, `run_b2`, or the v3 functions that currently take bare strings |
| Recognizer, one string | `single_segment_text` | `WhisperAdapter`, not used |
| Recognizer N-best | `native_nbest` or `beam_hypothesis` | Missing. The synthetic path rejects `native_nbest`. |

Future audio ingestion is `ASRBackend.transcribe`. `SyntheticHypothesisASR` does not implement it. Preprocessing for a recognizer is not built.

### Layer 2. Transcript normalization

WER and CER call `normalize()` after scoring, on both sides. The prefix parser and the lexical reader see the original string. A later pipeline must not casefold or strip tokens before those readers. `normalize()` does not delete the word “not”. The readers still do not record negation or uncertainty, so a string can contain those words and produce no such finding. That limitation stays in the audit record.

### Layer 3. NLU and semantic frame

Two readers, not one interchangeable parser.

| Reader | Intent | Slots | Used by |
| --- | --- | --- | --- |
| Prefix | `classify_intent` | `extract_slots` | `b0_prefix`, `b1_prefix`, `b2_prefix_controller` |
| Lexical | `assess` intent hits | lexicon values in `CRITICAL_SLOTS` | `b1_forced_lexical`, `b2_lexical_v3` |

The ten intents and their slot names are the ones in `intent_schema.json` and `CRITICAL_SLOTS`. No new intent is proposed.

Prefix confidence is 0, 0.5, or 1 from the rules in `score_hypothesis`. Lexical support is a count of complete candidates. Neither is a calibrated probability.

### Layer 4. Candidate comparison

| Strategy | Function | Tie rule | Missing slots | Contradictory slots |
| --- | --- | --- | --- | --- |
| Prefix selection | `select_candidate` | Higher confidence, then lower rank. | Confidence 0.5 for book, transfer, and play when the intent is present and the slot dict is empty. | Ambiguous intent sets confidence 0 and clears slots. |
| Forced lexical | `forced_selection` | One intent, then more filled critical slots, then earlier index. | Returns a partial frame. Callers must not treat it as a commit. | A slot with two lexicon values is omitted from the returned frame. |
| Selective | `decide_selective` | Not a ranker. It commits only when complete candidates agree. | CLARIFY, reason `intent_without_required_slots` or `slot_support_below_threshold`. | CLARIFY, reason `slot_value_disagreement`. Intent clash across complete frames is HOLD. |

A future ranking method is not part of this blueprint.

### Layer 5. Failure diagnosis

Operational categories, meaning the code already branches on them:

| Category | Prefix controller | Lexical layer |
| --- | --- | --- |
| Missing intent | `unknown` when intent is null or confidence is 0 | HOLD `no_intent_evidence` |
| Conflicting intent | `ambiguous` | CLARIFY `multiple_intents_in_a_candidate`, or HOLD `intent_disagreement` |
| Missing required slot | confidence 0.5 for three intents; other intents can still score 1.0 with an empty slot dict | CLARIFY |
| Conflicting slot values | not a separate prefix state | CLARIFY `slot_value_disagreement` |
| Low support | confidence below 1.0 is `low_confidence` | CLARIFY `slot_support_below_threshold` when complete candidates are fewer than `min_support` |
| Incomplete frame | the 0.5 case above | the missing-slot CLARIFY |

Speech-only diagnostics, such as a low decoder probability or an acoustic timeout, are blocked. No decoder score is stored on the frozen results.

### Layer 6. Recovery controller

The controllers stay separate. Details are in `docs/PHASE_1D5_B2_IMPLEMENTATION_PLAN.md`.

`simulated_candidate_rescore` is the RETRY this project uses. A later speech project would have to define a new decode under a different name. That work is outside the current scope.

### Layer 7. Evaluation and audit

Existing functions implement the approved metrics. The evaluation record for a future run uses `docs/PHASE_1D2_EVALUATION_CONTRACT.md` and does not retune a denominator. v3b already writes a 200-row log for the selective layer. Prefix B2 stores an action on `SystemOutput` and a `RecoveryDecision`.

## What a later implementation would add

Only after a separate authorization: a thin facade that builds the conceptual records in `docs/PHASE_1D5_INTERFACE_CONTRACTS.md` by calling the existing functions, writes to a new directory, and hashes the frozen files before and after. That facade is not started here.
