# Task and Label Schema

**Status:** The implementation candidate is Common Voice Scripted Speech v27.0 English. The TSV columns below are the public datasheet, not a file that was opened. Every field stays PENDING until the downloaded header is read. FSC and SLURP schemas are retained as superseded history.

## Milestone A — transcript

| Datasheet column | Intended use | Status |
|------------------|--------------|--------|
| `path` | Audio path relative to the archive | PENDING |
| `sentence` | Reference transcript | PENDING |
| `sentence_id` | Sentence identifier. Not automatically the sample id if one clip row is the sample. | PENDING |
| `locale` | Expected `en` if the catalogue page is the one confirmed by the owner | PENDING |
| Split file name | Source split. Datasheet says Train, Dev, and Test. Filenames unknown. | PENDING |

Do not put `client_id`, `age`, `gender`, or `accents` into public logs. `client_id` is not permission to identify a speaker. Speaker-overlap checks may use a speaker key only when the protocol names that key and forbids publishing it.

## Milestone B — manual semantic subset

Common Voice does not provide native general-purpose intent and slot labels. No intent accuracy or slot F1 is reported before this subset is annotated and checked.

For each pilot utterance, after ingestion:

| Field | Meaning | Status |
|-------|---------|--------|
| `intent` | What the speaker is trying to communicate, from a written taxonomy | Not created |
| `slots` | Entities or values required to understand the request, from written definitions | Not created |
| `transcript_correct` | Whether the reference transcript matches the audio | Not created |
| `ambiguity` | Whether a human can confidently determine the intended meaning | Not created |

The guide needs examples. A second reviewer marks a subset independently. Disagreements are adjudicated. If agreement is poor, revise the guide before expanding the set. Planning size: about 200–300 utterances. That is not a sample-size justification. The speech is scripted, so these labels are not evidence about spontaneous conversation.

## Superseded FSC schema

The block below is the publisher description of Fluent Speech Commands. It is **not** the current adapter schema.

## Illustrative frame

```json
{
  "intent": "PENDING",
  "slots": {
    "action": "PENDING",
    "object": "PENDING",
    "location": "PENDING"
  }
}
```

The key names `action`, `object`, and `location` come from the Fluent.ai dataset page and from Lugosch et al. 2019, Section 3.1, both read on 2026-11-02. They are not from Ruan et al. Ruan’s example slots are `city` and `date` on an ATIS-style weather utterance (Section 1). Those names must not be copied onto Fluent Speech Commands.

## Publisher mapping

| Dataset concept | Publisher statement | Cascade Pipeline field | Local status |
|-----------------|---------------------|--------------------|--------------|
| Transcription | CSV column for the utterance text | `transcript` | PENDING column name |
| Intent | Combination of the three slot values, not a separate free-text label. 31 such combinations stated. | `intent` as a canonical string of the three values, once the join rule is fixed | PENDING |
| Slots | `action`, `object`, `location` | `slots` object | PENDING |
| Location value `none` | Used when the command has no place | Keep the string `none`. Do not drop the slot. | PENDING |
| Speaker | Speaker ID in the split CSV | `speaker_id` | PENDING |
| Split | `train`, `valid`, `test` CSVs | `split` | PENDING |
| Audio path | Path in the CSV | `audio_path` | PENDING |

## Normalization rules (proposed, not yet applied)

- Compare slot values after stripping surrounding whitespace and lowercasing. Do not stem or spell-correct.
- A missing slot and an explicit `none` are different. Do not map one to the other.
- Do not invent a slot that the annotation omits.
- Multi-slot: the publisher description is exactly three slots per utterance. If a local row has more or fewer, record it as an annotation exception. Do not reshape it silently.
- Out-of-vocabulary slot values: if they appear in the file, they stay legal labels. Do not delete the row to improve accuracy.

## SLURP, from the official README example

**Source:** https://github.com/pswietojanski/slurp README, fetched 2026-11-02. This is one published example, not a census of the files.

| README field | Meaning in that example | Internal field | Status |
|--------------|-------------------------|----------------|--------|
| `slurp_id` | 4489 | `sample_id` | Example only |
| `sentence` | “wake me up at eight o'clock” | reference transcript | Example only |
| `intent` | `alarm_set` | `intent` | Do not map this string onto an FSC intent |
| `scenario` | `alarm` | dataset-native domain. Not an FSC slot. | Example only |
| `action` | `set` | Native SLURP field. Not the FSC `action` slot. | Keep separate |
| `entities[].type` and `span` | `time` over token 4 | slots, after a written span-to-value rule | The value rule is PENDING |
| `recordings[].file` | FLAC name, some with `-headset` | audio path | Close-talk and other mics are different files |
| `recordings[].wer` | Automatic score in the example | Not a human transcript and not a Cascade Pipeline metric | Do not train on it as a label |
| `metadata.json` `usrid` | Pattern such as `FO-488` | `speaker_id` | Encodes gender and whether English is native. Do not copy that into public logs unless a data-handling note allows it. |

Official split file names were not in the README section that was read. They are PENDING. Real and synthetic audio stay in separate conditions. Headset and non-headset files of the same utterance are not independent test items until a grouping rule is written.

## Class distribution

Not measured. No files are on disk.

| Item | Status |
|------|--------|
| Examples per intent | PENDING |
| Slot-value frequencies | PENDING |
| Rare values | PENDING |
| Train / valid / test label counts | PENDING |

Do not rebalance or oversample the test split when those counts exist.

## Ruan et al. label scheme

Not the scheme for this repository unless the owner approves a dataset change. ATIS intent and slot inventories were not loaded. Alexa label inventories are private and unavailable.
