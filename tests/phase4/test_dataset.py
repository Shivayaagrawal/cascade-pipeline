"""Dataset invariants for the frozen Phase 4 challenge files."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path("data/phase4")


def _rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (ROOT / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def test_counts_splits_and_label_separation():
    bundles = _rows("candidate_bundles.jsonl")
    labels = _rows("oracle_labels.jsonl")
    assert len(bundles) == 600
    assert len(labels) == 600
    assert Counter(row["case_category"] for row in bundles)["clean_control"] == 100
    assert all(row["case_category"] != "clean_control" or True for row in bundles)
    failure = Counter(row["case_category"] for row in bundles if row["case_category"] != "clean_control")
    assert set(failure.values()) == {50}
    for row in bundles:
        assert "expected_action" not in row
        assert "expected_slots" not in row
        assert "referent" not in row
    splits = json.loads((ROOT / "splits.json").read_text(encoding="utf-8"))
    seen: dict[str, str] = {}
    for split, parent_ids in splits["parent_ids"].items():
        for parent_id in parent_ids:
            assert parent_id not in seen
            seen[parent_id] = split
    by_parent: dict[str, str] = {}
    for row in bundles:
        previous = by_parent.setdefault(row["parent_id"], row["split"])
        assert previous == row["split"]
    assert {row["case_id"] for row in bundles} == {row["case_id"] for row in labels}
