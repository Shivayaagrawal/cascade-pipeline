# Dataset Card — Common Voice Scripted Speech (candidate)

**Card status:** Not frozen. Public pages were read on 2026-11-02. The owner has not confirmed them in a Mozilla Data Collective account, has not accepted the terms, and has not downloaded an archive. Nothing below is a local file measurement.

**Relation to the reference paper:** Ruan et al., Interspeech 2020, use ATIS, not Common Voice. This card does not license ATIS. CascadeGuard is not reproducing that paper. See `docs/REFERENCE_PAPER_NOTES.md`.

Evidence labels: **CATALOGUE** means text on a public page. **PENDING** means the owner’s account or the downloaded files have not confirmed it.

## Current candidate

| Item | Record | Status |
|------|--------|--------|
| Name | Common Voice Scripted Speech 27.0 — English | CATALOGUE |
| Why this candidate | Audio plus reference transcripts for an ASR-first milestone. No native intent or slot labels. Decision: `docs/PHASE_0_DECISION_LOG.md`. | Project decision. Not a download approval. |
| Source | Mozilla Data Collective only. Public page: https://mozilladatacollective.com/datasets/cmu5jplf300nwmh07iqvk9leo | CATALOGUE. Not confirmed while signed in. |
| Dataset ID on that page | `cmu5jplf300nwmh07iqvk9leo` | PENDING owner confirmation. Not frozen. |
| Locale on that page | English [`en`]. The organization list also shows code `en` for this title. | PENDING owner confirmation. Do not record `en-US` as the release id. |
| Corpus name on the datasheet | `cv-corpus-27.0-2026-09-11` | CATALOGUE |
| Release date on the page | 9/17/2026 | CATALOGUE |
| Format on the page | MP3 | CATALOGUE. Not opened. |
| Archive name displayed on the page | `common-voice-scripted-speech-27-0-englis-e4a13e08.tar.gz` | CATALOGUE. The filename is copied as displayed, including the truncated `englis`. Confirm before any download. |
| Size on the page | 88.43 GB | CATALOGUE. Not hashed locally. |
| Free space on this machine | about 60 GiB available on `/System/Volumes/Data` (`df -h`, 2026-11-02) | OBSERVED. The full archive does not fit. Do not download it by default. |
| Download date | None | Not downloaded. |
| Local path | None | |
| Checksum | UNKNOWN | |

`en-US` is not the locale code on that page. The datasheet’s accent table uses `us` for United States English inside the `en` corpus (574,821 clips and 11,023 speakers stated there). That accent slice is not a separate release and was not downloaded.

## Terms

**Owner decision: Pending. Accepted: N/A.** Selecting this candidate is not acceptance.

| Instrument | What was read on 2026-11-02 | What it does not do |
|------------|-----------------------------|---------------------|
| Dataset page license line | CC0-1.0, with SPDX link https://spdx.org/licenses/CC0-1.0.html | Does not by itself mean the owner agreed. |
| Dataset page restrictions | “Restrictions/Special Constraints: None provided.” Forbidden usage on the same page: do not attempt to determine speaker identity; do not re-host or re-share this dataset. The download sentence says that by downloading you agree not to determine speaker identity. | No download occurred, so that sentence was not accepted. |
| Common Voice terms | https://commonvoice.mozilla.org/en/terms — datasets are made available under CC0 unless otherwise specified, exclusively through MDC, and Mozilla asks users not to post, distribute, or mirror a Common Voice dataset, in whole or in part, on other platforms. | Platform terms are not a substitute for the dataset page, and neither was accepted. |

Do not commit audio. Do not put the archive in a public bucket or send it through an unrelated host. `client_id` on the datasheet is described as a hashed UUID. That description is not permission to identify a speaker.

The CC0 legal text itself was not re-read in full in this pass. The dataset page’s extra prohibitions are additional constraints beyond the copyright dedication. If the signed-in record differs, the signed-in record wins and this card must be updated before a download.

## Schema and splits (datasheet only)

The public datasheet says each clip row in a TSV has `client_id`, `path`, `sentence`, `sentence_id`, `sentence_domain`, `up_votes`, `down_votes`, `age`, `gender`, `accents`, `variant`, `locale`, and `segment`. It also names `validated_sentences.tsv` and `unvalidated_sentences.tsv`.

Those names are **not** an adapter contract until the downloaded files are opened. Demographic fields are optional self-reports on that page. Do not copy them into git or public logs.

The same page states clip buckets Validated / Invalidated / Other and training splits Train 1,147,829, Dev 16,403, Test 16,403, plus 2,591,456 clips, 3,795.9 hours, 2,826.8 validated hours, and 100,546 speakers. Those figures are catalogue statements. They are not local counts. Split filenames inside the archive were not seen.

## Milestones

**Milestone A.** Score ASR against `sentence` after the column is confirmed in the file. No intent accuracy and no slot F1.

**Milestone B.** A manual semantic subset. Intent, slots, transcript correctness, and ambiguity, with a written guide, a second review of a subset, and adjudication. Planning target: about 200–300 utterances after ingestion and an ASR baseline. Not a sample-size justification. Labels do not exist yet.

## Limitations

- Scripted read speech. Results are not evidence about spontaneous conversation.
- English `en` on this page mixes accents. A United States subset is an accent field, not a verified `en-US` release.
- The full archive is larger than the free disk measured on 2026-11-02.
- No native general-purpose intent or slot inventory.
- Speaker identity must not be inferred.

## Superseded datasets

Fluent Speech Commands was the previous primary candidate. SLURP was the previous secondary candidate. Both are **out of Phase 1**. Their license rows stay in `docs/DATASET_LICENSE_REGISTER.md`. Owner decisions there remain Pending. They were not Accepted and were not Refused. Acquisition of both stays blocked.

FSC still has two unread-as-a-bundle instruments: the Fluent.ai page names CC BY-NC-ND 4.0, and the linked PDF is the Fluent Speech Commands Public License. The page’s access link is a Google Group, not a pinned archive. That conflict was not resolved by switching datasets.

ATIS stays excluded. Google Speech Commands stays optional and off the critical path. Neither license was accepted.

## Phase 1 gate

Do not download until:

1. The owner confirms the dataset ID, locale, archive name, format, and size in their own MDC account and writes them here as confirmed.
2. The owner records Accepted for the terms that apply to that record.
3. The chosen download fits on disk, or a smaller official subset is identified without assuming one exists.
4. Raw audio stays outside git.
