# Repository Audit — Phase 0

**Date:** 2026-11-02.  
**Working directory:** `/Users/shivanyaagrawal/cnn/CascadeGuard`.  
**Inspection only.** No files were deleted. No dataset was downloaded. No package was installed.

## Commands and results

`pwd` printed `/Users/shivanyaagrawal/cnn/CascadeGuard`.

`git status --short --branch` and `git log -5 --oneline` both exited with `fatal: not a git repository (or any of the parent directories): .git`. There is no branch, no commit, and no tracked secret to review. Untracked-versus-modified does not apply until git is initialized. Git was not initialized in this phase.

`find . -maxdepth 3 -type f | sort` listed documentation, prompts, and 20 Cursor rule files. It did not list `src/`, `tests/`, notebooks, configs, datasets, checkpoints, or experiment outputs.

`tree -a -L 3 -I ".git|.venv|venv|__pycache__|data|artifacts"` succeeded. At audit time the tree was `.cursor/rules/`, `docs/`, `prompts/`, `AGENTS.md`, and `README.md`. This audit then added the Phase 0 documents named in the report, so a later listing is larger. No source code was added.

`python3 --version` → `Python 3.13.7`.  
`python3 -m pip --version` → `pip 26.0.1` from the Python 3.13 framework.

`uname -sm` → `Darwin arm64`.  
CPU → `Apple M1`.  
RAM → `17179869184` bytes.  
`df -h .` → about 59 GiB free on `/System/Volumes/Data` (460 GiB volume, 86% used).  
`nvidia-smi` → not available. No CUDA device was observed.

Import check on that interpreter:

| Package | Result |
|---------|--------|
| torch | not installed |
| torchaudio | not installed |
| librosa | not installed |
| numpy | 2.3.5 |
| pandas | 3.0.2 |
| scikit-learn | 1.8.0 |
| soundfile | not installed |
| pytest | 9.1.0 |
| matplotlib | not installed |

`requirements.txt`, `pyproject.toml`, `environment.yml`, `poetry.lock`, and `uv.lock` are absent. The installed versions above are system-interpreter packages, not a project lock.

`src/` is absent, so `python3 -m compileall src` was skipped.  
No `tests/` directory and no pytest config, so `python3 -m pytest -q` was not run. **No tests currently exist.** Exit code is not applicable. Passed, failed, and skipped counts are not applicable.

No linter or type checker is configured.

## What the tree is for

| Path | Role |
|------|------|
| `docs/PROJECT_SCOPE.md` | Research questions, B0/B1/B2, dataset intent |
| `docs/PHASE_PLAN.md` | 14-day schedule; CNN is optional |
| `docs/PHASE_WISE_IMPLEMENTATION_PLAN.md` | Phases 0–8; Phase 2 fundamentals are scheduled |
| `docs/PHASE_0_IMPLEMENTATION_PLAN.md` | This phase’s workstreams and exit gate |
| `.cursor/rules/` | Research and coding constraints |
| `prompts/` | Later agent prompts. Not executed as code. |

No model, notebook, script, or raw result exists to preserve.

## Technical debt

1. No version control.
2. README specifies Python 3.11. The interpreter used for the audit is 3.13.7.
3. Two schedules disagree on whether the CNN track is required. See D-001.
4. The first audit note treated Lugosch et al. 2019 as the method paper. The Phase 0 plan names Ruan et al. 2020. Both are now separated in `docs/REFERENCE_PAPER_NOTES.md`.
5. Dataset card license is still an owner decision.

## Recommended next change

Do not start the speech pipeline. After the owner clears the blockers in `docs/PHASE_0_REPORT.md`, Phase 1 may add a virtualenv, `pyproject.toml`, and the audio/data package only.
