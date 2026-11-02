# Synthetic simulation results

This file is the initial experiment record. Simulation Evaluation v2 is in `docs/SIMULATION_EVAL_V2.md` and does not replace the figures below.

**Date:** 2026-11-02.  
**Dataset:** synthetic only. Common Voice was not acquired.  
**Phase 1 approved:** no.  
**ASR backend:** `synthetic_hypothesis`. Whisper was not installed and was not run. Every candidate provenance is `synthetic_edit`.

These numbers are not a Common Voice benchmark and not a real-world speech result. B0, B1, and B2 saw only injected transcript variants. The original sentence was not one of the three candidates, so a perfect frame is possible only when an edit happens to leave the gold frame intact.

## Run

- Utterances: 200. Variants: 600. Seed: 17.
- Audio: 200 AIFF files, `afinfo` file type ID `AIFC`, 1 channel, 22050 Hz, 16-bit big-endian signed integer. Example `utt-000.aiff` duration 1.622177 seconds. Directory size about 16 MB. Audio is gitignored.
- Wall time: 437.66 seconds. Almost all of that is macOS `say`.
- Peak resident memory of the Python process: 24,051,712 bytes.
- Mean text-pipeline latency, excluding speech synthesis: B0 3.10e-6 s, B1 1.01e-5 s, B2 7.55e-6 s.

Normalizer: NFC, casefold, collapsed whitespace, punctuation kept. WER denominator is 935 reference words. CER denominator is 5,159 characters. No empty reference was excluded.

## Scores

| System | WER | CER | Intent accuracy | Slot precision | Slot recall | Slot F1 | Exact frame | Semantic error |
|--------|-----|-----|-----------------|----------------|-------------|---------|-------------|----------------|
| B0 | 0.4481 (419/935) | 0.4133 (2132/5159) | 0.310 | 0.1579 | 0.0409 | 0.0650 | 0.000 | 1.000 |
| B1 | 0.3091 (289/935) | 0.2673 (1379/5159) | 0.685 | 0.1440 | 0.0818 | 0.1043 | 0.005 | 0.995 |
| B2 | 0.3947 (369/935) | 0.3572 (1843/5159) | 0.565 | 0.1545 | 0.0773 | 0.1030 | 0.005 | 0.995 |

Slot pair counts: B0 matched 9 of 220 reference pairs (57 predicted). B1 matched 18 (125 predicted). B2 matched 17 (110 predicted).

B2 actions on the 200 utterances: CONTINUE 61, RETRY 52, CLARIFY 22, HOLD 65.

Recovery success rate: 0.005 (1 recovered frame out of 200 B0 frame failures). False recovery rate: undefined, because B0 had 0 exact-frame successes, so the denominator is zero. It is not reported as zero.

## Reproduce

```text
PYTHONPATH=src python3 experiments/run_simulation.py --seed 17
python3 -m pytest -q
```

`--skip-audio` repeats the text scores without calling `say`. The text scores above do not depend on the waveform. The waveform was generated and validated, and it was not decoded by a recognizer.
