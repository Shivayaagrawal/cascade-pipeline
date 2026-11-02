# Phase 4 limitations

The study is synthetic text. It does not measure speech, ASR N-best lists, or a deployed system.

The oracle and the controller were specified in the same session. The oracle does not call the controller, and the controller fails rules the oracle states and v4 does not implement. That is stronger evidence than Phase 3's action accuracy. It is still not an independent human gold set.

Test cases sit on 20 of the 40 parents assigned to the test split. Several variants of one parent remain together, which the bootstrap respects, and the parent sample is smaller than the split list suggests. Intervals on 10 cases in one category are wide. A null per-commit rate means the system did not commit, not that the unsafe rate is zero.

The selection rule minimizes unsafe commits first. On this grid that choice is threshold 0, which holds every scored continue. It is a visible tradeoff and a poor answer to the coverage question. Weights other than the threshold do not separate the 280 cells that still make 27 unsafe commits.

A4, A5, and A6 do not move the test outcomes. A4 is absent from v4. A5 and A6 are not shown to be useless; these bundles do not give them a separate decision to make.

## Proposal, not a new controller

`b2_semantic_v5` was not built. The failures that repeat on validation and test, and that the ablations do not remove, are:

1. A substituted lexicon value, such as a different amount or date, is committed as a normal frame.
2. `about`, `after`, `before`, and `instead` still produce the referent frame and are committed.
3. `Possibly`, `might`, and `If needed` are committed. `Maybe` is held.
4. The controller still does not emit the candidate id it committed. The harness reconstructs it.

A later controller would have to be a separate strategy, scored on this same frozen oracle, without retuning on the test split.
