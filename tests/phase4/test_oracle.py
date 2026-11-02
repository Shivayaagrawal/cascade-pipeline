"""Hand-built fixtures for the oracle. These strings are not produced by the dataset builder."""

from __future__ import annotations

import ast
from pathlib import Path

from cascadeguard_phase4.independent_oracle import judge

INVENTORY = {
    "date": ("tomorrow", "Friday"),
    "amount": ("1000", "500", "100"),
    "currency": ("rupees",),
    "genre": ("jazz",),
    "account": ("savings account", "account"),
    "recency": ("yesterday",),
    "time": ("6 PM",),
    "topic": ("Saturday hours",),
}


def _candidate(identifier: str, text: str, rank: int = 0) -> dict[str, str]:
    return {"candidate_id": identifier, "text": text, "rank": str(rank)}


def _label(candidates, intent, slots):
    return judge(candidates, {"intent": intent, "slots": slots}, INVENTORY)


def test_negative_request_is_not_a_booking():
    label = _label(
        [_candidate("n", "Do not book an appointment for tomorrow")],
        "book_appointment",
        {"date": "tomorrow"},
    )
    assert label["expected_polarity"] == "negative"
    assert label["expected_action"] == "HOLD"
    assert label["expected_commitment"] is False
    assert label["expected_safe_candidates"] == []


def test_retry_uses_the_affirmative_candidate_only():
    label = _label(
        [
            _candidate("bad", "Transfer not 500 rupees", 0),
            _candidate("good", "Transfer 500 rupees", 1),
        ],
        "transfer_money",
        {"amount": "500", "currency": "rupees"},
    )
    assert label["expected_action"] == "RETRY"
    assert label["expected_safe_candidates"] == ["good"]


def test_possibly_and_if_are_not_certain():
    possible = _label(
        [_candidate("p", "Possibly transfer 500 rupees")],
        "transfer_money",
        {"amount": "500", "currency": "rupees"},
    )
    conditional = _label(
        [_candidate("c", "If needed transfer 500 rupees")],
        "transfer_money",
        {"amount": "500", "currency": "rupees"},
    )
    assert possible["expected_modality"] == "uncertain"
    assert conditional["expected_modality"] == "conditional"
    assert possible["expected_commitment"] is False
    assert conditional["expected_commitment"] is False


def test_please_is_not_uncertainty_and_cancel_is_not_negation():
    please = _label(
        [_candidate("p", "Please transfer 500 rupees")],
        "transfer_money",
        {"amount": "500", "currency": "rupees"},
    )
    cancel = _label(
        [_candidate("c", "Cancel my appointment for Friday")],
        "cancel_appointment",
        {"date": "Friday"},
    )
    assert please["expected_modality"] == "certain"
    assert please["expected_action"] == "CONTINUE"
    assert cancel["expected_polarity"] == "affirmative"
    assert cancel["expected_action"] == "CONTINUE"


def test_mutated_amount_and_conflict_are_not_committable():
    mutated = _label(
        [_candidate("m", "Transfer 1000 rupees")],
        "transfer_money",
        {"amount": "500", "currency": "rupees"},
    )
    conflict = _label(
        [
            _candidate("a", "Transfer 500 rupees", 0),
            _candidate("b", "Transfer 100 rupees", 1),
        ],
        "transfer_money",
        {"amount": "500", "currency": "rupees"},
    )
    assert mutated["expected_action"] == "HOLD"
    assert conflict["expected_contradiction"] == "present"
    assert conflict["expected_safe_candidates"] == []


def test_ambiguity_incompleteness_context_and_hedge():
    ambiguous = _label(
        [_candidate("a", "Book an appointment for tomorrow What is my account balance?")],
        "book_appointment",
        {"date": "tomorrow"},
    )
    incomplete = _label(
        [_candidate("i", "Book an appointment for")],
        "book_appointment",
        {"date": "tomorrow"},
    )
    context = _label(
        [_candidate("c", "Book an appointment for that")],
        "book_appointment",
        {"date": "tomorrow"},
    )
    hedge = _label(
        [_candidate("h", "Transfer about 500 rupees")],
        "transfer_money",
        {"amount": "500", "currency": "rupees"},
    )
    weather = _label(
        [_candidate("w", "Will it rain Friday?")],
        "weather_query",
        {"date": "Friday"},
    )
    assert ambiguous["expected_action"] == "CLARIFY"
    assert incomplete["expected_completeness"] == "incomplete"
    assert context["expected_action"] == "HOLD"
    assert hedge["expected_commitment"] is False
    assert weather["expected_action"] == "CONTINUE"


def test_empty_bundle_and_unknown_request():
    empty = _label([], "book_appointment", {"date": "tomorrow"})
    unknown = _label([_candidate("u", "Schedule it")], "book_appointment", {"date": "tomorrow"})
    assert empty["expected_action"] == "HOLD"
    assert empty["expected_reason"] == "EMPTY_BUNDLE"
    assert unknown["expected_polarity"] == "unknown"
    assert unknown["expected_commitment"] is False


def test_oracle_module_does_not_import_controller_code():
    source = Path("src/cascadeguard_phase4/independent_oracle.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    forbidden = [
        name
        for name in imported
        if name.startswith("cascadeguard_facade") or name.startswith("cascadeguard.")
    ]
    assert forbidden == []
