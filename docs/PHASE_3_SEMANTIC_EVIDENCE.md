# Phase 3 semantic evidence

`assess()` is unchanged. It still returns intent hits and lexicon slot values.

`assess_v4()` in `src/cascadeguard_facade/semantic_evidence_v4.py` calls `assess()` and adds fields. Gold is not an argument.

| Field | States used |
| --- | --- |
| Polarity | `negative` if the token `not` is present. `affirmative` if an intent is present and `not` is absent. Otherwise `unknown`. |
| Modality | `uncertain` if the token `maybe` is present. `certain` if an intent is present and `maybe` is absent. Otherwise `unknown`. |
| Completeness | `complete` only when `frame_is_complete()` succeeds. `incomplete` when an intent is present but the frame is not. Otherwise `unknown`. |
| Ambiguity | `competing` when two intents match. Otherwise `none`. The check runs, so this field is not left `unknown` in the current extractor. |
| Context | `that` always. `it` only when the string is not a weather question. |
| Numbers | Digit spans. A digit inside a date is a number span, not automatically an amount. |
| Spans | Start and end offsets into the stored string. The string is not passed through text normalization. |
| Provenance | Copied from the candidate. `native_nbest` is still rejected by the Phase 2 candidate contract. |

Extraction is the spans and lexicon hits. Interpretation is the intent list, polarity, and modality. Commit eligibility on the assessment is preliminary. The policy in `commit_policy_v4.py` makes the decision, and an ablation can ignore a signal the extractor still reports.

`please` does not set modality to `uncertain`. An unseen sentence such as "The warehouse is closed today" stays `unknown` rather than being stored as a negative finding.
