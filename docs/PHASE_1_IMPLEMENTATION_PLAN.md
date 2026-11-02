# Phase 1 implementation plan

**Status:** Working plan. Phase 1B dataset preparation passed. Phase 1C methodology is recorded in `docs/PHASE_1C_DATASET_SUITABILITY.md`. **Human annotation is not done, so Phase 1C is not complete.** ASR, NLU, and B0/B1/B2 are not authorized.  
**Phase 1A provenance record:** `docs/PHASE_1_DATASET_PROVENANCE.md`, decision D-LS-001. The owner accepted CC BY 4.0 and authorized `dev-clean` and `test-clean`, including extraction.  
**Still blocked:** ASR integration, NLU, B0/B1/B2 on this audio, and any LibriSpeech archive other than the two named above. Common Voice acquisition stays blocked under D-CV-007. No further synthetic selector tuning.

Phase 1 establishes a reproducible real-audio and real-ASR foundation for studying how recognition errors reach spoken language understanding. The synthetic simulation is a separate development track. Its scores are not Common Voice results and are not ASR results.

No source files, adapters, or downloads are created by this plan.

## Purpose

The simulation showed four facts that this phase has to carry forward:

| Finding | Evidence | Implication |
|---------|----------|-------------|
| Candidate information is often preserved | 147/200 complete frames in the v1 candidate lists | Candidate generation is not the only bottleneck |
| The prefix reader loses information | 1/200 complete frames on the same lists | The existing semantic reader is inadequate |
| Slot-aware selection changes the frame count | 145/200 forced exact frames on those lists | Semantic comparison is worth measuring later |
| Agreement can reinforce an error | 16/36 unsafe commits when one number-corrupted paraphrase is the only candidate | Agreement is not proof that a critical value is correct |

The paraphrase condition reached 198/200 exact frames with selective risk 0/198. That is a written-candidate condition. It is not evidence that a recognizer is robust.

Phase 1 measures real waveforms, real decoder hypotheses, and whether those hypotheses are usable for later semantic labeling. It does not claim that B0, B1, or B2 improves semantic reliability on speech.

Common Voice Scripted Speech is read speech. A completed Phase 1 measures that dataset. It does not measure robustness to spontaneous conversational speech.

## Requirements inherited from simulation v3

These are design requirements for later phases. They are not claims that the behavior has been shown on real audio.

1. A candidate list may omit critical semantic information. Report candidate oracle coverage when labels exist.
2. Intent can be right while a critical slot is wrong. Score complete frames.
3. Two or more hypotheses can agree on the same wrong critical value. Agreement does not establish correctness.
4. A missing critical slot must not be filled in from the intent.
5. Selective risk is reported together with decision coverage. An always-HOLD result is not a reliability score.
6. When a real decoder exists, RETRY is a new decoding attempt. Rescoring a written list stays labelled as simulation.
7. Decoder hypotheses stay distinct from `synthetic_edit` rows. Beam alternatives, separate decoding runs, and retries are not pooled when agreement is calculated.

Three questions stay separate:

1. **Evidence availability.** Does at least one hypothesis contain the correct semantic information?
2. **Evidence consistency.** Do the hypotheses agree on the intent and the critical slots?
3. **Evidence reliability.** Is there a reason to believe the agreed value is actually correct?

v3 measured the first two on synthetic text. The third is what a real decoder experiment has to investigate. Three hypotheses can all contain the same wrong transfer amount.

## Current gates

| Gate | Status |
|------|--------|
| Phase 0 | Complete |
| Simulation v1–v3 | Complete as controlled synthetic evaluations |
| Preservation of v1 and v2 result files | Verified in `docs/SIMULATION_EVAL_V2.md` and `docs/SIMULATION_EVAL_V3.md` |
| Revised Phase 1 plan | Accepted as the working plan |
| Phase 1 execution | Not approved |
| Common Voice terms acceptance | Pending |
| Exact dataset record in the owner’s MDC account | Pending |
| Permitted subset acquisition method | Pending |
| Storage verification of that subset against the 5 GB limit | Pending. The limit itself is already written in `docs/STORAGE_DECISION.md`. |
| Common Voice acquisition | Pending owner decision |

Licensing rows stay as they are. This plan does not mark any terms Accepted or Refused.

## Phase boundaries

| Phase | Responsibility |
|-------|----------------|
| Phase 0 | Research, paper analysis, dataset and licensing decisions |
| Simulation v1–v3 | Synthetic architecture tests and failure analysis |
| Phase 1 | Real dataset, real ASR, hypothesis provenance, semantic-evaluation readiness |
| Phase 2 | Manual annotation, NLU baseline, semantic frame evaluation |
| Phase 3 | B0 on real speech |
| Phase 4 | B1 multi-hypothesis semantic selection |
| Phase 5 | B2 failure-aware selective recovery |
| Phase 6 | Comparative experiments and statistical analysis |
| Phase 7 | Ablations, error analysis, robustness |
| Phase 8 | Paper and reproducibility package |

`docs/PHASE_WISE_IMPLEMENTATION_PLAN.md` and `docs/PHASE_PLAN.md` are earlier schedules. Where they describe Phase 1, this document replaces them. Their later-phase text is not the current boundary table above.

## 1A — Dataset access and acquisition

Dataset access is a hard gate. Do not start 1A or 1B until all of the following are true and written down: the Common Voice record is confirmed in the owner’s MDC account, the applicable terms are accepted by the owner, a permitted subset route is identified, storage of that subset is shown to fit the 5 GB limit, and the owner explicitly approves acquisition. Accepting this plan is not that approval. Until those checks pass, the repository’s dataset state stays unchanged: nothing is downloaded, and no adapter is written against a guessed schema.

Intended dataset: Mozilla Common Voice Scripted Speech v27.0 English, through Mozilla Data Collective only.

Freeze these fields only after the owner sees them in the MDC account:

- Dataset release and identifier.
- Locale. The public catalogue page showed `en`. That value is not frozen. `en-US` is not assumed.
- Archive or the permitted subset source.
- Access date and the terms that apply.
- Audio format.
- Official split structure.
- Metadata schema.

Do not download the full archive listed at 88.43 GB. The local subset limit remains 5 GB. If Mozilla does not provide a permitted way to obtain a subset inside that limit, 1A stays blocked. Do not mirror, re-host, or redistribute the corpus. Do not invent metadata. Do not start 1B from a catalogue screenshot.

**Exit:** a dataset card and an acquisition record in which identity, terms, and the permitted access path are verified by the owner.

## 1B — Dataset ingestion and validation

Starts only after 1A.

Implement:

- `common_voice_adapter.py`
- manifest generation for the acquired files
- `audio_validation.py`
- `split_validation.py`
- `dataset_report.py`

The manifest records:

| Field | Purpose |
|-------|---------|
| `sample_id` | Stable utterance identifier from the source |
| `audio_path` | Local path of a permitted file |
| `reference_text` | Human reference transcript |
| `source_split` | Official split assignment |
| `locale` | Locale taken from the confirmed record |
| `duration` | Measured duration |
| `sample_rate` | Measured sample rate |
| `validation_status` | Outcome of the audio check |
| `speaker_id` | Only if the confirmed metadata contains a speaker key and the protocol allows its use |

Do not invent speaker identifiers or split names. Preserve source identifiers. Detect duplicate bytes and corrupted audio. Account for every selected record, including rows that fail validation. Audio stays under the gitignored raw-data path.

**Exit:** every selected record is accounted for, official splits are verified, and the quality report, checksums, and reproducibility metadata are written.

## 1C — Real ASR baseline

Starts only after 1B passes.

Select one lightweight CPU-compatible decoder for this Apple M1 with 16 GB RAM. Compare license, English support, model size, RAM, CPU speed, and whether the installed build actually returns more than one hypothesis. faster-whisper may be evaluated. It is not installed, and its public example returns one text string per segment. Do not treat `beam_size` as an N-best list until that build’s return value is inspected.

The waveform has to pass through the decoder. A text edit or a synthetic hypothesis is not an ASR prediction. Text-pipeline latency is not ASR latency.

Record, from measured runs:

- Reference transcript and predicted transcript.
- WER and CER, using `docs/METRIC_DEFINITIONS.md`.
- Empty prediction rate and failed decoding rate.
- Median and p95 latency.
- Peak memory.
- Results by official split.
- Decoder name, version, and decoding parameters.

**Exit:** a prediction manifest produced by waveform decoding, with the measurements above or an explicit statement that a named metric was not run.

## 1D — Hypothesis generation and provenance

Starts only after 1C. This stage carries the v3 failure mode into the real decoder: agreement is stored, and it is not treated as correctness.

For each audio sample, keep:

- `sample_id`
- `decoder_name` and `decoder_version`
- `decoding_run_id`
- `candidate_id` and `candidate_rank`
- `candidate_text`
- `candidate_score`, when the decoder provides one
- `candidate_source`
- decoding parameters

`candidate_source` is one of:

| Value | Meaning |
|-------|---------|
| `beam_hypothesis` | Another hypothesis from the same decoding run |
| `independent_decode` | Output of a separate decoding run |
| `retry_decode` | Output of a genuine second decoding attempt |
| `synthetic_edit` | Simulation-only text change |

Do not label a synthetic edit as a decoder hypothesis. Do not pool these four sources when computing agreement. The simulation’s existing refusal to call a text edit `native_nbest` stays in force.

1D follows the installed decoder. If that backend returns one transcript, record the single hypothesis and record that beam alternatives were not returned. Do not manufacture a beam list, duplicate the one-best text, or edit it into extra candidates. `beam_hypothesis` is used only for an alternative the decoder actually returned from that run. A separate decoding run may be labelled `independent_decode` only when a written methodological reason justifies that extra run. Otherwise it is not run.

When semantic labels exist, measure candidate oracle intent coverage, slot coverage, and complete-frame coverage. Also measure candidate disagreement, candidate diversity, per-hypothesis WER, and best-of-list WER. Without labels, report the transcript measures and leave the semantic oracle blank with that reason.

**Exit:** every candidate in the hypothesis manifest has a traceable provenance value from the table above.

## 1E — Semantic evaluation readiness

Common Voice does not provide the intent and slot labels this experiment needs. Do not derive those labels from reference transcripts and call them gold.

Annotation is independent of the ASR output. Annotators label the intended meaning from the reference transcript and any permitted context. They do not treat the decoder’s predicted transcript as the meaning to label, and they do not correct the reference to match a hypothesis. Each item records ambiguity when the intended meaning is unclear. A second reviewer labels a subset. Every disagreement is recorded and then adjudicated. The guide is frozen before any larger labeling pass.

After the ASR baseline works, prepare a manual annotation pilot of 200–300 utterances. That range is a planning target, not a justified sample size. Each item can carry:

- intent
- slot names and values
- a complete semantic frame
- an ambiguity flag
- a transcript-correctness label

**Exit:** the guide and the pilot subset are reviewed and quality-controlled, with ambiguity and reviewer disagreements still visible in the record. Phase 1 ends here. It does not score B0, B1, or B2 on those labels.

## Exit criteria

Phase 1 is complete only when all of the following are true:

- Dataset access and the applicable terms are verified.
- Dataset identity and schema are frozen from the acquired record.
- A permitted subset is acquired inside the 5 GB limit.
- Dataset validation passes, with splits and checksums recorded.
- Waveform decoding has been run and measured.
- ASR predictions can be reproduced from the recorded configuration.
- Every hypothesis has a provenance value, and the decoder’s actual hypothesis interface has been verified.
- The annotation guide and pilot subset are ready.
- The test suite passes.
- A Phase 1 report covers dataset identity, storage use, validation, decoder version, measured WER and CER, latency and memory, hypothesis provenance and diversity, annotation readiness, tests, limitations, and any gate that is still open.

Completion of that report does not validate B0, B1, or B2 on real semantic labels.

## Exclusions

Phase 1 does not include:

- The full Common Voice archive.
- Re-hosting or redistribution.
- Training a custom ASR model.
- Full NLU training.
- Comparative claims for B0, B1, or B2.
- Recovery-policy optimization or threshold fitting on real or synthetic scores.
- A production deployment.
- A claim of real-world robustness.

## Approval

| Item | Status |
|------|--------|
| Phase 0 | Complete |
| Simulation v1–v3 | Complete as controlled synthetic evaluations |
| This Phase 1 plan | Accepted as the working plan |
| Phase 1 execution | Not approved |
| Common Voice acquisition | Pending owner decision |

Accepting the plan does not mark Mozilla terms Accepted, does not freeze the dataset record, and does not authorize 1A, 1B, or a download. Cursor must not start those stages from this document. Previous Phase 0 records and the simulation reports stay in place. No further synthetic selector tuning.

The next action is to verify the dataset and the acquisition conditions in Mozilla Data Collective. Until the record, terms, permitted subset route, and storage feasibility are verified, and until the owner explicitly approves acquisition, the repository and the dataset state stay unchanged. Real ASR integration follows a passing dataset validation.
