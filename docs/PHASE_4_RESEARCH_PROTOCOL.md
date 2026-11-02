# Phase 4 research protocol

Dataset `synthetic-independent-challenge-v1`. Seed `20261104`. Oracle `phase4-oracle-v1`. Construction `phase4-construction-v1`.

## Question

Can the existing failure-aware controller avoid unsafe commitments, and select the permitted candidate, when the expected labels are produced by a specification that the controller does not import?

This is a text-only synthetic study. It does not estimate speech recognition accuracy, genuine ASR N-best behavior, or production reliability.

## Hypotheses

Scored on the unmodified Phase 3 weights and threshold 0.25. A parent-cluster bootstrap difference is supported only when the 95% interval lies entirely on the predicted side of zero. Otherwise it is inconclusive or contradicted.

| ID | Claim | Result rule |
| --- | --- | --- |
| H1 | E7 has a lower per-case unsafe-commit rate than E0, E1, and E2. | Interval for E7 minus baseline below zero. |
| H2 | E7 has higher path safety. | Reported as safe commits per case and, separately, as safe commits over commits. |
| H3 | Polarity handling reduces unsafe negative commits. | Negation category. |
| H4 | Critical-slot checks reduce unsafe value changes. | Slot-mutation category. |
| H5 | Provenance cases do not produce an invalid retry. | Candidate id in the bundle and in the safe set. |
| H6 | The safety change is not free in coverage. | Coverage difference against E0 and E4. |
| H7 | Clean controls are still committed. | Clean-control coverage. |

## What is frozen before the test split is read

The hypothesis configuration is the Phase 3 weight vector and threshold 0.25. The 350-cell grid is scored on validation only. Its winner is frozen in `experiments/phase4/frozen_policy.json` before `_load("test")` runs. Hypotheses use the Phase 3 configuration. The grid winner is a sensitivity run, not a replacement decided after the test.

No `b2_semantic_v5` is part of this protocol.
