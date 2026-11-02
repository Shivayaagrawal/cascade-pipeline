# Phase 6 evidence contract

| Evidence | Candidate-only | Critical-slot reference | Full transcript | Oracle only |
| --- | --- | --- | --- | --- |
| Candidate text, id, provenance, rank | yes | yes | yes | yes |
| Slots read from that candidate | yes | yes | yes | yes |
| Intent and critical values as a separate object | no | yes | yes | yes |
| Parent transcript | no | no | yes | yes |
| Expected action, commitment, or path | no | no | no | yes |

`stripped_bundle()` copies only `bundle_id` and the four candidate fields. Condition A is that object passed to the frozen controller.

The critical-slot object has `reference_id`, `reference_source` `authorized_synthetic_parent`, `reference_scope` `critical_slots`, `intent`, `critical_slots`, and `reference_provenance` `EXPLICIT`. It has no parent transcript.

The full-referent object adds `parent_transcript` and sets `reference_scope` to `full_referent`. For ordinary cases the transcript is the frozen parent sentence. For `parent_transcript_cue` it is `Maybe` plus that sentence. The slot values stay the same, so the extra hold, when it happens, comes from the transcript cue.

Oracle labels live in `oracle_labels.jsonl`. Neither controller imports `phase6_oracle` or reads that file. The reference file is opened by the reference-aware runner only.

A commit requires a candidate id that is in the bundle, a provenance value the bundle accepts, an execution-ready modality under the active switches, required slots supported by that candidate's text, and, when the reference check is on, normalized critical values equal to the authorized reference. HOLD and CLARIFY do not commit. The reference itself cannot be committed.

This separation is a module boundary. The specification and the checker were written in the same session. That is not human gold.
