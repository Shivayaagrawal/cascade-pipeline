# Phase 1D.5 interface contracts

**Date:** 2026-11-02  
**Scope:** the active records are synthetic text. Fields that mention a recognizer or LibriSpeech describe future work or historical data. They are not inputs the simulation must supply.  
**Status:** conceptual schemas. No schema file was added. No existing dataclass was changed.  
**Field status:** `required`, `optional`, `nullable`, `unavailable`.  
**Unavailable** means the current code cannot supply the value. It is not a guess.

These names are the planning contracts. Where a field already exists on `Hypothesis`, `SystemOutput`, `ScoredCandidate`, `SelectiveDecision`, or `RecoveryDecision`, the owner is that type. Proposed fields are marked proposed and have no owner in code.

## A. TranscriptInput

**Owner today:** `Hypothesis`. Proposed wrapper fields have no code owner.

| Field | Type | Status | Rule |
| --- | --- | --- | --- |
| `utterance_id` | string | required on the wrapper | `utt-000`–`utt-199` for Track A. Not stored on `Hypothesis` today. The runner passes it beside the hypothesis. |
| `transcript_text` | string | required | `Hypothesis.text`. |
| `candidate_id` | string | optional | Proposed. Today the identity is `rank`. |
| `provenance` | string | required | `synthetic_edit`, `reference_passthrough`, or, after a real decode only, `single_segment_text`, `native_nbest`, `beam_hypothesis`, `independent_decode`, `retry_decode`. |
| `transcript_source` | string | required on the wrapper | Proposed label: `SINGLE_TRANSCRIPT`, `SYNTHETIC_PROXY`, or `GENUINE_ASR_NBEST`. `SYNTHETIC_PROXY` is the only label for current edits. |
| `rank` | int | required | Existing field. |
| `metadata` | map of strings | optional | `ASRResult.metadata`. Empty for synthetic results. |

Validation: empty text is allowed only if a test names it. `native_nbest` on a synthetic row is invalid. `GENUINE_ASR_NBEST` without a recognizer call is invalid.

## B. CandidateBundle

**Owner today:** `tuple[Hypothesis, ...]` for the prefix path, and `list[str]` for the v3 path. The string list does not carry provenance. A future bundle must not drop provenance when it calls the v3 functions.

| Field | Type | Status | Rule |
| --- | --- | --- | --- |
| `utterance_id` | string | required | Same id for every candidate. |
| `candidate_count` | int | required | Length of `candidates`. |
| `candidates` | list of TranscriptInput | required | Order is rank order. |
| `candidate_source` | enum | required | `SINGLE_TRANSCRIPT`, `SYNTHETIC_PROXY`, or `GENUINE_ASR_NBEST`. |
| `candidate_generation_method` | string | required for proxies | `v1_injector`, `paraphrase`, `slot_removed`, or `split_evidence`. |
| `candidate_provenance` | string | required | One value for the bundle when every candidate shares it. Mixed bundles are invalid. |

`SINGLE_TRANSCRIPT` has count 1. `SYNTHETIC_PROXY` is the current three-candidate lists. `GENUINE_ASR_NBEST` is unavailable.

Validation: the gold sentence is not inserted. An empty candidate list is rejected by `select_candidate` and `forced_selection`. `decide_selective` currently returns HOLD instead. A facade must record that difference rather than hide it.

## C. SemanticFrame

**Owner today:** the intent and slot fields on `ScoredCandidate` or `SelectiveDecision`. There is no single frame type.

| Field | Type | Status | Rule |
| --- | --- | --- | --- |
| `utterance_id` | string | required on the wrapper | Passed beside the score today. |
| `predicted_intent` | string | nullable | Null when the reader finds none, or when the prefix reader is ambiguous. |
| `predicted_slots` | map string to string | required | Empty map means no slots predicted. It is not unavailable. |
| `frame_completeness` | bool | proposed | True only when the lexical `frame_is_complete` test passes, or when a later note defines the prefix equivalent. Not stored today. |
| `evidence` | object | optional | Prefix: matched cue names on `IntentPrediction`. Lexical: `Evidence.intents` and slot value tuples. |
| `confidence` | number | optional | Prefix: 0, 0.5, or 1. Lexical: `support` count. Not a probability. |
| `parser_version` | string | required on the wrapper | Proposed values: `prefix-cues` or `lexical-v3`. |
| `negation` | object | unavailable | No function returns it. |
| `uncertainty` | object | unavailable | No function returns it. |

Intent strings are the ten synthetic names. Slot names are the `CRITICAL_SLOTS` keys for that intent. A predicted slot value must come from the candidate text or, on the prefix path, from the template slice. The controller does not invent one.

## D. CandidateComparison

**Owner today:** none as a stored object. `select_candidate` and `forced_selection` return only the winner. `decide_selective` returns a reason string and a support count.

| Field | Type | Status | Rule |
| --- | --- | --- | --- |
| `candidate_ids` | list of strings | proposed | Ranks, until stable ids exist. |
| `extracted_frames` | list of SemanticFrame | proposed | One per candidate. The v3 audit log stores per-candidate evidence for the selective path. |
| `intent_agreement` | bool | optional | False when `candidate_disagrees` is true, or when complete frames have two intents. |
| `slot_agreement` | bool | optional | False on `slot_value_disagreement`. |
| `disagreement_details` | string | optional | The selective `reason`, or the prefix `ambiguous` flag. |
| `selected_candidate` | string | nullable | Null when the selective layer does not commit. |
| `selection_rationale` | string | required when a selector runs | `prefix_confidence_then_rank`, `forced_lexical`, or `selective_agreement`. |

## E. FailureAssessment

**Owner today:** `FailureKind` for the prefix controller, and `SelectiveDecision.reason` for the lexical layer. Do not translate one into the other.

| Field | Type | Status | Rule |
| --- | --- | --- | --- |
| `failure_category` | string | required | A name from the controller that ran. |
| `severity` | string | unavailable | No severity scale exists. Do not invent one. |
| `supporting_evidence` | string | required | The reason or the failure kind. |
| `confidence` | number | optional | The same non-probability score as the frame. |
| `affected_fields` | list of strings | optional | Slot names when the reason is a slot failure. Empty when the code does not name them. |

## F. RecoveryDecision

**Owners today:** `recovery_controller.RecoveryDecision` and the tuple from `recovery_action`.

| Field | Type | Status | Rule |
| --- | --- | --- | --- |
| `action` | enum | required | `CONTINUE`, `RETRY`, `CLARIFY`, `HOLD`. |
| `trigger_reason` | string | required | Prefix: `FailureKind`. Lexical: `SelectiveDecision.reason`. |
| `input_assessment` | FailureAssessment | required | From the controller that ran. |
| `selected_candidate` | string | nullable | Set when CONTINUE or RETRY commits a frame. For prefix CLARIFY and HOLD the code still returns `one_best` inside `RecoveryDecision.selected`. The audit must copy the action beside that text. |
| `retry_attempt_id` | string | nullable | Required when action is RETRY. Current value of the mechanism field is only `simulated_candidate_rescore`. |
| `retry_budget` | int | optional | Prefix `max_retries`, default 1. Lexical layer has no numeric budget. A missing second bundle means no retry. |
| `downstream_behavior` | string | required | Commit the frame, or leave it unresolved. |
| `decision_timestamp` | string | proposed | Not stored on the decision object. Run-level timestamps exist on the v3 and v3b reports. |
| `controller_id` | string | required on the wrapper | `b2_prefix_controller` or `b2_lexical_v3`. |

## G. EvaluationRecord

**Owner today:** the v3 report objects and the v3b decision log. Align new rows with `docs/PHASE_1D2_EVALUATION_CONTRACT.md`.

| Field | Type | Status | Rule |
| --- | --- | --- | --- |
| `gold_intent` | string | required on synthetic rows | Unavailable on LibriSpeech. |
| `predicted_intent` | string | nullable | Null on abstention for the selective exact-frame column. |
| `gold_slots` | map | required on synthetic rows | Unavailable on LibriSpeech. |
| `predicted_slots` | map | required | Empty when abstaining in that column. |
| `exact_frame_match` | bool | nullable | `frames_equal`. Null when gold is unavailable. |
| `recovery_action` | enum | optional | Required for a B2 row. |
| `expected_recovery_action` | enum | optional | Derived. Unavailable without gold. Not a human label. |
| `coverage_status` | enum | required for selective rows | `committed` for CONTINUE and RETRY, `abstained` for CLARIFY and HOLD. |
| `safety_status` | bool | nullable | False only for a committed frame that mismatches gold. Abstention is not false. |
| `evaluation_provenance` | string | required | `synthetic` plus the list name, or a future dataset name. |
| `audio_decoded` | bool | required | False for every current result. |

Validation: selective risk uses committed rows only. A zero commit count leaves the rate undefined. Forced exact-frame accuracy always has a prediction and is not reported as selective coverage.
