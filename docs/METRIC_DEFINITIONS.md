# Metric Definitions

These definitions are the scoring rules for later phases. They are not results. The current candidate is Common Voice. FSC and SLURP are superseded implementation tracks. Do not average datasets into one number. Changing a formula after a test run is a protocol change and must be logged in `docs/RESEARCH_DEVIATIONS.md` before new numbers are compared with old numbers.

On Common Voice, Milestone A may report WER and CER only. Intent accuracy, slot F1, exact frame match, and recovery metrics stay unused until a verified manual semantic subset exists. Publishing them on Common Voice before that subset is a false result.

The synthetic simulation is a different track. Its intent and slot labels are created with the utterances. Scores on that track are not Common Voice scores and must stay in a separate report.

If FSC or SLURP is ever revived, score each with its own slot names. An FSC `action` value and a SLURP `action` field are not the same feature. Missing slots count as recall misses.

## Text normalization for WER and CER

The synthetic runner uses `src/cascadeguard/evaluation/textnorm.py`: Unicode NFC, casefold, collapsed whitespace, and punctuation kept on both sides. Do not publish a Common Voice WER with that function until a downloaded release is checked.

Policy for both tracks:

- Compare after Unicode-normalizing to a single canonical form and collapsing internal whitespace.
- Lowercase both reference and hypothesis together. Do not lowercase only one side.
- Do not delete punctuation if the reference uses it to distinguish tokens, and do not strip it from only one side. The chosen punctuation rule is written in the run config before scoring.
- Tokenize words on whitespace after that normalization. Do not stem, spell-correct, or expand contractions unless the run config names that rule before the test split is scored.
- CER uses the same normalized string, including spaces, unless the run config says spaces are removed and applies that choice to both sides.

## ASR

Let the reference word sequence have length \(N\). Let \(S\), \(D\), and \(I\) be the minimum substitution, deletion, and insertion counts from word-level Levenshtein alignment.

\[
\mathrm{WER} = \frac{S + D + I}{N}
\]

If \(N = 0\), WER is undefined for that utterance. The utterance stays in the exclusion log. It is not dropped quietly.

Character error rate uses the same formula on characters after the same normalizer. CER is secondary. WER is required when a transcript is scored.

Report the micro-average: sum of errors over sum of reference words. Also report the utterance count and the total reference-word count.

## Intent

An intent prediction is correct when the predicted canonical intent string equals the reference canonical intent string from `docs/TASK_AND_LABEL_SCHEMA.md`.

\[
\mathrm{Intent\ accuracy} = \frac{\text{number of utterances with equal intent}}{\text{number of scored utterances}}
\]

Macro-F1 is the unweighted mean of per-intent F1. Utterances whose reference intent is absent from the label set are scoring errors, not a new class created at test time.

## Slots

A slot instance is the pair `(name, value)`.

- Precision: matching pairs in the prediction divided by pairs in the prediction.
- Recall: matching pairs in the prediction divided by pairs in the reference.
- F1: harmonic mean of precision and recall.

Empty prediction and empty reference: precision and recall are 1 for that utterance only if both sides have zero slots. A missing required slot is a recall miss, not a silent match.

Micro-F1 pools pair counts across utterances. Macro-F1 averages per-slot-name F1 and is reported beside it when counts exist. The primary slot number for B0/B1/B2 comparison is micro-F1, with the pair counts shown.

This is **not** the matched-entity restriction in Ruan et al., Section 2. Under that restriction, a slot whose span was destroyed by ASR is removed from the ASR-set score. Cascade Pipeline’s primary slot F1 does not remove those cases, because RQ1 asks whether the error changed the frame. A secondary matched-entity score may be reported later under a separate name. It must not replace the primary score.

## Exact frame match

An utterance matches only when intent accuracy would count it as correct **and** every reference slot pair equals the predicted pair set. Partial slot credit does not count as a frame match.

\[
\mathrm{Exact\ frame\ match} = \frac{\text{utterances with full match}}{\text{scored utterances}}
\]

## Detection and recovery

Define a reference failure before scoring:

- On a clean item, the reference outcome is a failure if the final frame does not exactly match the annotation.
- On a synthetic item, the injected type is stored for analysis and is **not** an input to the detector. The detector’s reference failure is still frame mismatch against the original annotation, unless a later protocol defines a different reference and versions the metric name.

Let a positive detection be “the controller does not choose CONTINUE”.

| Metric | Definition |
|--------|------------|
| Detection precision | Detected failures that are reference failures, divided by all detections |
| Detection recall | Detected reference failures, divided by all reference failures |
| Detection F1 | Harmonic mean of those two |
| False-positive rate | Clean utterances with a correct frame that were not CONTINUE, divided by clean utterances with a correct frame |
| Recovery success | Among reference failures where B2 intervenes, the fraction whose final frame matches and B0’s frame did not |
| Harmful recovery | Among utterances where B0’s frame matched, the fraction whose B2 final frame does not |
| Coverage | CONTINUE decisions divided by scored utterances |
| Clarification rate | CLARIFY decisions divided by scored utterances |
| HOLD rate | HOLD decisions divided by scored utterances |

If a denominator is zero, report the rate as undefined and give the count. Do not substitute zero.

## Latency

Per stage and end to end, in seconds, using a clock recorded in the trace. Report sample size, hardware, batch size, whether the first call is included, and P50 and P95. A single mean without the sample size is not a complete report.

## Confidence

A decoder score or class probability is a score. It is a calibrated probability only after a calibration measurement on validation data is saved. No calibration measurement exists.
