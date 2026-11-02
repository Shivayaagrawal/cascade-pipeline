"""Path-safety rates. Frame match is not one of these numerators."""

from __future__ import annotations

from cascadeguard_phase4.phase4_metrics import proportion


def path_safety(rows: list[dict[str, object]]) -> dict[str, object]:
    commits = [row for row in rows if row["committed"]]
    return proportion(
        sum(bool(row["candidate_safe"]) for row in commits),
        len(commits),
        "no committed candidate paths",
    )


def unsafe_selection(rows: list[dict[str, object]]) -> dict[str, object]:
    commits = [row for row in rows if row["committed"]]
    return proportion(
        sum(not bool(row["candidate_safe"]) for row in commits),
        len(commits),
        "no committed candidate paths",
    )


def correct_candidate_commitment(rows: list[dict[str, object]]) -> dict[str, object]:
    required = [row for row in rows if row["commitment_allowed"]]
    return proportion(
        sum(row["outcome"] == "SAFE_COMMIT" for row in required),
        len(required),
        "no cases required a commitment",
    )


def action_path_consistency(rows: list[dict[str, object]]) -> dict[str, object]:
    return proportion(
        sum(row["outcome"] != "INVALID_ACTION_PATH" for row in rows),
        len(rows),
        "no cases",
    )
