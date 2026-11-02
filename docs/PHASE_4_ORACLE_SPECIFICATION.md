# Phase 4 oracle specification

Version `phase4-oracle-v1`. Input: rank-ordered candidate texts and a referent intent with slots. Output: the fields in `oracle_labels.jsonl`.

## Reading one string

Tokens are alphanumeric spans. A candidate is negative when it contains the token `not`. `cancel` does not make a request negative. Modality is conditional when the token `if` is present, uncertain when `maybe`, `possibly`, or `might` is present, and certain when an intent is present and neither of those holds. `please` does not change modality.

`that` is context. `it` is context only when `rain` is absent, so `Will it rain Friday?` is not context. The hedges are `about`, `around`, `roughly`, `after`, `before`, and `instead`.

A string expresses the referent only when it is affirmative, certain, not contextual, not hedged, has that single intent, contains each required function token, and carries exactly the referent's slot values. Required tokens include `for` for booking and cancellation, `my` for cancellation, appointment checks, balance, and transactions, `at` for reminders, and `your` for general information.

## Bundle decision

1. No candidates: `HOLD`, reason `EMPTY_BUNDLE`.
2. Any string with two intents: `CLARIFY`.
3. Two or more affirmative, certain, complete frames that disagree: `HOLD`. No candidate is safe, including a copy of the referent.
4. Otherwise the safe ids are the strings that express the referent. `CONTINUE` if the first is safe. `RETRY` the earliest safe id otherwise. `HOLD` if none are safe.

The expected frame remains the referent. A commit of a different value is an incorrect frame. A commit of the referent frame from a candidate that is not in the safe set is a correct frame on an unsafe path.

Labels are recomputed by `scripts/validate_phase4_oracle.py` and compared with the frozen file.
