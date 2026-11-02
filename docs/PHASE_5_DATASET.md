# Phase 5 dataset

Dataset id `synthetic-semantic-integrity-v1`. Seed `20261105`. Construction reads the frozen file `data/synthetic/annotations/annotations.jsonl` and does not rewrite it.

Eligible parents: 198. Excluded, because their required slot is empty: `utt-020`, `utt-040`.

Reminder and transfer parents were split first, then the remaining parents. Each group uses `random.Random(20261105)`. Test and validation are each `round(0.2 * group)`. Parent lists do not overlap: development 118, validation 40, test 40.

## Why there are 280 cases, not 300

There are 20 reminder parents and 20 transfer parents. Date, negation, uncertainty, condition, clean, and provenance categories use 30 cases. Time and amount use 20. The built set is 280 cases with no shortfall: development 168, validation 56, test 56.

| Category | Cases |
| --- | ---: |
| clean_affirmative | 30 |
| negation | 30 |
| uncertainty_maybe | 30 |
| uncertainty_possibly | 30 |
| uncertainty_might | 30 |
| conditional_if_needed | 30 |
| critical_date_mutation | 30 |
| critical_time_mutation | 20 |
| critical_amount_mutation | 20 |
| candidate_provenance_conflict | 30 |

Clean cases include a `Please` prefix on about one third of each split (test: 2 please, 4 unchanged). Provenance cases are split between a negated candidate plus the clean parent, and two candidates with different in-inventory values. The oracle expects RETRY of the clean id in the first kind and HOLD in the second.

## Labels

`challenge_cases.jsonl` and `candidate_bundles.jsonl` have no referent and no `expected_*` field. Labels are only in `oracle_labels.jsonl`.

Hashes:

- `challenge_cases.jsonl` `8fcc2eabfc7f7d115059f0425fb56f27c4108cfe9f52a601201ff1fd61d45fae`
- `oracle_labels.jsonl` `7ac4aa1abe6f4ba94b80823aaa2c49580013bf1fafb155ff6ba90cf024cdd05b`
- `splits.json` `708cc65b8036b239bb26523f44f1db59b87dd3cf4f8fa12def2f50b3f848f6d0`

## Parent coverage inside a split

The parent lists are disjoint, and every case uses a parent from its own list. Allocation still walks each category from the start of that list and stops at the quota, and a parent is used once per category. The test cases therefore sit on 14 of the 40 test parents. The same is true of validation: 14 of 40. This was not repaired after the results were known.

## Where the out-of-inventory edits landed

`April 3` occurs once, on development case `p5-critical_date_mutation-dev-11`. `181` occurs once, on validation case `p5-critical_amount_mutation-val-03`. The test split has neither. Development was not scored. The validation hold on `181` is reported as a validation observation, not as a test result.
