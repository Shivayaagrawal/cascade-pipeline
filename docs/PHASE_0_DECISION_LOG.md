# Phase 0 decision log

**Date:** 2026-11-02.  
**Status of Phase 1:** NOT READY. This log records the direction. It does not accept Mozilla terms and it does not approve a download.

## D-CV-001 — Primary dataset candidate

- **Decision:** Mozilla Common Voice Scripted Speech v27.0, English, is the primary dataset **candidate**.
- **Why:** The previous primary corpus, Fluent Speech Commands, supplies intent and slot labels but its license texts conflict and were not accepted. Common Voice supplies read-speech audio and reference transcripts for an ASR-first milestone. Semantic labels will be added later by hand on a small subset.
- **What was not decided:** The owner has not confirmed this record inside a Mozilla Data Collective account, has not accepted the terms, and has not downloaded anything.
- **Locale:** The public catalogue datasheet says English [`en`]. `en-US` is an accent bucket on that page (`us`), not a confirmed release identifier. Freeze the locale only after the owner sees the same identifier in their MDC account.
- **Deferred:** SLURP as a secondary dataset. ATIS remains out of implementation. Google Speech Commands stays optional and off the critical path. FSC is no longer the implementation corpus. Its license review stays in `docs/DATASET_LICENSE_REGISTER.md` as history. Those licenses were not Accepted and were not Refused.

## D-CV-002 — Access path

- **Decision:** Acquisition, if it happens later, is through Mozilla Data Collective only.
- **Not allowed:** Re-hosting, mirroring, committing audio, putting archives in a public bucket, or sending the archive through an unrelated file host.
- **Terms:** Not accepted in this session. A public Common Voice terms page and the public dataset page were read. Reading them is not acceptance.

## D-CV-003 — First milestone

- **Milestone A:** ASR evaluation against reference transcripts. No intent accuracy and no slot F1 until Milestone B exists.
- **Milestone B:** A manually annotated semantic subset. Planning target: about 200–300 utterances after ingestion and an ASR baseline work. That number is not a justified sample size.
- **B0 / B1 / B2:** Definitions are unchanged in kind and are written in `docs/EXPERIMENTAL_PROTOCOL.md`. They are not implemented. B1 must not call proxy candidates genuine N-best.
- **Phase 1 scope at closeout:** Acquisition check, manifests, audio checks, split checks, preprocessing, and ASR baseline preparation. No model training. No recovery controller.
- **Later revision:** D-CV-006 replaces that scope after simulation v3. This entry stays as the closeout decision. It still does not approve Phase 1.

## D-CV-004 — Storage

- **Catalogue size observed 2026-11-02:** 88.43 GB for the English v27.0 archive named on the public dataset page.
- **Free space the same day:** about 60 GiB available on `/System/Volumes/Data` (`df -h`).
- **Consequence:** The full English archive does not fit. Do not download it by default. A pilot needs a smaller, still-official subset, which has not been identified in an MDC account.

## D-CV-005 — Where data lives

Recorded in `docs/STORAGE_DECISION.md`. Synthetic text may be committed. Synthetic audio stays local and out of Git. A Common Voice subset, if one is later permitted, stays under 5 GB on this Mac. The full archive stays at Mozilla Data Collective and is not copied to another host. An external SSD would only solve disk space. It would not change the terms.

## Owner actions still open

1. Sign in to Mozilla Data Collective and confirm the dataset ID, locale, archive name, format, and size on the account page.
2. Read and accept the applicable terms only if you agree.
3. Choose a download that fits on disk. Record access date, checksum, and the files actually present.
4. Approve the revised Phase 1 plan only after the dataset card records the confirmed access evidence. Approval is still outstanding.

## D-CV-006 — Phase 1 redefined after simulation v3

- **Date:** 2026-11-02.
- **Decision:** `docs/PHASE_1_IMPLEMENTATION_PLAN.md` is replaced. Phase 1 is a real-audio foundation in five stages: 1A access, 1B ingestion and validation, 1C waveform ASR, 1D hypothesis provenance, and 1E annotation readiness. B0, B1, and B2 comparisons move to later phases.
- **Why:** Simulation v3 separated preserved candidate information, prefix-reader loss, and agreement on a wrong critical value. The next measurement has to come from decoder hypotheses. Another synthetic selector pass is not the next milestone.
- **What was not decided:** Terms remain Pending. The MDC record is not frozen. No subset acquisition method is confirmed. The 5 GB limit is unchanged and has not been checked against an acquired subset. Phase 1 is not approved.
- **Design rules carried forward:** Do not infer a missing critical slot from the intent. Do not treat candidate agreement as correctness. Report selective risk with coverage. A real RETRY is a new decode. HOLD remains a valid outcome. `beam_hypothesis`, `independent_decode`, `retry_decode`, and `synthetic_edit` are not pooled.
- **Later status:** D-CV-007 accepts this document as the working plan and keeps execution unapproved.

## D-CV-007 — Working plan accepted, execution still blocked

- **Date:** 2026-11-02.
- **Decision:** The revised Phase 1 plan is the current baseline. Phase 0 is complete. Simulation v1–v3 are complete as controlled synthetic evaluations. No further synthetic selector tuning. Phase 1 execution is not approved. Common Voice acquisition remains a pending owner decision.
- **Hard gate:** 1A and 1B do not start until the MDC record, the applicable terms, a permitted subset route, and storage feasibility are verified, and the owner explicitly approves acquisition. Accepting the plan is not that approval. Until then the dataset state stays unchanged.
- **Decoder limit:** If the selected ASR backend returns one transcript, that limitation is recorded. Beam hypotheses are not manufactured. An independent decode is run only with a written methodological reason.
- **Annotation:** Annotators label intended meaning from the reference and permitted context. The predicted transcript is not ground truth. Ambiguity and reviewer disagreements are recorded.
- **Scope of any future result:** Common Voice is scripted speech. Phase 1 results, if they are later measured, describe that dataset. They do not describe spontaneous conversational speech.
- **What was not decided:** Terms remain Pending. The dataset identity remains unfrozen. Nothing was downloaded in this decision.
- **Later source proposal:** D-LS-001 proposes official OpenSLR LibriSpeech for the real-audio experiment. It does not approve a download, and it does not close the Common Voice decision.

## D-LS-001 — OpenSLR LibriSpeech, dev-clean and test-clean approved

### Original proposal, recorded 2026-11-02 before acceptance

- **Decision at that time:** The proposed real-audio source was the official OpenSLR LibriSpeech ASR corpus, SLR12, at https://www.openslr.org/12/. The proposed archives were `dev-clean.tar.gz` and `test-clean.tar.gz` only. The Kaggle dataset `pypiahmad/librispeech-asr-corpus` was an inspection reference and was not an approved source. Common Voice remained a pending candidate under D-CV-007.
- **Evidence at that time:** The catalog page was fetched the same day. It prints CC BY 4.0, dev-clean 337M, and test-clean 346M. The CC BY 4.0 deed was read. The legal code had not been recorded as read. Mirror URLs were copied from the catalog HTML. `md5sum.txt` had not been fetched. No archive had been downloaded by the project.
- **Use of the splits:** `dev-clean` is for development. `test-clean` is held out from tuning. The sample is a hash order of official utterance IDs, seed 17, not a smallest-file selection. The rule is `docs/PHASE_1_SAMPLING_PROTOCOL.md`.
- **Storage:** The cap is 5,000,000,000 bytes. Train archives stay out of scope.

### Owner acceptance, recorded 2026-11-02T10:42:00Z

- **Decision ID:** D-LS-001. This is the same decision, updated. It is not a second decision.
- **Communication time:** 2026-11-02T10:36:00+05:30. That is the conversation timestamp to the minute. Seconds were not given.
- **Recording time:** 2026-11-02T10:42:27Z, when this repository entry was written.
- **Source:** Explicit owner statement in this conversation. No handwritten signature, external signature, or legal opinion is claimed.
- **Statement:** "I explicitly authorize both dev-clean.tar.gz and test-clean.tar.gz for CascadeGuard research, including extraction into the project dataset directory. I have already read and accepted CC BY 4.0."
- **Legal code read completely:** true. The owner stated that the complete CC BY 4.0 legal code was read.
- **Owner licence acceptance:** true, for the proposed CascadeGuard research use.
- **`dev-clean.tar.gz` authorized:** true.
- **`test-clean.tar.gz` authorized:** true.
- **Extraction into the project dataset directory:** true.
- **Storage cap:** 5,000,000,000 bytes.
- **Status:** APPROVED for those two archives only.
- **Not authorized:** Any other LibriSpeech archive, Common Voice, ASR inference, and Phase 1C. A browser download attribute of `https://chatgpt.com/` is not rewritten here into an OpenSLR transfer time.
