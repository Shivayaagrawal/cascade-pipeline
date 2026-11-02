# Phase 1D.2 metric feasibility

**Date:** 2026-11-02  
**Authoritative synthetic numbers:** `experiments/sim-eval-v3/report.json`. v3b repeats the v1 section and does not replace it.

A metric function in the repository is not the same as a measured result.

| Metric | Existing assets support it | Source | Kind of result | Still required for a real-world claim |
| --- | --- | --- | --- | --- |
| WER | The function exists. No system hypothesis has been scored against LibriSpeech. Synthetic edits can be scored against the synthetic sentence. | Synthetic text, if computed. Not currently a frozen speech WER. | Transcript-only, synthetic | A decode of authorized audio and the official reference. |
| CER | Same as WER. | Same | Transcript-only, synthetic | Same |
| Intent accuracy | Yes, on the synthetic grammar | Frozen v1 and v3 reports | Synthetic, transcript-only | Task-speech gold and a real hypothesis |
| Slot precision, recall, and F1 | Yes. `slot_scores()` | v3 report and the v3b audit | Synthetic, transcript-only | Same. Empty predictions from abstention need a stated denominator. |
| Exact semantic-frame accuracy | Yes | v3. On the v1 list, selective exact frame with abstention counted wrong is 142/200. Forced selection is 145/200. Frozen B1 prefix selection is 1/200. | Synthetic | Same, plus the statement of how abstention is counted |
| Candidate coverage | Yes, as an oracle over written candidates | v3. The v1 lexical reader finds a complete frame in one candidate for 147/200. | Synthetic proxy lists | A recognizer list. Coverage of written edits is not N-best coverage. |
| Selective coverage | Yes | v3 v1 list: 145/200 received CONTINUE. RETRY was 0 because no second bundle was supplied. | Synthetic | Real hypotheses and a predeclared commit rule |
| Selective risk | Yes | 3/145 on that list. Undefined when nothing is committed. | Synthetic | The same definition on held-out speech |
| Unsafe commit rate | Yes | Those 3 commits are the reminder-time mismatches `utt-121`, `utt-124`, and `utt-129`. | Synthetic | A task-speech gold frame |
| Recovery action accuracy | Yes, against an expected action the evaluator derived | v3 v1 list: 192/200. The expected action is not a human label. | Synthetic, simulated policy | Gold recovery labels, which no current dataset has |
| Recovery gain | Yes, as defined in v3 | Exact-frame rate with abstention counted wrong, minus prefix B0 on the same ids. The v1-list gain uses a B0 exact-frame count of 0/200. | Synthetic | A speech B0 measured the same way |
| RETRY effectiveness | Only for `simulated_candidate_rescore` | The frozen recovery condition cites the slot-removed list plus the paraphrase bundle: 198 RETRY, selective risk 0/198. A retry is not marked correct merely because it ran. | Simulated | A second decode, labelled as a decode |
| Latency | Lexical wall time in v3b. Text-pipeline timing in v2. | Neither includes a recognizer. v3b says the measurement is not ASR latency. | Synthetic text processing | Timed decodes on the evaluation audio |

## Metrics that exist only because the recovery was simulated

RETRY effectiveness, the 198-retry condition, and any claim that recovery repaired a frame depend on a second list that the experiment supplied. The v1 list itself produced RETRY 0. Those simulated repairs are evidence about the controller’s rule. They are not evidence about a second pass through a recognizer.

WER and CER on LibriSpeech are not in this table as measured results. The references exist. The hypotheses do not.
