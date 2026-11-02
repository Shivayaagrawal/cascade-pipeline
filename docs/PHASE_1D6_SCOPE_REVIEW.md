# Phase 1D.6 scope review

**Date:** 2026-11-02  
**Communicated at:** 17:51 +05:30.  
**Status:** review prepared. The facade is not authorized.  
**Project:** Cascade Pipeline, a small synthetic simulation of transcript-error propagation and failure-aware semantic recovery.

## Definition

Cascade Pipeline studies how controlled transcript corruption changes intent and slot extraction, and whether multi-candidate selection and selective recovery reduce incorrect semantic commitments.

The research environment is synthetic, text-only, and controlled. The primary measurement is B0, B1, and B2 on reproducible written variants. The project is not a speech recognizer, a production SLU system, or a claim about real-world ASR.

Real audio recognition, production speech processing, and real-world ASR performance stay in the future-work section of `docs/PHASE_1D6_DECISION_REGISTER.md`. They are not unfinished tasks.

## What the blueprint already supported

The Phase 1D.5 plans already named the five execution identities, kept the two B2 controllers apart, kept RETRY as `simulated_candidate_rescore`, and refused to call proxy candidates N-best. Those parts match this scope. The metric definitions in `docs/PHASE_1D3_METRIC_DEFINITIONS.md` stay the scoring rules. Forced exact frame 145/200 is not selective coverage 145/200.

## What the blueprint treated as active dependencies

Before this review, several 1D.5 sections listed a decoder, LibriSpeech WER, SLURP, human listening, and operational RETRY as blocked stages on the way to a finished system. Under this scope those items are future work. The edits are in the blueprint, the blockers note, the execution sequence, the architecture introduction, the B0 plan, the test strategy, the readiness matrix, the risk-register introduction, and the component inventory.

LibriSpeech files and their historical documents stay in the repository. The simulation does not read them.

## Active components

Reuse `run_b0`, `run_b1`, `run_b2`, `forced_selection`, `recovery_action`, the existing metric functions, and the seed-17 proxy lists. Identities: `b0_prefix`, `b1_prefix`, `b2_prefix_controller`, `b1_forced_lexical`, `b2_lexical_v3`.

CLARIFY is stored as an action. No clarification question is required. HOLD does not commit a frame. An empty bundle, at the future facade only, is HOLD with reason `EMPTY_BUNDLE`.

## Frozen evidence that stays cited

On the v1 list, seed 17: coverage 145/200, correct commits 142/200, unsafe commits 3/145, abstentions 55/200, recovery gain 0.71, forced exact frame 145/200. The unsafe ids are `utt-121`, `utt-124`, and `utt-129`.

## Review result

The blueprint can describe the synthetic project after the edits above. Implementation is a separate decision, reserved for Phase 1D.7. This review does not start Phase 1E-S, Phase 1F-S, or Phase 2.
