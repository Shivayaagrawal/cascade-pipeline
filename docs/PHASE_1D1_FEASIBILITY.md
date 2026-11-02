# Phase 1D.1 feasibility

**Date:** 2026-11-02  
**Decision it follows:** `docs/PHASE_1D_DECISION.md`. Acquisition stays not approved.  
**Nothing was downloaded.** No licence was accepted. No existing experiment, LibriSpeech file, pilot row, or `test-clean` file was changed.

This note is a reading of the official SLURP release and the licences already identified in Phase 1D. It is not a legal opinion and it is not permission to acquire the data.

## Storage

Two different limits apply.

| Limit | Measurement on 2026-11-02 | What it controls |
| --- | --- | --- |
| Project cap | 5,000,000,000 bytes. `data/` is 1,430,267,408 bytes. Room remaining: 3,569,732,592 bytes. | The project rule. SLURP was not given an exception. |
| Volume free space | `df` on `/System/Volumes/Data` reported 61,288,712 one-kibibyte blocks available, which is 62,759,641,088 bytes. | Whether the machine has physical room. It does not raise the project cap. |

`slurp_real.tar.gz` is 3,918,185,662 bytes. Under the project cap the shortfall is 348,453,070 bytes before the archive is extracted and before any working files are written.

The pinned script `scripts/download_audio.sh` at commit `8eb16545762be97ace75334109d73824217311f1` downloads `slurp_real.tar.gz` and `slurp_synth.tar.gz`, then extracts both. Those two compressed files are 3,918,185,662 and 2,839,670,545 bytes, 6,757,856,207 bytes together. The README says that download needs around 6 GB. The extracted FLAC size was not measured. Keeping a verified archive and its extraction needs both. The compressed real file alone already misses the cap, so the working copy needs a larger allowance than 348 MB.

Options that were considered, and not taken:

| Option | Result |
| --- | --- |
| Stay inside the current cap | The real archive does not fit. |
| Delete LibriSpeech, synthetic audio, or other project data | Not allowed. The decision says additional storage must not come from deleting existing research data. |
| Treat free disk as permission | The volume has about 62.8 GB free. That fact does not change the cap or the licence. |
| Use the external SSD mentioned in `docs/STORAGE_DECISION.md` | An external disk can add room. The existing storage decision says extra disk does not change access rules. Using it for SLURP would be a new storage decision, which was not made. |
| Raise the project cap | An owner decision. Not made here. A later cap would still have to cover extraction and working files, not only the 348 MB gap. |

## Official subset

The Zenodo record 10.5281/zenodo.4274930 lists three files: `LICENSE.txt`, `slurp_real.tar.gz`, and `slurp_synth.tar.gz`. It does not list a development subset, a split archive, or per-utterance files.

The official download script has no argument that selects a split or skips an archive. It fetches both tar archives and extracts both.

The GitHub text files at the pinned commit are small: `train.jsonl` 12,745,012 bytes, `devel.jsonl` 2,221,203 bytes, `test.jsonl` 3,267,569 bytes, and `metadata.json` 18,473,896 bytes. They would fit under the cap. They are not an audio subset. They were not downloaded. Downloading them would still be acquisition of an unauthorized release, and text alone cannot evaluate ASR or recovery on speech.

An unofficial subset, a partial range request, or extracting some members after an unauthorized download is not an official selective download. None of those is adopted.

## Licence implications

The audio and the text are separate instruments.

The audio notice on Zenodo is CC BY-NC 4.0. The legal code limits reproduction and sharing to NonCommercial purposes. NonCommercial means not primarily intended for or directed towards commercial advantage or monetary compensation. Calling the project academic does not, by itself, answer that test. The owner still has to decide whether the intended research and use meet it. If the audio is shared, attribution is required. Adapted material may be shared only for NonCommercial purposes. The legal code does not waive privacy, publicity, or moral rights.

The text at the pinned commit is CC BY 4.0. That grant does not add a NonCommercial condition, and it does not remove the NonCommercial condition from the audio. Accepting the text licence would not authorize the recordings.

The README says a less strict audio licence can be requested from info@emotech.co. That request was not made. Until a written offer is received and accepted, the Zenodo CC BY-NC 4.0 notice is the audio instrument on record.

`usrid` encodes gender and whether English is native. A copyright decision does not decide whether those attributes may be copied into a report.

Publishing measurements is a different act from redistributing the files. Redistributing the audio remains under the audio licence. This note does not decide either act.

## Other candidates

No other candidate reviewed in Phase 1D is both clearer on the licence and small enough under the current cap.

| Candidate | Licence relative to SLURP | Storage relative to the remaining cap |
| --- | --- | --- |
| Fluent Speech Commands | Less clear. The page and the Public License PDF disagree. | Archive size and checksum are unknown. Not a verified fit. |
| Timers and Such v1.0 | Not clearer. The paper says CC0. The Zenodo licence id is `other-open`, and the record has no licence file. | The only file is 13,133,746,587 bytes. It does not fit. |
| Sonos / Snips | A custom academic licence was read. Access still requires the form, and commercial use is excluded. | Archive size is unknown. SmartSpeaker training recordings are absent. |
| STOP | Not clearer. The repository licence field is `Other`, and no grant was read. | 218 hours are reported. The archive size is unknown. |
| Prepared LibriSpeech | Already authorized for two archives. | Already inside `data/`. It has no intent or slot gold. |

Switching to one of these sets would trade away either licence clarity, task labels, or both. The storage shortfall is not a reason to do that.

## Trade-off

Waiting keeps the research claim tied to a real-speech, task-oriented release with official splits and entity spans. The cost is that B0, B1, and B2 on real task speech stay unmeasured. The synthetic results do not fill that gap, and LibriSpeech does not supply the missing frames.

Acquiring SLURP now would require three changes that have not been made: acceptance of CC BY-NC 4.0 for the audio, acceptance of CC BY 4.0 for the pinned text, and a storage decision that covers the compressed real archive plus extraction and working files without deleting existing data. A text-only download would fit and would still not be the speech experiment.

## What remains blocked

Phase 1E is blocked. No subset will be built to force a fit. The next owner decisions, if any, are the audio licence, the text licence, and the storage rule, each recorded separately.
