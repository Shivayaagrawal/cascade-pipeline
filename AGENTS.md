# CascadeGuard — Engineering and Research Instructions

This repository is a completed synthetic, text-only research project. Controllers read written transcript variants from a closed grammar. They do not decode speech, and they are not a production spoken-language-understanding system.

All contributors and coding agents must follow:

1. The research objectives in `docs/CASCADEGUARD_FINAL_RESEARCH_REPORT.md` and `docs/PROJECT_SCOPE.md`.
2. The approved methodology and the frozen experiment record.
3. All applicable rules in `.cursor/rules/`.
4. The dataset and licensing requirements.
5. The experiment reproducibility requirements.

## Non-negotiable principles

- Never fabricate data, metrics, model outputs, or research findings.
- Never silently deviate from the approved research methodology.
- Never introduce train-test leakage.
- Never tune on the test set.
- Never conceal negative results.
- Never claim improvement without measured evidence.
- Never call synthetic corruption a natural ASR error distribution.
- Never claim exact paper reproduction without verifying methodological equivalence.
- Never treat same-session oracle labels as independent human gold.
- Never claim real-speech robustness from these synthetic results.
- Never overwrite a frozen experiment directory or policy file.
- Never introduce unnecessary model complexity.
- Never remove baseline implementations to make a proposed method appear better.

## Development workflow

Before implementing:
1. Read relevant documentation.
2. Inspect existing code.
3. Identify dependencies and interfaces.
4. Define acceptance criteria.

After implementing:
1. Run the documented safe synthetic test command from `README.md`.
2. Validate output schemas.
3. Check research alignment.
4. Record experiment changes in a new directory. Do not overwrite an existing run.
5. Report unverified assumptions.

## Priority

Research validity > reproducibility > correctness > maintainability > performance optimization > convenience.

If requirements conflict, do not silently choose. Explain the conflict and request clarification.
