"""Phase 6 checks. They do not score the frozen test split."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard_phase6.candidate_only_adapter import run_candidate_only
from cascadeguard_phase6.critical_slot_comparator import compare_reference
from cascadeguard_phase6.evidence_contract import stripped_bundle
from cascadeguard_phase6.phase6_metrics import proportion
from cascadeguard_phase6.reference_aware_controller import ReferenceSwitches, run_reference_aware
from cascadeguard_phase6.reference_signal import critical_slot_reference, full_referent_reference

ROOT = Path(__file__).resolve().parents[2]
LEXICON = lexicon_from_utterances()


def _case(text: str, intent: str = "set_reminder", slots: dict[str, str] | None = None) -> dict[str, object]:
    return {
        "case_id": "unit",
        "candidate_bundle_id": "unit-bundle",
        "candidates": [{"candidate_id": "c0", "text": text, "provenance": "synthetic_edit", "rank": 0}],
        "referent": {"intent": intent, "slots": slots or {"time": "7 AM"}},
    }


def test_candidate_only_bundle_has_no_reference() -> None:
    case = _case("Remind me at 8 AM")
    case["reference"] = {"intent": "set_reminder"}
    bundle = stripped_bundle(case)
    assert set(bundle) == {"bundle_id", "candidates"}
    assert "reference" not in json.dumps(bundle)
    result = run_candidate_only(case, LEXICON)
    assert result["normalized"]["committed"] is True
    assert result["normalized"]["committed_frame"]["slots"]["time"] == "8 AM"


def test_reference_blocks_an_in_inventory_substitution_without_changing_v5() -> None:
    case = _case("Remind me at 8 AM")
    reference = critical_slot_reference("unit", "set_reminder", {"time": "7 AM"})
    result = run_reference_aware(case, reference, LEXICON)
    assert result["candidate_only_committed"] is True
    assert result["normalized"]["committed"] is False
    assert "REFERENCE_SLOT_CONFLICT" in result["normalized"]["blocking_reasons"]
    assert result["raw"]["action"] == "HOLD"


def test_full_transcript_cue_is_separate_from_the_slot_reference() -> None:
    case = _case("Remind me at 7 AM")
    slots = critical_slot_reference("unit", "set_reminder", {"time": "7 AM"})
    transcript = full_referent_reference("unit", "set_reminder", {"time": "7 AM"}, "Maybe remind me at 7 AM")
    assert "parent_transcript" not in slots
    assert run_reference_aware(case, slots, LEXICON)["normalized"]["committed"] is True
    held = run_reference_aware(case, transcript, LEXICON)
    assert held["normalized"]["committed"] is False
    assert "PARENT_REFERENT_NOT_EXECUTION_READY" in held["normalized"]["blocking_reasons"]


def test_missing_reference_does_not_infer_a_value() -> None:
    case = _case("Remind me at 7 AM")
    missing = run_reference_aware(case, None, LEXICON)
    assert missing["normalized"]["action"] == "HOLD"
    assert missing["normalized"]["committed"] is False
    disabled = run_reference_aware(case, None, LEXICON, ReferenceSwitches(reference=False))
    assert disabled["normalized"]["committed"] is True


def test_reference_is_not_committed_as_a_candidate() -> None:
    case = _case("Remind me at 8 AM")
    reference = critical_slot_reference("unit", "set_reminder", {"time": "7 AM"})
    result = run_reference_aware(case, reference, LEXICON)
    assert result["normalized"]["committed_candidate_id"] is None
    assert compare_reference({"intent": "set_reminder", "slots": {"time": "8 AM"}}, reference)["match"] is False


def test_oracle_and_controllers_do_not_import_each_other() -> None:
    package = ROOT / "src" / "cascadeguard_phase6"
    oracle = ast.parse((package / "phase6_oracle.py").read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(oracle):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not any("controller" in name or "adapter" in name for name in imported)
    for name in ("candidate_only_adapter.py", "reference_aware_controller.py"):
        text = (package / name).read_text(encoding="utf-8")
        assert "phase6_oracle" not in text
        assert "oracle_labels" not in text
    phase5 = (ROOT / "src" / "cascadeguard_phase5" / "semantic_controller_v5.py").read_text(encoding="utf-8")
    assert "cascadeguard_phase6" not in phase5


def test_zero_denominator_stays_null_and_splits_do_not_overlap() -> None:
    assert proportion(0, 0, "no committed decisions")["value"] is None
    splits = json.loads((ROOT / "data" / "phase6" / "splits.json").read_text(encoding="utf-8"))["split_parents"]
    assert set(splits["development"]).isdisjoint(splits["validation"])
    assert set(splits["development"]).isdisjoint(splits["test"])
    assert set(splits["validation"]).isdisjoint(splits["test"])
    pinned = json.loads((ROOT / "data" / "phase6" / "splits.json").read_text(encoding="utf-8"))["preassigned_test"]
    assert set(pinned.values()) <= set(splits["test"])
