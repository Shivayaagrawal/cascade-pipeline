# Phase 1D.5 B2 implementation plan

**Date:** 2026-11-02  
**Status:** plan. Neither controller was edited.  
**Evaluation rules:** `docs/PHASE_1D3_RECOVERY_EVALUATION.md`.

The two controllers are different systems. A table that mixes their action counts is invalid.

## Controller A. Frozen confidence controller

**Id:** `b2_prefix_controller`  
**Code:** `failure_detector.detect_failure` and `recovery_controller.decide`, called from `run_b2`.  
**Inputs:** scored one-best, other hypotheses, `max_retries` default 1. Gold is not an input. The injected error category is not an input.  
**Thresholds:** confidence values are only 0, 0.5, and 1. Anything below 1.0 is `low_confidence`. No other threshold exists. v3 did not fit one. A new numeric threshold is a separate design decision and is not proposed here.  
**Outputs:** `RecoveryDecision` plus `SystemOutput.action`.  
**Audit:** the action, the `FailureKind`, `retries` 0 or 1, and the selected hypothesis text. The selected text is present even when the action is CLARIFY or HOLD. Consumers must read the action before treating the text as a commit.  
**Frozen counts:** CONTINUE 61, RETRY 52, CLARIFY 22, HOLD 65. v2 action accuracy 88/200. v2 unsafe commitment 112/113. Hashes in `docs/PHASE_1D3_REPRODUCIBILITY_PROTOCOL.md`.

| Action | Trigger in code | Downstream | Failure handling |
| --- | --- | --- | --- |
| CONTINUE | Failure is `none`. | Keep the one-best frame. | Unsafe when that frame mismatches gold. |
| RETRY | `max_retries` ≥ 1, an alternative exists, its confidence is higher, and its failure is `none`. | Replace the frame with that alternative. The alternative was already written. | Not a decode. Wrong if the alternative frame mismatches gold. |
| CLARIFY | Failure is `ambiguous`. | Action is CLARIFY. The attached candidate is still the one-best. | No clarification question is generated. The code does not store a missing slot name. |
| HOLD | No retry budget, no alternative, or the best alternative is not a clean higher-confidence parse. | Action is HOLD. Attached candidate is the one-best. | A commit must not be recorded. |

Empty alternatives with a non-none, non-ambiguous failure become HOLD. An empty one-best is not representable: `run_b2` requires a hypothesis.

## Controller B. v3 selective layer

**Id:** `b2_lexical_v3`  
**Code:** `decide_selective` and `recovery_action`.  
**Inputs:** primary string list, lexicon, optional second list, `min_support` default 1. Gold is used only by `expected_recovery` at scoring time.  
**Configuration:** `min_support` 1, 2, and 3 are the published curve, not a value chosen on held-out speech. Changing the default is a design decision. This plan does not change it.  
**Outputs:** action, `SelectiveDecision`, mechanism string.  
**Audit:** v3b log rows already store the action, the reason, support, the frame, `frame_matches_reference`, and `unsafe_decision`. Negation and uncertainty stay unavailable on those rows.  
**Frozen v1 list, support 1:** CONTINUE 145, RETRY 0, CLARIFY 48, HOLD 7. Coverage 145/200. Exact frames with abstention counted wrong 142/200. Selective risk 3/145. Derived action accuracy 192/200. Recovery gain 0.71.

| Action | Trigger in code | Downstream | Failure handling |
| --- | --- | --- | --- |
| CONTINUE | Primary `decide_selective` returns COMMIT. | Commit that frame. Mechanism `primary_bundle`. | Unsafe only when the frame mismatches gold. The three ids are `utt-121`, `utt-124`, `utt-129`. |
| RETRY | Primary does not commit, a second list is passed, and that list commits. | Commit the second list’s frame. Mechanism `simulated_candidate_rescore`. | Correct only when that frame matches gold. The slot-removed plus paraphrase condition has 198 such commits, all matching, and 2 CLARIFY. |
| CLARIFY | No commit, and the primary or the retry decision is CLARIFY. | No frame is committed. | The reason string is the diagnosis. No user-facing question text is built. |
| HOLD | No commit and no CLARIFY decision. | No frame is committed. | Includes `no_intent_evidence` and `intent_disagreement`. |

### RETRY, two meanings

| Name | What it is |
| --- | --- |
| `simulated_candidate_rescore` | The caller supplied written strings. This is the only implemented RETRY. |
| Operational retry | A future `transcribe` call with provenance `retry_decode`, a timeout, and a retry cap written in that run’s config. Not implemented. An unavailable recognizer stays blocked rather than falling through to the simulated label. |

### CLARIFY content

The lexical reason names the gap: multiple intents, intent without required slots, slot disagreement, or support below `min_support`. A future question would name the intent and the missing or disputed slot names from that decision. The current code does not format that question. The prefix controller’s CLARIFY does not name a slot. Building question text is a design decision, not part of the frozen behavior.

### HOLD

HOLD and lexical CLARIFY store a null intent and an empty slot map on the selective decision, except slot-disagreement and low-support CLARIFY, which keep the intent and still use an empty slot map. Evaluation of the abstention column uses a null intent and an empty map, as `selective_report` does. That is what keeps abstention from counting as a correct frame.

## Facade rule for an empty bundle

When a future facade is authorized, an empty candidate bundle returns HOLD with reason `EMPTY_BUNDLE` before any existing function is called. `select_candidate` and `forced_selection` still raise `ValueError` on empty input. `decide_selective([])` still returns HOLD with reason `no_intent_evidence`. Those functions stay as they are. The facade reason is not a rename of `no_intent_evidence`.

## Shared failure cases

| Case | Prefix controller | Lexical layer | Future speech |
| --- | --- | --- | --- |
| Empty candidate list | `select_candidate` and a B1 call raise. `run_b2` requires a one-best, so this case is not reached there. | `decide_selective([])` returns HOLD. `forced_selection` raises. | A facade must log which function ran. |
| Missing frame | Null intent, empty slots, confidence 0. | HOLD or CLARIFY as above. | Same, after a real hypothesis exists. |
| Contradictory candidates | Ambiguous parse, or a lower confidence. | CLARIFY or HOLD by reason. | Same readers, new provenance. |
| No eligible retry | HOLD. | HOLD or CLARIFY when no second bundle is passed. v1 list RETRY count is 0. | Do not invent a bundle. |
| Exhausted retry budget | `max_retries` < 1 leads to HOLD for non-ambiguous failures. | No numeric budget. One second list is the only retry. | A cap belongs in a future config. |
| Unavailable ASR | Not applicable. This controller never calls one. | Same. | Block the run. Do not substitute proxy text. |
| Timeout | Not implemented. | Not implemented. | A design decision. No number is set here. |
| Repeated failure | One retry, then the alternative’s own failure can CLARIFY or HOLD. | A second list that also fails does not retry again. | A loop is out of scope. |

Latency of either controller on text is not ASR latency.
