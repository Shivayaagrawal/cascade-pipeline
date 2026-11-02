# Cascade Pipeline — Phase 0 Completion Report

## 1. Overall status

- **Status:** NOT READY FOR PHASE 1
- **Date:** 2026-11-02. Phase 0.5 licensing review, then the Common Voice direction, recorded the same day.
- **Git:** Repository initialized the same day on branch `research/common-voice-phase1`. No commit yet.
- **Current dataset candidate:** Common Voice Scripted Speech v27.0 English. Not frozen. Terms not accepted. Not downloaded.
- **Gate B (required terms Accepted):** Not met.
- **Gate C (owner approves Phase 1):** Not met. This report does not approve Phase 1.

The working direction is now Common Voice as the primary candidate, with no secondary dataset in Phase 1. FSC and SLURP are superseded and were not accepted. ATIS is out of implementation. The CNN is optional. Mozilla terms are not accepted. The full English archive listed at 88.43 GB does not fit in the 60 GiB free on this disk. No download, install, or training was done.

## 2. Repository audit

- **Structure:** Documentation, Cursor rules, and prompts. No `src/`, tests, data, or checkpoints.
- **Python:** 3.13.7 and pip 26.0.1. README asks for 3.11. No project environment.
- **Dependencies:** No requirements file or lockfile. System interpreter has numpy 2.3.5, pandas 3.0.2, scikit-learn 1.8.0, and pytest 9.1.0. torch, torchaudio, librosa, soundfile, and matplotlib are not installed.
- **Hardware:** Apple M1, 16 GiB RAM, about 59 GiB free, no NVIDIA GPU.
- **Tests:** No suite. Pytest and `compileall` were not applicable. Nothing passed or failed.
- **Known issues:** No git history. Two phase schedules. License not accepted.

## 3. Reference paper

- **Title:** Towards an ASR Error Robust Spoken Language Understanding System
- **Authors:** Weitong Ruan, Yaroslav Nechaev, Luoxin Chen, Chengwei Su, Imre Kiss
- **Publication:** Interspeech 2020, pages 901–905
- **Primary source:** https://www.isca-archive.org/interspeech_2020/ruan20_interspeech.pdf DOI 10.21437/Interspeech.2020-2844, read 2026-11-02
- **Methodology:** 1-best ASR text as a second view of the utterance. Intent loss adds KL between transcript and hypothesis predictions. Slot tagger uses entity-exact pseudo-labels and a marginalized CRF.
- **Dataset:** ATIS (4,478 / 500 / 893) with Amazon Transcribe hypotheses at about 3.5% and 4% WER, plus a private Alexa set. Not Fluent Speech Commands.
- **Architecture:** Frozen fastText, character CNN, two BiLSTMs, softmax or CRF. Section 3.
- **Evaluation:** Classification F1 and slot F1. Robustness requires a gain on ASR text and no loss on clean text. ASR slot scores ignore unmatched spans.
- **Limitations:** ATIS is small. Alexa data are private. Learning rate, batch size, and epochs are not in the paper. Code release is not specified.
- **Unknown:** Table 1’s absolute cells, because the PDF text extractor reordered them. Do not cite those cells from the notes.

## 4. Research alignment

- **Shared problem:** ASR errors change downstream intent and slots in a cascade.
- **Paper-inspired constraint:** Report clean and ASR conditions. Do not call a noisy-set gain a robustness win if the clean set gets worse.
- **Planned approximation:** None approved. A local recognizer would not match Transcribe.
- **Proposed extension:** Candidate provenance, diagnosis, RETRY / CLARIFY / HOLD, false alarms, and latency.
- **Deviations:** D-001 phase-2 schedule, D-002 reference paper versus FSC, D-003 local ASR instead of Transcribe. All PROPOSED.

## 5. Dataset

- **Dataset candidate:** Common Voice Scripted Speech 27.0 English. Wrong corpus for a Ruan reproduction. FSC and SLURP are superseded.
- **Exact release:** Not frozen. Public page https://mozilladatacollective.com/datasets/cmu5jplf300nwmh07iqvk9leo shows dataset ID `cmu5jplf300nwmh07iqvk9leo`, locale `en`, corpus `cv-corpus-27.0-2026-09-11`, MP3, 88.43 GB, and archive name `common-voice-scripted-speech-27-0-englis-e4a13e08.tar.gz`. The owner has not confirmed that page inside an MDC account.
- **Source:** Mozilla Data Collective only. Not downloaded.
- **Terms:** Owner decision Pending. The page prints CC0-1.0 and forbids speaker identification and re-sharing. https://commonvoice.mozilla.org/en/terms asks users not to mirror datasets and says CC0 unless otherwise specified. Neither instrument was accepted.
- **Annotation schema:** Datasheet lists TSV columns including `path` and `sentence`. Header not seen in a file. No native intent or slot labels.
- **Official splits:** Datasheet names Train, Dev, and Test with catalogue counts. Files not opened.
- **Speaker metadata:** Datasheet describes `client_id` as a hashed UUID and optional demographics. Not seen in a file. Not permission to identify a speaker.
- **Task compatibility:** Transcripts are the datasheet’s purpose. Semantic labels are absent. Milestone B is required before intent or slot scores.
- **Unresolved:** Account confirmation, terms acceptance, a download that fits in about 60 GiB free, checksum, real headers, real split files.

## 6. Experimental methodology

- **B0:** One transcript, then NLU.
- **B1:** A candidate list with an explicit provenance label. Native N-best is not claimed for faster-whisper.
- **B2:** Diagnosis then CONTINUE, RETRY, CLARIFY, or HOLD, with retry and timeout limits.
- **Metrics:** Formulas in `docs/METRIC_DEFINITIONS.md`. Primary slot F1 keeps unmatched ASR spans, unlike the reference paper.
- **Error injection:** Defined, not implemented. Synthetic is not natural prevalence.
- **Splits:** Train fits, validation tunes, test is frozen.
- **Leakage and overfitting:** Checklist written. Boxes that need files are open.
- **Reproducibility:** Run directory rules written. No run exists.

## 7. Architecture

- **Pipeline:** Audio, ASR, NLU, frame, diagnosis, recovery, trace. Documented in `docs/ARCHITECTURE_OVERVIEW.md`.
- **Boundaries:** Evaluation does not edit predictions. Recovery does not edit source audio.
- **Contracts:** Missing backend fields stay null.
- **Recovery:** Max retries, timeouts, no invented slots, injected labels hidden from the controller.

No Python modules were created.

## 8. Risks

- **R1:** License blocks legal use of the audio.
- **R2:** Unseen CSV headers can make the schema wrong.
- **R3:** Reporting an FSC cascade as a reproduction of Ruan et al. would be false.

The full list is `docs/RISK_REGISTER.md`.

## 9. Verification results

| Check | Evidence | Result |
|-------|----------|--------|
| Repository audit | Commands in `docs/REPOSITORY_AUDIT.md` | PASS |
| Existing tests | No suite | N/A |
| Paper verification | ISCA PDF read; Table 1 cells pending visual check | PASS with that limit |
| Dataset license | Phase 0.5 register. FSC conflict unresolved. SLURP audio and text read separately. Owner decisions Pending. | PENDING |
| Label feasibility | Publisher text only | PENDING |
| Split integrity | No files | PENDING |
| Metrics defined | `docs/METRIC_DEFINITIONS.md` | PASS |
| Leakage controls | Checklist, not yet runnable | PASS as policy |
| Architecture review | Proposal, no code | PASS as a draft |
| B0/B1/B2 definitions | `docs/EXPERIMENTAL_PROTOCOL.md` | PASS |
| Model route | CPU path documented; weights not fetched; N-best unverified | PASS as a provisional route |
| Phase 1 plan approved | Not signed | FAIL |

## 10. Amended decisions

| Decision | Outcome |
|----------|---------|
| Research design | Superseded later the same day. See section 15. FSC primary and SLURP secondary are no longer the implementation plan. |
| Reference paper | Still Ruan et al. 2020, with the author names printed on the PDF. The amendment draft’s initials were wrong and were not copied into the notes. The project is an extension, not a reproduction. |
| ATIS | Excluded from implementation. |
| CNN | Optional. |
| FSC permission | Pending, not Accepted and not Refused. Scope SUPERSEDED. Acquisition BLOCKED. |
| SLURP permission | Pending for audio, text, and `usrid`, separately. Scope SUPERSEDED for Phase 1. Acquisition BLOCKED. |
| Common Voice permission | Pending. Public pages read. Not accepted. Full archive does not fit on the measured free disk. |

## 10a. Contradictions

1. The amendment names https://github.com/GrindstoneLZX/FluentSpeechCommandsDataset as the FSC repository. The dataset paper’s data link is a Fluent.ai URL, and that GitHub account is a third party. The license register does not treat the mirror as official.
2. The amendment’s author line does not match the PDF. The notes keep Weitong Ruan, Yaroslav Nechaev, Luoxin Chen, Chengwei Su, and Imre Kiss.
3. Publisher FSC counts and the SLURP “18 domains” line are publisher or abstract statements. They are not local counts.
4. The SLURP paper body was not read, so its baseline numbers are not in the literature matrix.

## 11. Phase 1 readiness

- [x] Repository safe to modify. There is no code to overwrite.
- [ ] Research scope approved.
- [x] Reference paper verified well enough to avoid copying the wrong method. Table 1 cells remain limited.
- [ ] Applicable terms accepted. Common Voice is Pending. FSC and SLURP are superseded and still Pending.
- [ ] Dataset labels support the task on real files.
- [x] B0/B1/B2 definitions written.
- [x] Metrics defined.
- [x] Experimental protocol written.
- [x] A CPU route is feasible. It is not downloaded.
- [ ] Phase 1 plan approved.

## 12. Consistency audit

| Check | Result |
|-------|--------|
| Each of RQ1–RQ4 maps to an FSC comparison of B0, B1, or B2 | Pass, in `docs/RESEARCH_QUESTIONS.md` |
| B0, B1, and B2 definitions unchanged | Pass. Provenance labels still required for candidates. |
| FSC is not described as Ruan et al.’s dataset | Pass |
| ATIS and FSC scores are not pooled | Pass |
| Synthetic corruption is not a natural error rate | Pass, in the protocol |
| Confidence is not called calibrated | Pass. No calibration run exists. |
| Test split is not used for tuning | Pass, as a rule. Not yet enforceable in code. |
| CNN is not mandatory | Pass after Decision C. The older Phase 2 row in the phase-wise plan now points at that decision. |
| Reproduction claim | None. Hyperparameters, Alexa data, and Transcribe hypotheses are missing. |

## 13. Consistency audit for the amendment

| Check | Result |
|-------|--------|
| RQ1–RQ4 map to E1–E4 on each dataset separately | Pass |
| FSC and SLURP are not pooled | Pass |
| ATIS is not a Phase 1 deliverable | Pass |
| CNN is not mandatory | Pass |
| Ruan et al. methods are not attributed to Cascade Pipeline | Pass |
| Synthetic SLURP speech and synthetic corruption stay labelled | Pass |
| Confidence is not called calibrated | Pass |
| Test data are not a tuning set | Pass as a written rule |
| Licenses accepted | Fail. Common Voice is Pending. FSC and SLURP remain Pending and are superseded. This is intentional. |

## 14. Phase 0.5 licensing audit

| Check | Result |
|-------|--------|
| FSC publisher page re-read | Done. Academic-only wording and CC BY-NC-ND 4.0 name confirmed. Full-license link is the Public License PDF. |
| FSC access channel | Google Group `fluent-speech-commands` on fluent.ai. No release id, commit, or checksum. Group not joined. |
| FSC author URL | Timed out. Still UNKNOWN. |
| FSC Public License PDF | Re-read. Reproduce but not Share, NonCommercial and academic, with training/testing/bench-marking named inside the commercial-purpose sentence. |
| FSC CC BY-NC-ND 4.0 legal code | Read because the page names it. Not treated as the bundled file. |
| Third-party FSC GitHub | Not used and not cloned. |
| SLURP Zenodo record and `LICENSE.txt` | Read. CC BY-NC 4.0. Archives not downloaded. Recorded md5 values were not recomputed. |
| SLURP CC BY-NC 4.0 legal code | Read. NonCommercial is a purpose test, not an academic label. |
| SLURP GitHub text | Commit `8eb16545762be97ace75334109d73824217311f1`. `LICENSE.txt` and README license section read via raw URLs. No clone. |
| SLURP CC BY 4.0 legal code | Read. Separate from the audio license. |
| One license assumed for every SLURP artifact | Not done. Audio, text, and `usrid` are separate rows. |
| Owner Accepted inferred from a public page | Not done. |
| Downloads, installs, clones, `src/`, experiments | Not done. |
| `docs/IMPLEMENTATION_PLAN.md` marked approved | Not done. |
| Gate A | Complete as a documentation review. Open questions stay Pending. |
| Gate B | Not met. |
| Gate C | Not met. |

**Unresolved questions**

1. Which FSC text governs the Google Group distribution, and does the PDF allow noncommercial academic training and testing?
2. What release identifier and checksum would a later FSC download have to match?
3. Will the owner accept CC BY-NC 4.0 for SLURP audio, CC BY 4.0 for the pinned text commit, neither, or only one of them?
4. Will SLURP synthetic audio be acquired at all? It is a separate file and a separate experiment condition.
5. The author FSC URL still has no fetched contents.

**Blocked artifacts**

- FSC audio and annotations: Pending, acquisition blocked. A later Refused decision would block the primary benchmark.
- SLURP audio, including real and synthetic archives: Pending, acquisition blocked. A later Refused decision would block SLURP audio experiments under that license.
- SLURP text and `usrid` metadata: Pending, acquisition blocked.
- ATIS: out of implementation. License unread. Not a Gate B requirement.
- Google Speech Commands: optional, license unread.

**Exact next action**

The owner reads `docs/DATASET_LICENSE_REGISTER.md` and records, in writing, Accepted or Refused for FSC, for SLURP audio, and for SLURP text. Pending rows do not authorize a download. After those decisions, Phase 1 still needs a separate owner approval. If FSC is Refused, the primary benchmark stops. If SLURP audio is Refused, SLURP cannot be used for audio experiments under that license. This report stays **NOT READY FOR PHASE 1**.

## 15. Closeout gates

States: PASS means the check is done and evidenced. PENDING means a person or an external account still has to finish it. FAIL means the current approach cannot meet that requirement. SUPERSEDED means an earlier decision was replaced and its history kept.

| Gate | State | Evidence |
|------|-------|----------|
| Repository audit | PASS | `docs/REPOSITORY_AUDIT.md`. Git was initialized on 2026-11-02. No commit. Branch `research/common-voice-phase1`. |
| Research paper verification | PASS | ISCA PDF read. Table 1 absolute cells still limited by the extractor. |
| Dataset source and release | PENDING | Public MDC page read. Not confirmed in the owner’s account. Not downloaded. |
| User acceptance of applicable terms | PENDING | Pages read. Owner decision is Pending. |
| Exact locale and dataset ID | PENDING | Catalogue shows `en` and `cmu5jplf300nwmh07iqvk9leo`. Not frozen. `en-US` is not the release id on that page. |
| Dataset schema | PENDING | Datasheet column list only. No archive opened. |
| Official split availability | PENDING | Datasheet names Train, Dev, and Test. Files not opened. |
| Label compatibility | FAIL for native intent and slots | Common Voice is an ASR transcript corpus. Milestone B is the planned mitigation and is not done. |
| Experimental protocol | PASS | B0, B1, and B2 rewritten for an ASR-first milestone. No run. |
| Metric definitions | PASS as formulas | WER normalizer is specified as a policy and is not implemented. Do not publish a WER yet. |
| CPU feasibility | PASS for CPU availability | Apple M1, 16 GiB RAM, no NVIDIA GPU. |
| Full English archive on this disk | FAIL | Catalogue 88.43 GB. About 60 GiB free. |
| Phase 1 implementation plan | PASS as a document, revised after simulation v3 | `docs/PHASE_1_IMPLEMENTATION_PLAN.md`. Not approved. |
| Owner approval | PENDING | No Phase 1 approval and no terms acceptance. |

**Final decision: NOT READY FOR PHASE 1.**

The research direction is recorded. Acquisition is not permitted. No dataset archive was downloaded, no dependency was installed, no dataset repository was cloned, and no model was trained. Phase 1 does not start from this report. The owner’s next action is in `docs/PHASE_0_DECISION_LOG.md`.

## 16. Amendment after simulation v3

On 2026-11-02 the Phase 1 plan was replaced. Stages 1A–1E are the real-audio foundation described in `docs/PHASE_1_IMPLEMENTATION_PLAN.md` and decision D-CV-006. Simulation results were not edited. Terms stay Pending. The MDC record stays unfrozen. This report remains **NOT READY FOR PHASE 1**.
