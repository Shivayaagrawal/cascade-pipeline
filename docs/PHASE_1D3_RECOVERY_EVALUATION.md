# Phase 1D.3 recovery evaluation

**Date:** 2026-11-02  
**Status:** protocol for actions that are already implemented. No new recovery behavior is added.

Two implementations exist. A result names one of them.

| Implementation | Decision function | Failure inputs | RETRY mechanism |
| --- | --- | --- | --- |
| `b2_prefix_controller` | `recovery_controller.decide` | `none`, `ambiguous`, `unknown`, `low_confidence` from the prefix score. Confidence below 1.0 is `low_confidence`. Injected category labels are not inputs. | Selects another written hypothesis when its confidence is higher and its failure is `none`. This is not a second decode. |
| `b2_lexical_v3` | `recovery_action` | Missing critical slot, multiple intents, slot disagreement, support below `min_support`, no intent evidence. Gold is used only at scoring time. | Returned only when the caller passes a second bundle that can commit. The label is `simulated_candidate_rescore`. |

A completed simulated retry establishes that the controller committed the second bundle. It establishes that the meaning was recovered only when that committed frame equals the gold frame.

## Four actions

### CONTINUE

| Item | Prefix controller | Lexical layer |
| --- | --- | --- |
| Trigger | Prefix failure is `none`. | The primary bundle meets the selective commit rule. |
| Expected behavior | Keep the one-best frame. | Keep the agreed complete frame from the primary bundle. |
| Success | The kept frame equals gold. | The kept frame equals gold. |
| Failure | The kept frame does not equal gold. This is an unsafe commit. | Same. The v1-list failures are the three reminder-time commits. |
| Evidence required | The frame and the gold frame. | Same. |
| Supported now | Yes, on synthetic transcripts. Frozen count 61/200. | Yes. Frozen v1-list count 145, with RETRY 0. |

### RETRY

| Item | Prefix controller | Lexical layer |
| --- | --- | --- |
| Trigger | An alternative has higher confidence and failure `none`, and `max_retries` is at least 1. | A second bundle is supplied and that bundle can commit. |
| Expected behavior | Replace the frame with the alternative’s frame. The alternative was already written. | Commit the second bundle’s frame. |
| Success | The committed alternative frame equals gold. | The committed second-bundle frame equals gold. Running the retry is not the success test. |
| Failure | The alternative frame does not equal gold, or the controller retries when the derived label says another action. | Same for the frame. A retry of a second bundle that still lacks the gold frame is a failed recovery even though the action completed. |
| Evidence required | Provenance of the alternative, the committed frame, and the gold frame. | The mechanism string, the second bundle’s identity, and the frame comparison. |
| Supported now | Yes, as rescoring. Frozen count 52/200. | Yes, only in conditions that pass a second bundle. The v1 list has RETRY 0. The slot-removed plus paraphrase condition has RETRY 198, selective risk 0/198. |

### CLARIFY

| Item | Prefix controller | Lexical layer |
| --- | --- | --- |
| Trigger | The chosen parse is `ambiguous`. | Intent evidence without the required slots, or slot values disagree. |
| Expected behavior | Leave the frame unresolved. Ask. Do not fill a slot from outside the candidates. | Same. |
| Success | Against the derived label, the derived label is CLARIFY. Against a future human label, the human label is CLARIFY. | Same. |
| Failure | The system clarifies when the derived label is CONTINUE, or it commits a frame it should have clarified. | On the second-bundle condition the two CLARIFY rows are the empty-date cases. Their derived label is CONTINUE, so derived clarification precision is 0/2. |
| Evidence required | The action and the label source, named as derived or human. | Same. |
| Supported now | Yes, as an action. Frozen count 22/200. There is no dialogue that completes the clarification. | Yes, as an action. v1 list: 48. No follow-up utterance is collected. |

### HOLD

| Item | Prefix controller | Lexical layer |
| --- | --- | --- |
| Trigger | No alternative is usable: no retries left, no alternative, or the best alternative is not a clean higher-confidence parse. | No intent evidence, or complete frames disagree on intent. |
| Expected behavior | Leave the frame unresolved. Do not guess. | Same. |
| Success | The derived or human label is HOLD, and no frame is committed. | Same. |
| Failure | A commit when the label is HOLD, or a HOLD when a complete gold-preserving candidate was available and the label is CONTINUE. | Same. |
| Evidence required | The action, the label source, and confirmation that the stored frame is unresolved. | Same. |
| Supported now | Yes. Frozen count 65/200. | Yes. v1 list: 7. |

## Label sources

| Source | What it is | What a match means |
| --- | --- | --- |
| Derived expected action | `expected_recovery`, from the gold frame and the candidate strings, computed before the decision is read. | The system followed the evaluation rule. |
| Human-annotated expected action | An annotator id, a listened flag, and one of the four actions assigned without reading the system decision. | The system matched a person’s action judgment. |
| Simulated recovery outcome | The frame committed from a bundle the experiment supplied. | The written bundle’s frame matched or failed gold. |
| Operational recovery outcome | A new recognizer call with provenance `retry_decode`, then a frame from that transcript. | The new decode’s frame matched or failed gold. |

No current row has a human-annotated action. Derived accuracy stays labelled derived. The v3 v1-list figure 192/200 is derived. The v2 figure 88/200 is the prefix controller’s published action accuracy and is not rebased onto the lexical rule.

## Scoring rules that stay fixed

- Gold is hidden from both controllers.
- An unsafe commit is a CONTINUE or RETRY whose frame mismatches gold.
- CLARIFY and HOLD are abstentions. They are not unsafe commits.
- Selective risk uses the commit denominator. Zero commits leave the risk undefined.
- Recovery gain subtracts prefix B0’s exact-frame rate on the same ids from the rate of correct commits over all ids.
- The injected corruption category is analysis metadata. It is not a feature of the decision.
- Schema errors are not retried in a loop. `max_retries` on the prefix controller is part of the frozen configuration and is not tuned in this phase.

## What remains untested

A person’s judgment of the right action. A clarification that receives an answer. A second pass through a recognizer. Whether HOLD or CLARIFY is acceptable to a user. Latency of a decode. Those gaps are listed in `docs/PHASE_1D3_BLOCKERS.md`.
