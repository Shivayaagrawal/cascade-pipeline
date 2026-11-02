# Phase 1D.5 B0 implementation plan

**Date:** 2026-11-02  
**Status:** plan. `run_b0` was not modified.

## Existing implementation

`run_b0` in `pipeline.py` takes `utterance_id` and one `Hypothesis`. It rejects `native_nbest`, calls `score_hypothesis`, and returns `SystemOutput` with the prefix intent, prefix slots, the original text, and elapsed seconds. Gold is not an argument.

`score_hypothesis` calls `classify_intent` and, unless the prediction is ambiguous, `extract_slots`. Confidence is 0 when the intent is missing or ambiguous, 0.5 when the intent is `book_appointment`, `transfer_money`, or `play_music` and the slot dict is empty, and 1 otherwise. That rule is the frozen baseline. It is not a probability.

The frozen prefix B0 exact-frame count on the v1 first candidates is 0/200. WER on that cascade is 419/935. Those files stay in `experiments/B0`.

## Input contract

One `TranscriptInput` with `candidate_source` `SINGLE_TRANSCRIPT`. For the frozen comparison the text is rank 0 of the v1 injector list and provenance is `synthetic_edit`. The gold sentence is a different run, provenance `reference_passthrough`, and it is not a candidate in the ordinary list.

A future recognizer transcript enters as another `Hypothesis` with provenance `single_segment_text` and `audio_decoded` true on the evaluation record. The prefix parser is then called on that string. No parser change is required for the string to be accepted. Semantic scores still require gold intents and slots, which a LibriSpeech transcript does not have. WER and CER can be computed from the reference text without calling the parser.

## Parser contract

Reader id `prefix-cues`. Output is a nullable intent and a slot map. Ambiguous input yields null intent, empty slots, and confidence 0. The parser does not see gold. It does not record negation or uncertainty.

## Error handling

| Condition | Current behavior |
| --- | --- |
| Provenance `native_nbest` | `assert_synthetic_not_nbest` raises. |
| Empty text | The cues miss. Intent is null. This is a result, not an exception. |
| Unknown intent string in the schema | The cue list is the implementation. A schema name with no cue would not match. No such name exists in the ten. |

## Evaluation

Pair the output with synthetic gold through `frames_equal`, `intent_accuracy`, and `slot_scores`. Report the system as `b0_prefix`. Do not fill selective-risk fields. B0 always answers.

## Tests that already exist

`tests/test_nlu_and_pipeline.py`: clean templates match gold, ambiguous and incorrect labels, B0 does not need gold. `tests/test_metrics.py` covers WER, CER, and slot equality. A later phase adds no B0 test unless the authorization names a gap. Any new test must use a temporary directory and must not rewrite `experiments/B0/summary.json`.

## Acceptance criteria for a future change

A change is acceptable only if the frozen B0 hash stays `3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee`, the new outputs go to a new directory, the reader name is `prefix-cues`, and a speech transcript is not given an intent score without gold. This plan does not authorize that change.

## Future work

A recognizer transcript is not a B0 requirement. The active B0 input is one synthetic string with provenance `synthetic_edit`, or the gold sentence under `reference_passthrough` for the oracle only. The unused Whisper adapter is not part of this simulation.
