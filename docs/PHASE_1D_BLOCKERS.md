# Phase 1D blockers

**PHASE 1D DOCUMENTATION COMPLETE. ACQUISITION NOT APPROVED.**

The comparison, suitability note, licensing register, acquisition plan, and research-design note are written. The decision record is `docs/PHASE_1D_DECISION.md`. The feasibility check is `docs/PHASE_1D1_FEASIBILITY.md`. No new dataset was downloaded. No licence was accepted.

## Acquisition blockers

| Blocker | Status |
| --- | --- |
| SLURP audio licence not accepted | `authorization_required`. CC BY-NC 4.0 was identified, not accepted. |
| SLURP text licence not accepted | `authorization_required`. CC BY 4.0 at the pinned commit was identified, not accepted. |
| SLURP real archive does not fit | 3,918,185,662 bytes against 3,569,732,592 bytes remaining. Extracted size is `not_verified`. |
| SLURP synthetic audio | Not in the conditional plan. Still unauthorized. |
| Fluent Speech Commands licence conflict | Page says CC BY-NC-ND 4.0. The linked PDF is a different Public License. Bundle licence is `pending_verification`. |
| Fluent Speech Commands access | Google Group. No version, checksum, or archive name. |
| Timers and Such licence | Paper says CC0. Zenodo licence id is `other-open`. No licence file in the record. |
| Timers and Such size | One zip of 13,133,746,587 bytes. Real-only byte size is `not_verified`. |
| Sonos / Snips access | Form acceptance required. No checksum. |
| Sonos / Snips coverage | SmartSpeaker recordings are described as test-only. |
| STOP licence | Repository licence field is `Other`. No grant was read. |
| STOP size | 218 hours in the paper. Archive byte size is `not_verified`. |
| Storage cap | 5,000,000,000 bytes. `data/` measured at 1,430,267,408 bytes. Existing files were not deleted. |

## Evaluation blockers

| Blocker | Status |
| --- | --- |
| Task-oriented gold on LibriSpeech | Absent. Phase 1C rows remain `not_annotated` unless a later inspection shows a human save. |
| Recovery-action gold | Absent on every candidate. CONTINUE can be scored against a frame. RETRY and CLARIFY cannot be scored against a follow-up. |
| N-best lists | Absent. A later decoder would have to produce them. |
| Negation and uncertainty fields | Not present in the readers or dataset schemas inspected here. The synthetic v3b audit left both unavailable. |
| SLURP speaker-disjoint splits | `not_verified`. |
| SLURP sample rate | `not_verified`. |
| SLURP Table 2 versus Table 6 audio counts | 72,277 versus a 72,396 sum. Not resolved. |
| SLURP entity-type count | Introduction says 55. Table 4 says 56. Not resolved. |
| Held-out test | Not read, because no new split was opened. LibriSpeech `test-clean` was not used. |

## What is not a blocker for the existing tracks

LibriSpeech `dev-clean` and `test-clean` remain available for transcription experiments under the existing authorization. Synthetic v1, v2, v3, and v3b remain the controlled text record. Neither track is real-speech task-oriented SLU.

## Next gate

Phase 1E does not start from this document, from the Phase 1D.1 feasibility note, or from the Phase 1D.2 readiness documents. It starts only after the owner names an exact release, accepts the exact licence, and records a storage decision that keeps the project inside its cap without deleting unrelated files. The 2026-11-02 decision leaves acquisition on hold. The next design step is Phase 1D.3, not Phase 2.
