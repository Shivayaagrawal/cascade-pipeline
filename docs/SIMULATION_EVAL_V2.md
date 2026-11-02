# Simulation Evaluation v2

**Experiment ID:** `sim-eval-v2`  
**Date:** 2026-11-02  
**Seed:** 17  
**Git HEAD:** `f55b5bd5b74d760e00f3178a35cd9b9512fd1ccf` (working tree dirty; the simulation code is not in that commit)  
**Backend:** `synthetic_hypothesis`  
**ASR decode:** none  
**Phase 1:** not approved  
**Common Voice:** not acquired

The initial B0, B1, and B2 summaries were hashed before and after this run. They did not change. Recomputing the same controller reproduces the initial scores: B0 intent accuracy 0.310 and WER 0.448; B1 intent accuracy 0.685 and WER 0.309; B2 intent accuracy 0.565 and WER 0.395. This pass does not tune that controller.

## Candidate oracle

The three synthetic variants are the only candidates. The gold transcript is not one of them.

| Measure | Result |
|---------|--------|
| Oracle intent accuracy | 0.685 (137/200) |
| Oracle slot F1 | 0.101 (18 matched pairs, 137 predicted, 220 reference) |
| Complete-frame coverage | 0.005 (1/200) |
| Utterances with no recoverable frame | 199 |

B1 intent accuracy equals the oracle intent accuracy. Candidate comparison is already taking the intent gain that exists inside the list. It cannot repair a frame that no candidate still contains.

A separate ablation that adds the gold transcript, labelled `reference_passthrough`, covers all 200 frames. That ablation is not part of the primary oracle.

## B2 action contract

The controller code is unchanged. RETRY means `simulated_candidate_rescore`. It is not a second decode.

Expected action, in this order:

1. Ambiguous 1-best text, or the ambiguous-transcript condition, expects CLARIFY.
2. A 1-best frame that matches gold expects CONTINUE.
3. A wrong 1-best with another candidate that matches gold expects simulated RETRY.
4. Otherwise HOLD.

| Metric | Result |
|--------|--------|
| Action accuracy | 0.440 (88/200) |
| Recovery success | 0.005 (1/200 B0 frame failures) |
| False recovery | N/A. B0 had no exact-frame successes. |
| Unnecessary clarification | 0/175 utterances that did not expect CLARIFY |
| Unnecessary hold | 0/26 utterances that did not expect HOLD |
| Missed clarification | 0.120 (3/25 expected CLARIFY) |
| Unsafe commitment | 0.991 (112/113 CONTINUE or simulated RETRY decisions committed a wrong frame) |

## Error categories

Each rank-0 category has 25 utterances. WER can exceed 1 when the edit inserts more words than the reference, which is what the ambiguous and incorrect conditions do. Slot F1 is N/A only when a denominator is zero. Zero matches with both denominators present is 0.

B0, grouped by the rank-0 category:

| Category | WER | CER | Intent | Slot F1 | Semantic error |
|----------|-----|-----|--------|---------|----------------|
| deletion | 0.219 | 0.236 | 0.360 | 0.061 | 1.000 |
| substitution | 0.216 | 0.207 | 0.160 | 0.000 | 1.000 |
| insertion | 0.219 | 0.278 | 0.320 | 0.162 | 1.000 |
| entity corruption | 0.319 | 0.266 | 0.880 | 0.000 | 1.000 |
| number corruption | 0.216 | 0.134 | 0.360 | 0.167 | 1.000 |
| negation corruption | 0.208 | 0.149 | 0.280 | 0.121 | 1.000 |
| ambiguous transcript | 1.050 | 1.049 | 0.120 | 0.000 | 1.000 |
| incorrect transcript | 1.100 | 0.948 | 0.000 | N/A | 1.000 |

Entity corruption keeps the intent cue and changes the slot value, which is why intent stays high while the frame stays wrong. The full B1 and B2 tables are in `experiments/sim-eval-v2/report.json` under `by_v0_category`. Across all 600 variants, each category occurs 75 times (`by_variant_category`).

## Slots

Per-slot F1 on the unchanged system outputs:

| Slot | B0 | B1 | B2 | Gold count |
|------|----|----|----|------------|
| date | 0 | 0 | 0 | 78 |
| time | 0 | 0 | 0 | 20 |
| amount | 0 | 0 | 0 | 20 |
| currency | 0.519 | 0.889 | 0.857 | 20 |
| account | 0 | 0 | 0 | 20 |
| genre | 0 | 0 | 0 | 20 |
| recency | 0 | 0 | 0 | 20 |
| topic | 0 | 0 | 0 | 20 |

Currency is the only slot with matches, because the template word "rupees" often survives. Date, time, and amount values do not. Location is N/A: the schema has no location slot. Negation is N/A as a slot: it is an error category, and the gold labels were not edited.

## Ablations

| Setting | Intent accuracy | WER | Exact frame |
|---------|-----------------|-----|-------------|
| B1, 1 candidate, semantic comparison | 0.310 | 0.448 | 0.000 |
| B1, 2 candidates, semantic comparison | 0.555 | 0.360 | 0.005 |
| B1, 3 candidates, semantic comparison | 0.685 | 0.309 | 0.005 |
| B1, 3 candidates, no semantic comparison | 0.310 | 0.448 | 0.000 |
| B2 with failure diagnosis | 0.565 | 0.395 | 0.005 |
| B2 without failure diagnosis | 0.310 | 0.448 | 0.000 |

Removing semantic comparison makes B1 identical to B0. The third candidate accounts for the step from 0.555 to 0.685 intent accuracy. Diagnosis changes B2's intent accuracy, and it does not create correct frames.

## Latency

Audio synthesis was not repeated. The initial 437.66 seconds stays in `docs/SIMULATION_RESULTS.md` and is not ASR latency. Waveform decoding was not run, so ASR latency is N/A.

| Stage | n | Median | p95 | Mean |
|-------|---|--------|-----|------|
| Audio loading | 200 | 0.257 ms | 0.560 ms | 0.273 ms |
| Candidate generation | 1 | 9.87 ms | 9.87 ms | 9.87 ms |
| NLU | 600 | 2.21 µs | 3.00 µs | 2.35 µs |
| Candidate scoring | 200 | 8.75 µs | 10.2 µs | 9.03 µs |
| Failure diagnosis | 200 | 0.208 µs | 0.292 µs | 0.220 µs |
| Recovery decision | 200 | 6.71 µs | 8.00 µs | 5.56 µs |
| Text pipeline per utterance | 200 | 21.8 µs | 30.2 µs | 22.8 µs |

## Tests

`python3 -m pytest -q` — 16 passed.

## Reproduce

```text
PYTHONPATH=src python3 experiments/run_simulation_v2.py
```

Manifest checksums, the seed, and the preserved initial-file hashes are in `experiments/sim-eval-v2/report.json`.
