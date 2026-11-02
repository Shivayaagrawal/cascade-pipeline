# Phase 1D.2 research claims register

**Date:** 2026-11-02  
**Rule:** a claim may use only the allowed wording. The evidence column is not permission to broaden it.

| Research claim | Current evidence | Allowed wording | Evidence still needed |
| --- | --- | --- | --- |
| Selective commitment can refuse an incomplete synthetic frame | v3 commits 145/200 on the v1 list and leaves the rest uncommitted. Risk among commits is 3/145. | On this closed grammar and these written variants, agreement plus a complete slot frame commits 145 of 200 utterances, with 3 unsafe commits. | Task speech, a recognizer, and a held-out split not used to choose the rule. |
| The three unsafe commits are reminder times | v3b log: `utt-121` 8 AM against 7 AM, `utt-124` 6 PM against 5 PM, `utt-129` 3 PM against 2 PM. | In the synthetic list, the three unsafe commits replace one closed-grammar time with another. | A speech set where the gold time is independent of this grammar. |
| Multi-candidate comparison helps | Frozen B1 prefix exact frame is 1/200. The v3 forced selector reaches 145/200 and always answers. The selective layer reaches 142/200 correct frames if abstention counts as wrong. | On these proxy candidates, the lexical selector finds more exact frames than the prefix selector. The forced selector is not a safety result. | Genuine N-best lists from a decode. |
| RETRY repairs errors | The published recovery condition uses a second written bundle and records 198 simulated retries with selective risk 0/198. The v1 list itself has RETRY 0. | When a second written bundle is supplied, the v3 rule can commit that bundle. The mechanism is `simulated_candidate_rescore`. | An operational second decode. |
| The system understands speech | No B0/B1/B2 result comes from a waveform decode. | Not supported. | Authorized audio, a decode, and task gold. |
| LibriSpeech measures task understanding | References exist. The 30-row pilot is `not_annotated`. | LibriSpeech can support WER and CER after a decode. It does not provide intent or slot gold. | A task-oriented set, or a completed human annotation that still would not create task intents the audio does not contain. |
| Read speech stands in for commands | LibriSpeech is read audiobook speech. The synthetic set is prompted commands generated as text. | These are different speaking conditions. | Conversational or commanded speech with gold frames. |
| Proxy candidates are N-best | Provenance is `synthetic_edit`. The code rejects `native_nbest` for those strings. | The candidates are written variants. | A recognizer’s ordered list, stored as `native_nbest`. |
| Negation and uncertainty are handled | v3b marks both unavailable. A candidate can contain “not” and still receive no negation finding. | The current reader does not return negation or uncertainty. | A reader or a human layer that records them after listening. |
| Recovery actions have gold labels | Expected actions are computed from the gold frame and the strings. | The expected action is an evaluation rule, not a human or dataset label. | A protocol and labels for when CONTINUE, RETRY, CLARIFY, or HOLD was the right action. |
| Annotators agree | One pilot exists and is unannotated. v3b is one audit of one frozen run. | Agreement has not been measured. | Two independent annotators, compared before adjudication. |
| Results generalize beyond this grammar | Ten synthetic intents and the written edits. | The result is limited to that grammar and those edits. | Another domain, other speakers, and a sealed test. |
| SLURP is approved | Suitability 85/100. Acquisition not approved. | SLURP is the preferred candidate and is not authorized. | Licence acceptance, a storage decision, and Phase 1E. |

Synthetic v1, v2, v3, and v3b remain valid inside the wording in this table. They do not become speech results if the dataset decision stays unresolved.
