# Phase 1D.7 B1 specification

**Date:** 2026-11-02  
**Status:** two strategies, two records. No new selector. The adapters are not authorized.

B1 reads a `SYNTHETIC_PROXY` bundle and returns a frame. It does not abstain. Abstention belongs to B2.

The frozen v1 list gives prefix exact frame 1/200 and forced lexical exact frame 145/200. Those numbers use different readers. The gap is not a pure candidate-count effect. Prefix B0 on the first candidate of that same list is 0/200. That pair, 0/200 versus 1/200, is the same-reader comparison.

## A. `b1_prefix`

**Function:** `run_b1`, which calls `select_candidate`.  
**Input:** tuple of `Hypothesis`, provenance `synthetic_edit`.  
**Rule:** higher confidence, then earlier rank. Confidence is the existing 0, 0.5, or 1 rule.  
**Missing slots:** can lower confidence to 0.5 for `book_appointment`, `transfer_money`, and `play_music` when the slot map is empty.  
**Contradiction:** an ambiguous parse scores 0.  
**Empty tuple or empty list:** `select_candidate` raises `ValueError`. The facade does not call it. The facade returns HOLD / `EMPTY_BUNDLE`.  
**Output:** one `SystemOutput` with a parse. `action` is null. The facade marks the frame committed because this identity always answers.

`run_b1` already rejects `native_nbest`.

## B. `b1_forced_lexical`

**Function:** `forced_selection`.  
**Input:** list of strings plus the closed lexicon. Provenance stays on the bundle, not inside the function.  
**Rule:** one intent, then more critical slots with exactly one lexicon value, then the earlier index.  
**Missing or contradictory slots:** omitted from the returned map. Exact-frame scoring then fails if gold needed them.  
**No single intent:** `(None, {})`.  
**Empty list:** raises `ValueError`. The facade does not call it and uses `EMPTY_BUNDLE` instead.  
**Output:** always one attempt at a frame. It is not a safety decision and it is not selective coverage.

The frozen forced exact-frame count is 145/200. Selective coverage is also 145/200. They are different measures. The facade stores them on different identities.

## Records

A comparison table names the identity, the list (`v1_injector` or another published list), and the candidate count. Prefix and lexical rows are not pooled. No third selector is specified.
