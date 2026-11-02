# Phase 1D.7 B0 specification

**Date:** 2026-11-02  
**Identity:** `b0_prefix`  
**Function:** `run_b0`. This specification does not change it.  
**Status:** adapter boundary only. The adapter is not authorized.

## Input

One `SyntheticTranscriptInput` with `candidate_source` `SINGLE_TRANSCRIPT`. On the frozen comparison the text is variant `v0` of `synthetic-seed17-v1` and provenance is `synthetic_edit`. The gold sentence is a different condition, `reference_passthrough`, and is not a member of the proxy list.

## Parser

`run_b0` calls `score_hypothesis`, which calls `classify_intent` and, unless the prediction is ambiguous, `extract_slots`. Confidence is 0, 0.5, or 1 under the existing rules. The parser does not see gold. It does not record negation or uncertainty. `normalize()` is not applied before the parser.

## Output

`SystemOutput`: utterance id, the same text, intent or null, slot map, elapsed seconds, and `action` left as null. B0 does not choose CONTINUE or HOLD. It always returns the parse. The facade sets `committed` true for this identity because B0 has no abstention. That flag is a record label. It is not a change to `run_b0`.

## Errors

| Input | Existing behavior | Facade |
| --- | --- | --- |
| Provenance `native_nbest` | `assert_synthetic_not_nbest` raises. | Reject before the call when the source is not `SINGLE_TRANSCRIPT` with an allowed provenance. |
| Empty bundle | Not a B0 input. B0 is one transcript. | Do not call `run_b0`. This is not `EMPTY_BUNDLE` unless the caller claimed to send one transcript and sent none. In that case the facade still uses HOLD / `EMPTY_BUNDLE` and does not call `run_b0`. |
| Empty string as the one transcript | Cues miss. Intent is null. | Keep that result. Do not replace it with `EMPTY_BUNDLE`. |

## Evaluation

Score with gold from the manifest: intent accuracy, slot micro-F1, exact frame. Do not fill selective risk. Frozen prefix B0 exact frame on the v1 first candidates is 0/200. The facade may cite that figure. It may not overwrite `experiments/B0`.

## Adapter boundary

The adapter builds one `Hypothesis` and calls `run_b0`. It does not edit `pipeline.py`. A speech transcript is not a B0 input in this project.
