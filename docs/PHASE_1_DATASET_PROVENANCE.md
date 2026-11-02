# Phase 1 dataset provenance

**Date checked:** 2026-11-02  
**Status:** Owner acceptance is recorded in D-LS-001. `dev-clean` and `test-clean` were copied from local Downloads, checked against the official MD5 list, and extracted. Phase 1C is not authorized.  
**This note is not legal advice.** The catalog licence line was not itself the acceptance. The acceptance is the owner statement recorded in D-LS-001.

## Identity

| Field | Record |
|-------|--------|
| Name | LibriSpeech ASR corpus |
| Identifier | OpenSLR SLR12 |
| Catalog | https://www.openslr.org/12/ |
| Description printed on that page | Large-scale corpus of about 1000 hours of 16 kHz read English speech, prepared by Vassil Panayotov with the assistance of Daniel Povey. The speech is taken from LibriVox audiobooks, then segmented and aligned. |
| Paper named on that page | Vassil Panayotov, Guoguo Chen, Daniel Povey, and Sanjeev Khudanpur, “LibriSpeech: an ASR corpus based on public domain audio books,” ICASSP 2015. The PDF was not read for this note. |

The catalog page was fetched on 2026-11-02. Its download links point at mirrors. That catalog fetch did not download the archives. The later copy came from files already in Downloads.

## Licence

| Field | Record |
|-------|--------|
| Name printed on the catalog | CC BY 4.0 |
| Deed read the same day | https://creativecommons.org/licenses/by/4.0/deed.en |
| Legal code | The owner stated on 2026-11-02 that the complete CC BY 4.0 legal code was read. |
| Owner decision | Accepted. Decision D-LS-001, recorded 2026-11-02T10:42:27Z. |
| Accepted | Yes, for the proposed Cascade Pipeline research use of `dev-clean` and `test-clean`. |

The deed says it is a summary, not the licence. From that deed, sharing and adaptation are allowed, including commercially, if the terms are followed. Attribution means giving appropriate credit, linking to the licence, and indicating changes, without implying that the licensor endorses the use. The deed also says the licence does not waive other rights such as publicity, privacy, or moral rights, and that no warranties are given.

The owner has now recorded acceptance in D-LS-001. Attribution kept with the data and the report names the corpus, the preparers named on the catalog, OpenSLR SLR12, the catalog URL, CC BY 4.0, and the licence URL. The copied and extracted files were not modified.

## Proposed archives

The labels below are what https://www.openslr.org/12/ printed on 2026-11-02. Measured sizes and checksums are in the verification section below.

| Split | Archive | Printed size | Role |
|-------|---------|--------------|------|
| dev-clean | `dev-clean.tar.gz` | 337M | Development and debugging |
| test-clean | `test-clean.tar.gz` | 346M | Held-out evaluation after the configuration is frozen |

Mirror URLs listed on the catalog, deduplicated:

- https://openslr.trmal.net/resources/12/dev-clean.tar.gz
- https://openslr.elda.org/resources/12/dev-clean.tar.gz
- https://openslr.magicdatatech.com/resources/12/dev-clean.tar.gz
- https://openslr.trmal.net/resources/12/test-clean.tar.gz
- https://openslr.elda.org/resources/12/test-clean.tar.gz
- https://openslr.magicdatatech.com/resources/12/test-clean.tar.gz

The catalog also lists `md5sum.txt` at 600 bytes on those same mirror hosts. It was not downloaded. `checksum` in the acquisition manifest is null.

No other OpenSLR archive is proposed. `train-clean-100` is printed as 6.3G, `train-clean-360` as 23G, and `train-other-500` as 30G. Those exceed the 5 GB project cap. `dev-other` and `test-other` are separate, more challenging splits and are not part of this proposal.

## Splits

`dev-clean` is the development set of “clean” speech. `test-clean` is the test set of “clean” speech. They stay separate. Development work, decoder settings, and any later threshold choices use `dev-clean` only. `test-clean` is not read for those choices. The sampling rule is in `docs/PHASE_1_SAMPLING_PROTOCOL.md`.

## Limitations

- The speech is read audiobook speech. It is not spontaneous conversation and it is not a command corpus. Intent labels such as `transfer_money` are not native labels and must not be painted onto these sentences.
- The catalog does not supply intent, slot, negation, or semantic-frame annotation.
- Speaker and chapter numbers are part of the official utterance IDs. They are dataset keys. This record does not add names or other identity attributes.
- The CC BY 4.0 deed says privacy, publicity, and moral rights can still limit use. The extracted `LibriSpeech/LICENSE.TXT` states the CC BY 4.0 licence. No separate privacy policy was found in that short licence file.
- Extracted size, sample rate, channel count, and duration were measured in the preparation run recorded below.

## Kaggle copy

On 2026-11-02, `scripts/inspect_kaggle_dataset.py` listed files for the Kaggle dataset `pypiahmad/librispeech-asr-corpus`. That call did not download the audio. The upload is a third-party copy. It is an inspection reference only. It is not the acquisition source, and its file sizes are not treated as OpenSLR measurements.

The Kaggle listing included individual files under `dev-clean`, `test-clean`, `train-clean-360`, `intro-disclaimers`, `original-books`, and `raw-metadata`. Official `train-clean-100`, `dev-other`, `test-other`, and `train-other-500` archives were not top-level directories in that listing. That difference is another reason not to acquire from the Kaggle upload.

## Verification after the owner decision

The first pass on 2026-11-02 did not fetch `md5sum.txt` and did not have the archives. Later the same day the owner accepted CC BY 4.0 and authorized both archives. The preparation run then measured:

| Check | Result |
|-------|--------|
| Official MD5 | Both archives match `md5sum.txt` from `https://openslr.trmal.net/resources/12/md5sum.txt` |
| dev-clean size | 337,926,286 bytes compressed; 360,289,905 bytes extracted |
| test-clean size | 346,663,984 bytes compressed; 368,431,293 bytes extracted |
| Utterances | 2,703 dev-clean and 2,620 test-clean, each with one FLAC and one transcript line |
| Audio | 16,000 Hz, 1 channel, positive duration, `afconvert` decode failures 0 |
| Samples | 200 development and 200 held-out IDs, seed 17, no shared utterance or speaker |
| Transfer URL | Browser metadata still says `https://chatgpt.com/`. `downloaded_at` stays null. |

The speech remains read audiobook speech. It is not spontaneous conversation. No semantic labels were inferred from the transcripts.
