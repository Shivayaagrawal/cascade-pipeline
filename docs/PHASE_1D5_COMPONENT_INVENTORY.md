# Phase 1D.5 component inventory

**Date:** 2026-11-02  
**Method:** source inspection. A filename was not treated as a feature.  
**Code changes:** none.

Statuses: `EXISTING_AND_REUSABLE`, `EXISTING_BUT_REQUIRES_ADAPTATION`, `MISSING`, `BLOCKED_BY_DATA`, `RESEARCH_ONLY`, `OUT_OF_CURRENT_SCOPE`.

`OUT_OF_CURRENT_SCOPE` means the files may stay in the repository. The synthetic simulation does not depend on them.

Historical plans in `docs/IMPLEMENTATION_PLAN.md` and `docs/PHASE_1_IMPLEMENTATION_PLAN.md` are not this blueprint. The Phase 1 plan still says ASR, NLU, and B0/B1/B2 on LibriSpeech audio are not authorized.

| Component | Existing file/module | Responsibility | Current status | Planned action |
| --- | --- | --- | --- | --- |
| Synthetic utterance gold | `simulation/utterance_generator.py`, `data/schemas/intent_schema.json` | 10 intents, seed 17, ids `utt-000`–`utt-199` | EXISTING_AND_REUSABLE | Keep as Track A gold. Do not map SLURP labels onto it. |
| Proxy candidate writer | `simulation/error_injector.py`, `simulation/candidate_diversity.py` | Written edits, paraphrases, slot-removed and split lists. Gold sentence excluded. | EXISTING_AND_REUSABLE | Cite. Do not generate a new set in a later implementation unless a new seed and new ids are authorized. |
| Hypothesis type | `asr/base.py` `Hypothesis`, `ASRResult` | Text, provenance, rank. | EXISTING_AND_REUSABLE | The future `TranscriptInput` is a document contract around this type, not a new class in this phase. |
| Synthetic ASR backend | `SyntheticHypothesisASR.transcribe_id` | Returns prewritten hypotheses. `transcribe(audio_path)` raises `NotImplementedError`. | EXISTING_AND_REUSABLE | Keep waveform decode unimplemented on this class. |
| Whisper adapter | `asr/whisper_adapter.py` | Optional `faster_whisper` call, `beam_size=1`, provenance `single_segment_text`. | OUT_OF_CURRENT_SCOPE | Historical code. The simulation does not call it. |
| Prefix intent cues | `nlu/intent_classifier.py` | Closed substring cues. Ambiguous when two cues match. | EXISTING_AND_REUSABLE | B0 and prefix B1/B2 only. |
| Prefix slots | `nlu/slot_extractor.py` | Template prefixes. Missing slots stay missing. | EXISTING_AND_REUSABLE | Same reader family as the prefix intent cues. |
| Prefix score and select | `candidates/candidate_manager.py` | Confidence 0, 0.5, or 1. Select by confidence, then earlier rank. | EXISTING_AND_REUSABLE | Do not retune. See the empty-list note below. |
| Prefix B0/B1/B2 runners | `pipeline.py` `run_b0`, `run_b1`, `run_b2` | One utterance, no gold input. | EXISTING_AND_REUSABLE | Frozen behavior. A later facade calls them. It does not rewrite them. |
| Prefix recovery | `recovery/failure_detector.py`, `recovery/recovery_controller.py` | `none`, `ambiguous`, `unknown`, `low_confidence`. Actions CONTINUE, RETRY, CLARIFY, HOLD. | EXISTING_AND_REUSABLE | Separate from the v3 layer. `max_retries` default 1 was not tuned in v3. |
| Lexical evidence | `evaluation/semantic_evidence.py` | Intent cues plus lexicon values. `CRITICAL_SLOTS` per intent. | EXISTING_AND_REUSABLE | Negation and uncertainty are not returned. |
| Forced lexical selector | `selective.forced_selection` | Always one frame. Not a safety decision. | EXISTING_AND_REUSABLE | Report as `b1_forced_lexical`. Do not add another selector. |
| Selective commit | `selective.decide_selective` | Commit, clarify, or hold from support. `min_support` default 1. | EXISTING_AND_REUSABLE | The curve at 1, 2, and 3 stays the result. |
| v3 recovery | `selective.recovery_action` | CONTINUE, or RETRY only with a second bundle, else CLARIFY or HOLD. | EXISTING_AND_REUSABLE | Mechanism `simulated_candidate_rescore` only. |
| Metrics | `intent_metrics.py`, `slot_metrics.py`, `wer.py`, `cer.py`, `v3_metrics.py`, `rates.py` | Approved formulas. | EXISTING_AND_REUSABLE | Do not change denominators. |
| Text normalization | `evaluation/textnorm.py` | NFC, casefold, collapsed whitespace, punctuation kept. Used by WER and CER. | EXISTING_AND_REUSABLE | Do not run it before the parsers. It is an evaluation normalizer. |
| Latency summary | `evaluation/latency_stats.py`, `v3b_audit.lexical_timing` | Wall time of named calls. | EXISTING_AND_REUSABLE | `asr_latency` stays false until a decode exists. |
| v3b audit | `evaluation/v3b_audit.py`, `experiments/run_simulation_v3b.py` | Reads v3 and writes only `sim-eval-v3b`. | EXISTING_AND_REUSABLE | Do not point it at another directory. |
| LibriSpeech prep | `dataset/librispeech.py`, `sampling.py`, `acquisition.py` | Historical audio and transcripts. | OUT_OF_CURRENT_SCOPE | Retain the files and the docs. Do not use them as simulation inputs. |
| Phase 1C annotation | `src/annotation/` | Pilot UI and validator. | OUT_OF_CURRENT_SCOPE | Human listening is not required for this simulation. Do not auto-fill the pilot. |
| Spoken-audio preprocessing | none beyond `simulation/audio_generator.py` (`say` to AIFF) | Not an ASR front end. | RESEARCH_ONLY | Do not treat AIFF generation as preprocessing for a recognizer. |
| Unified record types | none | The seven conceptual schemas in `docs/PHASE_1D5_INTERFACE_CONTRACTS.md`. | MISSING | Documentation only until implementation is authorized. |
| Genuine N-best ingest | none | Would require a recognizer list. | OUT_OF_CURRENT_SCOPE | Provenance `native_nbest` stays rejected on the synthetic path. |
| Operational RETRY | none | A second `transcribe` call. | OUT_OF_CURRENT_SCOPE | The simulation RETRY is only `simulated_candidate_rescore`. |
| Human recovery labels | none | Gold CONTINUE, RETRY, CLARIFY, HOLD from a person. | OUT_OF_CURRENT_SCOPE | The active label is the derived `expected_recovery` rule. |
| Task-speech adapter | specified in `docs/PHASE_1D2_DATASET_ADAPTER_SPEC.md` | A future corpus. | OUT_OF_CURRENT_SCOPE | Historical specification. No acquisition in this project. |

## Observations that a later phase must not “clean up” silently

`select_candidate` raises `ValueError` on an empty tuple. `forced_selection` raises on an empty list. `decide_selective` on an empty list returns HOLD with reason `no_intent_evidence`. Those are different behaviors. A future facade has to record which function it called. Changing any of them is an implementation change and is not approved.

`select_candidate` skips a `native_nbest` item with `continue`, then contains a branch that cannot run for that provenance. `run_b0`, `run_b1`, and `run_b2` already reject `native_nbest` through `assert_synthetic_not_nbest`. The skip does not create an N-best path.

`run_b2` copies `decision.selected` intent and slots into `SystemOutput` for every action, including CLARIFY and HOLD. The action string is what marks a commit. A record that drops the action would look like a committed frame.

Two `RecoveryAction` enums exist, one in `recovery_controller.py` and one in `selective.py`. The string values match. The types are not one controller.

`WhisperAdapter` does not subclass `ASRBackend`. It has not been called.
