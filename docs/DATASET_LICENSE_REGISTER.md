# Dataset License Register

**Checked:** 2026-11-02 (Phase 0.5, the Common Voice direction, the OpenSLR proposal, and the same-day owner acceptance of CC BY 4.0 for the two LibriSpeech archives).  
**This register is not legal advice.**  
**Owner decision** is the only acceptance field that matters. `Accepted` is Yes only when the owner decision is Accepted, No only when it is Refused, and N/A when it is Pending. Pending is not a refusal and is not permission.

The original pass did not download dataset audio. On 2026-11-02 the owner authorized the two LibriSpeech archives already present in Downloads. Those files were copied into the project after an MD5 check. They were not fetched again from OpenSLR by this register. Common Voice, FSC, and SLURP were not acquired.

## Gates

| Gate | Status | Meaning |
|------|--------|---------|
| A — Licensing review documented | Complete as a record | Current candidate and superseded rows each have an owner decision. Open questions on other datasets stay Pending. |
| B — Acquisition may be considered | Met for two LibriSpeech archives only | The owner accepted CC BY 4.0 for OpenSLR SLR12 and authorized `dev-clean.tar.gz` and `test-clean.tar.gz`. Common Voice, FSC, and SLURP stay Pending and blocked. |
| C — Phase 1 authorized | Not met | Phase 1B preparation of the two archives is authorized. Phase 1C and the rest of Phase 1 are not. |

Required for Gate B under the LibriSpeech decision: the owner has accepted CC BY 4.0 for OpenSLR SLR12 and has authorized `dev-clean` and `test-clean`, including extraction into the project dataset directory. That acceptance does not cover any other archive. Common Voice remains a pending candidate and is not approved. FSC and SLURP are superseded as implementation datasets. Their rows are kept. ATIS is out of implementation. Google Speech Commands is optional.

## LibriSpeech ASR corpus — OpenSLR SLR12 (authorized archives)

| Field | Record |
|-------|--------|
| Scope status | Authorized for `dev-clean.tar.gz` and `test-clean.tar.gz` only. Other OpenSLR archives are not authorized. |
| Artifact | `dev-clean.tar.gz` and `test-clean.tar.gz`. |
| Declared source | https://www.openslr.org/12/ and the file URLs `https://openslr.trmal.net/resources/12/dev-clean.tar.gz` and `https://openslr.trmal.net/resources/12/test-clean.tar.gz`. |
| Observed transfer URL | Browser `kMDItemWhereFroms` was `https://chatgpt.com/` via Brave. That is not an OpenSLR host. `downloaded_at` stays null. |
| Description on the catalog page | About 1000 hours of 16 kHz read English speech from LibriVox audiobooks, prepared by Vassil Panayotov with Daniel Povey. |
| Measured sizes | dev-clean 337,926,286 bytes. test-clean 346,663,984 bytes. Extracted regular files: dev-clean 360,289,905 bytes, test-clean 368,431,293 bytes. |
| Checksums | Official `md5sum.txt` retrieved from `https://openslr.trmal.net/resources/12/md5sum.txt`. dev-clean MD5 `42e2234ba48799c1f50f24a7926300a1` matched. test-clean MD5 `32fa31d27d2e1cad72775fee3f4849a9` matched. SHA-256 values are in the acquisition manifest. |
| Date checked | 2026-11-02 |
| License name and version | CC BY 4.0 |
| Deed | https://creativecommons.org/licenses/by/4.0/deed.en |
| Legal code | https://creativecommons.org/licenses/by/4.0/legalcode.en. The owner stated on 2026-11-02 that the complete legal code was read. |
| Commercial use | Accepted by the owner for the proposed CascadeGuard research use, under the licence conditions. This register is not a legal opinion. |
| Modification | The licence allows adaptations if changes are indicated. The copied archives and extracted files were not modified. |
| Attribution | Keep the corpus name, the preparers named on the catalog, OpenSLR SLR12, the catalog URL, CC BY 4.0, and the licence URL with the data and reports. The files used here were not modified. Do not imply endorsement. |
| Redistribution | Audio and archives stay out of git. The Kaggle upload `pypiahmad/librispeech-asr-corpus` is not an approved source. |
| Intended-use analysis | Read audiobook speech for a real-audio dataset. Not spontaneous conversation and not a command corpus. Privacy, publicity, and moral rights are not waived by the licence. |
| Owner decision | Accepted |
| Accepted | Yes |
| Decision record | D-LS-001, recorded 2026-11-02T10:42:27Z from the owner statement communicated at 2026-11-02T10:36:00+05:30. |
| Open questions | None for licence acceptance of these two archives. Speaker overlap of the drawn samples is checked by the preparation script. Phase 1C is not authorized. |

## Common Voice Scripted Speech 27.0 — English (pending candidate, not this acquisition)

| Field | Record |
|-------|--------|
| Scope status | Current candidate. Not frozen. Not downloaded. |
| Artifact | The English scripted-speech archive listed at https://mozilladatacollective.com/datasets/cmu5jplf300nwmh07iqvk9leo |
| Catalogue dataset ID | `cmu5jplf300nwmh07iqvk9leo`. Pending confirmation in the owner’s MDC account. |
| Locale on that page | `en`. Not `en-US`. Pending confirmation in the account. |
| Release named on that page | Scripted Speech 27.0. Datasheet corpus string `cv-corpus-27.0-2026-09-11`. Page release date 9/17/2026. Archive string displayed: `common-voice-scripted-speech-27-0-englis-e4a13e08.tar.gz`. Size displayed: 88.43 GB. Format displayed: MP3. |
| Date checked | 2026-11-02. Page fetched without an account download. |
| License name and version on that page | CC0-1.0. SPDX link on the page: https://spdx.org/licenses/CC0-1.0.html |
| Other terms read the same day | https://commonvoice.mozilla.org/en/terms — CC0 unless otherwise specified; access through MDC; do not post, distribute, or mirror the dataset. The dataset page also forbids determining speaker identity and forbids re-hosting or re-sharing. |
| Commercial use | Not decided here. CC0 is a copyright dedication. The page adds use prohibitions that are not the CC0 text. The CC0 legal code was not re-read in full. |
| Modification | Not decided here. |
| Attribution | CC0 does not require attribution. This pass does not treat that as a waiver of the no-redistribution request. |
| Redistribution | The dataset page forbids re-hosting and re-sharing. The Common Voice terms ask users not to post, distribute, or mirror the dataset. Do not commit audio. |
| Intended-use analysis | Unclear until the owner accepts the terms that apply to the signed-in record. The public pages describe an ASR corpus and forbid speaker identification and redistribution. Academic use is not automatic acceptance. The full archive is larger than the free disk measured the same day, so a full download is not currently possible on this machine. |
| Owner decision | Pending |
| Accepted | N/A |
| Open questions | (1) Does the signed-in MDC page show the same ID, locale, archive name, and size? (2) Does the owner accept CC0 plus the no-redistribution and no-identification terms? (3) Which smaller official file, if any, can be downloaded within about 60 GiB free? |

## FSC — audio and annotations

**Scope status: SUPERSEDED on 2026-11-02 as the implementation dataset.** The owner decision below is unchanged. Pending was not converted into Refused. Acquisition stays blocked. History is retained because the license conflict was never resolved.

| Field | Record |
|-------|--------|
| Artifact | Fluent Speech Commands audio and split annotations, treated as one release until a downloaded bundle shows they are separable. |
| Source URL | Publisher page: https://fluent.ai/fluent-speech-commands-a-dataset-for-spoken-language-understanding-research/ |
| Access channel named on that page | Google Group https://groups.google.com/a/fluent.ai/forum/#!forum/fluent-speech-commands (HTML link labelled as dataset access, read 2026-11-02). This is not a versioned archive URL. |
| Author data link | https://www.fluent.ai/research/fluent-speech-commands/ cited from Lugosch et al. 2019 and from `docs/DATASET_CARD.md`. Fetch timed out again on 2026-11-02. Contents UNKNOWN. |
| Not an authority | https://github.com/GrindstoneLZX/FluentSpeechCommandsDataset is a third-party repository. It was not fetched as the license source and was not cloned. |
| Release / version / commit | UNKNOWN. No local bundle. No checksum. No commit hash for an official corpus. |
| Date checked | 2026-11-02 |
| License name and version (page) | The page says Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International, academic research only. |
| License file or legal-code URL (page instrument) | https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode — legal code read 2026-11-02. The page does not link this URL itself. |
| License name (PDF) | Fluent Speech Commands Public License. Not a Creative Commons deed. |
| License file URL (PDF) | https://fluent.ai/wp-content/uploads/2021/04/Fluent_Speech_Commands_Public_License.pdf — full text read 2026-11-02. The page links this PDF as the “full license”. |
| Bundled file inside a download | Not opened. No archive was downloaded, so the license file that would ship inside a release is UNKNOWN. |
| Commercial use | Page: not authorized for any commercial purpose, including training, testing, bench-marking, or developing a product. PDF Section 2(a)(1): not authorized for any commercial purpose, including training, testing, bench-marking, industrial research, or developing a product. |
| Modification | CC BY-NC-ND 4.0 Section 2(a)(1)(B): produce and reproduce Adapted Material for NonCommercial purposes only, but do not Share it. PDF Section 2(a)(4): technical modifications necessary to exercise the license are allowed and by themselves are not Adapted Material. PDF Section 3: no permission to Share Adapted Material. |
| Attribution | CC BY-NC-ND 4.0 Section 3 if you Share. PDF Section 3(a): if used for research, retain creator identification, copyright notice, license notice, warranty disclaimer, and a Fluent.ai URL where practicable. |
| Redistribution | PDF Section 2(a)(1): reproduce, but not Share, for NonCommercial and academic purpose only. Share is defined in Section 1(i) to include providing material to the public. CC BY-NC-ND 4.0 does allow NonCommercial Share of the unmodified material. The two instruments disagree. Do not commit audio or annotations. |
| Intended-use analysis | Unclear, and not permitted merely because the project is academic. The page and the PDF name different licenses. The PDF’s grant is NonCommercial and academic reproduction without Share, while the same sentence lists training, testing, and bench-marking inside “any commercial purpose.” Whether noncommercial academic training and evaluation fall inside the grant or inside that list is unresolved. Which text would govern a file obtained from the Google Group is unknown until that bundle’s own license file is read. |
| Owner decision | Pending |
| Accepted | N/A |
| Open questions | (1) Which instrument governs the chosen release? (2) Does the PDF allow noncommercial academic training and testing, or does the commercial-purpose list forbid them? (3) Is placing files in git or any other redistribution a forbidden Share? (4) What exact release, date, and checksum does the Google Group distribute? |

## SLURP — audio (`slurp_real` and `slurp_synth`)

**Scope status: SUPERSEDED on 2026-11-02.** SLURP is not a Phase 1 dataset. The owner decision below is unchanged.

| Field | Record |
|-------|--------|
| Artifact | Audio archives only. Text annotations are a separate row. `slurp_real.tar.gz` and `slurp_synth.tar.gz` are separate files under one Zenodo license notice. Synthetic speech stays a separate experiment condition. |
| Source URL | https://zenodo.org/records/4274930 |
| Release / version | Version 1.0. DOI 10.5281/zenodo.4274930. Concept DOI for all versions: 10.5281/zenodo.4274929. Published 2020-11-16. |
| Checksums printed on the record (not recomputed locally) | `LICENSE.txt` md5 eb6f866654ad4facb53b038dc24f9c6a. `slurp_real.tar.gz` md5 9efc0f058ced47bf5131c7cb2cade513 (3.9 GB). `slurp_synth.tar.gz` md5 6186b4d2475aa8020afe746096e30b4f (2.8 GB). Archives were not downloaded. |
| Date checked | 2026-11-02 |
| License name and version | Creative Commons Attribution-NonCommercial 4.0 International, as stated in the record and in the Zenodo `LICENSE.txt` fetched the same day. |
| License file URL | https://zenodo.org/records/4274930/files/LICENSE.txt — fetched 2026-11-02. It points to the legal code and does not restate the grant. |
| Legal-code URL | https://creativecommons.org/licenses/by-nc/4.0/legalcode — read 2026-11-02. |
| Catalog wording | Zenodo “Rights” says “Other (Non-Commercial)” with no further description. That label is not a second license text. The file that states the license is `LICENSE.txt`. |
| Commercial use | Not permitted. Section 1(i) defines NonCommercial as not primarily intended for or directed towards commercial advantage or monetary compensation. Section 2(a)(1) limits reproduce, Share, and Adapted Material to NonCommercial purposes. |
| Modification | Section 2(a)(1)(B) allows producing and Sharing Adapted Material for NonCommercial purposes only. Section 2(a)(4) technical modifications are allowed and are not themselves Adapted Material. |
| Attribution | Section 3 applies if the material is Shared, including credit, copyright notice, license notice, warranty disclaimer, and a link where practicable, plus a note of modifications. |
| Redistribution | NonCommercial Share is within the grant if attribution is kept. Committing audio to this repository is still forbidden by project policy. A less strict audio license is mentioned in the GitHub README as available by contacting info@emotech.co. That request was not made. |
| Intended-use analysis | The legal code permits reproduction for NonCommercial purposes and does not grant a commercial use. It does not say that academic or non-profit status is automatically NonCommercial. Whether this project’s use is NonCommercial is an owner fact. Headset versus distant files are recording conditions, not a separate license. Real and synthetic archives were not acquired. |
| Owner decision | Pending |
| Accepted | N/A |
| Open questions | (1) Does the owner accept CC BY-NC 4.0 for local noncommercial research, including training and evaluation? (2) Will real audio be acquired without synthetic audio? (3) Is a separate Emotech license wanted? None of these was decided in this pass. |

## SLURP — textual annotations and repository text

**Scope status: SUPERSEDED on 2026-11-02.** Not a Phase 1 dataset. The owner decision below is unchanged.

| Field | Record |
|-------|--------|
| Artifact | Text distributed in https://github.com/pswietojanski/slurp , including `dataset/slurp/` as described in the README. Not the Zenodo audio. |
| Source URL | https://github.com/pswietojanski/slurp |
| Release / commit | `master` tip inspected via the GitHub API, not by cloning. Commit `8eb16545762be97ace75334109d73824217311f1`, dated 2022-04-20, message “Update README.md”. Tree `8d366577406450b9e1331ca991a9e9c48a907815`. README blob `3db862ad2ae887747ffab96154879de6f36db347`. LICENSE blob `24f3edf8edddf3f9e9ac3eb34fe26c29578f1f4f`. |
| Date checked | 2026-11-02 |
| License name and version | CC BY 4.0 for the textual part, stated in `LICENSE.txt` at that commit and in the README license section. |
| License file URL | https://github.com/pswietojanski/slurp/blob/8eb16545762be97ace75334109d73824217311f1/LICENSE.txt |
| Legal-code URL | https://creativecommons.org/licenses/by/4.0/legalcode — read 2026-11-02. |
| What the same LICENSE.txt also says | The audio part is CC BY-NC 4.0. That sentence does not re-license the Zenodo files and does not make the text NonCommercial. Audio remains the Zenodo row above. |
| Commercial use | CC BY 4.0 Section 2 does not add a NonCommercial condition. |
| Modification | Produce, reproduce, and Share Adapted Material, with the Adapter’s License condition in Section 3(a)(4) if Adapted Material is Shared. |
| Attribution | Required when Sharing, Section 3. |
| Redistribution | Share is within the grant if attribution is kept. Cloning the repository was not done. A later clone would copy annotation files and must stay pinned to this commit unless the register is updated. |
| Intended-use analysis | The legal code permits reproduction and adaptation of the licensed text, with attribution if it is shared. That is not an owner acceptance. The repository also contains `scripts/` and `experiments/`; this pass did not treat those directories as the annotation license boundary beyond the LICENSE.txt wording (“textual part”). README `usrid` encodes gender and whether English is native. Copyright permission is not permission to publish those attributes. |
| Owner decision | Pending |
| Accepted | N/A |
| Open questions | (1) Does the owner accept CC BY 4.0 for the text at this commit? (2) Will a later acquisition copy only `dataset/slurp/` or the whole tree? |

## SLURP — speaker metadata inside the text release

| Field | Record |
|-------|--------|
| Artifact | `usrid` and related fields in `dataset/slurp/metadata.json`, as described in the README at the commit above. The file itself was not downloaded. |
| Source URL | Same repository and commit as the text row. |
| License | No separate license title. The README presents metadata as part of the textual release, so the text row’s CC BY 4.0 statement is the copyright notice on record. |
| Date checked | 2026-11-02 |
| Restrictions | `usrid` pattern in the README: gender (`F`, `M`, or `UNK`), language (`E` native English or `O` other), and a three-digit id. Example in the README: `FE-488`, `FO-488`, `UNK-323`. |
| Intended-use analysis | Unclear for publication. The copyright license does not decide whether those attributes may be copied into logs, papers, or git. Default: do not publish them. |
| Owner decision | Pending |
| Accepted | N/A |

## ATIS

| Field | Record |
|-------|--------|
| Artifact | Any LDC ATIS audio or text release. |
| Scope | Excluded from implementation. Not required for Gate B. |
| Source | LDC catalog pages checked in Phase 0. Agreement text was not read in Phase 0.5. |
| License | Not read. |
| Date checked | 2026-11-02 for this status note. Agreement text was not re-fetched. |
| Intended-use analysis | Not permitted under the current plan because the dataset is out of scope and no agreement was accepted. |
| Owner decision | Pending |
| Accepted | N/A |
| Note | Pending here means the license was not decided. It does not reopen ATIS as a Phase 1 dataset. |

## Google Speech Commands

| Field | Record |
|-------|--------|
| Artifact | Optional stretch audio. Not on the critical path. Not required for Gate B. |
| Release | Not selected. |
| License | Not inspected in this pass. |
| Date checked | 2026-11-02 |
| Intended-use analysis | Not applicable until a later note reads a specific release. |
| Owner decision | Pending |
| Accepted | N/A |

## Acquisition

LibriSpeech `dev-clean` and `test-clean` are authorized under D-LS-001. No other LibriSpeech archive is authorized. Common Voice acquisition is BLOCKED until the owner confirms the MDC record and records Accepted. FSC acquisition is BLOCKED. SLURP audio acquisition is BLOCKED. SLURP text acquisition is BLOCKED. Phase 1C is not authorized.
