# Research Deviations Log

Record material methodological changes here before implementing them (see `.cursor/rules/120-research-deviation-control.mdc`).

Use one entry per deviation. Link related experiment run IDs when applicable.

---

## Template (copy for each entry)

- **Date:**
- **Status:** PROPOSED | APPROVED | REJECTED | IMPLEMENTED
- **Author / agent session:**
- **Original design:**
- **Proposed change:**
- **Reason:**
- **Scientific implications:**
- **Affected experiments / metrics:**
- **Approval:** (who approved, or pending)
- **Implementation notes:**

---

## Entries

### D-001 — Two schedules in the repository

- **Date:** 2026-11-02
- **Status:** SUPERSEDED by Decision C on 2026-11-02
- **Author / agent session:** Phase 0 audit
- **Original design:** `docs/PHASE_PLAN.md` is a 14-day schedule. A CNN acoustic experiment is Day 11 and may be deferred. The research questions are ASR error propagation, candidate transcripts, failure-aware recovery, and accuracy/latency/false-alarm trade-offs on a cascade.
- **Proposed change:** Use `docs/PHASE_WISE_IMPLEMENTATION_PLAN.md` as the build order. That plan inserts Phase 2 (waveform, spectrogram, 1D/2D convolution, encoder-decoder explanation, and a small isolated CNN feature experiment) before the B0 cascade. The cascade remains the primary research system. The CNN experiment must be labelled as classification or feature extraction, not as ASR, unless it is actually an ASR model.
- **Reason:** The phase-wise plan was added so speech-representation fundamentals are demonstrable without replacing the cascade.
- **Scientific implications:** Phase 2 results are exploratory. They must not be merged into the B0/B1/B2 comparison. Skipping Phase 2 does not change H1–H4. Making Phase 2 required changes schedule and scope, not the definition of B0/B1/B2.
- **Affected experiments / metrics:** None yet. No experiments have been run. Later Phase 2 metrics (accuracy, model size, inference time) stay in a separate report from WER, intent accuracy, slot F1, exact frame match, recovery, and latency.
- **Approval:** Decision C, 2026-11-02: the CNN is optional and is not a Phase 1 or Phase 2 gate. Spectrogram features for the audio pipeline are separate and still allowed inside Phase 1 after Phase 1 itself is approved.
- **Implementation notes:** Do not add a CNN training loop. Phase 1 audio features are not this deviation.

### D-002 — Reference paper is not the dataset paper

- **Date:** 2026-11-02
- **Status:** PROPOSED
- **Author / agent session:** Phase 0, after the plan named Ruan et al. 2020
- **Original design:** `docs/PROJECT_SCOPE.md` selects Fluent Speech Commands and a cascade with B0, B1, and B2. An earlier alignment note discussed Lugosch et al. 2019 because that paper introduces the dataset.
- **Proposed change:** Treat Ruan, Nechaev, Chen, Su, and Kiss, Interspeech 2020, DOI 10.21437/Interspeech.2020-2844, as the reference methodology for ASR-error-robust NLU. Keep Fluent Speech Commands as the planned corpus. Do not describe CascadeGuard as a reproduction of either paper.
- **Reason:** The Phase 0 plan names Ruan et al. The PDF uses ATIS and a private Alexa set, Amazon Transcribe, and 1-best robustness training. It does not use Fluent Speech Commands, candidate recovery, or HOLD.
- **Scientific implications:** Copying their KL and marginalized-CRF training onto FSC would be an approximation with a different recognizer and label schema. Replacing FSC with ATIS would change the dataset and needs a separate license check. The B0/B1/B2 questions stay answerable on FSC without that training method.
- **Affected experiments / metrics:** Any future “paper baseline” must use their clean-versus-ASR rule and must not be mixed into the B0/B1/B2 table without its own rows. Primary slot F1 stays the definition in `docs/METRIC_DEFINITIONS.md`, not their matched-entity-only score, unless the metric name changes.
- **Approval:** Pending. Phase 0 did not train either system.
- **Implementation notes:** `docs/REFERENCE_PAPER_NOTES.md` is the source note. Table 1 absolute cells were not copied because the PDF text extractor reordered them.

### D-003 — Local ASR instead of Amazon Transcribe

- **Date:** 2026-11-02
- **Status:** PROPOSED
- **Author / agent session:** Phase 0 model feasibility
- **Original design:** The reference experiment decodes ATIS with Amazon Transcribe.
- **Proposed change:** Use a local recognizer or a transcript-input adapter. Do not call that service without an explicit paid-API approval.
- **Reason:** Project rules reject an unapproved paid API. This machine has no NVIDIA GPU.
- **Scientific implications:** Error patterns will not match the paper’s ASR-3.5 and ASR-4.0 sets. Robustness numbers cannot be compared with Table 1 as a reproduction.
- **Affected experiments / metrics:** WER and downstream F1 become measurements of the chosen local model. They are not Transcribe results.
- **Approval:** Pending. No model was downloaded.
- **Implementation notes:** faster-whisper is only a candidate. Native N-best is unverified. See `docs/MODEL_AND_COMPUTE_DECISIONS.md`.

### D-004 — Separate FSC and ATIS tracks

- **Date:** 2026-11-02
- **Status:** SUPERSEDED on 2026-11-02 by D-005. ATIS is no longer an implementation track.
- **Author / agent session:** Phase 0 decision pass
- **Original design:** One corpus choice could be read as either FSC or ATIS standing in for the other.
- **Proposed change:** FSC is the primary audio implementation track for B0, B1, and B2. ATIS is an optional comparison track for the reference paper and is not approved for download. Scores are not pooled.
- **Reason:** Ruan et al. use ATIS and a private Alexa set. FSC is a different task: spoken appliance commands with audio. The LDC catalog count for LDC94S19 does not match the paper’s 5,871-utterance split, and the LDC user agreement was not read.
- **Scientific implications:** An FSC result does not confirm or refute the paper’s F1 tables. An ATIS result would still not be an exact reproduction without Transcribe hypotheses, the missing hyperparameters, and the Alexa data.
- **Affected experiments / metrics:** Every results table names its track. Exact frame match on FSC uses action, object, and location only after the CSV header is read.
- **Approval:** Recorded as the working strategy. It does not accept the FSC license and does not start Phase 1.
- **Implementation notes:** No ATIS or FSC files were downloaded.

### D-005 — FSC primary and SLURP secondary

- **Date:** 2026-11-02
- **Status:** SUPERSEDED on 2026-11-02 by D-006. Licenses were not accepted and were not refused.
- **Author / agent session:** Amended Phase 0
- **Original design:** D-004 kept ATIS as an optional comparison. SLURP was blocked until the FSC cascade was stable.
- **Proposed change:** FSC is the primary audio benchmark. SLURP is a second benchmark with its own adapter, labels, and tables. ATIS is excluded from implementation. The CNN stays optional.
- **Reason:** The amended plan asks for a practical command set and a broader SLU set, without claiming to reproduce Ruan et al.
- **Scientific implications:** E5 is two evaluations, not one pooled score. SLURP `action` is not the FSC slot `action`. Real and synthetic SLURP speech are different conditions. Headset and distant files can leak if they are split apart.
- **Affected experiments / metrics:** RQ1–RQ4 are defined for both datasets. Phase 1, when approved, adds two adapters and no training.
- **Approval:** Research design recorded from the amended plan. Download permission is not granted.
- **Implementation notes:** SLURP README and Zenodo record were read. The SLURP paper body was not. No files were downloaded.

### D-006 — Common Voice candidate, ASR before semantics

- **Date:** 2026-11-02
- **Status:** RECORDED as the working direction. Terms not accepted. Phase 1 not approved.
- **Author / agent session:** Phase 0 closeout instruction
- **Original design:** D-005. FSC primary, SLURP secondary, separate scores, no pooled metric.
- **Proposed change:** Primary candidate is Mozilla Common Voice Scripted Speech v27.0 English, through Mozilla Data Collective only. No secondary dataset in Phase 1. Milestone A is ASR against reference transcripts. Milestone B is a manual intent and slot subset. B0, B1, and B2 stay defined and are not implemented in the first Phase 1 slice.
- **Reason:** FSC and SLURP licenses were never accepted. Common Voice provides read-speech audio and transcripts. It does not provide native intent and slot labels, so semantic claims have to wait for annotation.
- **Scientific implications:** Results are about scripted speech, not spontaneous conversation. They do not reproduce Ruan et al. A public catalogue page lists locale `en`, dataset ID `cmu5jplf300nwmh07iqvk9leo`, and an 88.43 GB archive. Those values are not frozen until the owner confirms them in an MDC account. The full archive does not fit in the 60 GiB free on this disk.
- **Affected experiments / metrics:** WER and CER are the first scores. Intent accuracy and slot F1 are invalid until Milestone B is annotated and checked. The same evaluation IDs are required when B0, B1, and B2 are later compared.
- **Approval:** Direction recorded from the owner’s Phase 0 closeout instruction. Mozilla terms: Pending. Phase 1: not approved.
- **Implementation notes:** No download. No package install. No ASR code. See `docs/DATASET_CARD.md` and `docs/PHASE_1_IMPLEMENTATION_PLAN.md`.
