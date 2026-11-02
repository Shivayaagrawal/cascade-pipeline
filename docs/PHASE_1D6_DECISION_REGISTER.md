# Phase 1D.6 decision register

**Date:** 2026-11-02  
**Communicated at:** 17:51 +05:30.  
**Implementation:** not authorized.

| ID | Decision | Status |
| --- | --- | --- |
| S1 | The current project is a synthetic, text-only simulation of transcript corruption and selective semantic recovery. It is not a recognizer and not a production SLU system. | Decided |
| S2 | Active systems are `b0_prefix`, `b1_prefix`, `b1_forced_lexical`, `b2_prefix_controller`, and `b2_lexical_v3`. The two controllers stay in separate tables. | Decided |
| S3 | The dataset for those systems is `synthetic-seed17-v1`: 200 gold utterances and 600 `SYNTHETIC_PROXY` edits, plus the already published paraphrase, slot-removed, and split lists. Nothing in that set is replaced. | Decided |
| S4 | Another synthetic version requires its own authorization, version id, seed, and directory. The Candidate A–D role names belong only to such a future version. | Decided. No new version is authorized. |
| S5 | Lexical RETRY remains `simulated_candidate_rescore`. Prefix RETRY remains rescoring of an already written alternative. | Decided |
| S6 | CLARIFY is an action record. A question string is not required. HOLD does not commit a frame. | Decided |
| S7 | A future facade maps an empty bundle to HOLD / `EMPTY_BUNDLE` and does not change `select_candidate`, `forced_selection`, `decide_selective`, or `run_b2`. | Decided as a contract. The facade is not built. |
| S8 | Prefix confidence and `min_support` stay as they are. No new selector. | Decided |
| S9 | New facade code, when authorized, lives in a new directory and does not change frozen functions or frozen outputs. | Decided as a constraint. Authorization is S11. |
| S10 | Real audio decoding, recognizer integration, genuine N-best lists, operational second decoding, speech WER/CER, human audio annotation, conversational generalization, production deployment, SLURP, and any new real corpus are future work. LibriSpeech stays a historical asset. | Decided |
| S11 | Implementation of the facade (Phase 1E-S) and the later validation report (Phase 1F-S) wait for a separate authorization in Phase 1D.7. | Open |
| S12 | Phase 2 stays stopped until its own authorization. | Open, and out of the current sequence |

Phase 1D.5 decisions D1 through D6 are superseded by this register. D1’s alternative, waiting for a task corpus before the project can proceed, is closed. The corpus is out of scope. The facade still waits on S11.
