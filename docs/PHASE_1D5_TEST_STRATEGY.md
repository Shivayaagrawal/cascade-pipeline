# Phase 1D.5 test strategy

**Date:** 2026-11-02  
**Status:** strategy. The suite was not modified.  
**Existing command:** `python3 -m pytest -q` from the Cascade Pipeline root. Last integrity run in Phase 1D.4: 71 passed.

## Unit tests already present

| Area | Tests |
| --- | --- |
| Input and provenance | `test_b1_rejects_native_nbest_label`, `test_three_variants_keep_ids_and_are_not_nbest`, `test_gold_transcript_stays_out_of_candidate_lists` |
| Intent and slots | `test_clean_templates_match_gold`, `test_ambiguous_and_incorrect_labels`, `test_missing_amount_does_not_commit`, `test_amount_inside_a_longer_number_is_not_a_slot` |
| Selection | `test_b0_b1_b2_do_not_need_gold`, `test_support_threshold_rejects_a_single_witness`, `test_corrupted_critical_amount_is_not_committed_when_candidates_disagree` |
| Recovery | `test_b2_clarify_and_hold`, `test_every_recovery_action`, `test_expected_actions_do_not_read_the_decision`, `test_wrong_commit_is_unsafe_and_retry_is_not_scored_as_success`, `test_abstention_is_not_an_unsafe_decision` |
| Metrics | `test_wer_and_empty_reference`, `test_cer_counts_characters`, `test_slots_and_semantic_error`, `test_zero_denominator_rate_stays_undefined`, `test_abstention_does_not_invent_a_zero_risk`, `test_slot_metrics_publish_precision_recall_and_f1` |
| Normalization boundary | WER tests call `normalize`. NLU tests pass raw template strings. No test feeds `normalize()` into the parser, and a future test must not start doing that as a silent default. |
| Timing | `test_timing_is_lexical_processing_only` |
| Negation and uncertainty | `test_negation_and_uncertainty_stay_unavailable` |

`textnorm` is covered through WER and CER. There is no separate normalizer unit test, and this phase does not add one.

## Integration tests already present

The v3 tests run the lexical path from strings through `recovery_action` to metric rates. `test_decision_log_matches_frozen_v1_aggregate` checks the 200-row log against the frozen aggregate. `test_nlu_and_pipeline.py` runs B0, B1, and B2 on hypotheses. `test_whisper_adapter_does_not_download_when_missing` checks the import failure without a model.

A future authorized facade would add, in a new test module:

| Flow | Assert |
| --- | --- |
| Transcript to prefix frame | `parser_version` is `prefix-cues`. Gold is absent from the call. |
| Bundle to both selectors | Prefix and forced lexical results are stored as different records. |
| Comparison to diagnosis | The reason string comes from the controller that ran. |
| Diagnosis to decision | CONTINUE and RETRY set `coverage_status` committed. CLARIFY and HOLD set abstained. |
| Decision to evaluation | `safety_status` is false only on a committed mismatch. Derived expected action is labelled derived. |

Those tests are not written now.

## Regression safeguards

Existing tests already hash frozen artifacts:

| Guard | Where |
| --- | --- |
| B0, B1, B2 summaries and `simulation_report.json` | `test_historical_simulation_hashes_are_unchanged`, `test_phase1c_did_not_change_simulation_hashes` |
| v3 report and v3 config | v3 tests and the v3b preserved-hash check |
| v3b decision log aggregate | `test_decision_log_matches_frozen_v1_aggregate` |
| Pilot CSV unannotated and hashed | `test_real_pilot_files_remain_unannotated` |
| Seed 17 sample order | `test_sampling_uses_seed_17_expression` |
| `test-clean` not offered to the annotator | `test_http_save_resumes_and_does_not_offer_heldout_audio`, `test_prepared_samples_are_isolated` |
| Output directory | `test_output_directory_cannot_be_v3` |

A later run hashes the manifest in `docs/PHASE_1D3_REPRODUCIBILITY_PROTOCOL.md` before and after. A mismatch stops the run. The pilot hash changes only after a person saves.

## Future work

Decoder, N-best, speech WER, and operational-RETRY tests are not part of the simulation’s test plan. They are not unfinished tests. The simulation is complete, as a test plan, when the synthetic unit, integration, and regression checks above pass.
