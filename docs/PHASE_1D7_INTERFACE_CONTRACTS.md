# Phase 1D.7 interface contracts

**Date:** 2026-11-02  
**Status:** conceptual. No type was added to the source tree.  
**Active provenance values:** `SINGLE_TRANSCRIPT` and `SYNTHETIC_PROXY` only. `GENUINE_ASR_NBEST` is future work and is not an active field.

`implemented` means a current object already holds the value. `proposed` means only the facade would hold it.

## SyntheticTranscriptInput

**Purpose:** one written string for one id.  
**Consumers:** `Hypothesis` today. `run_b0` takes one. Bundle members use the same shape.  
**Implemented:** text, provenance string, rank. Utterance id is passed beside `Hypothesis`.

| Field | Type | Null | Required | Rule |
| --- | --- | --- | --- | --- |
| `utterance_id` | string | no | yes | `utt-000`–`utt-199` on this dataset. |
| `transcript_text` | string | no | yes | May be empty only in an explicit negative test. |
| `candidate_source` | enum | no | yes | `SINGLE_TRANSCRIPT` or `SYNTHETIC_PROXY`. |
| `provenance` | string | no | yes | `synthetic_edit` for edits. `reference_passthrough` only for the gold-sentence oracle, which is not a bundle member. |
| `rank` | int | no | yes | Existing `Hypothesis.rank`. |
| `variant_id` | string | yes | no | Present on the 600-row file. |

Validation: `native_nbest` is invalid. Gold sentence is not inserted into a proxy bundle.

## CandidateBundle

**Purpose:** the ordered list for B1 or B2.  
**Consumers:** `run_b1` and `run_b2` take `Hypothesis` tuples. Lexical functions take `list[str]`. The facade keeps provenance outside those string lists.  
**Implemented:** the tuples and lists. The wrapper object is proposed.

| Field | Type | Null | Required | Rule |
| --- | --- | --- | --- | --- |
| `utterance_id` | string | no | yes | Shared by every member. |
| `candidate_count` | int | no | yes | Length of `candidates`. |
| `candidates` | list | no | yes | Empty is legal input to the facade and is not passed onward. |
| `candidate_source` | enum | no | yes | `SYNTHETIC_PROXY` for the 600 and for paraphrase, slot-removed, and split. `SINGLE_TRANSCRIPT` has count 1. |
| `generation_method` | string | no | yes for proxies | `v1_injector`, `paraphrase`, `slot_removed`, or `split_evidence`. |

Validation: mixed provenance in one bundle is invalid. Count must match the list. An empty list produces the facade HOLD below and calls nothing.

## CandidateProvenance

**Purpose:** the label that stops a proxy from being described as N-best.  
**Implemented:** `Hypothesis.provenance` and the CSV column.

Active values are `synthetic_edit` and, for the oracle only, `reference_passthrough`. The bundle-level enum is `SINGLE_TRANSCRIPT` or `SYNTHETIC_PROXY`. A future-work note may mention a recognizer list. That value is not accepted by this project’s validator.

## ExecutionStrategy

**Purpose:** which of the five identities runs.  
**Implemented:** separate functions. The enum is proposed.

Required value, not null, one of `b0_prefix`, `b1_prefix`, `b2_prefix_controller`, `b1_forced_lexical`, `b2_lexical_v3`. Any other string is invalid. One record has one identity.

## SemanticFrame

**Purpose:** intent and slots from one reader.  
**Implemented:** fields on `ScoredCandidate` and `SelectiveDecision`. A single frame type is proposed.

| Field | Type | Null | Required | Rule |
| --- | --- | --- | --- | --- |
| `utterance_id` | string | no | yes | |
| `predicted_intent` | string | yes | yes | Null when the reader finds none or is ambiguous on the prefix path. |
| `predicted_slots` | map | no | yes | Empty map means no slots. It is not “unknown”. |
| `parser_version` | string | no | yes | `prefix-cues` or `lexical-v3`. |
| `confidence_or_support` | number | yes | no | Prefix 0, 0.5, or 1. Lexical support count. Not a probability. |
| `committed` | bool | no | yes | True only for CONTINUE and RETRY after normalization. |

Negation and uncertainty are not fields. The readers do not produce them.

## CandidateComparison

**Purpose:** how a bundle became one selection.  
**Implemented:** only the winning score or the selective reason. The full comparison object is proposed.

Required: identity, candidate ranks, selected rank or null, rationale (`prefix_confidence_then_rank`, `forced_lexical`, or `selective_agreement`). Optional: per-candidate frames. Null selection means the identity abstained. Forced lexical and prefix B1 do not abstain. Selective B2 may.

A prefix-versus-lexical table is a reader change, not a candidate-count result.

## RecoveryDecision

**Purpose:** one action from one controller.  
**Implemented:** `recovery_controller.RecoveryDecision` and the tuple from `recovery_action`. The normalized record is proposed.

| Field | Type | Null | Required | Rule |
| --- | --- | --- | --- | --- |
| `execution_identity` | enum | no | yes | Which controller. |
| `action` | enum | no | yes | `CONTINUE`, `RETRY`, `CLARIFY`, `HOLD`. |
| `reason` | string | no | yes | Prefix `FailureKind`, lexical `SelectiveDecision.reason`, or facade `EMPTY_BUNDLE`. |
| `committed_frame` | SemanticFrame | yes | yes | Null for CLARIFY, HOLD, and `EMPTY_BUNDLE`. |
| `retry_mechanism` | string | yes | required when action is RETRY | Lexical value is only `simulated_candidate_rescore`. Prefix RETRY is rescoring a written alternative, not that string, and not a decode. |
| `raw_attached_output` | text | yes | no | The frame `run_b2` copies on CLARIFY and HOLD. Audit only. Not a commit. |

CLARIFY has no question text. HOLD has no committed frame.

Facade empty bundle, and only that path:

| Field | Value |
| --- | --- |
| `action` | HOLD |
| `reason` | `EMPTY_BUNDLE` |
| `committed_frame` | null |
| Functions called | none |

That reason is not `no_intent_evidence`. The lexical function still returns `no_intent_evidence` when it is actually called on an empty list. The facade must not call it.

## EvaluationRecord

**Purpose:** one scored decision.  
**Implemented:** v3 report objects and the v3b log. The facade row is proposed.  
**Owner of gold:** the manifest, used only at scoring time.

Required: utterance id, identity, gold intent, gold slots, predicted intent (nullable), predicted slots, exact-frame bool (nullable when gold is absent, which it is not on this dataset), action when the identity is a B2 identity, coverage status, safety status. `expected_recovery_action` is optional and, when present, is the derived rule, not a human label. `audio_decoded` is required and is false.

Safety is false only when a CONTINUE or RETRY frame mismatches gold. Abstention is not false.

## ExperimentRunMetadata

**Purpose:** reproducibility for a future facade run.  
**Implemented:** the frozen reports already store seed, hashes, and timestamps. A new run would store its own.  
**Proposed fields:** dataset version `synthetic-seed17-v1`, seed 17, strategy list, output directory name, config hash, and the hashes of the frozen files taken before the run. The output directory must not be one of the immutable experiment directories.

No field in the active contracts accepts a recognizer model id.
