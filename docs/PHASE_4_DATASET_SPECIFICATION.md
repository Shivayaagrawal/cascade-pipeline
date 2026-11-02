# Phase 4 dataset specification

`synthetic-independent-challenge-v1` has 600 cases. There was no shortfall. Seed `20261104`.

Eligible parents are the 198 gold utterances whose required slots are present in the text. `utt-020` (`Cancel my appointment`) and `utt-040` (`When is my appointment?`) are excluded because the schema requires a date. An empty slot map is not, by itself, the reason.

| Category | Cases |
| --- | ---: |
| Negation and polarity | 50 |
| Uncertainty and modality | 50 |
| Critical slot mutation | 50 |
| Temporal and numerical conflict | 50 |
| Semantic ambiguity | 50 |
| Contradictory candidates | 50 |
| Incomplete required slots | 50 |
| Context dependency | 50 |
| Function-word damage | 50 |
| Candidate provenance | 50 |
| Clean controls | 100 |

Uncertainty cycles through `Maybe`, `Possibly`, `I might`, and `If needed`. Provenance is 44 negated-plus-referent pairs and 6 empty bundles. Clean controls are 70 unmodified strings, 20 agreeing copies, and 10 `Please` prefixes.

Parents were shuffled and split 118 / 40 / 40. No parent id appears in two splits. Case targets are 360 / 120 / 120, with 30 or 10 failure cases and 60 or 20 clean cases.

Allocation walks each split's parent list from the start for every category and does not reuse a parent inside one category. In the test split, 20 of the 40 assigned parents received every case. The other 20 test parents have no cases. That is recorded as a limitation. The dataset was not rebuilt after the test results were known.

Bundles SHA-256 `593a00c6dd96a4c81dc4ad6b47901123ae89582a625cba2c9ee117674a832e3d`. Oracle SHA-256 `7770ceb1afda6c1889d2273b42a6090dae4ace4363eb89388eea815d3ad0adde`.

Currency remains `rupees`. No unsupported intent was added.
