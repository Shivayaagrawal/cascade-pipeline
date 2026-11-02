# Phase 6 design

Phase 6 compares two evidence conditions. It does not edit `b2_semantic_v5`.

Condition A, `b2_semantic_v5`, receives a bundle of candidate id, text, provenance, and rank. The adapter drops every other field before the call. The frozen function is `run_semantic_v5(bundle, lexicon, switches)`.

Condition B, `b2_reference_aware_v1`, calls that same function and then decides again. A v5 commit is not accepted. A candidate is committed only when its own frame, modality, provenance, and the explicit reference all pass. The reference is a second argument. It is not written into the candidate text, and it is not a candidate that can be selected.

The primary comparison is E3 versus E4: candidate-only versus the same candidates plus a critical-slot reference. E5 adds the parent transcript and is reported separately.

Mode 1 supplies intent and critical slot values. Mode 2 also supplies the parent transcript. On the frozen templates those two signals usually carry the same slot facts. They differ when the transcript contains a cue the slot record does not, such as "Maybe". One predeclared test row uses that cue. It is not a new parent in the frozen pool.

There is no weight search. The Phase 5 gates stay as they are, and the reference comparison is an additional block. Validation scores were recorded after the policy file was written. They were not used to change the switches.

A missing or partial reference is a hold. The controller does not fill in the missing value, and it does not commit the parent sentence in place of a candidate.
