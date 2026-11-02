# Phase 1D.3 experimental protocol

**Date:** 2026-11-02  
**Status:** methodology. No experiment was run. No dataset was acquired.  
**Frozen results stay in their directories.** This protocol cites them. It does not recompute them.

Two tracks stay separate. A number from Track A is a synthetic transcript result. A number from Track B, once Track B exists, is a speech result. They are not averaged.

## Track A. Existing synthetic transcript experiments

Track A is closed. The runner that wrote the v1 summaries is not executed again.

| Artifact | Identity | Role in the protocol |
| --- | --- | --- |
| Synthetic utterances | `utt-000`–`utt-199`, seed 17, 10 intents, 20 each | Gold intent and gold slots. Local simulation labels. |
| Original synthetic transcripts | The generator sentence for each id | Oracle-only. `reference_passthrough`. Absent from ordinary candidate lists. |
| v1 injector variants | 600 rows, provenance `synthetic_edit` | The three-candidate lists behind frozen B0, B1, and B2. |
| Paraphrase, slot-removed, and split lists | Built by `candidate_diversity.py` | Named v3 conditions. Still written text. The gold sentence is excluded. |
| `experiments/B0`, `B1`, `B2` and `artifacts/reports/simulation_report.json` | Prefix cascade | Frozen `b0_prefix`, `b1_prefix`, `b2_prefix_controller`. |
| `experiments/sim-eval-v2` | Same cascade, extra records | Oracle, policy, and text-pipeline timing. Timing excludes `say` and is not ASR latency. |
| `experiments/sim-eval-v3` | Lexical layer | Authoritative `b1_forced_lexical` and `b2_lexical_v3` counts. |
| `experiments/sim-eval-v3b` | Audit of v3 | Decision log and lexical wall time. `asr_latency` is false. |

Audio files under `data/synthetic/audio/` are macOS `say` fixtures. Track A decision scores do not come from decoding them.

### Proxy candidate construction

A proxy candidate is a string written by the project. Its provenance is `synthetic_edit`. The code rejects `native_nbest` on that path.

| List | How it is specified | What an evaluation may say |
| --- | --- | --- |
| v1 injector | Three edits per utterance from the seed-17 injector. Categories include deletion, substitution, insertion, entity corruption, number corruption, negation corruption, ambiguous transcript, and incorrect transcript. | A written-edit list. The rank-0 category table in v3 groups 25 ids and leaves the other two edits in the list. |
| Paraphrase | Three templates in `paraphrases()` that keep slot tokens and are not the gold sentence. | A wording change inside the grammar. |
| Slot removed | Slot values stripped from those wordings. | A list that usually cannot carry the gold frame. |
| Split evidence | Intent wording and slot wording placed in different candidates. | A list that can contain the pieces without containing the whole frame in one candidate. |

The v1 ambiguous edit may contain the original wording inside a longer string. That longer string is not a copy of the gold candidate. Exact gold copies are excluded from the v1 lists.

Oracle coverage asks whether some written candidate still contains the intent cue, the slot values, or both in one candidate. It is a property of the strings. It is not N-best coverage.

Candidate budget is part of the condition. `b0_prefix` sees one string. `b1_prefix`, `b1_forced_lexical`, and `b2_lexical_v3` see the named list. A comparison that changes both the budget and the reader is reported as both changes.

### Frozen conditions that stay cited

| Condition | System | Published record |
| --- | --- | --- |
| v1 injector, prefix cascade | `b0_prefix`, `b1_prefix`, `b2_prefix_controller` | `docs/SIMULATION_RESULTS.md`. B2 actions: CONTINUE 61, RETRY 52, CLARIFY 22, HOLD 65. |
| Same cascade, v2 policy record | `b2_prefix_controller` | Action accuracy 88/200. Unsafe commitment 112/113. Thresholds were not tuned. |
| v1 injector, lexical | `b1_prefix` exact frame 1/200; `b1_forced_lexical` 145/200; `b2_lexical_v3` coverage 145/200, selective risk 3/145, RETRY 0 | `docs/SIMULATION_EVAL_V3.md` |
| Slot-removed primary plus paraphrase retry | `b2_lexical_v3` | CONTINUE 0, RETRY 198, CLARIFY 2, HOLD 0. Selective risk 0/198. Mechanism `simulated_candidate_rescore`. |
| `min_support` 1, 2, 3 on the v1 list | `b2_lexical_v3` | Coverage 145/200, 74/200, 8/200. Risk 3/145, 0/74, 0/8. |

v3b repeats the v1-list aggregate and writes the 200-row log. It does not replace v3.

## Track B. Future real-speech experiments

Track B is designed and blocked. No component below is available for a semantic run.

| Requirement | Rule when the track opens | Status now |
| --- | --- | --- |
| Real audio | Files named in an acquisition decision, checksum verified, then extracted under the cap then in force. | Blocked. SLURP is the preferred candidate and is not authorized. |
| ASR model and version | Package name, version, and model id recorded in the run directory. | Blocked. `faster-whisper` is not installed. The adapter has not been called. |
| Decoder configuration | `beam_size`, temperature, and any other decode flag written before scoring. `beam_size=1` returns one string. That string is `single_segment_text`. | Blocked. |
| Reference transcripts | Copied from the release. The project does not edit them to match a hypothesis. | Blocked for a task corpus. LibriSpeech references exist and are a transcription resource only. |
| Genuine N-best | Stored only when one recognizer call returns the ordered list. Provenance `beam_hypothesis` or `native_nbest` requires that call. | Blocked. No such list exists. |
| Intent and slot gold | Taken from the task release, or from a completed human annotation with an annotator id. | Blocked. LibriSpeech has neither. The 30-row pilot is `not_annotated`. |
| Split isolation | Official train and development splits may set thresholds. The official test split is hashed and left unread until the configuration is frozen. | Blocked. `test-clean` stays unread for development. |

LibriSpeech `dev-clean` can later host a transcript B0 scored with WER and CER after a decode. That run uses reference text as the WER reference. It does not produce intent accuracy or slot F1. `test-clean` is not the development audio for that run.

Headset and distant recordings of one sentence, if a later corpus contains both, are two audio items. They are not two hypotheses.

## Fair comparison

A comparison table includes only systems that share utterance ids, gold references, the metric implementation, and a written exclusion list. The table names the candidate budget and the reader.

| Rule | Application |
| --- | --- |
| Shared ids | `utt-000`–`utt-199` inside Track A. A Track B table uses one release and one split. |
| Identical gold | Synthetic gold for Track A. Dataset gold for Track B. The gold sentence is not inserted into the candidate list to raise coverage. |
| Identical conditions | One named list and one named support. Paraphrase results are not merged with v1-injector results. |
| Candidate budget | Stated in the column header. B0’s budget is one. |
| Forced versus selective | Forced exact-frame accuracy uses every utterance as the denominator and always has a prediction. Selective exact-frame accuracy over all utterances counts abstention as incorrect and is printed beside coverage and selective risk. |
| Abstention | CLARIFY and HOLD. `decision_safe` is false only when a CONTINUE or RETRY frame mismatches gold. Abstention is not an unsafe commit. |
| Incomplete frames | A missing required slot is not an exact frame. The selective layer does not commit it. The forced layer may return it, and the exact-frame score then fails. |
| Unsupported slot values | A predicted pair that is not in the gold set counts against precision. The controller does not invent a slot value absent from the candidates and from a clarification response. |
| Empty gold slots | Both sides empty contribute one matched pair-set in micro slot scoring. The lexical gold oracle still withholds a commit when the schema lists a slot the text does not contain. Those two rows are the empty-date cancel and check-appointment cases in v3. |

### Comparisons that are valid on the frozen sample

| Comparison | Why it is valid | What it does not show |
| --- | --- | --- |
| `b0_prefix` vs `b1_prefix` vs `b2_prefix_controller` on the v1 injector list | One reader family, one id set, one gold set | A speech effect, or an effect of candidate count separated from the prefix score |
| `b1_prefix` vs `b1_forced_lexical` on one named v3 list | Same strings, same gold, readers named | A pure candidate-budget effect. The readers differ. |
| `b1_forced_lexical` vs `b2_lexical_v3` on one named list | Same reader. The difference is forced answer versus commit rule. | A human judgment that abstention was appropriate |
| `min_support` 1, 2, and 3 | Same list and reader. The curve is the result. | A threshold selected on held-out speech |
| v3 recovery condition versus the slot-removed list alone | The second bundle is the stated intervention | An operational retry |

### Comparisons that need new evidence

| Comparison | Missing evidence |
| --- | --- |
| Any Track A number against a speech number | A completed Track B run on its own ids |
| Proxy-list selection against genuine N-best selection | A recognizer list with provenance |
| `b2_prefix_controller` actions against `b2_lexical_v3` actions as one policy | They are different contracts. A future comparison has to say so in the table title. |
| Derived action accuracy against human action accuracy | Human labels for the four actions |
| LibriSpeech semantic scores | Intent and slot gold, which this corpus does not have |
| Generalization beyond the ten intents | Another domain and a sealed test |

## Acceptance before new implementation or a speech run

Phase 1D.4 reviews this protocol. Implementation after that review may add only the code the accepted protocol names, in a new directory, without rewriting frozen outputs. A speech run waits for an acquisition decision. This document does not start either step.
