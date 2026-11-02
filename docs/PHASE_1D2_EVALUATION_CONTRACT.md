# Phase 1D.2 evaluation contract

**Date:** 2026-11-02  
**Status:** specification only. No annotations were created. Synthetic rows were not relabelled as human speech.

One evaluation record describes one decision for one utterance under one named system. A system is `b0_prefix`, `b1_prefix`, `b1_forced_lexical`, `b2_prefix_controller`, or `b2_lexical_v3`. New names can be added later. Old records are not rewritten to match them.

Field status is `required`, `optional`, or `unavailable`. `unavailable` means the current assets cannot supply the value. It is not a guess and it is not `absent`.

| Field | Status now | Rule |
| --- | --- | --- |
| `utterance_id` | Required | Stable id from the source. Synthetic ids are `utt-000` through `utt-199`. |
| `dataset` | Required | `synthetic` or `librispeech`. A future set uses its own name. Do not put SLURP here until acquisition is authorized. |
| `split` | Required | `synthetic`, `dev-clean`, or a future official split. `test-clean` is not a development record. |
| `transcript_provenance` | Required | One of `synthetic_edit`, `reference_passthrough`, `single_segment_text`. `native_nbest` is allowed only after a recognizer returns an ordered list. |
| `transcript_text` | Required | The string that was scored. Do not replace a LibriSpeech reference. |
| `hypothesis_rank` | Optional | Rank in the candidate list. Omit when the record is the gold reference. |
| `asr_backend` | Required | `synthetic_hypothesis` for current results. `faster_whisper` only after an installed decode. `none` when the row is gold text. |
| `audio_decoded` | Required | `false` for every current synthetic and v3 result. |
| `predicted_intent` | Optional | Null when the system abstains or finds no intent. |
| `predicted_slots` | Optional | A list of `{name, value}` pairs. An empty list means the system predicted no slots. It is not `unavailable`. |
| `reference_intent` | Required on synthetic rows. Unavailable on LibriSpeech. | Synthetic gold comes from the generator. LibriSpeech has no intent gold. |
| `reference_slots` | Required on synthetic rows. Unavailable on LibriSpeech. | Same boundary. |
| `semantic_frame_correct` | Optional | True only when intent and every slot pair match. Null when the system abstained or the reference is unavailable. |
| `candidate_agreement` | Optional | Support count or a disagreement reason from the v3 layer. Unavailable for a one-transcript B0 row. |
| `confidence` | Optional | Prefix path: 0, 0.5, or 1. Lexical path: the support count, not a probability. |
| `uncertainty` | Unavailable | No current function returns an uncertainty finding. v3b records that fact. |
| `negation` | Unavailable | No current function returns a negation finding. The transcript may still contain the word. |
| `failure_diagnosis` | Optional | A name from the controller that actually ran. Do not translate a v1 failure into a v3 reason. |
| `recovery_action` | Optional | `CONTINUE`, `RETRY`, `CLARIFY`, or `HOLD`. Required for a B2 record. Omit for a bare B0 frame. |
| `retry_mechanism` | Required when the action is `RETRY` | Current value is only `simulated_candidate_rescore`. |
| `expected_recovery_action` | Optional | Assigned from the gold frame and the candidate strings before the decision is read. Unavailable when there is no gold frame. |
| `decision_safe` | Optional | False only when a CONTINUE or RETRY frame does not match gold. Abstention is not unsafe. Null when gold is unavailable. |
| `abstained` | Required for a B2 or selective record | True for CLARIFY and HOLD. False for CONTINUE and RETRY. |
| `annotator_id` | Unavailable | No human annotation has been completed. |
| `human_audio_reviewed` | Required on LibriSpeech pilot rows | Current value is `not_performed`. |

A record with `audio_decoded: false` and `dataset: synthetic` must not be described as a speech result. A record with `transcript_provenance: synthetic_edit` must not be described as N-best.

The contract does not authorize filling these fields for SLURP. That waits for Phase 1E.
