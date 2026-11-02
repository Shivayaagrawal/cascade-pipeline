# Phase 1D licensing and authorization register

**Date:** 2026-11-02  
**Statuses used here:** `verified`, `pending_verification`, `authorization_required`, `authorized`, `rejected`.  
**No row was set to `authorized` in this pass.** The earlier acceptance of CC BY 4.0 for the two LibriSpeech archives is recorded again because it already exists. It was not extended.

Owner decision remains Pending for every new candidate. Pending is not a refusal and is not permission to download. This register does not edit `docs/DATASET_LICENSE_REGISTER.md`.

## LibriSpeech `dev-clean` and `test-clean`

| Field | Record |
| --- | --- |
| Audio licence | CC BY 4.0. `verified` for the two local archives. |
| Transcript licence | Same release and same CC BY 4.0 statement. |
| Annotation licence | No task annotations are in the release. |
| Official source | https://www.openslr.org/12/ and https://creativecommons.org/licenses/by/4.0/legalcode |
| Commercial use | The CC BY 4.0 grant does not add a NonCommercial condition. |
| Attribution | Corpus name, preparers, OpenSLR SLR12, catalog URL, CC BY 4.0, and the licence URL. |
| Owner authorization | `authorized` for these two archives only, under the recorded D-LS-001 decision. |
| Other archives | `authorization_required`. Not covered by that decision. |

## SLURP audio

| Field | Record |
| --- | --- |
| Files | `slurp_real.tar.gz` and `slurp_synth.tar.gz`, Zenodo version 1.0, DOI 10.5281/zenodo.4274930 |
| Audio licence | CC BY-NC 4.0, stated in the record’s `LICENSE.txt`. `verified` as the text of that notice. |
| Zenodo API licence id | `other-nc`. That id is not a second grant. |
| Transcript and annotation licence | Not this row. The text is the GitHub row. |
| Official source | https://zenodo.org/records/4274930/files/LICENSE.txt and https://creativecommons.org/licenses/by-nc/4.0/legalcode |
| Commercial use | Not granted. NonCommercial is defined in the legal code and is an owner judgment for this project. |
| Attribution | Required if the material is shared. |
| Redistribution | NonCommercial sharing is inside the CC BY-NC grant. Project policy still forbids committing audio. |
| Derived annotations | Adapted material may be shared for NonCommercial purposes under the legal code. That question is not accepted for this project. |
| Research publication | The legal code does not forbid a paper. It does restrict commercial use. |
| Another licence | The GitHub README says a less strict audio licence may be requested from info@emotech.co. That request was not made. `pending_verification`. |
| Owner authorization | `authorization_required` |

## SLURP text and annotations

| Field | Record |
| --- | --- |
| Release | GitHub commit `8eb16545762be97ace75334109d73824217311f1`, read again on 2026-11-02 |
| Text licence | CC BY 4.0 for the textual part. `verified` as the README and LICENSE statement at that commit. |
| Audio licence named in the same README | CC BY-NC 4.0. That sentence does not replace the Zenodo file. |
| Official source | https://github.com/pswietojanski/slurp/blob/8eb16545762be97ace75334109d73824217311f1/LICENSE.txt |
| Commercial use | CC BY 4.0 does not add a NonCommercial condition. |
| Attribution | Required when sharing. |
| Speaker attributes | `usrid` encodes gender and whether English is native. Copyright permission is not permission to publish those attributes. |
| Owner authorization | `authorization_required` |

## Fluent Speech Commands

| Field | Record |
| --- | --- |
| Page instrument | The publisher page says CC BY-NC-ND 4.0, academic research only. `verified` as the page wording. |
| PDF instrument | Fluent Speech Commands Public License. `verified` as the PDF fetched from https://fluent.ai/wp-content/uploads/2021/04/Fluent_Speech_Commands_Public_License.pdf |
| Conflict | The page allows the CC BY-NC-ND name. The PDF grants reproduction, and not Share, for NonCommercial and academic purposes, and lists training, testing, bench-marking, industrial research, and product development inside “any commercial purpose.” The two texts do not say the same thing about sharing or about academic evaluation. |
| Bundle licence | `pending_verification`. No archive was opened. |
| Audio, transcript, and annotation | Treated as one release until a bundle shows they are separable. |
| Commercial use | Not granted by either instrument. |
| Attribution | The PDF requires creator identification, copyright notice, licence notice, warranty disclaimer, and a Fluent.ai URL where practicable, if the material is used for research. |
| Redistribution | Unresolved between the instruments. |
| Access | Google Group, not a versioned file URL. |
| Owner authorization | `authorization_required`. Not `rejected`. The conflict is unresolved, not a recorded refusal. |

## Timers and Such v1.0

| Field | Record |
| --- | --- |
| Paper statement | The paper says the Zenodo release is under CC0. `verified` as a sentence in the paper. |
| Zenodo API | Licence id `other-open`. No licence file is in the record. `pending_verification` for the instrument that applies to the zip. |
| File | `timers-and-such-v1.0.zip`, DOI 10.5281/zenodo.4623772 |
| Audio, transcript, and annotation | One zip. Separate licences were not found. |
| Commercial use | Not decided, because CC0 and `other-open` are not the same finding. |
| Attribution | Not decided until the zip’s licence is identified. |
| Owner authorization | `authorization_required` |

## Sonos / Snips spoken sets

| Field | Record |
| --- | --- |
| Licence | Custom terms in https://github.com/sonos/spoken-language-understanding-research-datasets/blob/master/LICENSE. `verified` as that file. |
| Grant | Internal academic or research use, including training. Publication of unmodified datasets to the academic or research community, under the same terms. |
| Commercial use | Precluded, including training models for commercial products. |
| Modification | Internal modification is granted. Publication of modified datasets is prohibited. |
| Attribution | Any publication must cite Saade et al. 2019. |
| Personal data | The terms say the recordings and demographic data may be personal data and assign controller responsibility to the recipient. |
| Access | A form must be accepted before the files are provided. No checksum was on the README. |
| Owner authorization | `authorization_required` |

## STOP

| Field | Record |
| --- | --- |
| Repository | https://github.com/facebookresearch/spoken_task_oriented_parsing is archived and labelled `Other`. |
| Licence text | `pending_verification`. No grant was read. |
| Download host | Named from the fairseq example page. The file page was not opened. |
| Audio, transcript, and annotation | Not separated into licence rows, because no instrument was found. |
| Owner authorization | `authorization_required` |

## What this register does not do

It does not accept CC BY-NC 4.0, CC BY 4.0 for SLURP text, CC BY-NC-ND 4.0, the Fluent Speech Commands Public License, CC0, the Sonos terms, or an unread STOP licence. It does not mark any of those datasets `rejected`. A later acceptance has to name the exact file, the exact instrument, and whether synthetic audio is included.
