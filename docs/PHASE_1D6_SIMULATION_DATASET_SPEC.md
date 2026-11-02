# Phase 1D.6 simulation dataset specification

**Date:** 2026-11-02  
**Status:** specification of the frozen set, plus rules for any later set. No utterance was generated.

## Frozen baseline

| Item | Value |
| --- | --- |
| Dataset version | `synthetic-seed17-v1` |
| Code | `generate_utterances()` and `generate_variants(..., seed=17)` |
| Config | `configs/simulation.yaml` |
| Gold rows | 200. Ids `utt-000` through `utt-199`. |
| Intent distribution | 10 intents, 20 utterances each, fixed order in `utterance_generator.py`. |
| Edited variants | 600. Three per gold row. Provenance `synthetic_edit`. Bundle source `SYNTHETIC_PROXY`. |
| Variant id | `{utterance_id}-v0`, `v1`, `v2`. |
| Category assignment | `categories_for_index`. Three distinct names from the eight categories, chosen by the utterance index. Not a sampled rate. |
| Edit seed | `random.Random(f"17:{utterance_id}:{category}")`. |
| Gold sentence in the bundle | Excluded. If an edit copies the gold text, the injector appends ` changed`. |
| Train / development / evaluation | No split. All 200 ids are the evaluation set. No training run exists. |
| Replacement rule | Do not overwrite these rows, `data/synthetic/`, or the frozen experiment directories. |

The eight categories are `deletion`, `substitution`, `insertion`, `entity_corruption`, `number_corruption`, `negation_corruption`, `ambiguous_transcript`, and `incorrect_transcript`. They are analysis labels on the written edit. They are not ASR error rates.

These 600 strings are not organised as Candidate A through Candidate D. That four-role layout is a template for a future version only. Applying those role names to `synthetic-seed17-v1` would misdescribe the file.

Other written lists over the same 200 ids, from `candidate_diversity.py`, are further `SYNTHETIC_PROXY` conditions: paraphrase, slot-removed, and split evidence. They are not a fourth variant inside the 600, and they are not a new dataset version.

## Gold frame

Each gold row has an id, an intent string, the original sentence, and a slot map.

| Intent | Slot names in the gold rows | Inventory length |
| --- | --- | --- |
| `book_appointment` | `date` | 20 dates |
| `cancel_appointment` | `date`, except `utt` of the sentence “Cancel my appointment”, which has an empty map | 1 empty, then 19 dates |
| `check_appointment` | `date`, except “When is my appointment?”, which has an empty map | 1 empty, then 19 dates |
| `check_balance` | `account` | 20 accounts |
| `transfer_money` | `amount`, `currency`=`rupees` | 20 amounts |
| `check_transaction` | `recency` | 20 recency phrases |
| `set_reminder` | `time` | 20 times |
| `weather_query` | `date` | 20 dates |
| `play_music` | `genre` | 20 genres |
| `general_information` | `topic` | 20 topics |

The value lists are the tuples in `utterance_generator.py`. Each checked inventory has length 20. The lexical reader’s `CRITICAL_SLOTS` still lists `date` for cancel and check-appointment, including the two rows whose gold map is empty. That difference is already part of the frozen v3 result. This specification does not change it.

Intent and slot labels are simulation labels. They are not human annotations of speech.

## Candidate provenance

Every edited candidate used by B0, B1, or B2 is `SYNTHETIC_PROXY` / `synthetic_edit`. The gold sentence, when scored alone, is `reference_passthrough` and is not a candidate. `native_nbest` is invalid on this dataset.

## Rules for a later dataset version

A new set is allowed only after an explicit authorization that names the version. It is a new directory and new ids. It does not reuse `utt-000` through `utt-199` as if they were new draws.

The authorization has to state, before any row is written:

| Field | Required statement |
| --- | --- |
| Utterance count | An integer, separate from 200. |
| Intent distribution | Counts per intent. |
| Slot types and values | The inventories, or a seed that builds them. |
| Error categories and how often each is applied | A rate, or a deterministic rule. “As needed” is not a rate. |
| Candidate count | An integer. |
| Provenance | `SYNTHETIC_PROXY` only, until a different project exists. |
| Role labels | If the four roles below are used, store the role name on the row. |
| Split | `evaluation` only, unless a training split is named and sealed away from this frozen 200. |
| Seed and version | Both written into the manifest. |

The four roles, if a future version uses them, mean:

| Role | Text |
| --- | --- |
| Candidate A | Unedited gold sentence, or a light edit that still contains the gold intent and the gold slot values. |
| Candidate B | A slot value substituted or removed. |
| Candidate C | The intent cue corrupted. |
| Candidate D | An ambiguous or incomplete transcript. |

`synthetic-seed17-v1` does not use this table. Creating that version is not authorized.

## Reproducibility

Cite seed 17, version `synthetic-seed17-v1`, and the frozen reports. Do not rerun `experiments/run_simulation.py`. A facade replay, after Phase 1D.7, writes elsewhere and hashes the frozen files before and after. Metric formulas stay those in `docs/PHASE_1D3_METRIC_DEFINITIONS.md`.
