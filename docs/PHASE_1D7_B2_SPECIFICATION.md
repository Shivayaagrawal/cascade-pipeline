# Phase 1D.7 B2 specification

**Date:** 2026-11-02  
**Status:** two controllers. Their actions are not added together. Neither function is changed. The adapters are not authorized.

## A. `b2_prefix_controller`

**Functions:** `detect_failure` and `decide`, through `run_b2`.  
**Input:** one-best `Hypothesis`, the other written hypotheses, `max_retries` default 1. Gold is not an input. The edit category is not an input.  
**Confidence:** only 0, 0.5, and 1. Below 1.0 is `low_confidence`. No new threshold.

| Action | When the code does this | Committed frame in the facade record |
| --- | --- | --- |
| CONTINUE | Failure is `none`. | The one-best frame. |
| RETRY | An alternative has higher confidence and failure `none`, and retries remain. | That alternative’s frame. This is written text, not a decode, and it is not labeled `simulated_candidate_rescore`. |
| CLARIFY | Failure is `ambiguous`. | Null. `run_b2` still attaches the one-best text. The facade stores that attachment as raw output only. No question string. |
| HOLD | No usable alternative or no retry budget. | Null. The attached one-best text is raw output only. |

Frozen counts on the v1 cascade: CONTINUE 61, RETRY 52, CLARIFY 22, HOLD 65. Those stay in the historical report.

## B. `b2_lexical_v3`

**Functions:** `decide_selective` and `recovery_action`.  
**Input:** primary strings, lexicon, optional second list, `min_support` default 1. The published curve also includes 2 and 3. The default is not retuned.  
**Gold:** used only by `expected_recovery` at scoring time.

| Action | When the code does this | Mechanism | Committed frame |
| --- | --- | --- | --- |
| CONTINUE | Primary decision is COMMIT. | `primary_bundle` | That frame. |
| RETRY | Primary does not commit, a second list is passed, and that list commits. | `simulated_candidate_rescore` | The second list’s frame. Correct only if that frame matches gold. |
| CLARIFY | No commit, and the primary or the retry decision is CLARIFY. | `primary_bundle` | Null. No question text. |
| HOLD | No commit and no CLARIFY. | `primary_bundle` | Null. |

On the v1 list with no second bundle the frozen counts are CONTINUE 145, RETRY 0, CLARIFY 48, HOLD 7. Coverage 145/200. Correct commits with abstention scored wrong 142/200. Unsafe commits 3/145, ids `utt-121`, `utt-124`, `utt-129`.

If the caller passes an empty list to `decide_selective`, the function returns HOLD with reason `no_intent_evidence`. The facade must not do that. An empty bundle stops at the facade with reason `EMPTY_BUNDLE`.

## What neither controller does

Neither calls a recognizer. Neither writes a clarification question. Neither is allowed to fill a slot that the selected text did not contain. A future report prints both identities or one named identity. It does not print a single “B2” that sums their actions.
