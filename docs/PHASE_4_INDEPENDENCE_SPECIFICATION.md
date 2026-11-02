# Phase 4 independence specification

## Two specifications

Specification A, `phase4-construction-v1`, decides which strings to put in a bundle. It inserts `not`, adds `Maybe` / `Possibly` / `I might` / `If needed`, replaces a slot value, deletes a slot value, appends a second request, or changes a linking word. It does not choose the recovery action.

Specification B, `phase4-oracle-v1`, reads the finished strings and the scenario referent. The referent is the parent gold frame from `synthetic-seed17-v1`. The oracle decides polarity, modality, completeness, ambiguity, contradiction, the safe candidate ids, the action, and whether a commit is allowed.

## What is not shared

`independent_oracle.py` does not import `cascadeguard_facade` or `cascadeguard.evaluation`. `semantic_controller_v4.py`, `commit_policy_v4.py`, and `risk_assessment_v4.py` do not import `cascadeguard_phase4`.

Candidate bundles do not contain expected actions, expected slots, or the referent. Those live in `oracle_labels.jsonl` and `scenario_referents.jsonl`. The runner builds a `CandidateBundle` from the bundle file alone.

## What is still shared

Both the oracle and the frozen grammar recognize the same ten intents, because there is one closed grammar. Duplicating the cue list in a second file would not create a second language. The oracle's additional rules are the ones v4 does not implement: `possibly`, `might`, and `if`; hedges `about`, `around`, `roughly`, `after`, `before`, and `instead`; required function tokens such as `my`, `for`, `at`, and `your`; and the rule that a candidate is safe only when its frame equals the referent and no other affirmative frame disagrees.

Hand-written fixtures in `tests/phase4/test_oracle.py` are not emitted by the dataset builder. `please` is not uncertainty. Weather `it` is not context. `cancel` is not a negated booking.

## Limit of this independence

The same implementation session wrote Specification B and already knew the v4 gates. The labels were not written by a separate annotator. Independence here means a frozen, non-imported outcome function plus cases that function marks unsafe and v4 still commits. It does not mean a blinded human gold set.
