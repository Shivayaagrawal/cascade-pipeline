Implement controlled perturbations and failure propagation analysis.

Keep original audio immutable.

Add reproducible audio transforms and separate transcript-level edits.

Store:

- Source sample ID.
- Transformation.
- Parameters.
- Random seed.

Add injected_failure_type to experiment metadata.

Never expose this label to the online detector/controller.

Compare clean and corrupted outcomes and report metrics with denominators.

Add tests for determinism and data lineage.
