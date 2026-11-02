# Architecture Overview

**Status:** Proposal only. No packages were created in Phase 0.

The same stage order serves Fluent Speech Commands and SLURP through separate dataset adapters. Native labels are not renamed into one shared intent inventory. Optional TTS is outside the research metrics. ATIS is not an adapter in the current scope. A CNN keyword branch is optional and is not part of B0, B1, or B2.

## Pipeline

```text
audio
  → preprocessing
  → ASR (one transcript, and candidates only when the backend returns them)
  → NLU
  → semantic frame
  → diagnosis
  → recovery: CONTINUE, RETRY, CLARIFY, or HOLD
  → stored trace
```

B0 stops at the frame. B1 adds a candidate list and a selection rule. B2 adds diagnosis and recovery. They call the same ASR and NLU types rather than three copies of the stack.

Response generation and a demo UI are outside Phase 1–3. The research prototype does not perform an external action.

## Boundaries

Later code, not created now, is expected under `src/cascadeguard/` as:

`audio/`, `data/`, `asr/`, `nlu/`, `pipeline/`, `perturbations/`, `diagnosis/`, `recovery/`, `evaluation/`, `experiments/`

Evaluation reads records. It does not rewrite predictions. Diagnosis does not edit the ASR text. Recovery does not edit the original dataset. The orchestrator does not contain a training loop.

## Contracts

Fields that a backend does not provide stay null and are labelled unavailable. They are not filled with a placeholder score.

**Audio sample.** `sample_id`, `audio_path`, `split`, `speaker_id` or null, `transcript` reference, `intent` reference, `slots` reference.

**ASR result.** `sample_id`, `text`, `model_name`, `model_version`, `decode_config`, `latency_seconds`, `status`. Optional and only if returned: segment times, token scores, candidate list. Each candidate has `text`, `rank`, `score` or null, and `provenance` (`native_nbest`, `independent_decode`, or `synthetic_edit`).

**Semantic frame.** `intent` or null, `slots` map, `unknown_intent` flag. Slot values come from the dataset schema after it is read. Missing and unknown stay distinct.

**Diagnosis.** List of rule identifiers that fired, inputs those rules actually saw, and `predicted_failure`. `injected_failure_type` is absent from this object.

**Recovery.** `action` in {CONTINUE, RETRY, CLARIFY, HOLD}, `reason`, `policy_id`, `retry_index`, `timeout_hit`.

**Trace.** `run_id`, `sample_id`, stage name, duration, status, and the objects above.

## Recovery invariants

- Config sets `max_retries` and a timeout. Defaults are not infinite.
- A deterministic schema failure does not retry until the limit for lack of a new input.
- Original ASR and NLU outputs remain in the trace after a retry.
- HOLD and CLARIFY do not invent slot values.
- An exception is an infrastructure failure, not a low-confidence frame.
- CONTINUE requires the configured acceptance rules, not a missing diagnosis object.
