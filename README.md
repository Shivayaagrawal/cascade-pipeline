# Cascaded Speech Processing Pipeline

A research prototype demonstrating how errors in upstream transcript processing can propagate into downstream Natural Language Understanding (NLU), and how failure-aware decision mechanisms can reduce unsafe semantic commitments.

## Overview

This project explores the downstream stages of a cascaded speech-processing pipeline using synthetic, text-only data.

It investigates three key questions:

- How does single-best versus multi-candidate transcript processing affect semantic decisions?
- How can downstream components identify potentially incorrect or ambiguous intent and slot values?
- Can reference-aware verification prevent incorrect critical-slot commitments, and what is the resulting coverage trade-off?

**Scope:** This is a synthetic text-based simulation.

## Architecture

The prototype consists of the following processing identities:

| Component | Description |
|---|---|
| B0 – Prefix Baseline | Conventional single-best transcript processing and prefix parsing. |
| B1 – Multi-Candidate Processing | Processes multiple transcript candidates and separates lexical and prefix-based selection. |
| B2 – Failure-Aware Controller | Evaluates semantic decisions and selects an appropriate recovery action. |
| Semantic v4 | Investigates semantic failure patterns and selective decision behaviour. |
| Semantic v5 | Adds semantic integrity and commitment controls. |
| Reference-Aware v1 | Verifies proposed critical-slot values against explicit reference evidence. |

### Recovery Actions

| Action | Purpose |
|---|---|
| CONTINUE | Proceed with the current semantic decision. |
| RETRY | Simulate rescoring alternative candidates. |
| CLARIFY | Indicate that additional information is needed. |
| HOLD | Abstain from committing a semantic frame. |

## Key Features

- Single-best and multi-candidate transcript processing.
- Intent and slot interpretation.
- Failure-aware semantic decision-making.
- Selective recovery through CONTINUE, RETRY, CLARIFY and HOLD.
- Semantic integrity and critical-slot verification.
- Reference-aware commitment control.
- Normalized decision facade with safe handling of empty candidate bundles.
- Experimental evaluation of coverage, selective risk and unsafe commitments.

## Edge Cases and Vulnerabilities Evaluated

The experiments investigate:

- **Critical-slot substitutions:** Incorrect but valid-looking values replacing intended values.
- **Negation:** Changes in meaning caused by negation.
- **Uncertainty:** Expressions such as maybe, possibly and might.
- **Ambiguity:** Inputs with multiple plausible interpretations.
- **Candidate conflicts:** Multiple candidates proposing different semantic values.
- **Out-of-inventory values:** Unsupported values such as unrecognized dates or numbers.
- **Empty candidate bundles:** No available transcript candidates.
- **Clean and polite variations:** Ensuring safeguards do not unnecessarily reject valid inputs.
- **Unsafe commitment:** Incorrect semantic frames being accepted despite upstream errors.
- **Missing reference evidence:** The inability of candidate-only processing to reliably identify a plausible but incorrect value.

## Experimental Findings

### Phase 5 – Semantic Integrity

- Test cases: 56
- Decision coverage: 23/56
- Unsafe commitments: 14/23

The candidate-only semantic integrity approach still committed all 14 tested in-inventory critical-slot substitutions.

### Phase 6 – Reference-Aware Verification

- Test cases: 36
- Candidate-only coverage: 19/36
- Reference-aware coverage: 11/36
- Reference-aware unsafe commitments: 0/11
- Critical-slot substitutions prevented: 9/9
- Clean/polite controls falsely rejected: 0/7

**Key finding:** Explicit critical-slot reference evidence prevented all tested in-inventory substitutions, but reduced decision coverage. This demonstrates a coverage-versus-safety trade-off rather than a universally safe solution.

The Phase 5 and Phase 6 experiments reuse the same eligible parent pool and should not be interpreted as independent population evaluations.

## Dataset

The project uses synthetically generated, text-only datasets containing:

- Reference utterances.
- Controlled transcript variations.
- Synthetic candidate bundles.
- Semantic annotations and expected slot values.
- Edge-case and challenge examples.

Historical research assets also include Common Voice and LibriSpeech metadata and annotations. These are not used to claim real-speech performance in the Phase 3–6 experiments.

Oracle labels represent same-session experimental specifications, not independent human annotations.

## Research Background

The project was developed alongside study of:

- Convolutional Neural Networks (CNNs).
- 1D and 2D convolution operations.
- Spectrogram-based speech representations.
- Dilated and causal convolutions.
- Cascaded processing and encoder-decoder architectures.

The implementation focuses on downstream semantic processing rather than implementing these audio-processing or ASR architectures.

## Research Limitations

- No waveform decoding or audio feature extraction.
- No real ASR model or genuine ASR N-best output.
- No real-world WER or CER evaluation.
- No independent human-gold evaluation.
- No production speech-understanding deployment.
- Results are limited to the evaluated synthetic grammar, datasets and utterance IDs.
- RETRY is simulated candidate rescoring, not a new speech-recognition pass.
- CLARIFY is a recovery action label; no natural-language clarification question is generated.

## Repository Structure

```text
CascadeGuard/
├── src/                 # Pipeline and controller implementations
├── tests/               # Automated tests
├── scripts/             # Research and execution scripts
├── configs/             # Configuration files
├── data/
│   ├── synthetic/       # Synthetic transcript data
│   ├── phase3/          # Phase 3 datasets
│   ├── phase4/          # Phase 4 datasets
│   ├── phase5/          # Phase 5 datasets
│   ├── phase6/          # Phase 6 datasets
│   └── schemas/         # Data schemas
├── experiments/
│   ├── phase3/
│   ├── phase4/
│   ├── phase5/
│   └── phase6/
├── docs/                # Research documentation
└── README.md
```

## Conclusion

This project demonstrates a failure-aware downstream cascaded processing pipeline. Its primary contribution is an experimental investigation of transcript-error propagation, semantic integrity, critical-slot substitutions and reference-aware recovery.

The findings highlight an important design trade-off: preventing unsafe semantic commitments may require sacrificing decision coverage when reliable reference evidence is available.
