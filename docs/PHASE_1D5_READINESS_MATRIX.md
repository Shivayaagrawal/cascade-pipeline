# Phase 1D.5 readiness matrix

**Date:** 2026-11-02  
**Scope revision:** real-speech readiness is not an active dependency. The last column records future-work status only.  
**Synthetic** means the written grammar and the proxy lists.

| Component | Existing implementation | Contract defined | Tests available | Additional work | Synthetic readiness | Real-speech status |
| --- | --- | --- | --- | --- | --- | --- |
| Prefix B0 | `run_b0` | Plan and `Hypothesis` | `test_nlu_and_pipeline.py`, metric tests | None to cite the frozen run. A facade is optional. | READY_FOR_FUTURE_IMPLEMENTATION | OUT_OF_CURRENT_SCOPE |
| Prefix B1 | `run_b1` | Plan | Provenance and pipeline tests | Keep the reader label on every row. | READY_FOR_FUTURE_IMPLEMENTATION | OUT_OF_CURRENT_SCOPE |
| Forced lexical B1 | `forced_selection` | Plan | v3 tests | Do not report 145/200 as coverage. | READY_FOR_FUTURE_IMPLEMENTATION | OUT_OF_CURRENT_SCOPE |
| Prefix B2 | `decide` | Plan | `test_b2_clarify_and_hold` | Copy the action into every audit row. | READY_FOR_FUTURE_IMPLEMENTATION | OUT_OF_CURRENT_SCOPE |
| Lexical B2 | `recovery_action` | Plan and v3b log | v3 and v3b tests | None to cite. Do not retune `min_support`. | READY_FOR_FUTURE_IMPLEMENTATION | OUT_OF_CURRENT_SCOPE |
| Unified record facade | Absent | Contracts, plus facade HOLD `EMPTY_BUNDLE` in `docs/PHASE_1D6_DECISION_REGISTER.md` | None for the facade | A new directory after Phase 1D.7. Do not edit frozen functions. | NOT_STARTED | OUT_OF_CURRENT_SCOPE |
| Evaluation metrics | Functions match the approved formulas | `docs/PHASE_1D3_METRIC_DEFINITIONS.md` | Metric tests | None for the synthetic metrics. | READY_FOR_FUTURE_IMPLEMENTATION | OUT_OF_CURRENT_SCOPE |
| Proxy candidate builders | Injector and diversity module | `docs/PHASE_1D6_SIMULATION_DATASET_SPEC.md` | Utterance tests | Do not draw a new seed into the same ids. | READY_FOR_FUTURE_IMPLEMENTATION | OUT_OF_CURRENT_SCOPE |
| Whisper path | Adapter source only | Not used | Import-failure test | None. Leave the adapter uncalled. | OUT_OF_CURRENT_SCOPE | OUT_OF_CURRENT_SCOPE |
| N-best ingest | Rejected on the synthetic path | `SYNTHETIC_PROXY` only | Rejection test | None. | OUT_OF_CURRENT_SCOPE | OUT_OF_CURRENT_SCOPE |
| Operational RETRY | Absent | `simulated_candidate_rescore` is the project RETRY | Simulated RETRY tests | None. | OUT_OF_CURRENT_SCOPE | OUT_OF_CURRENT_SCOPE |
| Negation and uncertainty | Readers do not return them | Recorded unavailable | v3b test | Accepted limitation. Not a build task. | READY_FOR_FUTURE_IMPLEMENTATION | OUT_OF_CURRENT_SCOPE |
| Clarification question text | Absent | Action `CLARIFY` is the record | None required | Not required in the current experiment. | OUT_OF_CURRENT_SCOPE | OUT_OF_CURRENT_SCOPE |
| LibriSpeech WER | Files exist. Unused by the simulation. | Historical | Prep tests exist and are not simulation tests | None. | OUT_OF_CURRENT_SCOPE | OUT_OF_CURRENT_SCOPE |
| Task corpus | Not used | Historical adapter note | None | None. | OUT_OF_CURRENT_SCOPE | OUT_OF_CURRENT_SCOPE |
| Human recovery labels | Absent | Derived `expected_recovery` is the active label | Derived-label tests | None. | OUT_OF_CURRENT_SCOPE | OUT_OF_CURRENT_SCOPE |

`READY_FOR_FUTURE_IMPLEMENTATION` means a later authorized phase can call the existing function. It does not authorize that phase. `OUT_OF_CURRENT_SCOPE` means the simulation can be finished without that row.
