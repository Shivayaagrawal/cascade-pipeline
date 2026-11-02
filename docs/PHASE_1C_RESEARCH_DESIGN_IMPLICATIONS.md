# Phase 1C research design implications

**Date:** 2026-11-02  
**No B0, B1, or B2 run was started.**

A metric is listed only where the gold it needs is identified. Gold that LibriSpeech does not have is marked as requiring another dataset.

## Shared distinction

WER and CER compare a hypothesis with the reference transcript. They do not say whether a request was understood. A lower WER can leave a name, number, polarity, or task slot wrong. A semantic metric needs a gold meaning that was fixed before the hypothesis was seen.

## B0

Single-best transcript, then an NLU step.

| Item | On LibriSpeech now | Needs a task-oriented corpus |
|------|--------------------|------------------------------|
| Input | The FLAC and the reference text. | Audio, transcript, intent, and slots. |
| Gold | Reference transcript. | Intent and slots, plus the transcript. |
| Output that can be scored | WER and CER, after ASR exists. | Intent accuracy, intent macro-F1, slot precision, recall, and F1, and exact frame accuracy. |
| Limitation | No NLU gold. | Licence and acquisition are not approved. |

## B1

Several transcripts from one decode, compared as meanings.

| Item | On LibriSpeech now | Needs a task-oriented corpus |
|------|--------------------|------------------------------|
| Input | More than one transcript for the same audio. The current decoder has not been run, and a beam must not be invented. | The same, plus gold intent and slots. |
| Gold | Reference transcript for WER. A sentence-level label only after a person annotates it. | Gold frame for each utterance. |
| Output | WER of each hypothesis. Later, whether hypotheses disagree on a human sentence-level label. | Whether the selected hypothesis keeps the gold frame. |
| Limitation | Candidate agreement is not correctness. | The selection rule has to be frozen on development data only. |

## B2

CONTINUE, RETRY, CLARIFY, and HOLD.

| Item | On LibriSpeech now | Needs a task-oriented corpus |
|------|--------------------|------------------------------|
| Input | A decision to answer, decode again, ask, or abstain. | The same, tied to a task frame. |
| Gold | Not available. A narrative sentence does not say which of the four actions is correct. | A definition of a correct frame, plus rules for when abstaining is required. |
| Output | None that can be called recovery success. | Recovery success, unnecessary recovery, clarification rate, false acceptance, and HOLD precision and recall, each only after those gold rules exist. |
| Limitation | Scoring these actions here would treat audiobook sentences as commands. | The held-out sample cannot be used to choose the rules. |

## Metrics that have gold today

WER and CER have gold: the LibriSpeech reference text. They are not semantic metrics.

Intent accuracy, intent macro-F1, slot F1, semantic frame accuracy, semantic error rate, recovery success, unnecessary recovery, clarification rate, false acceptance, and HOLD precision and recall do not have gold on this corpus. They are not reported as zero.

## Held-out data

The 200 test utterances stay unused for schema design, labeling, thresholds, and model outputs. A later test annotation pass needs its own written plan.
