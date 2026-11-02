# Research Alignment — Phase 0

**Date:** 2026-11-02.

## Reference paper

The Phase 0 plan names Ruan, Nechaev, Chen, Su, and Kiss, *Towards an ASR Error Robust Spoken Language Understanding System*, Interspeech 2020, DOI 10.21437/Interspeech.2020-2844. Identity and method are in `docs/REFERENCE_PAPER_NOTES.md`. The PDF was read. This repository does not implement that method.

## Shared problem

Both the paper and CascadeGuard start from a cascade: speech is transcribed, then a separate NLU assigns intent and slots, and transcription errors change the downstream frame. Ruan et al., Section 1, use the example of “buy” recognized as “by”.

## What is not shared

| Piece | Ruan et al. 2020 | CascadeGuard plan |
|-------|------------------|-------------------|
| Primary public data | ATIS, 4,478 / 500 / 893, plus aligned audio | Common Voice Scripted Speech v27.0 English is the candidate. Not downloaded. FSC is superseded. |
| Other data | Private Alexa corpus | Not available and not in scope |
| ASR | Amazon Transcribe for ATIS; 2019 Alexa ASR for the private set | Provisional local faster-whisper, not downloaded. Paid API not approved. |
| Hypothesis use | 1-best only (footnote 1) | B1 wants candidates, provenance required |
| Training idea | KL consistency and marginalized CRF | Not scheduled as the first system |
| Extra decisions | None | RETRY, CLARIFY, HOLD, false alarms, latency |
| End-to-end speech-to-intent | Cited as related work, not their system | Out of scope as the primary system |

Lugosch et al. 2019 introduce Fluent Speech Commands and an end-to-end model. That paper supplies the dataset description. It is not the robustness method.

## Categories

1. **Original methodology.** CNN-BiLSTM-CRF NLU trained to agree on human text and ASR 1-best. See the reference notes.
2. **Approximation possible here.** Not started. An approximation would need paired transcripts and 1-best text, a declared recognizer, and the clean-versus-ASR scoring rule. It would still miss unpublished hyperparameters and the Alexa data. It is not approved.
3. **CascadeGuard extension.** Error traces, candidate provenance, diagnosis, and bounded recovery. Specified. Not coded.

## Hypotheses

RQ1–RQ4 and H1–H3 are in `docs/RESEARCH_QUESTIONS.md`. They can fail. No measurement exists.

## Approval

The written distinction is ready for review. It is not an owner signature. Phase 1 stays blocked until the owner accepts the applicable Common Voice terms and approves the Phase 1 plan. A Common Voice run is not a reproduction of Ruan et al.
