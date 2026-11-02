"""Existing functions keep their empty-input behavior. The sample does not edit sources."""

import hashlib
from pathlib import Path

import pytest

from cascadeguard.candidates.candidate_manager import select_candidate
from cascadeguard.evaluation.selective import decide_selective, forced_selection
from cascadeguard_facade.manual_audit import load_tables, select_ids, write_audit

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/synthetic/manifest.csv"
VARIANTS = ROOT / "data/synthetic/transcripts/variants.csv"


def test_existing_empty_input_behavior_is_unchanged() -> None:
    with pytest.raises(ValueError, match="empty"):
        select_candidate(())
    with pytest.raises(ValueError, match="empty"):
        forced_selection([], {})
    decision = decide_selective([], {})
    assert decision.action.value == "hold"
    assert decision.reason == "no_intent_evidence"


def test_sample_is_three_per_intent_and_reproducible() -> None:
    gold, variants = load_tables(MANIFEST, VARIANTS)
    first = select_ids(gold, 20261102)
    second = select_ids(gold, 20261102)
    assert first == second
    assert len(first) == 10
    assert all(len(ids) == 3 for ids in first.values())
    flat = [utterance_id for ids in first.values() for utterance_id in ids]
    assert len(flat) == len(set(flat)) == 30
    grouped: dict[str, set[str]] = {}
    for row in variants:
        grouped.setdefault(row["utterance_id"], set()).add(row["variant_id"])
    for utterance_id in flat:
        assert utterance_id in grouped
        assert grouped[utterance_id]


def test_write_audit_matches_source_variants_and_leaves_sources(tmp_path: Path) -> None:
    before_manifest = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    before_variants = hashlib.sha256(VARIANTS.read_bytes()).hexdigest()
    summary = write_audit(tmp_path, MANIFEST, VARIANTS, 20261102)
    assert hashlib.sha256(MANIFEST.read_bytes()).hexdigest() == before_manifest
    assert hashlib.sha256(VARIANTS.read_bytes()).hexdigest() == before_variants
    assert summary["gold_rows"] == 30
    counts = summary["variant_counts"]
    assert isinstance(counts, dict)
    gold, variants = load_tables(MANIFEST, VARIANTS)
    selected = set(summary["utterance_ids"])
    from collections import Counter

    expected = Counter(row["utterance_id"] for row in variants if row["utterance_id"] in selected)
    assert counts == dict(expected)
    sheet = (tmp_path / "annotations.csv").read_text(encoding="utf-8")
    assert "human_intent" in sheet.splitlines()[0]
    assert "gold_intent" not in sheet.splitlines()[0]
    assert ",pending" in sheet or sheet.count("pending") == 30 + sum(expected.values())
    comparison = (tmp_path / "comparison_report.json").read_text(encoding="utf-8")
    assert '"comparison_performed": false' in comparison
