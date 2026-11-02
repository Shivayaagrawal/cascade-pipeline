# Phase 0 Implementation Plan

**Executed:** 2026-11-02.  
**Project:** Uncertainty-aware cascaded speech understanding with failure diagnosis and recovery.

This file is the in-repo checklist for Phase 0. The long agent prompt that accompanied it was the user instruction for that run. Phase 0 is audit and planning. It does not authorize training or pipeline code.

## Objectives

1. Verify the reference paper and its method.
2. Separate that method from Cascade Pipeline.
3. Record deviations.
4. Verify dataset source, release, and license, or mark them pending.
5. Define the semantic output using the real label schema, or mark it pending.
6. Choose provisional ASR and NLU routes without downloading models.
7. Define the experiment and the metrics.
8. Write leakage and overfitting rules.
9. Audit the repository and the machine.
10. Draft architecture and a risk register.
11. Leave a Phase 1 plan that does not start itself.

Missing facts stay `PENDING`. They are not filled from memory.

## Workstreams

| ID | Work | Output |
|----|------|--------|
| A | Repository, git, Python, hardware, dependencies, tests | `docs/REPOSITORY_AUDIT.md` |
| B | Ruan et al., Interspeech 2020, read from the ISCA PDF | `docs/REFERENCE_PAPER_NOTES.md` |
| C | Related work limited to papers actually read | `docs/RELATED_WORK.md`, `docs/LITERATURE_MATRIX.md`, `docs/RESEARCH_QUESTIONS.md` |
| D | Fluent Speech Commands source and license. Local files only if present. | `docs/DATASET_CARD.md` |
| E | Label schema and metric formulas | `docs/TASK_AND_LABEL_SCHEMA.md`, `docs/METRIC_DEFINITIONS.md` |
| F | Provisional models and this machine | `docs/MODEL_AND_COMPUTE_DECISIONS.md` |
| G | B0, B1, B2, splits, injection, negative results | `docs/EXPERIMENTAL_PROTOCOL.md`, `docs/LEAKAGE_AND_OVERFITTING_CHECKLIST.md`, `docs/EXPERIMENT_LOG_TEMPLATE.md` |
| H | Interfaces and risks. No empty Python packages. | `docs/ARCHITECTURE_OVERVIEW.md`, `docs/RISK_REGISTER.md` |

Also required: `docs/RESEARCH_ALIGNMENT.md`, `docs/RESEARCH_DEVIATIONS.md`, `docs/PHASE_0_REPORT.md`.

## Prohibited in this phase

Model training, ASR or NLU implementation, recovery code, Streamlit, TTS, new dependency installs, fabricated metrics, and unapproved dataset changes.

## Exit gate

Phase 0 is complete only when each row passes or the owner accepts a named limitation.

| Requirement | Required state |
|-------------|----------------|
| Repository audit | PASS |
| Paper verification | PASS, or an approved limit |
| Alignment and deviations | PASS |
| Dataset release and license | PASS |
| Labels and splits checked on files | PASS |
| B0, B1, B2 and metrics | PASS |
| Leakage and overfitting rules | PASS |
| Model route | PASS |
| Architecture and risks | PASS |
| Phase 1 plan | APPROVED |

An unresolved license, an unseen label schema, or an unknown split blocks data loading. It is not bypassed.

## Amended design, 2026-11-02

| Decision | Status |
|----------|--------|
| Research design | Superseded the same day by Common Voice as the primary candidate. No Phase 1 secondary dataset. Scores are not pooled with FSC, SLURP, or ATIS. |
| ATIS | Excluded from implementation. The reference paper still used it. Cascade Pipeline does not claim to reproduce that paper. |
| CNN | Optional. Not a Phase 1 deliverable. |
| FSC license | Owner decision Pending. Acquisition BLOCKED. Phase 0.5 re-read the page, the Public License PDF, and the CC BY-NC-ND 4.0 legal code. The page’s access link is the Fluent.ai Google Group. The GrindstoneLZX URL is not the official channel and was not cloned. |
| SLURP license | Owner decision Pending on audio and on text, separately. Zenodo version 1.0 audio is CC BY-NC 4.0. GitHub text at commit `8eb16545762be97ace75334109d73824217311f1` is CC BY 4.0. |

## Phase 0.5 licensing gate, 2026-11-02

This checklist is the documentation review. It does not approve Phase 1 and it does not accept a license.

| Item | State |
|------|--------|
| FSC official channel recorded | Publisher page plus Google Group access link. Author URL still UNKNOWN after a timeout. No archive version. |
| FSC license evidence recorded | Page, PDF, and CC BY-NC-ND 4.0 legal code. Conflict left Pending. |
| SLURP audio evidence recorded | Zenodo record, `LICENSE.txt`, CC BY-NC 4.0 legal code. Archives not downloaded. |
| SLURP text evidence recorded | Commit pinned. `LICENSE.txt` and CC BY 4.0 legal code read. Repository not cloned. |
| Owner decision values | Pending, Accepted, or Refused only. No row uses “No” to mean both Pending and Refused. All current data rows are Pending. |
| Gate A review documented | Yes. |
| Gate B required artifacts Accepted | No. |
| Gate C owner approves Phase 1 | No. |
| Implementation plan marked approved | No. |

## Phase 1 scope, not yet approved

The FSC-and-SLURP dataset-engineering list that used to sit here is superseded. The current scope is `docs/PHASE_1_IMPLEMENTATION_PLAN.md`: real Common Voice access, validated ingestion, waveform ASR, hypothesis provenance, and annotation readiness. Gate C remains unmet. This file does not approve that phase. FSC and SLURP stay superseded, and their license decisions stay Pending.
