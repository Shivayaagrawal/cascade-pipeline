# Phase 1D.5 risk register

**Date:** 2026-11-02  
**Rule:** nothing here is marked resolved. Severity is the effect on a claim. Uncertainty is named when a probability would be a guess.

As of the synthetic-only scope revision, rows about LibriSpeech gold, a decoder, SLURP, the storage cap for a new corpus, and operational RETRY do not block the simulation. They remain future-work risks. Treating synthetic results as speech performance is still an active risk inside this project.

| Risk | Severity | Uncertainty | Impact | Mitigation already in the protocol | Who can close it | Blocks |
| --- | --- | --- | --- | --- | --- | --- |
| Synthetic text is treated as speech | High | Certain if a paper drops the label | The claim becomes false | Track A wording in `docs/PHASE_1D3_CLAIM_ACCEPTANCE_MATRIX.md` | Authors, before any sentence is published | Real-speech claims only. Synthetic implementation can proceed later under the label. |
| Read audiobook speech stands in for commands | High | Certain for LibriSpeech | Wrong task | LibriSpeech limited to WER/CER | Owner, by choosing a task corpus | Task-speech evaluation |
| Proxy lists called N-best | High | Certain if provenance is dropped | RQ2 is misstated | `assert_synthetic_not_nbest` and the bundle source enum | Implementation owner, by keeping the check | Real N-best claims. Not the synthetic facade. |
| LibriSpeech has no intent or slot gold | High | Certain | Intent and slot metrics cannot be computed | Contract marks those fields unavailable | A task corpus, or a finished human annotation that still would not invent task intents | Semantic scores on LibriSpeech |
| Pilot unannotated | High | Certain today | No human semantic review and no agreement | CSV left `not_annotated` | A person who listens, then a second person | Phase 1C. Not the synthetic track. |
| No human recovery labels | High | Certain | Action accuracy is derived | The field is named derived | A future labelling protocol | Gold-action claims |
| Negation and uncertainty ignored | Medium | Certain in the current readers | A “not” edit can still match the frame | v3b stores `available: false` | A new reader or a listening layer, as its own decision | Any claim that those phenomena are handled |
| Simulated RETRY called a second decode | High | Certain if the mechanism string is omitted | RQ4 is overclaimed | Only `simulated_candidate_rescore` is legal today | Owner, before operational RETRY is specified | Operational RETRY. Not the simulated report. |
| Decoder not chosen | High | Open | No speech hypothesis exists | Adapter is uncalled. `beam_size=1` is specified as one string | Owner names a package, model, and device | Stage 12 |
| Model and library drift | Medium | Unknown until a decode exists | A later rerun can change text | Record package versions in the run directory | Implementation owner at stage 12 | Reproducible speech results |
| Latency quoted as ASR latency | Medium | Certain if the v3b clock is reused | The paper reports the wrong quantity | `asr_latency: false` | Authors | Speech latency claims |
| SLURP licence not accepted | High | Open decision | Acquisition would be unauthorized | Phase 1E blocked | Owner, separately for audio and text | Phase 1E |
| Storage cap | High | The real archive does not fit. Extraction size is unverified | A download would break the cap | Cap unchanged. No deletions | Owner, with a storage decision that covers extraction | Phase 1E |
| Two controllers pooled | High | Certain if one table sums their actions | The recovery result is not interpretable | Separate ids in the blueprint | Implementation owner | Any B2 comparison |
| Empty-list behavior differs by function | Medium | Certain in the source | A facade could hide a HOLD that another function would raise | Inventory records the difference | Owner chooses the facade rule without editing the functions | Stage 1 facade only |
| Prefix B2 still attaches a frame on HOLD | Medium | Certain in `run_b2` | An audit that drops `action` looks like a commit | Contract requires the action beside the text | Facade author | Stage 8 records |
| `min_support` or confidence retuned on the 200 ids | High | Not done | The frozen curve would no longer be confirmatory | Protocol forbids it | Owner would have to authorize a new sample | The current synthetic claims |
| Older Phase 1 plan wording | Low | The file still says the prefix reader is inadequate | A reader can cite it against the approved protocol | This blueprint cites the approved reader-difference wording | Documentation owner at the next blockers edit | None, if 1D.3 remains the metric authority |

Domain shift, conversational speech, and generalization beyond the ten intents remain unsupported claims. No mitigation in this repository has produced the missing evidence.
