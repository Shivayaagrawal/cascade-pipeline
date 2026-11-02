# Phase 1D.3 statistical analysis plan

**Date:** 2026-11-02  
**Status:** reporting plan. No interval, bootstrap, or significance test is computed in this phase.

The frozen sample is 200 synthetic utterances from one grammar, one seed, and written edits. A descriptive count on that sample is the result. A confidence interval around it describes resampling of those 200 rows. It does not describe conversational speech, another grammar, or a recognizer.

## Unit and pairing

The unit is the utterance. Comparisons that share `utt-000` through `utt-199` are paired. A table that mixes ids, lists, or readers is not a paired comparison.

For a binary outcome such as exact-frame match, the paired summary is the count of ids where system A matches and system B does not, and the count of the reverse. Both discordant counts are reported. A gain that is one or two utterances is reported as that count.

## What is reported for every rate

- Numerator, denominator, and the rate.
- The utterance count.
- Undefined, when the denominator is zero, with the reason string already used by `rate()`.
- The system name and the candidate list name.

Selective risk is always printed next to selective coverage. An operating point taken from the middle of the `min_support` curve is labelled with that support. The curve at supports 1, 2, and 3, plus always-HOLD, is the published object. A later writer does not replace the curve with the support that has the smallest risk.

## Error distribution

Beside each rate, report the count of slot-critical mismatches and the utterance ids when the count is small enough to list. The three v1-list unsafe commits are already listed. Category tables keep their own denominators:

- One corrupted paraphrase applied to all 200 ids is an isolated category result.
- The rank-0 grouping has 25 ids per category and still contains the other two edits. It is not an isolated category result.

A zero in a cell of 25 is a zero count. It is not evidence that the error cannot occur.

## Intervals, if a later phase computes them

The interval is a percentile bootstrap of utterance ids.

| Choice | Rule |
| --- | --- |
| Resample unit | The utterance, with replacement. |
| What is resampled | The paired difference, or the risk numerator and coverage numerator together so the interval cannot hide the coverage. |
| Draws | `B` is written in the run config before the run. |
| Seed | Recorded. It is not seed 17 reused as if it were a new sample of people. |
| Interval | Percentile. The sample being resampled is these 200 strings. |
| Empty commit set | No interval is substituted for an undefined risk. |

A bootstrap interval on this grammar is a stability check of these strings. The sentence that reports it says that. It does not say the interval covers a speech population.

McNemar’s test is an appropriate paired test for exact-frame match on shared ids if a later confirmatory analysis is approved. It is not computed now. A small p-value on these 200 rows would still be a statement about these rows.

## Multiple comparisons

The v3 category tables cross eight edit types with several metrics, and they already exist. They are exploratory descriptions. They are not a family of confirmatory tests, and a cell is not promoted to a primary result after inspection.

If a later experiment names one primary contrast, it names it before scoring. The two contrasts that match this protocol are:

1. Exact-frame paired difference for one named reader, rank-0 transcript versus the full named list.
2. Unsafe-commit count and coverage for forced selection versus selective commitment at one `min_support` named in the config.

Other cells stay secondary.

## Sample size

Two hundred utterances, twenty per intent, is the whole synthetic evaluation set. It was not drawn from a speech population. Rank-0 category slices are twenty-five. The development pilot of LibriSpeech is thirty rows and is unannotated, so it adds no semantic sample.

No power calculation is invented for a corpus that has not been acquired. A future speech protocol states the split size from the official release after acquisition, and it does not treat 200 as that size.

## Conclusions that this sample can support

- The published counts for a named system, list, and denominator.
- The direction of a paired difference on these ids, stated as a count.
- The coverage that accompanies a selective-risk count.
- The observation that support 2 on the v1 list removes the three wrong times and also lowers coverage from 145/200 to 74/200.

## Conclusions that this sample cannot support

- A general claim of statistical significance.
- A speech error rate, a conversational error rate, or an N-best error rate.
- A user-acceptable coverage or latency. No acceptability threshold has been set.
- A claim that a zero selective risk at support 2 or 3 means the remaining utterances were answered correctly. Those utterances were not committed.
- Transfer of a Track A interval to Track B.

Negative differences, high HOLD rates, and retries that do not repair the frame are reported in the same table as gains.
