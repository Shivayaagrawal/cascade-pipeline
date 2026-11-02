# Phase 1D.3 blockers

**PHASE 1D.3 PROTOCOL WRITTEN. PHASE 1E BLOCKED. PHASE 2 NOT STARTED.**

No dataset was downloaded. No implementation file was changed. No experiment was run. Frozen outputs and the Phase 1C pilot were not edited.

`docs/PHASE_1D_BLOCKERS.md` still says the next design step is Phase 1D.3. That sentence records the gate before this protocol. The current next step is Phase 1D.4.

## Still blocked

| Blocker | Effect on the protocol |
| --- | --- |
| Protocol not yet reviewed | Phase 1D.4 has not accepted this methodology. New experimental code waits. |
| SLURP acquisition not approved | Track B has no task-speech gold. Phase 1E does not start. |
| Audio licence not accepted | CC BY-NC 4.0 remains unauthorized. |
| Text licence not accepted | CC BY 4.0 does not authorize the recordings. |
| Project cap | The real archive exceeds the remaining cap before extraction. |
| No official SLURP subset | A partial download is not a Track B dataset. |
| No recognizer run | WER, CER, and N-best on speech are unmeasured. |
| `faster-whisper` not installed | The adapter is not an available decoder. |
| Phase 1C pilot unannotated | LibriSpeech has no human semantic review. |
| `test-clean` held out | Not available for development, tuning, or error analysis. |
| No human recovery-action labels | Action accuracy is derived. |
| No operational RETRY | `simulated_candidate_rescore` is the only RETRY mechanism that has been scored. |
| Negation and uncertainty unavailable | The reader does not return them. |
| Two controllers | Prefix B2 and v3 recovery stay in separate columns. |
| Single synthetic seed and grammar | Intervals and significance claims stay inside `docs/PHASE_1D3_STATISTICAL_ANALYSIS.md`. |
| No acceptability threshold | “Acceptable” latency and clarification rate remain undefined. |

## What this protocol can already cite

The frozen Track A counts, with the wording in `docs/PHASE_1D3_CLAIM_ACCEPTANCE_MATRIX.md`. LibriSpeech `dev-clean` and `test-clean` remain authorized for a future transcription experiment that this phase does not run.

## Next phase

Phase 1D.4 reviews and either accepts or revises this protocol. It does not download data and does not implement Phase 2.

Phase 1E waits for a separate acquisition decision. Phase 2 waits until the evaluation inputs and the scope are approved. A dataset-independent implementation track, if one is approved after the review, uses a new directory and the preservation rules in `docs/PHASE_1D3_REPRODUCIBILITY_PROTOCOL.md`.
