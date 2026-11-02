# Phase 1D.5 blockers

**PHASE 1D.5 BLUEPRINT WRITTEN. SCOPE REVISED TO SYNTHETIC-ONLY IN PHASE 1D.6. IMPLEMENTATION NOT AUTHORIZED. PHASE 2 NOT STARTED.**

The decisions below are the state before the 2026-11-02 scope revision. The current record is `docs/PHASE_1D6_DECISION_REGISTER.md`. Real-speech acquisition is not an active blocker for the simulation.

No source file was edited. No experiment ran. No dataset was downloaded. No archive was extracted. The pilot CSV and the frozen outputs were not modified. `test-clean` was not opened.

## Decisions required before any implementation

A later phase may write code only after the user records each of these. Phase 1D.6 can accept or revise the blueprint. Acceptance of the blueprint is not these decisions.

| ID | Decision | Default if unanswered |
| --- | --- | --- |
| D1 | Build a dataset-independent facade around the existing synthetic functions first, or wait until a task corpus and a decoder are authorized. | Wait. This blueprint does not choose. |
| D2 | Any new code lives in a new directory and calls `run_b0`, `run_b1`, `run_b2`, `forced_selection`, and `recovery_action` without changing their signatures or the frozen outputs. | Required if D1 chooses the facade. Editing those functions is not offered. |
| D3 | `b2_prefix_controller` and `b2_lexical_v3` stay separate systems in every table and log. | Required. Pooling is already forbidden. |
| D4 | The facade’s empty-bundle behavior is specified without changing the current functions, which raise or return HOLD depending on the function. | Unspecified. Stage 1 stays closed. |
| D5 | No new selector, and no change to prefix confidence or to `min_support`. | Required. |
| D6 | Implementation authorization is a separate sentence from Phase 1D.6 blueprint approval, from Phase 1E, and from Phase 2. | This document is not that sentence. |

## Speech items

Those items are future work. They are not required to define or, later, to run the synthetic simulation. LibriSpeech files stay on disk as historical assets.

## Next phase

Phase 1D.6 is the synthetic-only scope review. It does not implement the facade.
