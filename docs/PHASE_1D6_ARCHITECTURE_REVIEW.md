# Phase 1D.6 architecture review

**Date:** 2026-11-02  
**Status:** the synthetic architecture is consistent with the revised scope. No module was added.

## Execution path

```text
Gold sentence + gold intent + gold slots
        |
        +-- one synthetic transcript -------- b0_prefix
        |
        +-- SYNTHETIC_PROXY bundle
                 |
                 +-- prefix reader -- b1_prefix
                 |                 \- b2_prefix_controller
                 |
                 +-- lexical reader -- b1_forced_lexical
                                   \- b2_lexical_v3
                                         CONTINUE
                                         RETRY = simulated_candidate_rescore
                                         CLARIFY  (action only)
                                         HOLD
        |
Evaluation against the gold frame
```

Audio and ASR are not on this path.

## Boundaries

| System | Reads | Must not |
| --- | --- | --- |
| `b0_prefix` | One string. Rank 0 of the v1 list in the frozen comparison. | Read the rest of the bundle. Read gold. |
| `b1_prefix` | The proxy bundle, prefix scores, confidence then rank. | Use the lexical reader. Abstain. The prefix selector always returns a scored candidate. |
| `b1_forced_lexical` | The same strings, lexical evidence. Always one frame. | Be reported as selective coverage. |
| `b2_prefix_controller` | Prefix failure kind and the other written candidates. `max_retries` default 1. | Share a table with the lexical controller. Call a decoder. |
| `b2_lexical_v3` | Lexical evidence, `min_support` unchanged, optional second written bundle. | Treat a finished simulated RETRY as correct unless the committed frame matches gold. |

Prefix confidence stays 0, 0.5, or 1. `min_support` stays the published curve at 1, 2, and 3. No new selector is added.

## Empty bundle

The future facade, and only the facade, returns:

| Field | Value |
| --- | --- |
| Action | HOLD |
| Reason | `EMPTY_BUNDLE` |
| Committed frame | None |
| Functions called | None |

Existing behavior stays in the source, undocumented as a facade result:

| Function | Empty input |
| --- | --- |
| `select_candidate(())` | Raises `ValueError`. |
| `forced_selection([])` | Raises `ValueError`. |
| `decide_selective([])` | HOLD, reason `no_intent_evidence`. |
| `run_b2` | Requires a one-best hypothesis, so an empty bundle does not reach it. |

`EMPTY_BUNDLE` is not a synonym for `no_intent_evidence`. A bundle that contains text and no intent cue is still `no_intent_evidence` if the lexical controller runs.

## Evaluation boundary

Report intent accuracy, slot micro-F1, exact frame, selective coverage, selective risk, and unsafe commits with the approved denominators. Derived recovery-action accuracy may be reported and must be labelled derived. WER and CER on these strings may be reported as text-edit distance against the gold sentence. They are not speech WER.

## Fit

The architecture can be implemented later as a facade in a new directory. This review does not authorize that directory.
