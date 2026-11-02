# Phase 1D.7 blockers and open questions

**PHASE 1D.7 PREPARED. FACADE NOT AUTHORIZED. PHASE 2 STOPPED.**

No source file was edited. No experiment ran. No dataset row was written. Frozen outputs and the pilot CSV were not modified. `test-clean` was not opened. The existing test suite was not run. Frozen hashes were not recomputed in this phase.

## Open decisions

| ID | Question | Who answers | Default while unanswered |
| --- | --- | --- | --- |
| Blueprint | Accept the Phase 1D.7 documents, or name the sections to change. | User | READY_FOR_REVIEW. No code. |
| Facade | Grant or withhold the new directory and the sequence in `docs/PHASE_1D7_IMPLEMENTATION_SEQUENCE.md`. | User, in a later instruction | NOT_AUTHORIZED. |
| Phase 2 | Start or keep stopped. | User, in its own instruction | STOPPED. |
| Further synthetic data | Authorize a new version, or keep `synthetic-seed17-v1` only. | User | No new version. Candidate A–D is unused. |

## Not open, and not blockers

Real audio, a recognizer, N-best lists, a second decode, speech WER/CER, human annotation, SLURP, and a new real corpus. They are out of scope. LibriSpeech stays a historical asset.

The empty-bundle split is specified: facade `EMPTY_BUNDLE` versus the existing raise or `no_intent_evidence`. Nothing is blocked on choosing it again.

Category counts are known: 75 rows for each of the eight labels in the 600. No open question remains about whether that file is balanced by label. Severity is still not claimed to be equal.

## Known limits that stay in the report

The lexical reader does not return negation or uncertainty. Prefix CLARIFY and HOLD still attach a frame inside `run_b2`; the facade record must not promote it. The two 145/200 figures are different measures. Derived recovery labels are not human labels.
