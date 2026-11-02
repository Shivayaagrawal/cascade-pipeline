# Phase 1D.7 final scope

**Date:** 2026-11-02  
**Communicated at:** 18:04 +05:30.  
**Status:** scope recorded. The synthetic facade is not authorized.

Cascade Pipeline is a synthetic, text-only simulation. It studies how controlled transcript edits change intent decisions and slot extraction, whether five named strategies change those decisions, whether selective recovery reduces incorrect commitments, and what coverage that selectivity costs.

It is not a speech recognizer, a real ASR system, a production SLU system, a conversational benchmark, a real-world robustness study, or a production recovery controller. Claims stay inside `synthetic-seed17-v1`.

## What remains inside Phase 1

| Work | Kind | State |
| --- | --- | --- |
| Scope, contracts, metrics, test plan, and the authorization record | Documentation | Prepared in this phase. Ready for review. |
| Facade over the five existing identities | Implementation | Not authorized. |
| Reproducible evaluation report through that facade | Implementation, then a report | Not started. |
| Real speech, SLURP, human listening, a decoder | Outside this project | Not a remaining Phase 1 task. |

Phase 1 is not complete. Planning can be reviewed. The simulation code for the facade has not been written.

## Active pieces

The project reuses `run_b0`, `run_b1`, `run_b2`, `forced_selection`, `recovery_action`, the metric functions, and the seed-17 proxy lists. The identities `b0_prefix`, `b1_prefix`, `b2_prefix_controller`, `b1_forced_lexical`, and `b2_lexical_v3` stay separate. Prefix confidence and `min_support` stay as they are. No new selector is added. Frozen functions and frozen outputs stay unchanged.

Lexical RETRY is `simulated_candidate_rescore`. CLARIFY is an action label. HOLD commits no frame.

## Dataset

`synthetic-seed17-v1` is 200 gold utterances, 10 intents, 20 each, and 600 `synthetic_edit` rows. All 200 ids are the evaluation set. There is no train split and no development split. The count of the eight category labels in `data/synthetic/transcripts/variants.csv` is 75 each. That is a balanced label count. It is not a claim about severity or about speech. The 600 rows are not Candidate A–D. No new dataset version is authorized.

The manifest column `audio_path` points at existing `say` fixtures. Scoring does not decode them. No new audio file is part of this project.

## Empty bundle

Only a future facade returns HOLD / `EMPTY_BUNDLE` and calls no processing function. `select_candidate` and `forced_selection` still raise on empty input. `decide_selective([])` still returns HOLD / `no_intent_evidence`.

## Out of scope

Real decoding, recognizer integration, genuine N-best lists, a second decode, speech WER/CER, human audio annotation, conversational generalization, production deployment, SLURP, and any new real corpus. LibriSpeech remains a historical asset and is not an input to this dataset.
