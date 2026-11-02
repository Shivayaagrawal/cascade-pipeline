# Phase 1D.7 implementation sequence

**Date:** 2026-11-02  
**Status:** a sequence that does not start.  
**Authorization:** every step requires a separate implementation grant. Blueprint review does not grant it. Phase 1D.7 does not grant it.

The output directory for any of these steps must be new. It must not be `experiments/B0`, `B1`, `B2`, `sim-eval-v2`, `sim-eval-v3`, or `sim-eval-v3b`.

| Step | Inputs | Output | Depends on | Acceptance | Risk | Authorization |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Isolated directory | This plan, a directory name that is not frozen. | Empty package. | None. | Imports nothing from a frozen writer. | Writing into `experiments/`. | Required. Not granted. |
| 2. Executable contracts | `docs/PHASE_1D7_INTERFACE_CONTRACTS.md`. | Types only. | Step 1. | Fields match the contract. No `GENUINE_ASR_NBEST` value. | Inventing a sixth strategy. | Required. Not granted. |
| 3. Input validation | Types, the 200 ids. | Reject rules. | Step 2. | Bad provenance and bad strategy fail. Empty bundle does not call a processor. | Calling `decide_selective([])` and labeling it `EMPTY_BUNDLE`. | Required. Not granted. |
| 4. B0 adapter | `run_b0`. | `b0_prefix` records. | Step 3. | One transcript. Gold not an argument. | Running `normalize()` first. | Required. Not granted. |
| 5. B1 prefix adapter | `run_b1`. | `b1_prefix` records. | Step 3. | Confidence-then-rank unchanged. | Pooling with lexical rows. | Required. Not granted. |
| 6. B1 lexical adapter | `forced_selection`. | `b1_forced_lexical` records. | Step 3. | Always a frame attempt. Not labeled coverage. | Treating 145/200 as the same measure as coverage. | Required. Not granted. |
| 7. B2 prefix adapter | `run_b2`. | `b2_prefix_controller` records. | Step 3. | CLARIFY and HOLD have null committed frames. | Dropping `action` and keeping the attached text as a commit. | Required. Not granted. |
| 8. B2 lexical adapter | `recovery_action`. | `b2_lexical_v3` records. | Step 3. | RETRY mechanism string exact. `min_support` unchanged. | A second decode. | Required. Not granted. |
| 9. Decision normalization | Steps 4–8. | One record shape, five identities. | Those steps. | Identity field required. | One combined B2 column. | Required. Not granted. |
| 10. Audit records | Normalized decisions. | One row per id per identity. | Step 9. | Raw prefix attachment stored separately from the committed frame. | Question text invented for CLARIFY. | Required. Not granted. |
| 11. Evaluation | Gold manifest, metric functions. | Rates with numerators. | Step 10. | Undefined risk stays null. Derived actions labeled derived. | A new denominator. | Required. Not granted. |
| 12. Facade unit tests | `docs/PHASE_1D7_TEST_STRATEGY.md`. | New tests. | Steps 3–11. | The fourteen rows in that plan. | Editing tests under `tests/` that guard frozen hashes, instead of adding facade tests. | Required. Not granted. |
| 13. Regression | Existing suite plus facade tests. | A recorded command and result. | Step 12. | Frozen files unchanged. | Calling `run_simulation.py`. | Required. Not granted. |
| 14. Hash verification | Preservation list. | Before and after hashes. | Step 13. | Match, or the run stops. | Claiming a match without computing it. | Required. Not granted. |
| 15. Simulation report | The new directory. | A report that cites frozen figures and marks any replay as a replay. | Step 14. | Five identities, separate tables. | A speech sentence. | Required. Not granted. |

Steps 12–15 are still implementation. They are not this documentation phase.
