"""Judge recovery actions. Gold labels are used only in this evaluator.

RETRY in the synthetic track is a rescore of another written variant.
It is not a second ASR decode.
"""

from __future__ import annotations

from cascadeguard.evaluation.rates import rate

SIMULATED_RETRY = "simulated_candidate_rescore"


def expected_action(
    *,
    category: str,
    one_best_ambiguous: bool,
    one_best_frame_ok: bool,
    other_candidate_frame_ok: bool,
) -> str:
    """Expected action for one synthetic 1-best condition.

    Order is fixed:
    1. Ambiguous 1-best text, or the ambiguous-transcript condition, expects CLARIFY.
    2. A 1-best frame that already matches gold expects CONTINUE.
    3. A wrong 1-best with some other candidate that matches gold expects RETRY.
       That retry is simulated. It does not call a recognizer.
    4. Otherwise the available candidates cannot support a safe frame, so HOLD.
    """

    if one_best_ambiguous or category == "ambiguous_transcript":
        return "CLARIFY"
    if one_best_frame_ok:
        return "CONTINUE"
    if other_candidate_frame_ok:
        return "RETRY"
    return "HOLD"


def action_report(rows: list[dict[str, str | bool]]) -> dict[str, object]:
    """Score action choices. Each row needs expected, actual, b0_frame_ok, b2_frame_ok, committed."""

    count = len(rows)
    matches = sum(1 for row in rows if row["expected"] == row["actual"])
    b0_wrong = [row for row in rows if row["b0_frame_ok"] is False]
    b0_right = [row for row in rows if row["b0_frame_ok"] is True]
    recovered = sum(1 for row in b0_wrong if row["b2_frame_ok"] is True)
    harmed = sum(1 for row in b0_right if row["b2_frame_ok"] is False)
    not_clarify = [row for row in rows if row["expected"] != "CLARIFY"]
    unnecessary_clarify = sum(1 for row in not_clarify if row["actual"] == "CLARIFY")
    not_hold = [row for row in rows if row["expected"] != "HOLD"]
    unnecessary_hold = sum(1 for row in not_hold if row["actual"] == "HOLD")
    expected_clarify = [row for row in rows if row["expected"] == "CLARIFY"]
    missed_clarify = sum(1 for row in expected_clarify if row["actual"] != "CLARIFY")
    committing = [row for row in rows if row["committed"] is True]
    unsafe = sum(1 for row in committing if row["b2_frame_ok"] is False)
    return {
        "action_accuracy": rate(matches, count, "no utterances"),
        "recovery_success": rate(recovered, len(b0_wrong), "B0 had no exact-frame failures"),
        "false_recovery": rate(harmed, len(b0_right), "B0 had no exact-frame successes"),
        "unnecessary_clarification": rate(
            unnecessary_clarify,
            len(not_clarify),
            "every utterance expected CLARIFY",
        ),
        "unnecessary_hold": rate(
            unnecessary_hold,
            len(not_hold),
            "every utterance expected HOLD",
        ),
        "missed_clarification": rate(
            missed_clarify,
            len(expected_clarify),
            "no utterance expected CLARIFY",
        ),
        "unsafe_commitment": rate(
            unsafe,
            len(committing),
            "no CONTINUE or simulated RETRY committed a frame",
        ),
        "retry_mechanism": SIMULATED_RETRY,
        "asr_decode": False,
    }
