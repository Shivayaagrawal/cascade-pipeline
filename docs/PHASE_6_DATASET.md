# Phase 6 dataset

Dataset `synthetic-reference-integrity-v1`. Seed `20261106`. Parents are read from `data/synthetic/annotations/annotations.jsonl` and are not rewritten. Eligible parents: 198. Excluded: `utt-020`, `utt-040`.

Before any score was computed, three parents were placed in the test list: `utt-097` (amount 180), `utt-013` (April 2), and `utt-121` (7 AM). Every parent is in exactly one split: development 117, validation 39, test 42. The lists do not overlap.

Built cases: 184. Development is short one time row and one amount row because those quotas assumed 20 parents and one parent from each group had already been reserved for test. No extra parents were created.

| Category | Cases |
| --- | ---: |
| clean_affirmative | 24 |
| clean_polite_instruction | 12 |
| negation | 24 |
| uncertainty | 24 |
| conditionality | 12 |
| date_substitution | 16 |
| time_substitution | 19 |
| amount_substitution | 19 |
| candidate_provenance_conflict | 16 |
| ambiguous_candidate_bundle | 12 |
| parent_transcript_cue | 6 |

A multiple-critical-slot category was not built. `transfer_money` is the only intent with two required slots, and the second slot is always `rupees`.

`181` is not a parent value. The test row for `utt-097` substitutes it. `April 3` is not a parent value. The test row for `utt-013` substitutes it. `utt-121` becomes 8 AM. The 6 PM parent becomes 5 PM on a validation row, `utt-120`, because that parent was not one of the three preassigned test ids.

Test cases: 36, on 14 of the 42 test parents. The allocator uses each parent once per category and stops at the quota, so most test parents receive no row. That limit is recorded, not repaired after the scores.

Hashes:

- `challenge_cases.jsonl` `dd6dd7946c7231b80d92d19c65a0aa767f08a11723c543d496363ddb35d38580`
- `reference_signals.jsonl` `ab074b8c7499dc55c27c09e091bf49203093d148057d5d730f178ce4d28cd0aa`
- `oracle_labels.jsonl` `a38b0117716b097afc0567ab9d1651bced9254b7e2aefb839ec903768409dff5`
- `splits.json` `3d9ff8f0eb725107788ec020cab3f8f1056beffb2bdda6bc16de261976e8245d`

The challenge file has no referent and no expected action. References and labels are separate files. The labels are a specification written in the same session as the checker. They are not human gold.
