Implement only the clean baseline after the data adapter passes.

Add:

- Typed sample/result schemas.
- Local ASR adapter.
- NLU baseline.
- WER/intent/slot/exact-frame metrics.
- Per-sample prediction persistence.
- Stage latency.

Keep ASR replaceable.

Provide a transcript-input mode for testing downstream modules without ASR.

Add tests with synthetic toy examples.

Run on a small deterministic subset first.

Report actual commands and results; do not invent performance numbers.
