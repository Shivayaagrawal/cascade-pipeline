# Phase 1D.2 blockers

**PHASE 1D.2 DOCUMENTED. PHASE 1E BLOCKED. PHASE 2 NOT STARTED.**

No dataset was downloaded. No implementation behavior was changed. Frozen experiment files and the Phase 1C pilot were not edited.

## Still blocked

| Blocker | Effect |
| --- | --- |
| SLURP acquisition not approved | No real task-speech gold. Phase 1E does not start. |
| Audio licence not accepted | CC BY-NC 4.0 remains `authorization_required`. |
| Text licence not accepted | CC BY 4.0 does not authorize the recordings. |
| Project cap | The real archive exceeds the remaining cap before extraction. |
| No official SLURP subset | A partial download is not a workaround. |
| No recognizer run | WER, CER, and N-best claims on speech are unmeasured. |
| `faster-whisper` not installed | The adapter cannot be treated as an available decoder. |
| Phase 1C pilot unannotated | LibriSpeech has no human semantic review. |
| `test-clean` held out | Not available for development or tuning. |
| No gold recovery actions | Action accuracy is against a derived expected action. |
| Negation and uncertainty | Unavailable in the current reader. |
| Two controllers | v1 B2 and v3 recovery are separate. They must not be described as one tuned system. |

## What is not blocked

Synthetic transcript experiments that are already frozen can be cited with the wording in `docs/PHASE_1D2_RESEARCH_CLAIMS_REGISTER.md`. LibriSpeech `dev-clean` and `test-clean` remain authorized for transcription work that has not yet been run. Design work for a later adapter may continue from `docs/PHASE_1D2_DATASET_ADAPTER_SPEC.md`.

## Next phase

Phase 1D.3 can write the final experimental protocol from these contracts. It still does not download data and does not start Phase 2. Phase 1E waits for a separate acquisition decision. Phase 2 waits until the evaluation inputs and scope are approved.
