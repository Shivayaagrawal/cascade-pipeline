# Phase 4 evaluation metrics

A commit is a returned intent. `HOLD` and `CLARIFY` do not commit. Forced lexical selection does not commit; its exact-frame figure is `forced_exact_frame_accuracy`.

| Metric | Numerator | Denominator |
| --- | --- | --- |
| Coverage | Commits | All cases |
| Selective risk | Commits whose frame differs from the referent | Commits |
| Unsafe-commit rate | `UNSAFE_COMMIT` and `CORRECT_FRAME_UNSAFE_PATH` | Commits |
| Path safety | Commits whose candidate id is in the oracle safe set | Commits |
| Safe-commitment accuracy | `SAFE_COMMIT` | Commits |
| Correct candidate commitment | `SAFE_COMMIT` | Cases the oracle allows |
| Unnecessary abstention | `UNNECESSARY_ABSTENTION` | Cases the oracle allows |
| Exact frame | Frame matches the referent | All cases |
| Critical-slot safety | `SAFE_COMMIT` among mutation, conflict, and contradiction commits | Those commits |

A zero denominator is null, with a reason. Abstention is not an unsafe commit and is not a selective error.

Wilson intervals use z = 1.959963984540054. Paired differences resample parent ids, keeping every case of a drawn parent together. The stored H2 contrast is the per-case indicator "this case was a safe commit." The path-safety rate among commits is reported separately because abstention would otherwise look like an unsafe path.

Prefix strategies have no recovery action. An always-answer commit is not marked `INVALID_ACTION_PATH`. `HOLD` or `CLARIFY` with a frame is invalid. `RETRY` or `CONTINUE` without a bundle id is invalid.

Outcomes are exactly one of `SAFE_COMMIT`, `UNSAFE_COMMIT`, `SAFE_ABSTENTION`, `UNNECESSARY_ABSTENTION`, `INVALID_ACTION_PATH`, `INCORRECT_FRAME`, and `CORRECT_FRAME_UNSAFE_PATH`.
