# Phase 1D.5 execution sequence

**Date:** 2026-11-02  
**Status:** a future order. No stage was started.  
**Authorization:** Stages 1–11 are the synthetic simulation. They start only after Phase 1D.7 records implementation authorization. Stages 12 and 13 are future work. They are not required to finish this project.

| Stage | Dependencies | Deliverable | Tests | Exit | Blocked when |
| --- | --- | --- | --- | --- | --- |
| 1. Contract validation | This blueprint accepted. Phase 1D.7 authorizes the facade. | New module that only constructs the records in `docs/PHASE_1D5_INTERFACE_CONTRACTS.md` and calls existing functions. New output directory. Empty bundle returns HOLD / `EMPTY_BUNDLE` without calling the old functions. | Unit tests that reject `native_nbest` on proxy text and reject an empty provenance. | Records round-trip for one synthetic id without writing under `experiments/B0`, `B1`, `B2`, `sim-eval-v2`, `sim-eval-v3`, or `sim-eval-v3b`. | Phase 1D.7 has not authorized implementation. |
| 2. B0 integration | Stage 1. | Facade calls `run_b0` on rank 0. | Existing `test_nlu_and_pipeline.py` still passes. | Output reader is `prefix-cues`. Gold is not an argument. | A change inside `run_b0` is proposed. That is out of scope. |
| 3. B0 regression | Stage 2. | Hash comparison. | Frozen B0 hash unchanged. | Hash matches the manifest. | Any byte change in `experiments/B0/summary.json`. |
| 4. B1 candidate ingestion | Stage 1. | Bundle builder sets `SYNTHETIC_PROXY` and the generation method. | Provenance test. | v1, paraphrase, slot-removed, and split bundles do not contain the gold sentence. | A new generator or a new seed is proposed. |
| 5. B1 comparison | Stage 4. | Records for `select_candidate` and `forced_selection` on the same bundle. | Both records stored. | The report names the reader on each row. | A new selector is proposed. |
| 6. B1 regression | Stage 5. | Hash comparison for B1 and the v3 report. | Existing v3 tests. | Forced exact frame remains the frozen 145/200 citation, not a recomputed headline. | The facade reruns `experiments/run_simulation.py` or `run_simulation_v3.py`. |
| 7. B2 diagnosis | Stages 2 and 5. | Failure records from each controller, untranslated. | Reason strings match the function that ran. | Prefix kinds and lexical reasons are separate columns. | One combined failure enum is proposed. |
| 8. B2 controllers | Stage 7. | Facade calls `decide` and `recovery_action` separately. | Action tests already in the tree. | RETRY from the lexical path carries `simulated_candidate_rescore` or is absent. | A second decode is wired in. |
| 9. B2 safety tests | Stage 8. | Evaluation records for the three known unsafe ids and for one abstention. | `unsafe_decision` true only on the mismatched commits. | Abstention is not unsafe. Risk denominator is the commit count. | Thresholds are fit to the 200 ids. |
| 10. Evaluation pipeline | Stage 9. | One report that cites frozen numbers and, if new rows are produced, marks them as a facade replay. | Metric tests. Denominator of zero stays null. | No pooled controller table. | A metric formula changes. |
| 11. Reproducibility | Stage 10. | Config hash, seed 17, environment note, before-and-after manifest. | `python3 -m pytest -q`. | The preservation hashes match. Frozen synthetic files unchanged. | The run writes inside an immutable directory. |

Stages 1 through 11 are the synthetic project. They still do not start until Phase 1D.7 authorizes implementation.

## Future work, not part of this project

| Stage | What it was | Current status |
| --- | --- | --- |
| 12. Real ASR | A `dev-clean` decode and WER | Out of scope. Not a missing stage of the simulation. |
| 13. Task-speech evaluation | An authorized task corpus | Out of scope. The adapter note in `docs/PHASE_1D2_DATASET_ADAPTER_SPEC.md` stays a historical specification. |
