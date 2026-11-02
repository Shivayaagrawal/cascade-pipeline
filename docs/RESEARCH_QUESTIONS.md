# Research Questions and Hypotheses

These are questions to test. They are not expected outcomes. An experiment that rejects a hypothesis is a valid result and must be reported.

The questions match `docs/PROJECT_SCOPE.md`. They are not the training objective in Ruan et al. 2020. That difference is documented in `docs/RESEARCH_DEVIATIONS.md`.

## Questions

**RQ1.** How do ASR errors propagate into downstream intent classification and slot extraction?

**RQ2.** Can multiple transcript candidates improve semantic understanding compared with a single-best transcript?

**RQ3.** Can failure-aware diagnosis identify unreliable semantic predictions?

**RQ4.** Can recovery actions improve reliability while keeping latency and false-positive rate acceptable?

“Acceptable” is not defined numerically yet. Thresholds for latency and false alarms are PENDING owner limits before any test-set run.

## Hypotheses

**H1.** Increasing ASR error severity can increase downstream semantic errors.

Falsified if, on a fixed sample set, a higher-severity condition does not raise intent error, slot error, or exact-frame error relative to a lower-severity or clean condition, within the uncertainty method named in `docs/EXPERIMENTAL_PROTOCOL.md`.

**H2.** Multiple transcript candidates may improve semantic accuracy on some ambiguous cases.

Falsified for a declared candidate source if exact-frame accuracy on the paired evaluation IDs is not higher than B0. A gain that appears only on a subset must be reported as a subset result, with the subset rule fixed before looking at test outcomes.

**H3.** Failure-aware recovery may reduce harmful predictions at the cost of higher latency or more clarification.

Falsified if B2 does not reduce unsafe final decisions relative to B0 on the same IDs, or if it does so only by changing the metric definition. The cost side is descriptive: report latency, clarification rate, and HOLD rate even when accuracy does not improve.

## Which dataset can answer them

Amended 2026-11-02. Each question is scored once on FSC and, separately, once on SLURP real speech. Synthetic SLURP audio is a third condition, not a mix-in. ATIS is not an implementation dataset. A CNN keyword model does not answer these questions.

| Question | Experiments | Metrics |
|----------|-------------|---------|
| RQ1 | E1 clean or natural decode, and E2 acoustic corruption kept separate from transcript edits | WER when audio is decoded, intent accuracy, slot micro-F1, exact frame match |
| RQ2 | E3: B1 versus B0 on the same IDs. Candidate source is `native_nbest` or a named proxy. | Exact frame match, candidate agreement, latency |
| RQ3 | E4 detection against frame mismatch. Injected labels are hidden from the detector. | Detection precision, recall, F1, false-positive rate on correct clean frames |
| RQ4 | E4 actions CONTINUE, RETRY, CLARIFY, HOLD | Recovery success, harmful recovery, clarification rate, HOLD rate, latency |

No expected gain is stated. A negative result is a valid outcome.

## What would not answer these questions

- An end-to-end speech-to-intent model with no transcript.
- A robustness-training run that reports only F1 and never traces which words changed the frame.
- A candidate list whose origin is unrecorded.
- A comparison of B0, B1, and B2 on different sample IDs.

## Status

Defined. Not tested. No dataset has been loaded.
