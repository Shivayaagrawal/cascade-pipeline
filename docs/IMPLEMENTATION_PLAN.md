# Implementation Plan — Phase 0 status

**Canonical build order:** `docs/PHASE_WISE_IMPLEMENTATION_PLAN.md` (Phases 0–8).  
**Earlier schedule, still in the repo:** `docs/PHASE_PLAN.md` (14 days). Differences are recorded in `docs/RESEARCH_DEVIATIONS.md`.

This file is the Phase 0 execution record. It does not replace the phase-wise plan.

## Current phase

**Phase 0 — research foundation.** Common Voice Scripted Speech v27.0 English is the candidate recorded on 2026-11-02. Terms are not accepted. This file is not an approval to implement. **Phase 1 code has not been started. Status: NOT READY FOR PHASE 1.** See `docs/PHASE_0_REPORT.md`, `docs/PHASE_0_DECISION_LOG.md`, and `docs/PHASE_1_IMPLEMENTATION_PLAN.md`.

| Deliverable | State |
|-------------|--------|
| `docs/REPOSITORY_AUDIT.md` | Written 2026-11-02 from a directory listing and local environment checks |
| `docs/RESEARCH_ALIGNMENT.md` | Written 2026-11-02. Paper and license pages cited there were fetched. No experiment was run. |
| `docs/DATASET_CARD.md` | Updated. Local composition fields remain TODO. |
| `docs/RESEARCH_DEVIATIONS.md` | Template kept. One open scope note added. No approved methodology change. |
| `docs/IMPLEMENTATION_PLAN.md` | This file |

## Exit criteria

| Criterion | Result |
|-----------|--------|
| Research questions are testable | **Met as specifications.** H1–H4 in `docs/PROJECT_SCOPE.md` name the measurements. They are not tested. |
| Dataset source and license verified, or explicitly unresolved | **Partly met.** Publisher page, arXiv dataset section, and the Public License PDF were read. Local release, checksum, and which license governs a download are **unresolved**. |
| No unverified paper details stated as facts | **Met in the Phase 0 docs.** Only the abstract and dataset sections that were fetched are used. Paper metrics were not copied. |
| Scope approved | **Not met.** Waiting on the project owner. |

## What Phase 1 is allowed to do after approval

Order from `docs/PHASE_WISE_IMPLEMENTATION_PLAN.md` section 6:

1. Environment and minimal package.
2. License decision, then official dataset acquisition if approved.
3. Manifest from the real CSV schema.
4. Integrity checks, including speaker overlap.
5. Audio loader and preprocessing.
6. Waveform, STFT spectrogram, log-Mel features.
7. Inspection script.
8. Pytest and `docs/PHASE_1_REPORT.md`.

Phase 1 still must not train ASR or NLU, add B0/B1/B2, or build a demo UI.

## Blockers before Phase 1 data work

1. Owner accepts or rejects `docs/RESEARCH_ALIGNMENT.md`.
2. Owner records the license decision in `docs/DATASET_CARD.md`.
3. Owner confirms that the phase-wise plan, including a required Phase 2 fundamentals track, is the plan to execute.

Environment setup (a virtualenv and an empty package) can proceed without the dataset. Dataset download cannot.
