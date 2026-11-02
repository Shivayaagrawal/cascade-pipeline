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
- **Phase 1 scope:** Acquisition check, manifests, audio checks, split checks, preprocessing, and ASR baseline preparation. No model training. No recovery controller.

## D-CV-004 — Storage

- **Catalogue size observed 2026-11-02:** 88.43 GB for the English v27.0 archive named on the public dataset page.
- **Free space the same day:** about 60 GiB available on `/System/Volumes/Data` (`df -h`).
- **Consequence:** The full English archive does not fit. Do not download it by default. A pilot needs a smaller, still-official subset, which has not been identified in an MDC account.

## Owner actions still open

1. Sign in to Mozilla Data Collective and confirm the dataset ID, locale, archive name, format, and size on the account page.
2. Read and accept the applicable terms only if you agree.
3. Choose a download that fits on disk. Record access date, checksum, and the files actually present.
4. Approve Phase 1 after that evidence is in the dataset card.
