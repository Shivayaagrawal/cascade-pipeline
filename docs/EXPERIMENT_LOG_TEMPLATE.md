# Experiment Log

Metric names used below are defined in `docs/METRIC_DEFINITIONS.md`. Name the dataset in every log: Fluent Speech Commands or SLURP, and for SLURP also real or synthetic. Do not put both datasets in one score. Do not fill this template with values that were not computed from a saved prediction file. Synthetic conditions must name the transform and must not be described as a natural error rate. Candidate lists must name `native_nbest` or the proxy method. ATIS is out of the current implementation.

- Run ID:
- Date/time:
- Git commit:
- Dataset release/checksum:
- Split:
- Sample IDs / count:
- Method: B0 / B1 / B2 / ablation
- ASR model/version:
- NLU model/version:
- Decoding/config:
- Perturbation and parameters:
- Random seed:
- Hardware:
- Package versions:
- Metrics file:
- Prediction file:
- Notes / deviations:

## Results

| Metric | Value | Denominator / population |
|---|---:|---|
| WER | TODO | TODO |
| Intent accuracy | TODO | TODO |
| Slot F1 | TODO | TODO |
| Exact frame match | TODO | TODO |
| Detection precision/recall | TODO | TODO |
| Recovery success | TODO | TODO |
| False-positive rate | TODO | TODO |
| Mean latency | TODO | TODO |

## Interpretation

- What changed?
- Which cases improved?
- Which cases regressed?
- What alternative explanation exists?
- What can and cannot be concluded?
