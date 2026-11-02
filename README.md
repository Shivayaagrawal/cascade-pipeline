# CascadeGuard

CascadeGuard is a synthetic, text-only research project. It studies how controlled transcript edits change a downstream semantic decision, and whether multi-candidate selection plus failure-aware recovery can refuse an unsafe frame.

The research question is: when the only evidence is candidate text from a closed grammar, which semantic failures can a controller detect, and which failures require an explicit reference that is not one of the candidates?

## What this repository implements

- A closed grammar of ten intents and fixed slot inventories.
- Written transcript variants used as proxy candidate bundles.
- Prefix, lexical, and semantic controllers that read those candidate strings.
- A shared facade for the five original execution identities.
- Separate packages for `b2_semantic_v4`, `b2_semantic_v5`, and `b2_reference_aware_v1`.
- Same-session oracle specifications that score commit, abstention, and unsafe-commit outcomes.
- Parent-level development, validation, and test splits for Phases 3–6.
- Frozen experiment outputs, policy files, and phase reports for the completed six-phase study.

Phase 5 and Phase 6 evaluate new case constructions over the same 198 eligible synthetic parents. The narrative report is `docs/CASCADEGUARD_FINAL_RESEARCH_REPORT.md`.

## Architecture

Controllers operate on candidate text and emit a recovery action plus an optional semantic frame.

| Identity | What it does |
| --- | --- |
| `b0_prefix` | Takes the first-rank candidate. |
| `b1_prefix` | Selects among prefix candidates without a recovery policy. |
| `b2_prefix_controller` | Prefix selection plus a recovery action. |
| `b1_forced_lexical` | Forces a lexical frame. That selection is scored separately from a safety commit. |
| `b2_lexical_v3` | Lexical evidence and selective recovery. Retry rescores a supplied candidate string. |
| `b2_semantic_v4` | Diagnosis and commitment gates over candidate text alone. |
| `b2_semantic_v5` | Stricter candidate-only gates. Emits the selected candidate id. |
| `b2_reference_aware_v1` | Calls `b2_semantic_v5` unchanged, then verifies the selected frame against a separate reference object. |

`b0_prefix`, `b1_prefix`, `b2_prefix_controller`, `b1_forced_lexical`, and `b2_lexical_v3` are the facade strategies. `b2_semantic_v4`, `b2_semantic_v5`, and `b2_reference_aware_v1` live in their own packages. An empty candidate bundle returns `HOLD` with reason `EMPTY_BUNDLE` before adapters run.

## Six phases

1. **Phase 1.** Synthetic baseline, metric definitions, and the early simulation record.
2. **Phase 2.** Shared facade over the five original strategies, with raw controller output kept separate from the normalized decision.
3. **Phase 3.** `b2_semantic_v4` on a 40-case synthetic test. Coverage 4/40; unsafe commits among those commits 0/4.
4. **Phase 4.** Independent evaluation of the same v4 policy on a 120-case set. Coverage 56/120; unsafe commits 27/56; path safety 29/56.
5. **Phase 5.** `b2_semantic_v5` on 56 test cases. Coverage 23/56; unsafe commits 14/23; native path-safe commits 9/23.
6. **Phase 6.** Candidate-only v5 versus `b2_reference_aware_v1` on 36 test cases. Candidate-only: 19/36 coverage and 9/19 unsafe. Critical-slot reference: 11/36 coverage and 0/11 unsafe, with all 9 in-inventory substitutions held and all 7 clean or polite controls committed.

The parent-cluster interval for the Phase 6 unsafe-commit difference, reference minus candidate-only, is −0.518 with CI −0.741 to −0.277 on 14 clusters. The coverage interval is −0.500 with CI −0.750 to −0.205.

## Repository structure

| Path | Role |
| --- | --- |
| `src/cascadeguard/` | Prefix baselines, lexical recovery, and the synthetic grammar |
| `src/cascadeguard_facade/` | Five facade identities and `b2_semantic_v4` |
| `src/cascadeguard_phase4/` | Phase 4 evaluation |
| `src/cascadeguard_phase5/` | `b2_semantic_v5` |
| `src/cascadeguard_phase6/` | `b2_reference_aware_v1` |
| `data/synthetic/` | Shared synthetic parents, transcripts, and annotations |
| `data/phase3/` through `data/phase6/` | Frozen case sets, oracles, and split manifests |
| `experiments/` | Frozen run outputs |
| `docs/` | Phase reports and the final research report |
| `tests/` | Controller, dataset, and regression tests |

## Frozen outputs

Inspect existing runs. Write new work into a new directory.

| Run | Path | Policy SHA-256 |
| --- | --- | --- |
| Phase 5, authoritative | `experiments/phase5/run-20261102-stage4-scored` | `0840ee89f84553b2d345d56c141056f57428950320904b23abd11f91ac7393b9` |
| Phase 6, authoritative | `experiments/phase6/run-20261102-phase6` | `6f976bb1f01d4ba005ac1dbdb0dae1fe2ff2a02f38169d9a218d6514073e6b22` |

`experiments/phase5/run-20261102-stage4` is retained for history and marked superseded in that directory. Cite `run-20261102-stage4-scored`.

Read a run’s `validation/frozen_policy.json` and the summary or report JSON already present. Phase 6 summaries are under `experiments/phase6/run-20261102-phase6/reports/`.

## Tests

Recorded interpreter: Python 3.13.7. The synthetic tests use the standard library and `pytest`. From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
  --ignore=tests/test_phase1c_annotations.py \
  --deselect tests/test_phase1c_workflow.py::test_real_pilot_files_remain_unannotated \
  --deselect tests/test_librispeech_phase1b.py::test_prepared_samples_are_isolated \
  --deselect tests/test_librispeech_phase1b.py::test_project_archives_match_official_md5_when_present \
  --deselect tests/test_phase1a_metadata.py::test_librispeech_audio_stays_under_the_dataset_root
```

That command is the documented safe synthetic suite. Last recorded result: 135 passed, 4 deselected.

`pytest.ini` sets `pythonpath = src` and `testpaths = tests`.

## Labels and evaluation scope

- Oracles are same-session specifications for the synthetic grammar under test.
- Reported metrics cover the frozen case sets and utterance IDs in `data/phase3` through `data/phase6`.
- `data/manual_audit/` stores an exploratory labeling pass used only for process review.
- `data/librispeech/annotations/phase_1c_pilot_30.csv` records the unfinished pilot sheet.

## Environment

Local audio, archives, LibriSpeech processed tables, `__pycache__`, and `.pytest_cache` stay outside the tracked tree. Frozen text reports under `artifacts/reports/` are kept.
