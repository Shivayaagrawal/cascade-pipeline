# Related Work

**Access date:** 2026-11-02.  
**Scope:** What was actually read. This is not a claim that the literature search is complete.

## Problem shared with the reference paper

Ruan, Nechaev, Chen, Su, and Kiss, Interspeech 2020, study a pipeline in which ASR text is passed to a separate NLU. Section 1 says NLU trained on human transcripts is then exposed to ASR errors at deployment. That is the same cascade failure Cascade Pipeline is built to measure.

Their response is training-time robustness: make the intent distribution agree on the transcript and the 1-best hypothesis, and train the slot tagger with pseudo-labelled 1-best text. Footnote 1 says the experiments use ASR 1-best only. Section 1 treats n-best reranking as prior work, not as their contribution.

## What Cascade Pipeline does not inherit

- The reference experiments use ATIS and a private Alexa corpus (Section 5.1). They do not use Fluent Speech Commands.
- The reference ASR for ATIS is Amazon Transcribe (Section 5.1). Cascade Pipeline’s current rules avoid paid APIs unless the owner approves one.
- The reference does not define RETRY, CLARIFY, HOLD, false-alarm rate, or latency.
- Lugosch et al., Interspeech 2019, introduce Fluent Speech Commands for end-to-end speech-to-intent models. That architecture removes the transcript Cascade Pipeline needs in order to trace ASR errors. It is the description of the primary dataset, not the system to copy.
- Bastianelli, Vanzo, Swietojanski, and Rieser, EMNLP 2020, release SLURP. The abstract and the repository README were read on 2026-11-02. The paper body was not. SLURP is the secondary dataset. It is not the Ruan training method, and its abstract describes end-to-end SLU as a motivation, which is not Cascade Pipeline’s primary system.

## Gap that is still unchecked

Whether a diagnosis and recovery controller improves reliability over robustness training, n-best reranking, or lattices is **not** established by the two papers read here. Those alternatives were not implemented and most of the cited papers were not read. The project may study that gap. It may not call the gap novel until the unread papers are checked.

## Hypotheses this literature motivates

Stated as questions, not as findings:

- If NLU sees only clean text, ASR substitutions can change intent or slots (Ruan et al., Section 1 example: “buy” versus “by”).
- A gain on noisy transcripts that is paid for by a loss on clean transcripts is not, under their Section 2 rule, a robustness improvement.
- Candidate lists and abstention are separate from that training method and need their own baselines.

Details and citations are in `docs/LITERATURE_MATRIX.md` and `docs/REFERENCE_PAPER_NOTES.md`.
