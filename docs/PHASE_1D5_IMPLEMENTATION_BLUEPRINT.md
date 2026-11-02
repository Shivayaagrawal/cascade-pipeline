# Phase 1D.5 implementation blueprint

**Date:** 2026-11-02  
**Scope revision:** 2026-11-02, 17:51 +05:30. The current project is a synthetic, text-only simulation. Real audio, a recognizer, and a task corpus are future work. They are not unfinished requirements for this simulation.  
**Status:** planning. No component was implemented.  
**Approved methodology:** `docs/PHASE_1D4_APPROVAL_RECORD.md`. This file does not extend that approval to code. The scope review is `docs/PHASE_1D6_SCOPE_REVIEW.md`.

## What would be built, after a separate authorization

A facade that records the contracts in `docs/PHASE_1D5_INTERFACE_CONTRACTS.md` and calls the functions that already implement B0, B1, and B2. It writes only to a new directory. It does not add a parser, a selector, a threshold, or a recognizer.

The layer map is `docs/PHASE_1D5_ARCHITECTURE.md`. The inventory of what already runs is `docs/PHASE_1D5_COMPONENT_INVENTORY.md`.

```text
Transcript input
  single transcript or a candidate bundle
  provenance stays on the record
        |
        +-- prefix reader ---- b0_prefix
        |                  \-- b1_prefix
        |                  \-- b2_prefix_controller
        |
        +-- lexical reader --- b1_forced_lexical
                           \-- b2_lexical_v3
                                    |
                                    CONTINUE / RETRY / CLARIFY / HOLD
                                    RETRY is simulated_candidate_rescore
        |
Evaluation record
  intent, slots, exact frame, coverage, risk, derived action
```

## What already exists

The prefix runner, the lexical selector, both controllers, the metric functions, the proxy lists, and the tests named in `docs/PHASE_1D5_TEST_STRATEGY.md`. Frozen headline counts, v1 list, seed 17: selective coverage 145/200, correct commits 142/200, unsafe commits 3/145, abstentions 55/200, recovery gain 0.71. Forced exact frame on that list is also 145/200 and is a different measurement from coverage.

## What the current simulation still does not have, as code

The unified record facade. It waits for a separate implementation authorization. CLARIFY is recorded as an action. A clarification question is not required. Negation and uncertainty stay unavailable in the current readers. That is a limitation of this simulation, not a reason to add a recognizer.

Real decoding, genuine N-best lists, operational RETRY, task-speech gold, and human audio annotation are future work. They are listed in `docs/PHASE_1D6_SCOPE_REVIEW.md` and are not dependencies of the synthetic project.

## Plans

| System | Document |
| --- | --- |
| B0 | `docs/PHASE_1D5_B0_IMPLEMENTATION_PLAN.md` |
| B1 | `docs/PHASE_1D5_B1_IMPLEMENTATION_PLAN.md` |
| B2 | `docs/PHASE_1D5_B2_IMPLEMENTATION_PLAN.md` |
| Tests | `docs/PHASE_1D5_TEST_STRATEGY.md` |
| Order | `docs/PHASE_1D5_EXECUTION_SEQUENCE.md` |
| Risks | `docs/PHASE_1D5_RISK_REGISTER.md` |
| Readiness | `docs/PHASE_1D5_READINESS_MATRIX.md` |
| Decisions still required | `docs/PHASE_1D5_BLOCKERS.md` |

## Evidence that a future implementation is correct

The frozen hashes still match. New rows name the reader and the controller. Selective risk uses the commit denominator. The three unsafe ids remain unsafe only as commits. Abstention is not unsafe. Proxy provenance is not `native_nbest`. A RETRY row says `simulated_candidate_rescore`. An operational decode is outside this project.

## Stop

Phase 1D.6 prepares the synthetic-only review. Phase 1D.7 is where implementation authorization would be recorded. The facade is not authorized. Phase 2 does not start.
