# Project Scope and Research Protocol

## 1. Problem statement

Cascaded speech systems pass the output of one component to the next. An ASR transcription error can become an NLU slot error, which can cause an incorrect downstream action.

Conventional pipelines may not detect that an early-stage error has made the final decision unsafe.

CascadeGuard will implement and evaluate a modular cascade with explicit uncertainty checks, error tracing and recovery policies.

## 2. Objective

Build a reproducible research prototype that compares:

- B0 — Single-best baseline: one ASR transcript → NLU → decision.
- B1 — Multi-candidate cascade: a set of transcript candidates → NLU for each → candidate ranking/ambiguity handling.
- B2 — Failure-aware cascade: risk checks → selective retry/clarification/HOLD → final decision.

The project must report where each method helps, where it fails, and the cost in latency and false alarms.

## 3. Primary dataset choice

**Superseded 2026-11-02.** Fluent Speech Commands is no longer the implementation dataset. SLURP is not a Phase 1 secondary dataset. The license history stays in `docs/DATASET_LICENSE_REGISTER.md`.

**Current candidate:** Mozilla Common Voice Scripted Speech v27.0, English, through Mozilla Data Collective only. The public catalogue lists locale `en`. Do not treat `en-US` as the release identifier until the owner confirms the account page. Terms are not accepted. The full archive listed at 88.43 GB does not fit on the disk measured the same day.

Common Voice provides audio and transcripts, not native intent and slot labels. Milestone A is ASR evaluation. Milestone B is a manual semantic subset. See `docs/PHASE_0_DECISION_LOG.md`.

Preserve the dataset's official splits; do not randomly mix speakers across splits.

Google Speech Commands remains optional for a separate keyword-classification experiment. Its labels are not equivalent to general SLU intent/slot labels.

## 4. Scope boundaries

### In scope

- Audio loading, validation and preprocessing.
- ASR integration with a local model or a clearly documented transcript-input adapter.
- NLU intent and slot extraction using dataset labels and a transparent baseline.
- Controlled audio and transcript perturbations.
- Multi-candidate evaluation where genuine ASR N-best output is available.
- Failure detection, recovery policy and HOLD/clarification action.
- Evaluation, ablations, error analysis, demo and research report.

### Out of scope

- Production deployment, authentication, billing, real telephony, multilingual coverage claims.
- Training Whisper or another large ASR model from scratch.
- Manual creation/annotation of a new dataset.
- Claims that synthetic corruption represents the natural prevalence of errors.
- Claims of root-cause diagnosis from confidence scores alone.

## 5. Research hypotheses

These are hypotheses to test, not assumed outcomes.

- H1: ASR errors that alter task-critical words/entities cause a measurable drop in slot and end-to-end task accuracy.
- H2: Candidate-based interpretation can improve task accuracy on ambiguous/noisy cases, potentially at higher latency.
- H3: A selective failure-aware policy can reduce unsafe task decisions, but may increase HOLD/clarification frequency.
- H4: Recovery benefits depend on error type; no single recovery policy will dominate every condition.

## 6. Pipeline specification

1. Dataset adapter:
   Returns sample ID, audio path, transcript, intent, slots, speaker and official split.

2. Audio validation:
   Sample rate, channels, duration, empty/corrupt audio checks.

3. Preprocessing:
   Deterministic resampling/channel handling; optional normalization. Preserve original audio.

4. ASR:
   Local ASR model produces transcript and, if supported, N-best candidates and token/segment metadata. Store model/config.

5. NLU:
   Predicts intent and slots from transcript. Start with a transparent baseline; add a learned model only after baseline metrics work.

6. Risk analysis:
   Compare candidate agreement, slot validity, missing required slots, out-of-domain output and ASR metadata. Treat scores as heuristics unless calibrated.

7. Controller:
   CONTINUE, RETRY, CLARIFY or HOLD. Define deterministic rules and log the reason.

8. Output:
   Structured prediction and trace. No external action is executed by the research prototype.

9. Evaluation:
   Compare B0/B1/B2 on identical samples and perturbation conditions.

## 7. Failure taxonomy

Keep these categories separate.

### Acoustic failures
- Background noise
- Low amplitude
- Clipping
- Reverberation
- Speed/pitch perturbation

### ASR text failures
- Deletion
- Insertion
- Substitution
- Word-boundary errors
- Number/entity corruption

### Semantic failures
- Wrong intent
- Wrong slot
- Missing slot
- Slot-value swap
- Negation/polarity change

### Pipeline/control failures
- Timeout
- Empty output
- Malformed output
- Schema violation
- Stale result

For every perturbation, store the transformation name, parameter values, seed, source sample ID and whether it was audio-level or transcript-level.

Do not label a deliberately injected cause as an online diagnosis. The experiment knows the injected cause; the deployed-style controller does not.

## 8. Evaluation metrics

### ASR
- Word Error Rate (WER)
- Character Error Rate (CER), optionally

### NLU
- Intent accuracy
- Slot precision
- Slot recall
- Slot F1

### End-to-end
- Exact semantic frame match
- Task success rate

### Failure detection
- Precision
- Recall
- F1
- False-positive rate
- Detection coverage

### Recovery
- Recovery success among eligible failed cases
- Harmful recovery rate
- HOLD/clarification rate

### Efficiency
- Per-stage latency
- End-to-end latency
- Throughput
- Memory where practical

Report metrics by clean/noise/error condition and by failure category.

Include confidence intervals or bootstrap intervals where feasible. State sample counts and denominators.

## 9. Experimental controls

- Use official speaker-independent splits.
- Keep the same evaluation sample IDs across B0/B1/B2.
- Fix and log random seeds.
- Tune thresholds only on validation data; do not tune on test.
- Preserve a clean, unmodified evaluation condition.
- Separate audio corruption from transcript corruption.
- Do not compare methods on different sample subsets without explaining the difference.
- Store raw predictions and per-sample traces, not just aggregate scores.

## 10. Definition of done

The project is complete when:

1. A reproducible command runs the clean baseline end-to-end.
2. B0/B1/B2 run on the same evaluation set.
3. Perturbations are reproducible and traceable.
4. Metrics are calculated from saved predictions.
5. At least three detailed failure case studies are documented.
6. An ablation explains which components contribute.
7. Limitations, licensing, dataset bias and synthetic-data caveats are explicit.
8. A demo and report can be reproduced from documented commands.
