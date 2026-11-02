# Phase 1D.5 B1 implementation plan

**Date:** 2026-11-02  
**Status:** plan. No selector was added.

B1 is any path that reads more than one transcript for one id and returns one frame or an explicit abstention. Three strategies exist. They are not one strategy with a flag.

## Ingestion and provenance

| Bundle | Generator | Provenance | Budget on the frozen v1 comparison |
| --- | --- | --- | --- |
| v1 injector | `error_injector` | `synthetic_edit` | 3 |
| Paraphrase, slot-removed, split | `candidate_diversity.py` | written strings; the v3 caller labels them `synthetic_edit` when it builds `Hypothesis` objects | 3 |
| Gold sentence | generator | `reference_passthrough` | oracle only, not in the bundle |
| Future N-best | a recognizer call that returns several hypotheses | `native_nbest` or `beam_hypothesis` | unavailable |

Validation: every candidate shares the utterance id. The bundle’s `candidate_source` is `SYNTHETIC_PROXY` for every current list. `GENUINE_ASR_NBEST` is refused until a recognizer produced the list. `run_b1` already raises if any item is `native_nbest`.

The v3 functions take `list[str]`. Provenance lives outside those functions. A future caller must keep the provenance beside the strings. Passing bare strings into a report that omits provenance would hide the proxy label.

## Strategy 1. Prefix selection

**Function:** `select_candidate`, used by `run_b1`.  
**Inputs:** tuple of `Hypothesis`.  
**Output:** one `ScoredCandidate`. Always a frame or a null intent.  
**Rule:** score each candidate, sort by descending confidence, then ascending rank.  
**Ties:** equal confidence keeps the earlier rank because the sort key is `(-confidence, rank)`.  
**Missing slots:** the 0.5 confidence rule can lose to a later candidate with confidence 1.  
**Contradictions:** an ambiguous candidate scores 0 and loses to any higher score.  
**Unsupported:** confidence 0 stays in the list and is chosen only when every candidate scores 0.  
**Empty list:** `ValueError`.

Frozen result on the v1 list: exact frame 1/200, intent accuracy 0.685, slot micro-F1 0.10434782608695653. This is the same-reader comparison against prefix B0 at 0/200. The gain is one utterance.

## Strategy 2. Forced lexical selection

**Function:** `forced_selection`.  
**Inputs:** list of strings and the closed lexicon.  
**Output:** `(intent or null, slot map)`. Always returns. A null intent means no candidate had exactly one intent.  
**Rule:** prefer a single intent, then more critical slots that have exactly one lexicon value, then the earlier index.  
**Ties:** the sort key uses `-index`, so the earlier index wins when intent count and filled-slot count match.  
**Missing slots:** the returned map simply omits them. Exact-frame scoring then fails.  
**Contradictory slots:** a slot with a value tuple whose length is not 1 is omitted.  
**Unsupported:** all candidates with no single intent return `(None, {})`.  
**Empty list:** `ValueError`.

Frozen v1-list exact frame is 145/200. That number always answers. It is not selective coverage, which is also 145/200 and counts commits. The mismatch count is 200 − 145 = 55. That 55 is not selective risk.

## Strategy 3. Selective agreement

This is the commit rule documented with B2. It can abstain. It is not a third B1 ranker. Reports that need “B1 always answers” use strategy 1 or 2 and name which one.

## Disagreement and ranking

Prefix disagreement is the `ambiguous` flag or a lower confidence. Lexical disagreement is `candidate_disagrees` or the selective reasons `slot_value_disagreement` and `intent_disagreement`. Ranking is the sort above. There is no learned ranker.

## Evaluation

Same ids and same gold as B0. State the reader, the list name, and the budget in the column header. Forced exact-frame accuracy uses all 200 utterances. Do not put it in the selective-risk column.

## Future work

Genuine N-best integration is outside this simulation. If a later project has a recognizer list, it would use a different provenance and would not be pooled with `SYNTHETIC_PROXY`. `beam_size=1` would still be one string. No new selector is specified for the current project.
