# Simulation Evaluation v3

**Experiment ID:** `sim-eval-v3`  
**Date:** 2026-11-02T08:50:05Z  
**Seed:** 17  
**Utterance IDs:** `utt-000` through `utt-199`  
**Git HEAD:** `f55b5bd5b74d760e00f3178a35cd9b9512fd1ccf` (working tree dirty; this experiment is not in that commit)  
**Config SHA-256:** `ac4bb7ea743195e6ea860a4f2c34dc546437321f28c811055782fe4b1c5ed842`  
**Manifest SHA-256:** `abc3cceec6a90e0953ac6614e1a6fee63b91c1401324798e0232ef1aa4f723e9`  
**Backend:** `synthetic_hypothesis`  
**ASR decode:** none  
**RETRY label:** `simulated_candidate_rescore`  
**Phase 1:** not approved  
**Common Voice:** not acquired  
**B2 thresholds:** not tuned

v1 summaries and the v2 report were hashed before and after this run. The hashes matched.

| File | SHA-256 |
|------|---------|
| `experiments/B0/summary.json` | `3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee` |
| `experiments/B1/summary.json` | `597a2800c946018467865dfcf3d8e547bc51c10487596cc134ca2181fee695b2` |
| `experiments/B2/summary.json` | `34a40fdd233f5d4faa00af73c26f1afcc32c4d83922db8df57b7a7184dce0e5d` |
| `artifacts/reports/simulation_report.json` | `7adf69ee6ac344e7ef205099af3686ddf7cceaffa111a8789f03b83ed8319856` |
| `experiments/sim-eval-v2/report.json` | `74499b716103e26ef829cb56816bf738d67d3d3e5961848c4cfe37f2e8f4f77d` |

The full JSON is `experiments/sim-eval-v3/report.json`. Rates below use the counts in that file. A missing denominator is N/A. It is not recorded as zero.

## 1. Candidate information coverage

Two ceilings are reported for the original three variants. They answer different questions.

The frozen v2 prefix parser can find the gold intent in 137/200 candidates and a complete frame in 1/200. The v3 lexical reader, on the same three strings, finds the intent cue in 193/200, every gold slot value somewhere in the list in 198/200, and a complete frame inside one candidate in 147/200. Fifty-three utterances have no single candidate that still carries both. Sixty-eight of 200 lists disagree about intent. The gold sentence is not added to this list. The ambiguous edit keeps the original wording and appends a second question, so that longer string is not a separate copy of the reference.

| Candidate list | Intent cue | Slot values | Complete frame in one candidate | Intent disagreement | Gold slot value missing |
|----------------|------------|-------------|---------------------------------|---------------------|-------------------------|
| v1 injector | 193/200 | 198/200 | 147/200 | 68/200 | 2/200 |
| Paraphrase, gold sentence excluded | 200/200 | 200/200 | 200/200 | 0/200 | 0/200 |
| Slot values removed | 180/200 | 2/200 | 2/200 | 0/200 | 198/200 |
| Intent and slots split across candidates | 180/200 | 200/200 | 2/200 | 0/200 | 0/200 |

The two complete frames in the destroyed and split lists are the first cancel example and the first check-appointment example. Their gold slot sets are empty, so an intent cue alone preserves the gold frame. The other 198 gold slot values are gone from the slot-removed list. In the split list those values survive, but only in a different candidate from the intent words. A commit requires one candidate to carry the whole frame, so the split list does not raise complete-frame coverage.

Removing the currency word also removes the transfer cue, because that cue is the word “rupee(s)”. Those 20 transfer utterances are the ones missing an intent cue in the slot-removed and split lists.

## 2. Slot-aware selector comparison

B1 is the existing prefix selector. The slot-aware forced selector always returns one frame from intent compatibility, filled critical slots, and candidate order. It does not read gold labels. The selective layer is separate: it commits only when every schema slot has one agreed value. A high-confidence intent with a missing amount, recipient currency, date, time, account, recency, genre, or topic does not commit.

| List | B1 intent | B1 slot F1 | B1 exact frame | Forced intent | Forced slot F1 | Forced exact frame |
|------|-----------|------------|----------------|---------------|----------------|--------------------|
| v1 injector | 0.685 | 0.104 | 1/200 | 0.940 | 0.848 | 145/200 |
| Paraphrase | 0.300 | 0.168 | 0/200 | 1.000 | 1.000 | 200/200 |
| Slot values removed | 0.000 | 0.018 | 0/200 | 0.900 | 0.018 | 2/200 |
| Split evidence | 0.000 | 0.018 | 0/200 | 0.900 | 0.018 | 2/200 |

On the original variants, B1’s exact-frame count stays at the frozen 1/200. The slot-aware reader uses slot strings that the prefix cues skip. Its forced exact-frame count is 145/200. That number always answers. It is not a safety result.

On paraphrases that keep the slot tokens and do not contain the gold sentence, B1’s exact-frame count is 0/200. The slot-aware forced selector matches 200/200, including the two gold rows with an empty date. The selective layer does not commit those two, because the schema lists a date and the text does not contain one.

## 3. Selective prediction risk and coverage

Coverage is the share of utterances that receive CONTINUE or a simulated RETRY. Selective risk is the frame error among those commitments. Exact-frame accuracy over all 200 counts every abstention as incorrect. An always-HOLD system has coverage 0/200 and its selective risk is N/A.

| List | Coverage | Selective risk | Slot-critical unsafe | Exact frame, abstention counted wrong | Exact frame among commits |
|------|----------|----------------|----------------------|---------------------------------------|---------------------------|
| v1 injector | 145/200 | 3/145 | 3/145 | 142/200 | 142/145 |
| Paraphrase | 198/200 | 0/198 | 0/198 | 198/200 | 198/198 |
| Slot values removed | 0/200 | N/A | N/A | 0/200 | — |
| Split evidence | 0/200 | N/A | N/A | 0/200 | — |

The three unsafe v1 commits are reminder times. The only complete candidate has moved the clock onto another closed-grammar time: “7 AM” to “8 AM” (`utt-121`), “5 PM” to “6 PM” (`utt-124`), and “2 PM” to “3 PM” (`utt-129`). The candidate that still contains the gold time has lost the intent cue or has two intents, so agreement has nothing correct to compare. All three are slot-critical. Intent on the committed v1 decisions is 145/145. The frame errors are the times.

Risk-coverage on the v1 list, by how many complete candidates must agree:

| Rule | Coverage | Selective risk |
|------|----------|----------------|
| One agreeing candidate | 145/200 | 3/145 |
| Two agreeing candidates | 74/200 | 0/74 |
| Three agreeing candidates | 8/200 | 0/8 |
| Always HOLD | 0/200 | N/A |

Requiring two witnesses removes the three wrong times and also drops coverage from 145/200 to 74/200. The zero error at that point is the error among the remaining commits. It does not mean the other 126 utterances were answered correctly.

When all three paraphrases agree, support 1, 2, and 3 each commit 198/200 with selective risk 0/198. When only one paraphrase keeps its slots and the other two have those values removed, support 1 commits 198/200 with risk 0/198, and support 2 or 3 commits 0/200 with risk N/A.

## 4. B2 policy evaluation

The original B2 controller was not edited. Its v2 record stands: action accuracy 88/200 and unsafe commitment 112/113. Those thresholds were not fit to the v1 or v2 scores.

The v3 contract is a separate layer. Expected actions are assigned from the gold frame and the candidate strings, before the decision is read:

1. A primary candidate that preserves the gold intent and every gold slot value expects CONTINUE.
2. Otherwise a supplied second list that preserves that frame expects RETRY. Without a second list, this step does not apply.
3. A missing gold slot, evidence split across candidates, or more than one intent cue expects CLARIFY.
4. Otherwise HOLD.

RETRY is returned only when the caller supplies a second list and that list can commit. Every such RETRY is labelled `simulated_candidate_rescore`. No waveform was decoded.

On the v1 list, with no second list, the layer chose CONTINUE 145, CLARIFY 48, HOLD 7, and RETRY 0. Action accuracy was 192/200. Clarification precision was 43/48. Clarification recall was 43/46. Recovery gain over prefix B0, counting abstention as not correct, was 0.710. Prefix B0’s exact-frame count on these first candidates is 0/200, which matches the frozen v1 result.

The recovery condition uses the slot-removed list first and the paraphrase list as the second bundle. It chose RETRY 198 and CLARIFY 2. All 198 retries carry the simulated-rescore label. Selective risk on those commitments is 0/198. Recovery gain over prefix B0 on the slot-removed first candidates is 0.990. The two CLARIFY decisions are the empty-date cancel and check-appointment rows. Their expected action is CONTINUE, because the gold frame has no slot value and the wording still has the intent. The policy asks for a date anyway. Clarification precision on this condition is 0/2. Clarification recall is N/A because no row expected CLARIFY.

The slot-removed list alone commits nothing, so its recovery gain over B0 is 0.000 and its selective risk is N/A. Refusing every input does not create a recovery gain.

## 5. Corruption-category analysis

The category tables use the selective layer. Intent, slot F1, and exact frame count an abstention as an incorrect frame. Oracle frame coverage is lexical: one candidate still contains the gold intent cue and every gold slot value.

### One corrupted paraphrase

Each category is applied to the first paraphrase of all 200 utterances. This is the isolated category result.

| Category | Intent | Slot F1 | Exact frame | Oracle frame | Coverage | Selective risk | Unsafe commits |
|----------|--------|---------|-------------|--------------|----------|----------------|----------------|
| Deletion | 0.345 | 0.523 | 66/200 | 67/200 | 69/200 | 3/69 | 3 |
| Substitution | 0.340 | 0.515 | 66/200 | 68/200 | 68/200 | 2/68 | 2 |
| Insertion | 0.990 | 1.000 | 198/200 | 200/200 | 198/200 | 0/198 | 0 |
| Entity corruption | 0.000 | 0.018 | 0/200 | 2/200 | 0/200 | N/A | 0 |
| Number corruption | 0.180 | 0.171 | 20/200 | 20/200 | 36/200 | 16/36 | 16 |
| Negation corruption | 0.990 | 1.000 | 198/200 | 200/200 | 198/200 | 0/198 | 0 |
| Ambiguous transcript | 0.005 | 0.027 | 1/200 | 20/200 | 1/200 | 0/1 | 0 |
| Incorrect transcript | 0.000 | 0.018 | 0/200 | 0/200 | 0/200 | N/A | 0 |

Entity corruption and a fully replaced transcript produce no commits. Their selective risk is N/A. Exact-frame accuracy over all inputs is 0. Insertion of “please” and insertion of “not” leave the lexical frame intact, so the layer still commits. Negation is a category, not a gold slot, so a committed frame can match gold after “not” is inserted. Number corruption is the dangerous cell: 16 of 36 commits land on a different closed-grammar number, and the single candidate agrees with itself.

The one ambiguous commit is the balance utterance whose reference sentence is the fixed question appended by that category. The append contains that reference sentence. The other balance paraphrases then contain two account values, so they are not committed. Oracle frame coverage for the ambiguous category is 20/200; decision coverage is 1/200.

### One corrupted paraphrase beside two clean ones

| Category | Oracle frame | Coverage | Exact frame | Selective risk | Slot-critical unsafe |
|----------|--------------|----------|-------------|----------------|----------------------|
| Deletion | 200/200 | 195/200 | 195/200 | 0/195 | 0 |
| Substitution | 200/200 | 196/200 | 196/200 | 0/196 | 0 |
| Insertion | 200/200 | 198/200 | 198/200 | 0/198 | 0 |
| Entity corruption | 200/200 | 198/200 | 198/200 | 0/198 | 0 |
| Number corruption | 200/200 | 182/200 | 182/200 | 0/182 | 0 |
| Negation corruption | 200/200 | 198/200 | 198/200 | 0/198 | 0 |
| Ambiguous transcript | 200/200 | 198/200 | 198/200 | 0/198 | 0 |
| Incorrect transcript | 200/200 | 198/200 | 198/200 | 0/198 | 0 |

Disagreement blocks the wrong in-lexicon number. Number-corruption coverage falls to 182/200, and the selective risk among the commits that remain is 0/182.

### Original three variants, grouped by the rank-0 category

Each group has 25 utterances. The other two variants stay in the list, so a rank-0 incorrect transcript can still be rescued by another edit. This table is not an isolated category result.

| Rank-0 category | Oracle frame | Intent | Slot F1 | Exact frame | Coverage | Selective risk |
|-----------------|--------------|--------|---------|-------------|----------|----------------|
| Deletion | 25/25 | 0.960 | 1.000 | 24/25 | 24/25 | 0/24 |
| Substitution | 13/25 | 0.560 | 0.571 | 12/25 | 14/25 | 2/14 |
| Insertion | 25/25 | 1.000 | 1.000 | 25/25 | 25/25 | 0/25 |
| Entity corruption | 10/25 | 0.400 | 0.526 | 10/25 | 10/25 | 0/10 |
| Number corruption | 13/25 | 0.520 | 0.634 | 12/25 | 13/25 | 1/13 |
| Negation corruption | 25/25 | 1.000 | 1.000 | 25/25 | 25/25 | 0/25 |
| Ambiguous transcript | 11/25 | 0.400 | 0.541 | 10/25 | 10/25 | 0/10 |
| Incorrect transcript | 25/25 | 0.960 | 0.981 | 24/25 | 24/25 | 0/24 |

## 6. Gold-transcript oracle comparison

| Quantity | What it measures | Result |
|----------|------------------|--------|
| Candidate oracle coverage | Whether the ordinary list still contains the intent cue, the slot values, or both in one candidate. The reference sentence is not added. | v1 lexical: intent 193/200, slots 198/200, complete frame 147/200. Frozen v2 prefix reader on the same list: intent 137/200, complete frame 1/200. |
| Gold-transcript oracle | The reference sentence scored by itself, as its own condition. | Prefix reader: intent 200/200, slot F1 1.000, exact frame 200/200. Lexical reader: intent 198/200, slot F1 1.000, exact frame 198/200. |
| Achieved selective performance | Frames the v3 layer commits on the ordinary list. | v1 list: 145 commits, 142 correct frames, selective risk 3/145. Paraphrase list: 198 commits, 198 correct, selective risk 0/198. |

The lexical gold oracle misses the two rows whose schema lists a date and whose gold slot set is empty. The prefix reader matches those empty frames. That gap is the safety rule, not a missing reference sentence.

The reference sentence is not an exact candidate in the v1, paraphrase, slot-removed, or split lists. In the controlled ambiguous edit, one appended question is the reference sentence of one balance utterance. That containment is counted in the report. It is not part of the primary lists.

## 7. Tests and reproducibility

`python3 -m pytest -q` passed 26 tests. The v3 tests cover a transfer with no amount, a wrong in-lexicon amount accepted by one candidate and rejected when another candidate disagrees, the reading of “75” inside “751”, abstention with an undefined selective risk, CONTINUE, simulated RETRY, CLARIFY, and HOLD, expected actions assigned without reading the decision, a zero denominator, exclusion of the gold sentence from the paraphrase lists, exact gold copies excluded from the v1 lists, and a support threshold of 2.

Seed 17 and the utterance IDs are unchanged. The run recorded the UTC timestamp, git HEAD, config hash, manifest hash, and the five preserved result hashes above. No Common Voice archive was downloaded. No extra package was installed. No GPU was required.

## 8. Limitations and next research milestone

The lexical layer is a closed grammar. Its 147/200 complete-frame ceiling means those strings still contain the cue and the slot values. It does not mean a general parser, or a recognizer, would recover 147 frames. The prefix parser’s ceiling on the same strings remains 1/200, and that frozen result stands.

Three commitments are wrong because a corrupted time is another legal time and it is the only complete candidate. A single number edit has the same hole: 16 of 36 number-corruption commits are slot-critical. Agreement with a second clean wording blocks those errors and lowers coverage. The layer cannot see that a unanimous wrong value is wrong.

Negation does not change the gold schema, so a frame with “not” inserted is still committed when the slots match. Transfer evidence disappears together with the currency word. The layer does not build one frame out of an intent candidate and a separate slot candidate.

The revised Phase 1 plan is `docs/PHASE_1_IMPLEMENTATION_PLAN.md`. It is not approved. The next measurement is waveform decoding after the Common Voice access gates are met. Until then the contract stays a design requirement: commit only a complete agreed frame, clarify when a critical slot is missing or disputed, hold when intent evidence is absent, and do not treat agreement as correctness. That does not require retuning the frozen B2 thresholds. A lower error rate is reported with the coverage that produced it.
