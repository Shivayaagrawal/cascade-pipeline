# 14-Day Phase Plan

**Superseded.** This schedule assumed a Fluent Speech Commands download. The current Phase 1 document is `docs/PHASE_1_IMPLEMENTATION_PLAN.md`. It is not approved, and it does not authorize an FSC or Common Voice download.

This is a focused prototype schedule. Prioritize a working baseline and defensible evaluation over adding many model architectures.

## Day 1 — Environment and data audit

Tasks:
- Create repository and Python environment.
- Download/obtain FSC using its official instructions.
- Read and record license, release, split files and directory structure.
- Build a dataset inspection script.
- Count samples per split, speaker and intent.

Deliverables:
- Environment lock/requirements
- data_manifest.csv
- DATASET_CARD.md

Exit gate:
Data loads and labels map correctly; no split leakage.

## Day 2 — Dataset adapter and audio QA

Tasks:
- Implement typed sample schema and dataset adapter.
- Validate file existence, duration, channels, sample rate and corrupt/empty audio.
- Create a small deterministic smoke-test subset.

Deliverables:
- Dataset loader
- QA report
- Unit tests

Exit gate:
Loader returns audio, transcript, intent, slots, speaker and split.

## Day 3 — Baseline NLU and metrics

Tasks:
- Implement transcript-to-intent/slot baseline.
- Add intent accuracy, slot F1 and exact semantic-frame match.
- Save per-sample predictions.

Deliverables:
- NLU baseline
- Metric tests

Exit gate:
Metrics can be computed from saved predictions, independent of the model.

## Day 4 — Local ASR integration

Tasks:
- Integrate local faster-whisper or another approved local ASR.
- Add ASR adapter and transcript-input fallback for debugging.
- Compute WER and stage latency.

Deliverables:
- Audio → ASR → NLU CLI pipeline

Exit gate:
Clean end-to-end run completes on a small subset. Record ASR model/version and decoding settings.

## Day 5 — Baseline benchmark

Tasks:
- Run B0 on a fixed validation/test subset as allowed by protocol.
- Save config, logs, per-sample outputs and metrics.
- Inspect failures and verify several examples manually.

Deliverables:
- Baseline results CSV/JSON
- Error examples

Exit gate:
All reported values trace to actual output files.

## Day 6 — Controlled perturbation framework

Tasks:
- Add audio-level transforms: noise, volume change, clipping and speed change.
- Add transcript-level transforms: deletion, insertion, substitution and task-slot corruption.
- Keep transform metadata and deterministic seeds.

Deliverables:
- Perturbation module
- Manifest

Exit gate:
Original samples remain untouched; transformed samples are reproducible.

## Day 7 — Failure propagation analysis

Tasks:
- Compare ASR WER changes with intent/slot/task accuracy changes.
- Track error propagation by failure category.
- Generate confusion tables and per-stage traces.

Deliverables:
- Failure propagation analysis

Exit gate:
Report includes examples and denominators, not only aggregate claims.

## Day 8 — Multi-candidate cascade (B1)

Tasks:
- Use genuine ASR N-best output if supported by the selected decoder.
- If unavailable, do not call paraphrases or random edits N-best.
- Use clearly labelled candidate-generation experiments, such as independent decoding configurations, as a proxy.
- Run NLU over each candidate and rank using explicit criteria.

Deliverables:
- B1 candidate evaluator

Exit gate:
Provenance of every candidate is stored.

## Day 9 — Failure-aware controller (B2)

Tasks:
- Implement risk rules:
  - Missing required slot
  - Conflicting candidates
  - Invalid schema
  - Low-quality ASR metadata
  - Out-of-domain prediction
- Controller chooses CONTINUE, RETRY, CLARIFY or HOLD.
- Log trigger and action reason.

Deliverables:
- Deterministic controller
- Tests

Exit gate:
No unlogged decision; thresholds are configurable and validation-tuned.

## Day 10 — Recovery experiments

Tasks:
- Evaluate retry and clarification policies on eligible cases.
- Measure recovery success, harmful recovery, false alarms and latency.
- Compare B0/B1/B2 on identical IDs.

Deliverables:
- Comparative results table

Exit gate:
All methods use same evaluation population and perturbation conditions.

## Day 11 — CNN acoustic experiment (optional stretch)

Tasks:
- If time and compute permit, train a small 1D waveform CNN or 2D log-Mel CNN on Google Speech Commands.
- Treat it as a separate keyword-recognition experiment, not a replacement for the FSC ASR system.
- Report accuracy, model size and inference time.

Deliverables:
- Reproducible CNN experiment

Exit gate:
If compute/time is insufficient, document as deferred rather than weakening core evaluation.

## Day 12 — Ablations and robustness

Tasks:
- Remove candidate agreement, risk rules or recovery action one at a time.
- Compare effects by perturbation type.
- Analyze threshold sensitivity and clean-condition false positives.

Deliverables:
- Ablation and sensitivity tables

Exit gate:
Conclusions are limited to observed experiments.

## Day 13 — Demo and case studies

Tasks:
- Build a lightweight Streamlit or CLI demo.
- Show audio, transcript, NLU frame, risk flags, controller action and trace.
- Prepare at least three case studies:
  - Propagated error
  - Successful recovery
  - False alarm or unresolved ambiguity

Deliverables:
- Demo
- Architecture diagram
- Case studies

Exit gate:
Demo output agrees with saved evaluation records.

## Day 14 — Research report and reproducibility pass

Tasks:
- Write abstract, motivation, related-work notes, methodology, dataset, experiments, results, limitations and conclusion.
- Re-run core benchmark from documented commands.
- Verify all tables are generated from saved results.

Deliverables:
- Final report
- README
- Experiment configs
- Demo instructions

Exit gate:
A reviewer can reproduce the baseline and comparative evaluation.

## Scope control

If behind schedule, defer in this order:

1. CNN stretch experiment.
2. SLURP secondary dataset.
3. TTS and polished UI.
4. Additional ASR models.

Do not defer baseline metrics, controlled perturbations, fair B0/B1/B2 comparison, or limitations.
