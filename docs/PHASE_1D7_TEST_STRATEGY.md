# Phase 1D.7 test strategy

**Date:** 2026-11-02  
**Status:** a plan for tests that do not exist yet. None of them were written or run.  
**Existing suite:** 11 files under `tests/`. This phase did not execute them, so it does not report a pass count.

When a facade is authorized, its tests live with the facade and use temporary directories. They do not rewrite `experiments/B0`, `B1`, `B2`, `sim-eval-v2`, `sim-eval-v3`, or `sim-eval-v3b`.

| # | Future test | Pass condition |
| --- | --- | --- |
| 1 | One adapter test per identity | The recorded call is the existing function for that identity, and the other four are not called. |
| 2 | Empty bundle | HOLD, reason `EMPTY_BUNDLE`, null committed frame, and none of `select_candidate`, `forced_selection`, `decide_selective`, `run_b0`, `run_b1`, or `run_b2` is called. |
| 3 | Invalid provenance | `native_nbest` on a proxy row is rejected. The existing reject path is not edited. |
| 4 | Invalid strategy | A sixth name is rejected. |
| 5 | Invalid frame | A CONTINUE record with a null committed frame fails validation. A HOLD record with a committed frame fails validation. |
| 6 | CONTINUE | Prefix failure `none`, and lexical COMMIT, each store a committed frame and the right identity. |
| 7 | RETRY | Lexical RETRY stores `simulated_candidate_rescore`. Prefix RETRY does not use that string. A retry whose frame mismatches gold is not marked correct. |
| 8 | CLARIFY | Committed frame is null. No question field is required. Prefix raw attachment is not the committed frame. |
| 9 | HOLD | Committed frame is null. `EMPTY_BUNDLE` and `no_intent_evidence` stay different reasons. |
| 10 | Metrics | A zero commit set leaves selective risk undefined. Abstention is not an unsafe commit. Forced exact frame is not written into the coverage field. |
| 11 | Determinism | Same ids, seed 17, and `min_support` produce the same actions on two facade calls in one process. |
| 12 | Frozen behavior | Existing tests still import the unchanged functions. The facade tests do not monkeypatch those functions to hide `EMPTY_BUNDLE`. |
| 13 | Hashes | Before and after, the preservation list in `docs/PHASE_1D3_REPRODUCIBILITY_PROTOCOL.md` matches. A mismatch fails the run. |
| 14 | Five identities | Each identity has at least one test that would fail if its record were relabeled as another identity. |

The existing tests already cover the functions the adapters would call, including empty-reference WER, undefined rates, native-nbest rejection, and the v3b log’s agreement with the frozen aggregate. Those tests are not a substitute for the facade tests, and they were not rerun for this document.
