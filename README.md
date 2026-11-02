# CascadeGuard

CascadeGuard is a completed synthetic, text-only research project. It studies how controlled transcript edits change a downstream semantic decision, and whether multi-candidate selection plus failure-aware recovery can refuse an unsafe frame.

The research question is: when the only evidence is candidate text from a closed grammar, which semantic failures can a controller detect, and which failures require an explicit reference that is not one of the candidates?

## Scope

The experiments use written transcript variants. They do not decode speech.

- No waveform decoding.
- No real ASR integration.
- No genuine ASR N-best lists.
- No WER or CER evaluation of a recognizer.
- Not a production spoken-language-understanding system.
- No independent human gold annotations.
- Results apply only to the evaluated synthetic grammar and utterance IDs.

Oracle labels are same-session specifications written with the rules under test. They are not independent human annotations. A language-model labeling pass stored under `data/manual_audit/` is exploratory and is not gold. The LibriSpeech pilot at `data/librispeech/annotations/phase_1c_pilot_30.csv` remains `not_annotated`.

Phase 5 and Phase 6 reuse the same 198 eligible synthetic parents. Phase 6 is a new case construction on that pool. It is not an independent population evaluation.

## Architecture

The grammar has ten intents and fixed slot inventories. Controllers read candidate strings. They do not read audio.

| Identity | What it does |
| --- | --- |
| `b0_prefix` | Takes the first-rank candidate. |
| `b1_prefix` | Selects among prefix candidates without a recovery policy. |
| `b2_prefix_controller` | Prefix selection plus a recovery action. |
| `b1_forced_lexical` | Forces a lexical frame. That selection is not a safety commit. |
| `b2_lexical_v3` | Lexical evidence and selective recovery. Retry rescores a supplied candidate. It does not decode speech again. |
| `b2_semantic_v4` | Adds diagnosis and commitment gates. It is not given the parent referent. |
| `b2_semantic_v5` | Stricter candidate-only gates. It emits the selected candidate id. |
| `b2_reference_aware_v1` | Calls `b2_semantic_v5` unchanged, then checks a separate reference object. The reference is not inserted into the candidate bundle. |

`b0_prefix`, `b1_prefix`, `b2_prefix_controller`, `b1_forced_lexical`, and `b2_lexical_v3` are the facade strategies. `b2_semantic_v4`, `b2_semantic_v5`, and `b2_reference_aware_v1` are separate packages. An empty candidate bundle returns `HOLD` with reason `EMPTY_BUNDLE` before those adapters run.

## Six phases

1. **Phase 1.** Synthetic baseline, metric definitions, and a LibriSpeech acquisition record. The 30-row pilot was not annotated. `test-clean` is not an input to the later experiments.
2. **Phase 2.** One facade over the five original strategies, with raw controller output kept separate from the normalized decision. The human annotation sheet was left unfinished.
3. **Phase 3.** `b2_semantic_v4` on a 40-case synthetic test. It committed 4/40, with 0 unsafe commits among those 4. Prefix and lexical baselines covered more cases and committed frames the specification marked unsafe. The selected weight cell was one of many validation ties.
4. **Phase 4.** The same v4 policy on a 120-case set whose labels were written beside the controller. Coverage was 56/120. Unsafe commits were 27/56. Path safety among commits was 29/56. In-lexicon slot substitutions were committed.
5. **Phase 5.** `b2_semantic_v5`, still without the referent. On 56 test cases it committed 23/56, with 14/23 unsafe and 9/23 native path-safe commits. The unsafe commits were the in-inventory critical substitutions in that split.
6. **Phase 6.** `b2_reference_aware_v1` on 36 test cases drawn from the same parent pool. Candidate-only v5 committed 19/36 with 9/19 unsafe. The critical-slot reference committed 11/36 with 0/11 unsafe, held all 9 in-inventory substitutions, and did not reject the 7 clean or polite controls. Removing the reference held every row, including those controls. That is blanket abstention, not useful detection.

The parent-cluster interval for the Phase 6 unsafe-commit difference, reference minus candidate-only, is −0.518 with CI −0.741 to −0.277 on 14 clusters. The coverage interval is −0.500 with CI −0.750 to −0.205. Zero observed unsafe commits among 11 commits is not a general safety guarantee.

The narrative report is `docs/CASCADEGUARD_FINAL_RESEARCH_REPORT.md`.

## Repository structure

| Path | Role |
| --- | --- |
| `src/cascadeguard/` | Prefix baselines, lexical recovery, and the synthetic grammar |
| `src/cascadeguard_facade/` | Five facade identities and `b2_semantic_v4` |
| `src/cascadeguard_phase4/` | Phase 4 evaluation |
| `src/cascadeguard_phase5/` | `b2_semantic_v5` |
| `src/cascadeguard_phase6/` | `b2_reference_aware_v1` |
| `data/synthetic/` | Shared synthetic parents, transcripts, and annotations. Local audio under `audio/` is not part of the text experiments |
| `data/phase3/` through `data/phase6/` | Frozen case sets, oracles, and split manifests |
| `experiments/` | Frozen run outputs |
| `docs/` | Phase reports and the final research report |
| `tests/` | Controller, dataset, and regression tests |

## Frozen outputs

Do not rerun an experiment into an existing directory. Do not overwrite a policy file.

| Run | Path | Policy SHA-256 |
| --- | --- | --- |
| Phase 5, authoritative | `experiments/phase5/run-20261102-stage4-scored` | `0840ee89f84553b2d345d56c141056f57428950320904b23abd11f91ac7393b9` |
| Phase 6, authoritative | `experiments/phase6/run-20261102-phase6` | `6f976bb1f01d4ba005ac1dbdb0dae1fe2ff2a02f38169d9a218d6514073e6b22` |

`experiments/phase5/run-20261102-stage4` is an earlier scoring directory. Do not cite it. The authoritative Phase 5 summary is `experiments/phase5/run-20261102-stage4-scored`.

Inspect a run by reading its `validation/frozen_policy.json` and the summary or report JSON already in that directory. Phase 6 summaries are under `experiments/phase6/run-20261102-phase6/reports/`.

Both scored runs were produced at git `f55b5bd5b74d760e00f3178a35cd9b9512fd1ccf`, before this documentation release. The controllers were not edited for the release.

## Tests

Recorded interpreter: Python 3.13.7. The synthetic tests use the standard library and `pytest`. There is no PyTorch, whisper, or ASR package requirement. From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
  --ignore=tests/test_phase1c_annotations.py \
  --deselect tests/test_phase1c_workflow.py::test_real_pilot_files_remain_unannotated \
  --deselect tests/test_librispeech_phase1b.py::test_prepared_samples_are_isolated \
  --deselect tests/test_librispeech_phase1b.py::test_project_archives_match_official_md5_when_present \
  --deselect tests/test_phase1a_metadata.py::test_librispeech_audio_stays_under_the_dataset_root
```

That command does not open `data/librispeech/processed/test-clean/sample-200.csv`, the `test-clean` archive, or the raw `test-clean` audio. The ignored annotation module and the three deselected tests are the ones that read those held-out files. They were not modified and were not run for the release check. `python3 -m pytest -q` without those exclusions is not the release command.

`pytest.ini` sets `pythonpath = src` and `testpaths = tests`.

## Limitations

- The grammar and utterance IDs are closed. A result on these rows is not a result about real ASR.
- Retry chooses another supplied string. It is not a second recognition pass.
- Same-session oracle labels can be satisfied by a checker that implements the same rules.
- Phase 6 has 36 test cases on 14 parent clusters. The confidence intervals are wide.
- An in-inventory substitution is invisible to candidate-only v5 when the substituted value is itself a legal slot value. Detecting it requires the reference value.
- A missing reference must not be treated as a successful detector. Holding every row also “detects” substitutions and rejects clean controls.
- LibriSpeech `dev-clean` and `test-clean` audio, archives, and processed sample tables stay outside git. They were not decoded for these experiments.

## Environment note

Local audio, archives, `__pycache__`, and `.pytest_cache` are ignored. The frozen text reports under `artifacts/reports/` are kept. Do not commit credentials or a new Common Voice download.
