# Phase 1D dataset comparison

**Date:** 2026-11-02  
**Role:** Research and acquisition planning. No archive was downloaded. No licence was accepted.  
**Storage measured the same day:** `data/` is 1,430,267,408 bytes. The project cap is 5,000,000,000 bytes, so 3,569,732,592 bytes remain. Nothing was deleted.

A field that was not read from an official source is `not_verified`. A count taken from a paper table is attributed to that table. Secondary comparisons are labelled as secondary.

## Candidates

| Candidate | Official source read on 2026-11-02 | Acquisition in this phase |
| --- | --- | --- |
| LibriSpeech `dev-clean` and `test-clean` | Already local. OpenSLR SLR12. | Already authorized for those two archives only. Not a task-oriented SLU corpus. |
| SLURP | Zenodo 10.5281/zenodo.4274930 and GitHub commit `8eb16545762be97ace75334109d73824217311f1` | Not downloaded. Not authorized. |
| Fluent Speech Commands | Publisher page, Public License PDF, Interspeech 2019 paper | Not downloaded. Not authorized. |
| Timers and Such v1.0 | Zenodo 10.5281/zenodo.4623772 and the NeurIPS Datasets and Benchmarks paper | Not downloaded. Not authorized. |
| Sonos / Snips spoken SLU sets | GitHub `sonos/spoken-language-understanding-research-datasets` README and LICENSE | Not requested. Not downloaded. Not authorized. |
| STOP | arXiv 2207.10643 and `facebookresearch/spoken_task_oriented_parsing` | Not downloaded. Licence text not found. Not authorized. |

ATIS remains out of implementation. The LDC agreement was not re-read. Common Voice remains a pending read-speech candidate and does not supply task intents or slots.

## LibriSpeech, prepared splits

| Field | Record |
| --- | --- |
| Name | OpenSLR SLR12, `dev-clean` and `test-clean` only |
| Owner | OpenSLR / LibriSpeech preparers named on the catalog |
| Access | Already local |
| Paper | Panayotov et al., the LibriSpeech paper. Not re-read in this pass. |
| Year | Corpus release predates this project. Not re-dated here. |
| Utterances | 2,703 `dev-clean` and 2,620 `test-clean`, from the Phase 1B validation |
| Speakers | Official speaker tables exist in the extracted release. This pass did not recount them. |
| Intents, slots, domains | None |
| Language | English, read audiobook speech |
| Audio | 16 kHz, mono, FLAC, from the Phase 1B validation |
| Transcripts | Yes, chapter-level `.trans.txt` |
| Speaker-independent splits | The prepared development and held-out samples use disjoint speaker sets. That fact is from Phase 1B, not a new count. |
| Licence | CC BY 4.0, accepted for these two archives only |
| Storage | Already inside the measured `data/` total |
| Limitation | No task intent or slot gold. Phase 1C annotation is still `not_annotated`. |

## SLURP

| Field | Record |
| --- | --- |
| Name | SLURP: A Spoken Language Understanding Resource Package, version 1.0 |
| Owner | Bastianelli, Vanzo, Swietojanski, and Rieser. Audio hosted on Zenodo. Text hosted by the GitHub repository. |
| Access | https://zenodo.org/records/4274930 and https://github.com/pswietojanski/slurp |
| Paper | Bastianelli et al., EMNLP 2020. https://aclanthology.org/2020.emnlp-main.588/ |
| Year | 2020. Zenodo publication date 2020-11-16. |
| Audio files | Paper Table 2, SLURP column: 72,277. Close range 34,603. Far range 37,674. |
| Sentences | Paper Table 3, SLURP lexicalised column: 17,181. |
| Speakers | Paper Table 2: 177. The introduction also says “100+ participants”. The table is the count used here. |
| Scenarios | Paper Table 4: 18 |
| Actions | Paper Table 4: 46. The introduction also says 46. |
| Entity types | Paper Table 4: 56. The introduction says 55. Those two figures were not reconciled. |
| Annotated entity instances | Paper Table 4: 16,792 |
| Language | English |
| Audio format | README at the pinned commit: FLAC, close-talk files named with `-headset`, plus distant files. Sample rate: `not_verified`. |
| Average duration | Paper Table 2: 2.9 seconds. Total duration in that table: 58 hours. |
| Transcripts | Yes. README field `sentence`. The paper says the textual data is the gold transcription. |
| Intent | Scenario and action. README example: scenario `alarm`, action `set`, intent `alarm_set`. |
| Slots | Entity spans and types. README example type: `time`. |
| Speaker IDs | README `usrid` encodes gender, native-English status, and a three-digit id. Do not publish those attributes. |
| Official splits | GitHub tree at the pinned commit contains `train.jsonl`, `devel.jsonl`, and `test.jsonl`. Paper Table 6: train 11,514 sentences and 50,628 audio files; dev 2,033 sentences and 8,690 audio files; test 2,974 sentences and 13,078 audio files. Those three audio counts sum to 72,396, while Table 2 says 72,277. The difference was not resolved. Speaker-disjoint splits: `not_verified`. |
| Audio licence | CC BY-NC 4.0, stated in Zenodo `LICENSE.txt`. The Zenodo API licence id is `other-nc`. |
| Text licence | CC BY 4.0 for the textual part, stated in the repository README and LICENSE at commit `8eb16545762be97ace75334109d73824217311f1`. |
| Compressed sizes from the Zenodo API | `slurp_real.tar.gz` 3,918,185,662 bytes, MD5 `9efc0f058ced47bf5131c7cb2cade513`. `slurp_synth.tar.gz` 2,839,670,545 bytes, MD5 `6186b4d2475aa8020afe746096e30b4f`. `LICENSE.txt` 287 bytes. |
| Extracted size | `not_verified`. The README says the download script needs around 6 GB for the acoustic data. |
| Owner decision | Pending. Not authorized. |
| Limitation | Single-turn commands. No follow-up gold for CLARIFY. Real and synthetic audio are separate archives. The real archive alone is larger than the remaining cap. |

## Fluent Speech Commands

| Field | Record |
| --- | --- |
| Name | Fluent Speech Commands |
| Owner | Fluent.ai, as named on the publisher page and in Lugosch et al. |
| Access | Publisher page https://fluent.ai/fluent-speech-commands-a-dataset-for-spoken-language-understanding-research/ and Google Group https://groups.google.com/a/fluent.ai/g/fluent-speech-commands. The author URL https://www.fluent.ai/research/fluent-speech-commands/ was not re-fetched. |
| Paper | Lugosch et al., Interspeech 2019, https://www.isca-archive.org/interspeech_2019/lugosch19_interspeech.pdf |
| Year | 2019 |
| Utterances | Paper Table 1: train 23,132, valid 3,118, test 3,793, total 30,043 |
| Speakers | Paper Table 1: train 77, valid 10, test 10, total 97. The paper says no speaker appears in more than one split. |
| Hours | Paper Table 1: 14.7, 1.9, 2.4, total 19.0 |
| Intents | 31. The paper defines an intent as the combination of the three slot values. |
| Slots | Three: `action`, `object`, `location` |
| Phrases | 248, written before collection |
| Domains | One prompted smart-home / virtual-assistant command setting. The paper does not assign a separate domain label. |
| Language | English. Native and non-native speakers contributed phrasings. Demographic fields are included with the release. |
| Audio | 16 kHz, single-channel `.wav` |
| Average duration | `not_verified` as a published average. Paper Table 1 gives hours and utterance counts. |
| Transcripts | Yes. Each split CSV lists speaker ID, path, transcription, and slots. |
| Audio licence on the page | The page says CC BY-NC-ND 4.0, academic research only. |
| Licence PDF linked as the full licence | Fluent Speech Commands Public License, https://fluent.ai/wp-content/uploads/2021/04/Fluent_Speech_Commands_Public_License.pdf |
| Archive size and checksum | `not_verified`. No release version is pinned. |
| Owner decision | Pending. Not authorized. |
| Limitation | The page and the PDF are different instruments. The bundle that a group member would receive was not opened, so the licence inside that bundle is unknown. |

## Timers and Such v1.0

| Field | Record |
| --- | --- |
| Name | Timers and Such v1.0 |
| Owner | Loren Lugosch, as named on the Zenodo record |
| Access | https://zenodo.org/records/4623772 |
| Paper | Lugosch et al., arXiv:2104.01604, accepted to NeurIPS 2021 Datasets and Benchmarks |
| Year | Zenodo publication date 2021-03-19 |
| Real utterances | Paper Table 1: train-real 1,640, dev-real 271, test-real 240, all-real 2,151 |
| Real hours | Paper Table 1: 1.9, 0.3, 0.3, all-real 2.5 |
| Real speakers | Paper Table 1 marks speaker counts as approximate: train-real 74, dev-real 11, test-real 10, all-real 95. The paper says it is unknown whether 89 website sessions are 89 people. |
| Synthetic audio | train-synth 192,000 audios / 132.2 hours; dev-synth 24,000 / 15.8 hours; test-synth 36,000 / 23.5 hours. These are VoiceLoop syntheses, not the real-speech condition. |
| Intents | Four: `SetTimer`, `SetAlarm`, `SimpleMath`, `UnitConversion` |
| Slots | Semantic dictionaries with numeric slots. The paper says the labels are not word-aligned. |
| Domains | Offline numeric commands. Not a multi-domain assistant. |
| Language | English. Prompts were generated from a small grammar. |
| Audio format and sample rate | `.wav` is named in the paper. Sample rate: `not_verified`. |
| Transcripts | Yes, in the split CSV files described by the paper. |
| Licence in the paper | The paper says the Zenodo release is under CC0. |
| Licence on the Zenodo API | `other-open`. The record contains one zip and no separate licence file. |
| File | `timers-and-such-v1.0.zip`, 13,133,746,587 bytes, MD5 `23e819241f46dbc71d09a84c2ad5d527` |
| Owner decision | Pending. Not authorized. |
| Limitation | The only published file is larger than the cap. The real subset’s byte size inside that zip was not measured. |

## Sonos / Snips spoken sets

| Field | Record |
| --- | --- |
| Name | Datasets from Saade et al., “Spoken Language Understanding on the Edge” |
| Owner | Sonos Voice Experience Team. The README says the Snips team joined Sonos in November 2019. |
| Access | https://github.com/sonos/spoken-language-understanding-research-datasets and the form https://forms.gle/JtmFYM7xK1SaMfZYA |
| Paper | Saade et al., arXiv:1810.12735, EMC2 workshop at NeurIPS 2019 |
| Year | 2019 |
| SmartLights queries | README: six intents, 296, 296, 296, 300, 299, and 278 queries. Slots include `room`, `brightness`, and `color`. |
| SmartSpeaker | README: English and French. For this assistant, recordings are available only for the test set. English test material described as 1,500 `play some music by #ARTIST` queries. |
| Audio files and hours | `not_verified` from the bundle. The SLURP paper’s Table 2, as a secondary comparison, lists 5,886 Snips audio files, 69 speakers, and 5.5 hours. That is not a measurement of the Sonos form bundle. |
| Audio conditions | README: one crowdsourced utterance per available text query, plus far-field replay at 2 meters. Some text queries have no recording. |
| Transcripts, intents, slots | Described as present. The files were not opened. |
| Speaker-independent splits | `not_verified` |
| Licence | Custom Sonos terms in the repository LICENSE. Academic and research use. No commercial use. Publication of modified datasets is prohibited. Personal-data clauses apply. |
| Archive size and checksum | `not_verified` |
| Owner decision | Pending. Not authorized. |
| Limitation | Access is an approval form, not a pinned archive. SmartSpeaker training audio is absent. |

## STOP

| Field | Record |
| --- | --- |
| Name | Spoken Task-Oriented Semantic Parsing (STOP) |
| Owners | Tomasello and colleagues at Meta, as named on the paper |
| Access named by the authors | https://github.com/facebookresearch/fairseq/tree/main/examples/audio_nlp/nlu. That page points at download links. Those links were not opened and no checksum was read. |
| Paper | arXiv:2207.10643. Later IEEE SLT 2023 version was not used for the counts. |
| Year | arXiv versions 2022 |
| Audio files | Paper Table 3: 236,477 |
| Speakers | Paper Table 3: 885. The paper says a speaker may appear in only one split. |
| Duration | Paper Table 3: 218 hours |
| Intents and slot types | Semantic parses inherited from TOPv2. The number of intents and slot types was `not_verified` in this pass. |
| Domains | The paper uses Weather and Reminder as held-out domains and treats the other TOPv2 domains as held-in. The full domain count was `not_verified`. |
| Language | English |
| Audio format and sample rate | `not_verified` |
| Transcripts | The paper includes a normalized spoken form and the original written form. |
| Annotations | Semantic parse trees. Exact match of the full parse is one of the paper’s metrics. |
| Licence | The GitHub repository is marked `Other`. No licence text was found or read. |
| Archive size | `not_verified` |
| Owner decision | Pending. Not authorized. |
| Limitation | 218 hours of audio cannot be planned inside the remaining cap until an official byte size exists. The missing licence text blocks a recommendation by itself. |

## Scores

Full points require a verified property that meets the research need. Unknown information does not receive full points. A licence score is about whether the terms are clear. It is not owner acceptance. Owner acceptance is recorded separately and is Pending for every new candidate.

| Dimension | Weight | LibriSpeech prepared splits | SLURP | FSC | Timers and Such | Sonos / Snips | STOP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Actual speech recordings | 15 | 15 | 15 | 15 | 15 | 12 | 15 |
| Reference transcripts | 10 | 10 | 10 | 10 | 10 | 10 | 10 |
| Intent annotations | 15 | 0 | 15 | 12 | 10 | 12 | 12 |
| Slot or entity annotations | 15 | 0 | 15 | 12 | 12 | 12 | 12 |
| Licensing clarity | 15 | 15 | 9 | 3 | 6 | 7 | 2 |
| Speaker metadata and split quality | 10 | 8 | 6 | 10 | 5 | 2 | 8 |
| Dataset size and diversity | 10 | 6 | 8 | 6 | 4 | 4 | 8 |
| Reproducible access and documentation | 5 | 5 | 4 | 2 | 3 | 2 | 2 |
| Suitability for recovery evaluation | 5 | 1 | 3 | 2 | 3 | 2 | 3 |
| Total | 100 | 60 | 85 | 72 | 68 | 63 | 72 |

LibriSpeech’s 60 is an acoustic and transcript score. It fails intent and slot gold, so it is not the task-oriented recommendation. SLURP has the highest score and still cannot be acquired: the owner has not accepted CC BY-NC 4.0, and `slurp_real.tar.gz` is 3,918,185,662 bytes, which is 348,453,070 bytes above the remaining cap before extraction.

## What was not claimed

No candidate was counted for negation, uncertainty, or contradictory slots by opening its annotation files. The SLURP README publishes one example whose entity type is `time`. That example shows the schema, not a corpus frequency. Timers and Such is designed around numbers; that is a property of the paper’s grammar, not a count of negation.
