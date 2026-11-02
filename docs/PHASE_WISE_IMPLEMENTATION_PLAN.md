# CascadeGuard — Phase-wise Implementation Plan

**Superseded for Phase 1 on 2026-11-02.** The current Phase 1 scope, stages 1A–1E, and the later phase boundary table are in `docs/PHASE_1_IMPLEMENTATION_PLAN.md`. That plan is not approved. The sections below are the earlier roadmap. Do not download FSC or start the Phase 1 prompt in this file.

**Project:** Uncertainty-Aware Cascaded Speech Understanding with Failure Diagnosis and Recovery

---

## 1. Objective

Build a research-oriented Voice AI prototype that demonstrates:

- **Speech and acoustic fundamentals:** waveform, spectrogram, log-Mel spectrogram, 1D/2D convolution, and encoder-decoder concepts.
- A working **cascaded ASR → NLU** pipeline.
- Measurement of **ASR error propagation** into intent and slot extraction.
- **Multi-candidate** transcript evaluation.
- **Failure diagnosis** and bounded recovery.
- Reproducible evaluation of accuracy, false alarms, recovery success, and latency.

**Core pipeline:**

```text
Audio → Preprocessing → ASR → Transcript candidate(s) → NLU → Failure diagnosis → Recovery controller → Final decision
```

**Configurations:**

- **B0:** Single-best ASR transcript → NLU.
- **B1:** Multiple valid transcript candidates → NLU and candidate selection.
- **B2:** Failure diagnosis → CONTINUE / RETRY / CLARIFY / HOLD.

Do not silently replace the cascade with an end-to-end speech-to-intent system.

---

## 2. Overall roadmap

| Phase | Focus | Expected deliverable |
|------:|-------|----------------------|
| 0 | Research and repository audit | Verified scope and research alignment |
| 1 | Environment, dataset and audio foundation | Validated dataset and audio feature pipeline |
| 2 | Speech fundamentals | Optional stretch. Spectrograms may support the audio pipeline. A CNN keyword model is not required. See Decision C in `docs/PHASE_0_IMPLEMENTATION_PLAN.md`. |
| 3 | B0: Cascaded baseline | Working ASR → NLU pipeline |
| 4 | Error injection and propagation | Controlled speech/text corruption experiments |
| 5 | B1: Multi-candidate pipeline | Multiple transcript candidate evaluation |
| 6 | B2: Failure diagnosis and recovery | CONTINUE / RETRY / CLARIFY / HOLD |
| 7 | Comparative evaluation | B0/B1/B2 comparisons and ablations |
| 8 | Demo and research report | Complete demonstrable research prototype |

---

## 3. Phase overview (summary)

| Phase | Name | Main outcome |
|------:|------|--------------|
| 0 | Research and repository audit | Verified scope, paper notes, dataset choice, repository audit |
| 1 | Environment, dataset and audio foundation | Reproducible setup, validated dataset manifest, audio feature extraction |
| 2 | Speech fundamentals and acoustic modeling | Waveform/spectrogram study, convolution experiment, encoder-decoder understanding |
| 3 | B0 cascaded baseline | Working single-best ASR → NLU pipeline and baseline metrics |
| 4 | Controlled failures and error propagation | Audio/text corruption framework and per-sample propagation analysis |
| 5 | B1 multi-candidate cascade | Candidate-based semantic comparison |
| 6 | B2 diagnosis and recovery | Risk analysis and bounded recovery controller |
| 7 | Comparative evaluation and ablations | Fair B0/B1/B2 comparison, sensitivity and ablation results |
| 8 | Demo, report and reproducibility handoff | Working demonstration and evidence-backed research report |

---

## 4. Detailed phase plan

### Phase 0 — Research and repository audit

**Goal:** Establish the exact research question and prevent accidental deviation.

**Tasks:**

- Inspect the repository and existing code before modifying anything.
- Read project scope and applicable Cursor rules.
- Verify the target paper's title, authors, year, methods, dataset, model, and evaluation protocol from the paper itself.
- Separate paper-inspired baseline, reproduction/approximation, proposed CascadeGuard extension, and exploratory experiments.
- Verify dataset candidates, exact release, annotations, splits, speaker metadata, and license.
- Record assumptions and unresolved questions.

**Deliverables:**

- `docs/REPOSITORY_AUDIT.md`
- `docs/RESEARCH_ALIGNMENT.md`
- `docs/RESEARCH_DEVIATIONS.md`
- `docs/DATASET_CARD.md`
- `docs/IMPLEMENTATION_PLAN.md` (or this document as the canonical plan)

**Exit criteria:**

- Research questions are testable.
- Dataset source and license are verified or explicitly unresolved.
- No unverified paper details are stated as facts.
- Scope is approved.

---

### Phase 1 — Environment, dataset and audio foundation

**Goal:** Build a reproducible Python environment, validate the chosen dataset, and implement the audio-processing foundation. **Do not train complex models yet.**

#### 1. Environment

- Use Python 3.11 unless a verified dependency constraint requires otherwise.
- Create an isolated virtual environment.
- Add a minimal dependency manifest with compatible pinned/bounded versions.
- Establish package structure, YAML configuration loading, logging, and pytest.
- Support CPU execution first; detect GPU availability rather than assuming it.
- Record Python, OS, package, and hardware details.

#### 2. Dataset verification and adapter

- Verify the dataset's source, exact release, and license before use.
- Preserve official train/validation/test splits.
- Preserve speaker independence if speaker metadata is available.
- Build a manifest containing stable sample ID, audio path, split, transcript, semantic labels, speaker ID if available, duration, and sample rate.
- Validate missing files, invalid labels, duplicate IDs, corrupt audio, and unexpected split/speaker overlap.
- Inspect the real annotation schema; do not guess field names or sample counts.
- Keep original data immutable and derived data separate.

#### 3. Audio loading and preprocessing

Implement:

- Audio loading.
- Channel inspection and documented channel handling.
- Sample-rate inspection and explicit resampling when required.
- Duration and amplitude statistics.
- Empty/silent audio checks.
- Waveform visualization.
- STFT spectrogram generation.
- Log-Mel spectrogram generation.

Record feature parameters: sample rate, FFT size, hop length, window length, Mel-bin count, and normalization.

#### 4. Audio inspection

Inspect reproducible samples from each split:

- waveform,
- duration and sample rate,
- amplitude range,
- spectrogram,
- log-Mel representation,
- transcript and semantic annotation.

Do not infer dataset-wide properties from a few examples. Run a documented full-manifest analysis for dataset-level statistics.

#### 5. Tests

- Audio loader tests.
- Invalid/corrupt audio tests.
- Sample-rate and channel tests.
- Manifest schema tests.
- Split and speaker integrity tests where applicable.
- Duplicate ID tests.
- Feature shape and finite-value tests.
- Deterministic preprocessing tests.

#### Phase 1 deliverables

- `pyproject.toml` or equivalent dependency manifest.
- `.gitignore`
- `configs/default.yaml`
- `configs/dataset.yaml`
- `src/cascadeguard/audio/loader.py`
- `src/cascadeguard/audio/preprocessing.py`
- `src/cascadeguard/audio/features.py`
- `src/cascadeguard/data/manifest.py`
- `src/cascadeguard/data/validation.py`
- `scripts/validate_dataset.py`
- `scripts/inspect_audio.py`
- `tests/`
- `docs/DATASET_CARD.md`
- `docs/PHASE_1_REPORT.md`

#### Phase 1 exit criteria

- A clean environment can install the project.
- Dataset source, release, and license are recorded.
- Official splits are preserved and integrity checks pass.
- Sample audio can be loaded and waveform, spectrogram, and log-Mel features generated.
- Feature extraction is deterministic under a fixed configuration.
- Tests pass and commands/results are recorded.
- **No model performance claims are made in Phase 1.**

#### Phase 1 non-goals

No custom ASR training, no recovery controller, no complex UI, no unnecessary additional datasets, and no CNN architecture before the feature pipeline is validated.

**Do not start custom ASR training or the recovery controller in Phase 1.**

---

### Phase 2 — Speech fundamentals and acoustic modeling

**Goal:** Demonstrate practical understanding of speech representations, convolution, and encoder-decoder structures.

**Tasks:**

- Document waveform, framing, windowing, STFT, spectrogram, and log-Mel concepts.
- Explain 1D convolution over waveform/features versus 2D convolution over time-frequency representations.
- Implement a small, isolated CNN feature experiment on a suitable task.
- Clearly label an auxiliary classification experiment as classification—not general-purpose ASR.
- Demonstrate how 2D feature maps can be pooled/projected into a 1D sequence of feature vectors.
- Study encoder-decoder ASR: encoder, decoder, attention, teacher forcing, and autoregressive inference.
- Explain conceptual differences between encoder-decoder and CTC-style ASR where relevant.

**Deliverables:**

- `docs/SPEECH_FUNDAMENTALS.md`
- `notebooks/01_audio_representations.ipynb`
- `notebooks/02_convolution_experiments.ipynb`
- `src/cascadeguard/acoustic/`
- Saved configuration and results for the small feature/CNN experiment.

**Exit criteria:**

- Explain each representation and convolution dimension.
- Show actual tensor shapes.
- Explain how acoustic features become a sequence for downstream modeling.
- Distinguish the auxiliary CNN task from the main ASR → NLU pipeline.
- Do not claim the CNN performs ASR unless it actually does.

---

### Phase 3 — B0 single-best cascaded baseline

**Goal:** Build the first end-to-end pipeline.

**Tasks:**

- Select and configure an approved ASR backend.
- Implement a stable ASR interface.
- Preserve raw transcripts and available decoding metadata.
- Implement a dataset-compatible NLU baseline for intent and slot extraction.
- Normalize outputs into a typed semantic-frame schema.
- Build an orchestrator connecting audio → ASR → NLU.
- Preserve sample IDs and per-stage outputs.
- Evaluate clean audio without tuning on test data.

**Deliverables:**

- `src/cascadeguard/asr/`
- `src/cascadeguard/nlu/`
- `src/cascadeguard/pipeline/`
- `configs/asr.yaml`
- `configs/nlu.yaml`
- `scripts/run_b0.py`
- `src/cascadeguard/evaluation/`
- `artifacts/experiments/<run_id>/`
- `docs/BASELINE_REPORT.md`

**Metrics:**

- WER/CER where appropriate.
- Intent accuracy and macro-F1.
- Slot precision, recall, and F1.
- Exact semantic-frame match.
- Per-stage and end-to-end latency.

**Exit criteria:**

- B0 runs from audio to semantic output.
- Predictions and metrics are saved.
- Raw ASR and NLU outputs are traceable per sample.
- Baseline configuration and test IDs are frozen.
- Failure cases are not manually corrected.

---

### Phase 4 — Controlled failures and error propagation

**Goal:** Test how acoustic and transcript errors affect semantic interpretation.

**Audio-level conditions:**

- Background noise.
- Amplitude reduction.
- Clipping.
- Reverberation.
- Speaking-rate perturbation where semantics remain intact.

**Transcript-level conditions:**

- Substitution.
- Deletion.
- Insertion.
- Word-boundary changes.
- Number/entity corruption.
- Negation corruption.

**Tasks:**

- Implement configurable transforms as separate functions.
- Keep clean source data immutable.
- Store derived samples separately.
- Record source ID, transform, parameters, severity, and seed.
- Run B0 on clean and perturbed conditions.
- Compare ASR error with intent, slot, and semantic-frame changes.
- Separate natural ASR errors from synthetic corruption.

**Deliverables:**

- `src/cascadeguard/perturbations/audio.py`
- `src/cascadeguard/perturbations/text.py`
- `scripts/generate_perturbations.py`
- `scripts/run_error_analysis.py`
- `docs/ERROR_PROPAGATION_REPORT.md`

**Exit criteria:**

- Every transformed sample maps to its original.
- Corruption is reproducible.
- Clean and perturbed conditions use comparable sample IDs.
- Per-condition metrics and representative traces are available.
- Synthetic stress tests are not presented as natural error prevalence.

---

### Phase 5 — B1 multi-candidate cascade

**Goal:** Test whether multiple transcript candidates improve semantic interpretation.

**Tasks:**

- Check whether the ASR backend genuinely exposes N-best hypotheses.
- Preserve candidate order and scores if available.
- If unavailable, use separately decoded candidates only as an explicitly labelled proxy.
- Run NLU on each candidate.
- Compare semantic-frame agreement and disagreement.
- Implement transparent candidate selection.
- Compare B1 with B0 on identical samples.

**Deliverables:**

- `src/cascadeguard/asr/candidates.py`
- `src/cascadeguard/nlu/candidate_analysis.py`
- `src/cascadeguard/pipeline/b1.py`
- `scripts/run_b1.py`
- `docs/B1_REPORT.md`

**Exit criteria:**

- Candidate provenance is explicit.
- No fabricated N-best output or metadata.
- Candidate selection is documented.
- Accuracy, latency, and failure cases are compared with B0.

---

### Phase 6 — B2 failure diagnosis and recovery

**Goal:** Identify risky outputs and select a bounded, conservative recovery action.

**Potential signals:**

- ASR confidence/metadata when genuinely provided.
- Candidate disagreement.
- NLU confidence, if meaningful.
- Missing required slots.
- Semantic inconsistency.
- Invalid schema.
- Empty output or timeout.

**Actions:**

- CONTINUE
- RETRY
- CLARIFY
- HOLD

**Tasks:**

- Define typed diagnosis and recovery schemas.
- Implement transparent rules before learned risk models.
- Select thresholds on validation data only.
- Set retry limits and timeouts.
- Prevent infinite retry loops.
- Record signals, diagnosis, policy, action, and outcome.
- Evaluate successful and harmful/unnecessary recovery.

**Deliverables:**

- `src/cascadeguard/diagnosis/`
- `src/cascadeguard/recovery/`
- `src/cascadeguard/pipeline/b2.py`
- `scripts/run_b2.py`
- `docs/RECOVERY_POLICY.md`
- `docs/B2_REPORT.md`

**Exit criteria:**

- All four actions are testable.
- Recovery is bounded and traceable.
- Unresolved ambiguity does not become an invented answer.
- Thresholds are not selected on test data.
- False alarms, harmful recovery, recovery success, and latency are reported.

---

### Phase 7 — Comparative evaluation and ablations

**Goal:** Test whether B1 and B2 add measurable value over B0, and at what cost.

**Tasks:**

- Freeze configurations and selected models.
- Run B0, B1, and B2 on identical evaluation sample IDs.
- Report clean and each corruption condition separately.
- Run ablations:
  - B2 without candidate disagreement.
  - B2 without retry.
  - B2 without clarification.
  - B2 without selected risk signals.
  - Threshold sensitivity.
- Use multiple seeds for stochastic training where feasible.
- Report mean/standard deviation or confidence intervals where appropriate.
- Use paired comparisons on shared samples where suitable.
- Analyze class-wise and error-category performance.

**Deliverables:**

- `scripts/run_comparison.py`
- `scripts/run_ablations.py`
- `reports/metrics/`
- `reports/figures/`
- `docs/FINAL_EVALUATION.md`

**Exit criteria:**

- Comparisons are fair and reproducible.
- Metrics have precise definitions.
- Negative results and regressions are reported.
- Latency and false-alarm costs accompany accuracy claims.
- No unsupported superiority claims.

---

### Phase 8 — Demo, report and reproducibility handoff

**Goal:** Make the system understandable and independently runnable.

**Demo should show:**

- Audio input and playback.
- Transcript.
- Intent and slots.
- Diagnosis signals.
- Recovery action and reason.
- Final semantic output.
- Per-stage and end-to-end latency.

**Include three case studies:**

- ASR error propagates into incorrect semantics.
- Recovery improves an incorrect or uncertain outcome.
- False alarm or unresolved ambiguity.

**Research report should include:**

- Problem and motivation.
- Related work and verified paper comparison.
- Dataset and license.
- Methods and architecture.
- Experimental setup.
- B0/B1/B2 results.
- Ablations.
- Error analysis.
- Limitations and threats to validity.
- Reproducibility instructions.

**Deliverables:**

- Demo entry point.
- `docs/FINAL_REPORT.md`
- `docs/REPRODUCIBILITY.md`
- `docs/LIMITATIONS.md`
- Saved configs, predictions, metrics, and figures.

**Exit criteria:**

- Demo works from documented instructions.
- A fresh environment can reproduce at least baseline evaluation.
- Every reported number traces to a saved experiment.
- Limitations and deviations are explicit.

---

## 5. Phase 1 — What to implement first (prioritized)

**Objective:** Establish the foundation before implementing ML models.

| # | Task |
|---|------|
| 1 | Repository and Python environment audit |
| 2 | Dataset source, release and license verification |
| 3 | Dataset adapter and manifest generation |
| 4 | Dataset integrity and split validation |
| 5 | Audio loading and preprocessing |
| 6 | Waveform and spectrogram generation |
| 7 | Log-Mel spectrogram extraction |
| 8 | Unit tests and Phase 1 report |

**Phase 1 exit criteria (checklist):**

- Reproducible Python environment.
- Dataset source and license verified.
- Official dataset splits preserved.
- Audio loader and preprocessing functional.
- Waveform, spectrogram and log-Mel features generated.
- Tests executed and passing.
- Dataset and implementation documented.

---

## 6. Phase 1 actionable checklist

Complete these tasks **in order** before starting Phase 2.

### Task 1 — Repository and environment audit

- Inspect existing files and Git status.
- Check Python version and CPU/GPU availability.
- Check existing dependencies.
- Preserve working code; do not overwrite blindly.
- Create or validate the virtual environment.
- Establish the minimal package structure.

**Acceptance:** Installation instructions work from a clean checkout.

### Task 2 — Dataset and license verification

- Verify exact dataset source and release.
- Read the license and usage restrictions.
- Inspect official split files and annotation format.
- Confirm whether speaker metadata exists.
- Record dataset version and retrieval date.
- Do not download/use if provenance or license remains unclear.

**Acceptance:** `docs/DATASET_CARD.md` records verified source, release, license, split details, fields, and unresolved issues.

### Task 3 — Dataset manifest

Adapt the following suggested fields to the **actual** dataset:

- `sample_id`
- `audio_path`
- `split`
- `transcript`
- `intent`
- `slots`
- `speaker_id` (if available)
- `duration_seconds`
- `sample_rate`

**Acceptance:** Manifest generation is repeatable and schema validation passes.

### Task 4 — Dataset integrity

Check missing audio, corrupt audio, missing annotations, invalid labels, duplicate IDs, split overlap, speaker overlap where metadata exists, and unexpected audio formats/sample rates.

**Acceptance:** Validation report lists detected issues and exclusion reasons. Nothing is silently dropped.

### Task 5 — Audio loader and preprocessing

Implement loading, channel inspection, sample-rate handling, duration, amplitude statistics, silence detection, and explicit resampling.

**Acceptance:** Unit tests cover valid audio and invalid/boundary inputs.

### Task 6 — Feature extraction

Implement waveform representation, STFT spectrogram, and log-Mel spectrogram. Store parameters in YAML.

**Acceptance:** Repeated extraction with the same input/config produces consistent shapes and values within expected numerical tolerance.

### Task 7 — Audio inspection

Create a script or notebook displaying waveform, spectrogram, log-Mel spectrogram, transcript, semantic annotation, and audio metadata. Inspect examples from each split.

**Acceptance:** Outputs can be regenerated using documented commands.

### Task 8 — Testing and report

Run Phase 1 tests and create `docs/PHASE_1_REPORT.md`.

Report environment versions, dataset provenance/license, manifest and integrity results, measured audio statistics, feature configuration, actual test outcomes, and unresolved issues.

**Acceptance:** All Phase 1 exit criteria are met.

---

## 7. Suggested Phase 1 repository structure

Adapt the existing repository rather than blindly replacing it. Do not create empty modules for future phases.

```text
cascadeguard/
├── configs/
│   ├── default.yaml
│   └── dataset.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── manifests/
├── docs/
│   ├── DATASET_CARD.md
│   ├── REPOSITORY_AUDIT.md
│   └── PHASE_1_REPORT.md
├── notebooks/
│   └── 01_audio_inspection.ipynb
├── scripts/
│   ├── validate_dataset.py
│   └── inspect_audio.py
├── src/
│   └── cascadeguard/
│       ├── audio/
│       │   ├── loader.py
│       │   ├── preprocessing.py
│       │   └── features.py
│       ├── data/
│       │   ├── manifest.py
│       │   └── validation.py
│       └── utils/
│           ├── config.py
│           ├── logging.py
│           └── paths.py
├── tests/
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## 8. Cursor Agent prompt — Phase 1

Copy this prompt into Cursor Agent mode after adding the project rules and this plan to the repository.

```markdown
You are implementing Phase 1 of CascadeGuard.

Before making changes:

- Read AGENTS.md, all applicable .cursor/rules/*.mdc files, and the project scope/phase plan.
- Inspect the current repository, existing code, dependency files, and Git status.
- Inspect actual dataset documentation and files available locally.
- Verify dataset source, exact release, license, annotation schema, official splits, and speaker metadata where available.
- Do not assume dataset field names, sample counts, audio format, or license terms.

Objective: Build a reproducible environment and data/audio foundation. Do not implement the ASR/NLU pipeline or recovery controller in this phase.

A. Audit
- Write docs/REPOSITORY_AUDIT.md.
- Identify existing code to preserve.
- List missing prerequisites and unresolved questions.

B. Environment
- Establish the project package structure.
- Use a compatible Python environment.
- Add only necessary dependencies.
- Support CPU execution.
- Add configuration loading and structured logging.
- Document installation and verification commands.

C. Dataset
- Verify provenance and license before download/use.
- Build a manifest from the real annotation schema.
- Preserve official splits and speaker independence.
- Keep original files immutable.
- Implement integrity checks for missing, corrupt, duplicated, and invalid records.
- Record exclusions and reasons.

D. Audio
- Implement audio loading and explicit preprocessing.
- Inspect sample rate, channels, duration, amplitude, and silence.
- Generate waveform, STFT spectrogram, and log-Mel features.
- Store transform parameters in YAML.
- Make preprocessing deterministic where applicable.

E. Tests
- Add pytest coverage for loaders, manifests, validation, and feature extraction.
- Include invalid files, empty audio, unexpected sample rates, and malformed annotations.
- Run tests and report actual outcomes only.

F. Documentation
- Create docs/DATASET_CARD.md, docs/REPOSITORY_AUDIT.md, docs/PHASE_1_REPORT.md, and notebooks/01_audio_inspection.ipynb or an equivalent reproducible inspection script.

Constraints
- Do not train a custom ASR or NLU model.
- Do not implement B0/B1/B2 yet.
- Do not introduce a Streamlit UI.
- Do not add unnecessary model frameworks.
- Do not modify original data.
- Do not fabricate dataset statistics or test results.
- Do not change the approved research direction.
- If a methodological or dataset decision is unclear, document it and ask before proceeding.

Completion report
- Files created or modified.
- Environment and dependency versions.
- Dataset source, release, and license verification status.
- Manifest and integrity-check results.
- Audio feature extraction configuration.
- Tests actually executed and their outcomes.
- Unresolved issues and risks.
- Whether every Phase 1 exit criterion is satisfied.

Do not begin Phase 2 until Phase 1 is reviewed and approved.
```

---

## 9. Non-negotiable implementation rules

- Implement **one phase at a time**.
- Do not skip baseline evaluation to build advanced recovery logic.
- Never train on test data or tune thresholds on test results.
- Do not treat model confidence as proof of correctness.
- Do not fabricate native N-best hypotheses.
- Do not conflate synthetic corruption with natural ASR error prevalence.
- Preserve raw predictions, sample IDs, configurations, and logs.
- Report negative results and regressions.
- Obtain approval for material research deviations (record in `docs/RESEARCH_DEVIATIONS.md`).
- Prefer a small, validated implementation over a large, untested one.

**Priority:** Research validity → data integrity → reproducibility → correctness → maintainability → performance optimization.

---

## 10. Research alignment (three layers)

Use this framing to align with Voice AI / speech-fundamentals expectations while keeping CascadeGuard as the main project:

| Layer | Content |
|-------|---------|
| **Layer 1 — Speech and acoustic fundamentals** | Raw audio, spectrogram, log-Mel, 1D/2D convolution, CNN feature extraction, encoder-decoder concepts |
| **Layer 2 — Cascaded Voice AI pipeline** | Audio → ASR → Transcript → NLU → intent and slots |
| **Layer 3 — Research contribution** | ASR error propagation, multi-candidate transcripts, failure diagnosis, retry/clarify/HOLD, accuracy/latency/recovery evaluation |

Phases 1–2 emphasize Layer 1; Phase 3+ emphasize Layers 2–3.

---

## 11. How to execute

1. Put this file in `docs/` (this document: `PHASE_WISE_IMPLEMENTATION_PLAN.md`).
2. Ensure `.cursor/rules/` (20 rule files) and `AGENTS.md` are in place.
3. Open Cursor Agent mode.
4. Copy the **Phase 1 Cursor prompt** (Section 8) or use `prompts/07_INITIAL_CODING_FOUNDATION.md` / `prompts/01_PHASE_1_DATA.md` as entry points.
5. Review the repository audit and Phase 1 deliverables before proceeding.

**Important:** Complete and validate Phase 1 before moving to Phase 2. This prevents model code on top of an unreliable dataset or preprocessing foundation.
