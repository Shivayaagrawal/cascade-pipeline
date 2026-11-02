# Implementation Plan — Phase 0 status

**Current Phase 1 document:** `docs/PHASE_1_IMPLEMENTATION_PLAN.md`, accepted as the working plan after simulation v3. Execution is not approved. Acquisition is pending.  
**Earlier schedules, still in the repo:** `docs/PHASE_WISE_IMPLEMENTATION_PLAN.md` and `docs/PHASE_PLAN.md`. Their Phase 1 sections are superseded by the revised plan. Differences are recorded in `docs/RESEARCH_DEVIATIONS.md`.

This file is the Phase 0 execution record. It does not approve Phase 1.

## Current phase

**Phase 0 is complete.** Common Voice Scripted Speech v27.0 English remains the candidate recorded on 2026-11-02. Terms are not accepted. The revised Phase 1 plan is the working baseline, and **Phase 1 execution has not started. Status: NOT READY TO EXECUTE PHASE 1.** See `docs/PHASE_0_DECISION_LOG.md` decision D-CV-007.

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

The allowed order is 1A through 1E in `docs/PHASE_1_IMPLEMENTATION_PLAN.md`:

1. Confirm the MDC record, accept the applicable terms personally, and acquire only a permitted subset inside 5 GB.
2. Validate audio, transcripts, official splits, and duplicates.
3. Decode real waveforms with one lightweight CPU ASR model and measure WER, CER, latency, and memory.
4. Store hypotheses with provenance: `beam_hypothesis`, `independent_decode`, `retry_decode`, or `synthetic_edit`.
5. Prepare a manual annotation guide and a 200–300 utterance pilot. Do not treat generated labels as gold.

Phase 1 still must not train ASR or NLU, run a B0/B1/B2 comparison, fit a recovery policy, or build a demo UI.

## Blockers before Phase 1 data work

1. The owner confirms the dataset identity in the MDC account.
2. The owner records Accepted for the terms that apply to that record.
3. A permitted subset acquisition method is identified, and the subset is checked against the 5 GB limit.
4. The owner explicitly approves the revised Phase 1 plan.

Dataset download cannot start from this file. A virtualenv is not a substitute for those gates.
