# Experimental Protocol

**Status:** Rules for later experiments. No run has been executed.  
**Date:** 2026-11-02.

## Question each configuration answers

| ID | Question | Independent variable | Dependent variables |
|----|----------|----------------------|---------------------|
| B0 | What does one transcript produce? | Single ASR transcript or the human transcript in transcript-input mode | WER when audio is used, intent accuracy, slot micro-F1, exact frame match, latency |
| B1 | Do extra candidates change the frame? | Candidate source, declared in the config | Same semantic metrics, plus candidate count and latency |
| B2 | Does a bounded controller avoid bad frames? | Diagnosis rules and validation-chosen thresholds | Detection precision and recall, false-positive rate, recovery success, harmful recovery, clarification rate, HOLD rate, latency |

Hypotheses are in `docs/RESEARCH_QUESTIONS.md`. Metric formulas are in `docs/METRIC_DEFINITIONS.md`.

## Dataset tracks

Amended again 2026-11-02. Research design only. **Not a terms acceptance and not a download.**

| Track | Role | Data | Status |
|-------|------|------|--------|
| Reference notes | What Ruan et al. 2020 did | ATIS and a private Alexa set, Amazon Transcribe, 1-best | Paper read. ATIS is **out of implementation scope**. Not a reproduction. |
| Common Voice | Primary candidate for Milestone A (ASR) and later Milestone B (manual semantics) | Scripted Speech v27.0 English, MDC only | Candidate. Locale and dataset ID are not frozen. Terms not accepted. No secondary dataset in Phase 1. |
| FSC | Previous primary | Fluent Speech Commands | SUPERSEDED as the implementation dataset. License still Pending. Do not download. |
| SLURP | Previous secondary | Real and synthetic speech | SUPERSEDED for Phase 1. Licenses still Pending. Do not download. |
| CNN / Google Speech Commands | Optional stretch | Not the cascade | Not on the critical path. |
| ATIS | Excluded | LDC releases | Do not download under this plan. |

Do not pool Common Voice scores with FSC, SLURP, or ATIS. Sample IDs are not mixed. Synthetic corruption stays a stress test, not a natural error rate. Scripted read speech is not spontaneous conversation.

Milestone A reports WER and CER only. Milestone B is required before intent accuracy or slot F1. The manual subset uses the same utterance IDs across B0, B1, and B2 when those configurations are later compared.

The local recognizer is not Amazon Transcribe. CNN keyword classification is not an experiment under RQ1–RQ4.

## Splits

Use the official Common Voice split files once they are present in the downloaded archive. A public datasheet names Train, Dev, and Test. Those names are not confirmed on disk. Do not invent a random partition. Do not rename a source split. The validation split, whatever the file calls it, is the only split used to choose models and thresholds. The test split stays frozen.

The earlier FSC rule, kept for the superseded track: if FSC were ever revived, use its official train, valid, and test files. The publisher calls the middle split `valid`.

| Split | Allowed use |
|-------|-------------|
| Train | Fit lexicons, feature statistics, and any later model. Training-time augmentation stays inside this split. |
| Valid | Choose hyperparameters, checkpoints, and recovery thresholds. |
| Test | One frozen evaluation after the configuration is saved. No threshold edits after seeing test scores. No checkpoint pick based on test scores. |

ATIS is excluded from the current implementation. A later revival would need its own deviation entry, license, and table. It is not part of E1–E5.

## B0

Single-best ASR transcript passed to the NLU component.

```text
Audio → ASR → one transcript → NLU → semantic frame
```

Until Milestone B exists, B0 on Common Voice stops at the transcript and is scored with WER and CER. Transcript-input mode skips ASR and sets WER to “not applicable”, with the supplied text stored as the transcript. That mode is for tests and debugging. It is not a substitute for an audio evaluation.

## B1

Multiple transcript candidates passed through semantic evaluation. Genuine ASR N-best hypotheses must be distinguished from independently decoded candidates or synthetic variants. Never label proxy candidates as genuine N-best.

```text
Audio → ASR → candidate list → NLU on each candidate → documented selection rule → one frame
```

Label each hypothesis with one of:

- `beam_hypothesis` only when one decoding run returns that alternative;
- `independent_decode` when the text comes from a separate decoding run;
- `retry_decode` when a real decoder is invoked again for that sample;
- `synthetic_edit` when the text was produced by editing a transcript.

Do not pool those four labels in one agreement score. The simulation track continues to use `synthetic_edit`. Its code rejects a synthetic row labelled `native_nbest`. That older name is not a substitute for `beam_hypothesis`.

`beam_size` on a decoder that returns one string is not a beam hypothesis. Ruan et al. footnote 1 used 1-best only. A B1 result is not a reproduction of that paper. B1 semantic comparison is a later phase. Phase 1D only records which of the four provenance values the installed decoder can actually produce.

## B2

A bounded failure-aware controller selects CONTINUE, RETRY, CLARIFY, or HOLD using documented signals and policies.

```text
Audio → ASR → NLU → diagnosis → CONTINUE, RETRY, CLARIFY, or HOLD → final record
```

RETRY has a maximum count and a timeout, both set in the experiment config. Schema errors are not retried in a loop. The controller never writes a slot value that was not in a candidate or a clarification response. CLARIFY and HOLD leave the frame unresolved rather than guessing.

The injected corruption label is analysis metadata. It is not a feature of the controller. Natural ASR errors and synthetic corruption stay in separate experiments. On a real decoder, RETRY means `retry_decode`. Rescoring a written candidate list remains a simulation label. B2 comparison is not part of Phase 1.

## Error injection

Audio transforms and text edits are separate. Each derived row stores source sample ID, derived ID, transform name, parameters, severity, seed, and level (`audio` or `transcript`). Source files stay unchanged.

Synthetic conditions are stress tests. They are not an estimate of how often those errors occur outside the lab.

Audio conditions to implement later: background noise, low amplitude, clipping, reverberation, speed change that keeps the words the same.

Text conditions to implement later: deletion, insertion, substitution, word-boundary split, entity or number corruption, negation change.

## Fair comparison

B0, B1, and B2 in one comparison table must share:

- dataset release and checksum;
- evaluation sample IDs;
- reference labels;
- metric implementation version;
- a written list of excluded IDs and reasons.

Latency is reported next to accuracy. A method that holds every utterance can look safe and must show the HOLD rate.

## Robustness rule borrowed as a report constraint

Ruan et al., Section 2: do not describe a change as robustness if ASR-condition scores rise and clean-condition scores fall. CascadeGuard reports both conditions even though it does not adopt their training loss.

## Statistics

When a training run is stochastic, use more than one seed if the run is cheap enough, and report mean and standard deviation. A single seed is labelled as a single seed. Seeds do not make GPU or beam search deterministic; record the library versions anyway.

Paired comparisons use the same utterance IDs. Do not call a small difference an improvement without the counts.

## Reproducibility record

Each run directory stores config, seed, dataset version, model identifier, package versions, hardware, predictions, exclusions, and the clock method. Do not overwrite a previous run ID.

## Negative results

Report accuracy drops, useless retries, clarification that does not identify a slot, high HOLD rates, and latency increases in the same table as gains.

## Clean-test rule

The test split is not used to edit prompts, lexicons, thresholds, or feature normalization. Validation may be read for those choices. Reading the test set to decide the next code change breaks this protocol.
