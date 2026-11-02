Build the experiment runner to compare B0, B1 and B2 on identical sample IDs and perturbation conditions.

Tune thresholds only on validation.

Save:

- Raw per-sample outputs.
- Configuration.
- Random seed.
- Model identifiers.
- Run ID.

Calculate metrics from saved outputs.

Include:

- Clean false positives.
- Recovery success.
- Harmful recovery.
- Latency.
- Breakdown by failure type.

Add ablations and tests.

Never fabricate results or silently exclude failures.
