# synthetic-semantic-challenge-v1

This is a new text challenge set. It is not `synthetic-seed17-v1` and it does not replace it.

The 240 rows are controlled edits of eligible parents from the frozen 200-utterance manifest. Expected labels come from the transformation operators in `transformation_metadata.json`. They are not human labels and not the Phase 2 LLM annotations.

Parents are split with seed `20261103` before cases are drawn. Every case from one parent stays in that parent's split. `utt-020` and `utt-040` are excluded because their gold slot maps are empty while `cancel_appointment` and `check_appointment` still require `date`.

| Split | Parents | Cases |
| --- | ---: | ---: |
| Development | 138 | 168 |
| Validation | 30 | 32 |
| Test | 30 | 40 |

Each of the eight categories has 30 cases: 21 development, 4 validation, and 5 test. The test split was not used to choose risk weights.
