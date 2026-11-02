# Phase 2 limitations

Cascade Pipeline remains a synthetic, text-only simulation. The facade does not add a recognizer, an audio decoder, a genuine N-best list, a speech WER or CER result, a latency claim, or a population-level result. Proxy candidates are edited strings. They are not ASR hypotheses.

## Naming

This Phase 2 is the synthetic facade. Phase 1D.7 still says the facade was not authorized and that the older speech Phase 2 was stopped. The 2026-11-02 prompt authorized the facade and the text audit. It did not authorize speech Phase 2 or Phase 3.

## Commit rule for non-controller identities

`b0_prefix` and `b1_prefix` set both `answered_frame` and `committed_frame` because those functions always return a parse. `b1_forced_lexical` sets `answered_frame` and leaves `committed_frame` empty, because `forced_selection` says its frame is not a safety commit. Exact-frame scoring for that identity uses the answered frame. Coverage does not.

## Two different 145/200 figures

Forced exact-frame accuracy and selective coverage can both be 145/200 on the frozen v3 run. They are different measures. The facade keeps them in different fields. 142/200 is correct commits when abstention is scored wrong. 3/145 is unsafe commits among commits. Those figures were not recomputed by this phase.

## Empty input

`EMPTY_BUNDLE` is a facade reason. `decide_selective([])` still returns `HOLD` / `no_intent_evidence`. `select_candidate(())` and `forced_selection([])` still raise `ValueError`. Those functions were not edited.

## Prefix text on CLARIFY and HOLD

`run_b2` still copies one-best text into `SystemOutput` for `CLARIFY` and `HOLD`. The facade stores that text on `RawControllerOutput` and leaves the committed frame empty.

## Retry labels

Lexical `RETRY` is `simulated_candidate_rescore`. It is not a second recognition pass. Prefix `RETRY` rescores a written alternative inside `run_b2` and is not given that lexical label.

## Audit

The sample is one annotator and text only. Inter-annotator agreement is not claimed. Audio review is not applicable. Judgement cells are blank and `annotation_status` is `pending`. No comparison with gold was run. Opening `sealed_gold.json` or `sampling_manifest.json` during annotation would reveal gold intent.

The 600 edited rows used by the sample are `variants.csv`. `annotations.jsonl` is the 200 gold utterances and was not treated as extra variants.

Some gold rows for cancel-appointment and check-appointment have an empty slot map, while the lexical `CRITICAL_SLOTS` table still lists `date` for those intents. The facade does not change that frozen behavior.

## What this phase did not do

No experiment output was regenerated. No frozen report was rewritten. LibriSpeech `test-clean` was not read. The Phase 1C pilot CSV was not edited.
