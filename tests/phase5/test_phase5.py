"""Phase 5 unit checks. They do not score the frozen test split."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard_phase5.commit_policy_v5 import GateSwitches
from cascadeguard_phase5.critical_slot_verifier_v5 import compare_to_referent, normalize_value, support_in_candidate
from cascadeguard_phase5.modality_analyzer_v5 import analyze_modality
from cascadeguard_phase5.phase5_metrics import proportion
from cascadeguard_phase5.semantic_controller_v5 import run_semantic_v5

ROOT = Path(__file__).resolve().parents[2]
LEXICON = lexicon_from_utterances()


def _bundle(texts: list[str]) -> dict[str, object]:
    return {
        "bundle_id": "unit",
        "candidates": [
            {
                "candidate_id": f"c{index}",
                "text": text,
                "provenance": "synthetic_edit",
                "rank": index,
            }
            for index, text in enumerate(texts)
        ],
    }


def test_modality_categories_and_scope() -> None:
    assert analyze_modality("Book an appointment for April 2").modality == "AFFIRMATIVE"
    assert analyze_modality("Book an appointment for April 2").is_execution_ready is True
    assert analyze_modality("Please book an appointment for April 2").modality == "REQUEST_OR_POLITE_INSTRUCTION"
    assert analyze_modality("Please book an appointment for April 2").is_execution_ready is True
    assert analyze_modality("Cancel my appointment for Friday").modality == "AFFIRMATIVE"
    assert analyze_modality("Do not book an appointment for April 2").modality == "NEGATION"
    assert analyze_modality("Don't book an appointment for April 2").modality == "NEGATION"
    assert analyze_modality("Maybe book an appointment for April 2").modality == "UNCERTAINTY"
    assert analyze_modality("Possibly book an appointment for April 2").modality == "UNCERTAINTY"
    assert analyze_modality("I might book an appointment for April 2").modality == "UNCERTAINTY"
    assert analyze_modality("I may book an appointment for April 2").modality == "UNCERTAINTY"
    assert analyze_modality("Book an appointment for May 5").modality == "AFFIRMATIVE"
    assert analyze_modality("If needed book an appointment for April 2").modality == "CONDITIONAL"
    mixed = analyze_modality("Maybe don't book an appointment for April 2")
    assert mixed.modality == "AMBIGUOUS_OR_MIXED"
    assert mixed.confidence == 0.5
    assert mixed.is_execution_ready is False
    assert analyze_modality("").confidence == 0.0
    assert analyze_modality("Could you book an appointment for April 2").is_execution_ready is True


def test_critical_values_are_normalized_without_using_a_referent_in_the_controller() -> None:
    assert normalize_value("time", "7 AM") == "07:00"
    assert normalize_value("time", "8 AM") == "08:00"
    assert normalize_value("time", "noon") == "12:00"
    assert normalize_value("amount", "180") == "180"
    assert compare_to_referent({"date": "April 2"}, {"date": "April 3"})["status"] == "CONFLICT"
    assert compare_to_referent({"time": "7 AM"}, {"time": "8 AM"})["status"] == "CONFLICT"
    assert compare_to_referent({"amount": "180"}, {"amount": "181"})["status"] == "CONFLICT"
    assert compare_to_referent({"date": "April 2"}, {})["status"] == "MISSING"
    held = support_in_candidate({"date": "April 2"}, "Book an appointment for April 3", LEXICON)
    assert "OUT_OF_INVENTORY" in held["blocking_reasons"]
    copied = support_in_candidate({"amount": "180"}, "Transfer 181 rupees", LEXICON)
    assert copied["verified"] is False


def test_missing_and_duplicate_ids_hold_without_a_commit() -> None:
    missing = run_semantic_v5({"bundle_id": "m", "candidates": [{"candidate_id": "", "text": "Book an appointment for April 2", "provenance": "synthetic_edit"}]}, LEXICON)
    duplicate = run_semantic_v5(
        {
            "bundle_id": "d",
            "candidates": [
                {"candidate_id": "same", "text": "Book an appointment for April 2", "provenance": "synthetic_edit"},
                {"candidate_id": "same", "text": "Book an appointment for Friday", "provenance": "synthetic_edit"},
            ],
        },
        LEXICON,
    )
    assert missing["normalized"]["committed"] is False
    assert duplicate["normalized"]["action"] == "HOLD"
    assert duplicate["normalized"]["committed_frame"] is None


def test_empty_bundle_does_not_call_the_reader(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*_args, **_kwargs):
        raise AssertionError("empty bundle called the reader")

    monkeypatch.setattr("cascadeguard_phase5.semantic_controller_v5.read_candidate", fail)
    monkeypatch.setattr("cascadeguard_phase5.semantic_controller_v5.analyze_modality", fail)
    result = run_semantic_v5({"bundle_id": "empty", "candidates": []}, LEXICON)
    assert result["processors_invoked"] is False
    assert result["normalized"]["action"] == "HOLD"
    assert result["raw"]["reasons"] == ["EMPTY_BUNDLE"]
    assert result["normalized"]["committed"] is False


def test_gate_blocks_negation_uncertainty_conflict_and_keeps_raw() -> None:
    negated = run_semantic_v5(_bundle(["Book not an appointment for April 2"]), LEXICON)
    proposal = {"action": negated["raw"]["action"], "candidate_id": negated["raw"]["candidate_id"], "frame": negated["raw"]["frame"], "reasons": list(negated["raw"]["reasons"])}
    assert negated["raw"] == proposal
    assert negated["normalized"]["action"] == "HOLD"
    assert negated["normalized"]["committed"] is False
    uncertain = run_semantic_v5(_bundle(["Maybe book an appointment for April 2"]), LEXICON)
    assert uncertain["normalized"]["committed"] is False
    conflict = run_semantic_v5(
        _bundle(["Book an appointment for April 2", "Book an appointment for Friday"]),
        LEXICON,
    )
    assert conflict["normalized"]["action"] == "HOLD"
    assert conflict["normalized"]["committed_frame"] is None
    clarify = run_semantic_v5(_bundle(["Book an appointment for April 2 What is my account balance?"]), LEXICON)
    assert clarify["normalized"]["action"] == "CLARIFY"
    assert clarify["normalized"]["committed"] is False


def test_retry_emits_the_selected_id_and_a_clean_or_polite_line_can_commit() -> None:
    recovered = run_semantic_v5(
        _bundle(["Book not an appointment for April 2", "Book an appointment for April 2"]),
        LEXICON,
    )
    assert recovered["normalized"]["action"] == "RETRY"
    assert recovered["normalized"]["committed_candidate_id"] == "c1"
    assert recovered["provenance"]["provenance_status"] == "CONTROLLER_EMITTED"
    clean = run_semantic_v5(_bundle(["Book an appointment for April 2"]), LEXICON)
    assert clean["normalized"]["action"] == "CONTINUE"
    assert clean["normalized"]["committed_frame"]["slots"]["date"] == "April 2"
    polite = run_semantic_v5(_bundle(["Please book an appointment for April 2"]), LEXICON)
    assert polite["normalized"]["committed"] is True
    swapped = run_semantic_v5(_bundle(["Remind me at 8 AM"]), LEXICON)
    assert swapped["normalized"]["committed_frame"]["slots"]["time"] == "8 AM"
    unknown = run_semantic_v5(_bundle(["Book an appointment for April 3"]), LEXICON)
    assert unknown["normalized"]["committed"] is False


def test_disabled_gate_is_isolated_and_a_zero_denominator_stays_null() -> None:
    blocked = run_semantic_v5(_bundle(["Maybe book an appointment for April 2"]), LEXICON, GateSwitches(modality=False))
    assert blocked["normalized"]["committed"] is True
    opened = run_semantic_v5(_bundle(["Maybe book an appointment for April 2"]), LEXICON, GateSwitches(gate=False))
    assert opened["normalized"]["committed"] is True
    assert opened["normalized"]["blocking_reasons"] == ["GATE_DISABLED"]
    assert proportion(0, 0, "no committed decisions")["value"] is None


def test_dataset_parents_do_not_cross_splits() -> None:
    data = ROOT / "data" / "phase5"
    splits = json.loads((data / "splits.json").read_text(encoding="utf-8"))
    assert set(splits["development"]).isdisjoint(splits["validation"])
    assert set(splits["development"]).isdisjoint(splits["test"])
    assert set(splits["validation"]).isdisjoint(splits["test"])
    cases = [json.loads(line) for line in (data / "challenge_cases.jsonl").read_text(encoding="utf-8").splitlines()]
    forbidden = {"referent", "expected_action", "expected_commit", "intended_referent"}
    for case in cases:
        assert forbidden.isdisjoint(case)
        assert case["parent_utterance_id"] in splits[case["split"]]


def test_protected_phase_files_and_v4_do_not_import_phase5() -> None:
    import hashlib

    from tests.phase4.test_regression import PROTECTED

    for relative, digest in PROTECTED.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    for relative in (
        "src/cascadeguard_facade/semantic_controller_v4.py",
        "src/cascadeguard_facade/commit_policy_v4.py",
        "src/cascadeguard/evaluation/semantic_evidence.py",
    ):
        assert "cascadeguard_phase5" not in (ROOT / relative).read_text(encoding="utf-8")

    package = ROOT / "src" / "cascadeguard_phase5"
    oracle = ast.parse((package / "phase5_oracle.py").read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(oracle):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
    assert not any("semantic_controller" in name or "commit_policy" in name for name in imported)
    for path in package.glob("*.py"):
        if path.name == "phase5_oracle.py":
            continue
        text = path.read_text(encoding="utf-8")
        assert "phase5_oracle" not in text
        assert "oracle_labels" not in text
        assert "compare_to_referent" not in text or path.name == "critical_slot_verifier_v5.py"
