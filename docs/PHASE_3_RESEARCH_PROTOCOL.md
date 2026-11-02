# Phase 3 research protocol

Status: decisions D-P3-1 through D-P3-6 were accepted by the Phase 3 execution instruction. This document records that authorization. It is not a claim that the hypotheses were confirmed.

Phase 3 is a proposed synthetic, text-only extension. It does not add speech recognition, waveform decoding, genuine N-best lists, operational second-pass decoding, speech WER or CER, human audio annotation, conversational generalization, or production deployment. It does not replace frozen Phase 1 or Phase 2 results.

Proposed title: Failure-Aware Semantic Diagnosis and Safe Commitment in Synthetic Spoken Language Understanding.

## Central question

Can a failure-aware SLU controller identify when transcript evidence is incomplete, contradictory, ambiguous, or semantically unsafe, and choose a recovery action without unnecessarily reducing answer coverage?

The controller is a text simulator. "Transcript" means a synthetic string with recorded provenance. It does not mean recognizer output.

## What is already true

These points are the baseline this protocol must not rewrite.

| Item | Position |
| --- | --- |
| Dataset `synthetic-seed17-v1` | 200 gold utterances and 600 `variants.csv` edits. Frozen. |
| B0, B1, B2 prefix | Frozen experiment outputs. `run_b0`, `run_b1`, and `run_b2` stay as they are. |
| Lexical B1 and B2 | `forced_selection` and `recovery_action` stay as they are. Lexical RETRY is `simulated_candidate_rescore`. |
| `assess()` | Returns intent hits and lexicon slot values only. It does not represent negation, modality, or ambiguity. |
| Facade identities | `b0_prefix`, `b1_prefix`, `b2_prefix_controller`, `b1_forced_lexical`, `b2_lexical_v3`. Unknown names are rejected. |
| Empty bundle | Facade returns `HOLD` / `EMPTY_BUNDLE` and does not call those processors. |
| LLM audit | 120 provisional labels. Gold transcripts agreed 30/30 on intent and slots. Edited rows agreed 57/90 on intent and 43/90 on slots. Exploratory only. Not ground truth. |
| Human sheet | Still pending. No inter-annotator agreement. No audio review. |

The audit showed cases the current metrics do not separate: an inserted `not`, two requests in one line, a changed date or amount, and a damaged function word. Those observations motivate the hypotheses. They do not label the new challenge set.

## Hypotheses

These are questions to test. The report must not assume they hold.

| ID | Hypothesis | Evidence that would bear on it |
| --- | --- | --- |
| H1 | Explicit polarity reduces unsafe commits. | Polarity accuracy and unsafe-commit rate on negation cases. |
| H2 | Ambiguity detection improves action selection. | Ambiguity precision and recall, and action accuracy. |
| H3 | Critical slot checks reduce wrong date, time, and amount commits. | Critical-slot safety. |
| H4 | Cross-candidate contradiction detection improves commit safety. | Contradiction recall and selective risk. |
| H5 | Completeness checks reduce commits on incomplete requests. | Unsafe commits on incomplete cases. |
| H6 | Failure-aware recovery has a better risk-coverage balance than the frozen baselines. | Risk and coverage reported together. |
| H7 | The full semantic controller differs from diagnosis-only processing. | E5 versus E7 on the same split. |

H6 says "better" only as a hypothesis. A curve that lowers risk by holding almost everything does not support H6. Coverage and selective risk are reported as a pair. A zero denominator is undefined, not zero.

## Claim boundary

| Source | What it may support |
| --- | --- |
| Frozen B0/B1/B2 and v2/v3/v3b outputs | Historical synthetic results only. |
| Phase 2 facade | That the five identities can be called without changing those results. |
| LLM provisional audit | Which failure types were visible in a 120-row sample. |
| Deterministic challenge labels | Expected effects of declared transformations, after the challenge set exists and its validation passes. |
| Human annotation | Nothing yet. The human fields are blank. |

Phase 3 results, once they exist, are results on `synthetic-semantic-challenge-v1` only. They are not results on `synthetic-seed17-v1`, and they are not speech-robustness results.

## Decisions required before any implementation

The plan recommends three decisions. None is accepted by this document.

| ID | Decision | Status |
| --- | --- | --- |
| D-P3-1 | `synthetic-semantic-challenge-v1` targets 240 cases, eight categories, 30 each. The 30-utterance LLM audit stays exploratory. | Accepted |
| D-P3-2 | Expected labels come from the transformation operator and the parent gold frame. LLM labels are not gold. | Accepted |
| D-P3-3 | `b2_semantic_v4` is registered only on the Phase 3 path. The five Phase 2 identities stay unchanged. | Accepted |
| D-P3-4 | Parent split seed `20261103`. Validation and test are each `round(0.15 * eligible parents)`. The remainder is development. | Accepted |
| D-P3-5 | Weights are chosen from the predeclared quarter-weight grid and thresholds `(0, 0.25, 0.5, 0.75, 1)` on the validation split only, then frozen. | Accepted |
| D-P3-6 | An empty gold slot map is eligible only when that intent's `CRITICAL_SLOTS` entry is empty. None is, so `utt-020` and `utt-040` are excluded. | Accepted |

Writing this protocol does not by itself confirm a hypothesis. The test numbers are in `docs/PHASE_3_RESULTS.md`.

## Out of scope

Real ASR, real audio, genuine N-best hypotheses, a second recognition pass, speech WER or CER, human audio labels, new intents, new slot types, clarification dialogue text, and any rewrite of frozen data, reports, or the Phase 2 facade behavior.
