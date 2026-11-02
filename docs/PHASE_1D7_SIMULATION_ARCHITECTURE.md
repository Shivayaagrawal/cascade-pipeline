# Phase 1D.7 simulation architecture

**Date:** 2026-11-02  
**Status:** proposed facade. Not permission to create it.

```text
Synthetic transcript input
        |
Input validation and provenance
        |
Execution strategy router
        |
        +-- b0_prefix              -> run_b0
        +-- b1_prefix              -> run_b1
        +-- b2_prefix_controller   -> run_b2
        +-- b1_forced_lexical      -> forced_selection
        +-- b2_lexical_v3          -> recovery_action
        |
Decision normalization
        |
Evaluation and audit record
        |
Metric aggregation
        |
Research report
```

The router calls one identity per record. It does not blend prefix and lexical results into one system.

## Calls that preserve current behavior

| Identity | Call | Facade must |
| --- | --- | --- |
| `b0_prefix` | `run_b0(utterance_id, one Hypothesis)` | Pass one `synthetic_edit` or, for the oracle only, `reference_passthrough`. |
| `b1_prefix` | `run_b1(utterance_id, tuple of Hypothesis)` | Keep provenance `synthetic_edit`. Reject `native_nbest`, which `run_b1` already rejects. |
| `b2_prefix_controller` | `run_b2(utterance_id, one_best, alternatives)` | Leave `max_retries` at the existing default unless a later authorization changes it. It does not. |
| `b1_forced_lexical` | `forced_selection(strings, lexicon)` | Keep the string list beside the provenance. The function itself takes strings. |
| `b2_lexical_v3` | `recovery_action(primary, lexicon, retry_candidates, min_support)` | Pass a second list only when the condition already has one. Do not change `min_support`. |

An empty bundle is handled before any of these calls: HOLD, reason `EMPTY_BUNDLE`, no frame, no call.

## Decision normalization

Prefix `SystemOutput` carries intent and slots even when `action` is CLARIFY or HOLD, because `run_b2` copies `decision.selected`. The normalized record stores that text as raw attached output and sets the committed frame to null for CLARIFY and HOLD. CONTINUE and RETRY are the only actions with a committed frame.

Lexical CLARIFY may carry an intent with an empty slot map. The committed frame is still null. HOLD from `decide_selective` on a non-empty list uses reason `no_intent_evidence` or `intent_disagreement`, not `EMPTY_BUNDLE`.

Normalization does not merge `b2_prefix_controller` with `b2_lexical_v3`. Every record keeps `execution_identity`.

## Report

Aggregation uses the existing metric functions and the denominators in `docs/PHASE_1D7_EVALUATION_CONTRACT.md`. A new report directory is required. The frozen directories are not that directory.

This diagram authorizes nothing.
