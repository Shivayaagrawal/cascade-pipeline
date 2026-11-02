"""Build synthetic-semantic-challenge-v1. Expected labels come from the operators."""

from __future__ import annotations

import csv
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path

from cascadeguard.evaluation.semantic_evidence import (
    CRITICAL_SLOTS,
    intent_hits,
    lexicon_from_utterances,
    value_in_text,
)

DATASET = "synthetic-semantic-challenge-v1"
SEED = 20261103
CATEGORIES = (
    "NEGATION_SHIFT",
    "SLOT_VALUE_CORRUPTION",
    "SEMANTIC_AMBIGUITY",
    "CONTRADICTORY_EVIDENCE",
    "INCOMPLETE_EVIDENCE",
    "UNCERTAINTY_OR_MODALITY",
    "CONTEXT_DEPENDENCY",
    "FUNCTION_WORD_DAMAGE",
)
TARGET_PER_CATEGORY = 30
CATEGORY_SPLIT_TARGETS = {"development": 21, "validation": 4, "test": 5}


@dataclass(frozen=True)
class Parent:
    utterance_id: str
    intent: str
    text: str
    slots: dict[str, str]


def parse_slots(text: str) -> dict[str, str]:
    if not text.strip():
        return {}
    slots = {}
    for part in text.split("|"):
        name, value = part.split("=", 1)
        slots[name] = value
    return slots


def load_parents(manifest: Path) -> list[Parent]:
    with manifest.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [
        Parent(row["utterance_id"], row["intent"], row["text"], parse_slots(row["slots"]))
        for row in rows
    ]


def legitimate_empty_slot_intent(intent: str) -> bool:
    """True only when the grammar's critical-slot list for this intent is empty."""

    return len(CRITICAL_SLOTS[intent]) == 0


def eligible(parent: Parent) -> bool:
    """A parent may be a challenge source when every required slot is present in the text.

    An empty gold map is eligible only if that intent requires no slots. No current
    intent does, so the two frozen empty-map rows are excluded.
    """

    required = CRITICAL_SLOTS[parent.intent]
    if not required:
        return legitimate_empty_slot_intent(parent.intent)
    if not parent.slots:
        return False
    for name in required:
        value = parent.slots.get(name, "")
        if not value or not value_in_text(parent.text, value):
            return False
    return True


def assign_splits(parents: list[Parent], seed: int = SEED) -> dict[str, str]:
    """70/15/15 by rounding the two 15% cuts, remainder to development."""

    rng = random.Random(seed)
    order = [parent.utterance_id for parent in parents]
    rng.shuffle(order)
    count = len(order)
    validation_count = round(0.15 * count)
    test_count = round(0.15 * count)
    development_count = count - validation_count - test_count
    splits = {}
    for index, utterance_id in enumerate(order):
        if index < development_count:
            splits[utterance_id] = "development"
        elif index < development_count + validation_count:
            splits[utterance_id] = "validation"
        else:
            splits[utterance_id] = "test"
    return splits


def _replace_once(text: str, value: str, replacement: str) -> str | None:
    lowered = text.casefold()
    target = value.casefold()
    start = 0
    while True:
        index = lowered.find(target, start)
        if index < 0:
            return None
        end = index + len(target)
        before = index == 0 or not text[index - 1].isalnum()
        after = end == len(text) or not text[end].isalnum()
        if before and after:
            return text[:index] + replacement + text[end:]
        start = index + 1


def _other_value(lexicon: dict[str, tuple[str, ...]], slot: str, current: str) -> str:
    choices = sorted(value for value in lexicon[slot] if value.casefold() != current.casefold())
    if not choices:
        raise ValueError(f"No alternate lexicon value for {slot}")
    return choices[0]


def _primary_slot(parent: Parent) -> str:
    if parent.intent == "transfer_money":
        return "amount"
    return CRITICAL_SLOTS[parent.intent][0]


def _tidy(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _frame_preserved(parent: Parent, text: str) -> bool:
    if intent_hits(text) != (parent.intent,):
        return False
    return all(value_in_text(text, value) for value in parent.slots.values())


def build_case(category: str, parent: Parent, lexicon: dict[str, tuple[str, ...]], alternate: bool) -> dict[str, str]:
    slot = _primary_slot(parent)
    original = parent.text
    second = ""
    if category == "NEGATION_SHIFT":
        match = re.match(r"(\s*\S+)", original)
        transformed = original[: match.end()] + " not" + original[match.end() :]
        if alternate:
            second = original
    elif category == "SLOT_VALUE_CORRUPTION":
        transformed = _replace_once(original, parent.slots[slot], "other")
        if transformed is None:
            raise ValueError(parent.utterance_id)
    elif category == "SEMANTIC_AMBIGUITY":
        suffix = " Show my card transaction" if parent.intent == "check_balance" else " What is my account balance?"
        transformed = original + suffix
    elif category == "CONTRADICTORY_EVIDENCE":
        transformed = original
        second = _replace_once(original, parent.slots[slot], _other_value(lexicon, slot, parent.slots[slot]))
        if second is None:
            raise ValueError(parent.utterance_id)
    elif category == "INCOMPLETE_EVIDENCE":
        transformed = _tidy(_replace_once(original, parent.slots[slot], "") or "")
        if not transformed or transformed == original:
            raise ValueError(parent.utterance_id)
    elif category == "UNCERTAINTY_OR_MODALITY":
        transformed = f"Maybe {original}"
    elif category == "CONTEXT_DEPENDENCY":
        transformed = _replace_once(original, parent.slots[slot], "that")
        if transformed is None:
            raise ValueError(parent.utterance_id)
    elif category == "FUNCTION_WORD_DAMAGE":
        match = re.match(r"(\s*)(\S+)", original)
        transformed = match.group(1) + "banana" + original[match.end(2) :]
    else:
        raise ValueError(category)
    expected = _expected(category, parent, transformed, bool(second), alternate and category == "NEGATION_SHIFT")
    expected.update(
        {
            "parent_id": parent.utterance_id,
            "category": category,
            "original_text": original,
            "transformed_text": transformed,
            "alternate_text": second,
            "provenance": "synthetic_edit",
            "dataset": DATASET,
        }
    )
    return expected


def _expected(category: str, parent: Parent, transformed: str, has_second: bool, negation_retry: bool) -> dict[str, str]:
    slots = "|".join(f"{name}={parent.slots[name]}" for name in sorted(parent.slots))
    base = {
        "expected_intent": parent.intent,
        "expected_slots": slots,
        "expected_polarity": "affirmative",
        "expected_modality": "certain",
        "expected_completeness": "complete",
        "expected_ambiguity": "none",
        "expected_contradiction": "none",
        "expected_commit_safety": "false",
        "expected_action": "HOLD",
        "expected_reason": "INSUFFICIENT_EVIDENCE",
        "candidate_availability": "alternate" if has_second else "single",
    }
    if category == "NEGATION_SHIFT":
        base["expected_polarity"] = "negative"
        if negation_retry:
            base["expected_commit_safety"] = "true"
            base["expected_action"] = "RETRY"
            base["expected_reason"] = "ALTERNATE_CANDIDATE_AVAILABLE"
        else:
            base["expected_reason"] = "POLARITY_CONFLICT"
    elif category == "SLOT_VALUE_CORRUPTION":
        base["expected_completeness"] = "incomplete"
        base["expected_reason"] = "CRITICAL_SLOT_CONFLICT"
    elif category == "SEMANTIC_AMBIGUITY":
        base["expected_ambiguity"] = "competing"
        base["expected_completeness"] = "incomplete"
        base["expected_action"] = "CLARIFY"
        base["expected_reason"] = "AMBIGUOUS_INTENT"
    elif category == "CONTRADICTORY_EVIDENCE":
        base["expected_contradiction"] = "candidates_disagree"
        base["expected_reason"] = "CRITICAL_SLOT_CONFLICT"
    elif category == "INCOMPLETE_EVIDENCE":
        base["expected_completeness"] = "incomplete"
        base["expected_reason"] = "INCOMPLETE_FRAME"
    elif category == "UNCERTAINTY_OR_MODALITY":
        base["expected_modality"] = "uncertain"
        base["expected_reason"] = "INSUFFICIENT_EVIDENCE"
    elif category == "CONTEXT_DEPENDENCY":
        base["expected_completeness"] = "incomplete"
        base["expected_reason"] = "INSUFFICIENT_EVIDENCE"
    elif category == "FUNCTION_WORD_DAMAGE":
        if _frame_preserved(parent, transformed):
            base["expected_commit_safety"] = "true"
            base["expected_action"] = "CONTINUE"
            base["expected_reason"] = "SAFE_COMPLETE_FRAME"
        else:
            base["expected_completeness"] = "unknown"
            base["expected_reason"] = "INSUFFICIENT_EVIDENCE"
    return base


def select_cases(parents: list[Parent], splits: dict[str, str], lexicon: dict[str, tuple[str, ...]], seed: int = SEED) -> list[dict[str, str]]:
    """Continue one Random(seed) after the caller has already drawn the split with a separate Random(seed)."""

    rng = random.Random(seed)
    by_split: dict[str, list[Parent]] = {"development": [], "validation": [], "test": []}
    for parent in parents:
        by_split[splits[parent.utterance_id]].append(parent)
    cases: list[dict[str, str]] = []
    shortfalls: list[str] = []
    for category in CATEGORIES:
        for split, target in CATEGORY_SPLIT_TARGETS.items():
            pool = list(by_split[split])
            rng.shuffle(pool)
            taken = 0
            for index, parent in enumerate(pool):
                if taken >= target:
                    break
                alternate = category == "NEGATION_SHIFT" and taken % 2 == 1
                try:
                    case = build_case(category, parent, lexicon, alternate)
                except ValueError:
                    continue
                taken += 1
                case["split"] = split
                case["case_id"] = f"p3-{category.lower()}-{split[:3]}-{taken:02d}"
                cases.append(case)
            if taken < target:
                shortfalls.append(f"{category}/{split}:{taken}/{target}")
    if shortfalls:
        raise RuntimeError("Category shortfall: " + ", ".join(shortfalls))
    return cases


def write_dataset(root: Path, manifest: Path) -> dict[str, object]:
    parents = [parent for parent in load_parents(manifest) if eligible(parent)]
    excluded = [
        parent.utterance_id
        for parent in load_parents(manifest)
        if not eligible(parent)
    ]
    splits = assign_splits(parents, SEED)
    lexicon = lexicon_from_utterances()
    cases = select_cases(parents, splits, lexicon, SEED)
    destination = root / "data" / "phase3"
    destination.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "parent_id",
        "split",
        "category",
        "original_text",
        "transformed_text",
        "alternate_text",
        "expected_intent",
        "expected_slots",
        "expected_polarity",
        "expected_modality",
        "expected_completeness",
        "expected_ambiguity",
        "expected_contradiction",
        "expected_commit_safety",
        "expected_action",
        "expected_reason",
        "candidate_availability",
        "provenance",
        "dataset",
    ]
    with (destination / "challenge_cases.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cases)
    (destination / "splits.json").write_text(
        json.dumps(
            {
                "seed": SEED,
                "method": "Shuffle eligible parent ids with random.Random(seed). validation and test are round(0.15 * n). The remainder is development.",
                "eligible_parent_count": len(parents),
                "excluded_parent_ids": excluded,
                "exclusion_rule": "Empty gold slot maps are included only when CRITICAL_SLOTS for that intent is empty. It is not empty for any intent.",
                "counts": {name: sum(split == name for split in splits.values()) for name in ("development", "validation", "test")},
                "parents": splits,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (destination / "transformation_metadata.json").write_text(
        json.dumps(
            {
                "dataset": DATASET,
                "seed": SEED,
                "label_source": "deterministic_transformation",
                "llm_labels_used_as_gold": False,
                "categories": list(CATEGORIES),
                "operators": {
                    "NEGATION_SHIFT": "Insert ' not' after the first token. Odd selected rows in each split also keep the parent text as an alternate candidate.",
                    "SLOT_VALUE_CORRUPTION": "Replace the primary critical slot span with the placeholder other.",
                    "SEMANTIC_AMBIGUITY": "Append a second closed-grammar request that adds a different intent.",
                    "CONTRADICTORY_EVIDENCE": "Pair the parent text with a copy whose primary critical value is the first other lexicon value.",
                    "INCOMPLETE_EVIDENCE": "Delete the primary critical slot span.",
                    "UNCERTAINTY_OR_MODALITY": "Prefix 'Maybe '.",
                    "CONTEXT_DEPENDENCY": "Replace the primary critical slot span with that. Weather it is not the dependency.",
                    "FUNCTION_WORD_DAMAGE": "Replace the first token with banana.",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    counts: dict[str, int] = {}
    for case in cases:
        counts[case["category"]] = counts.get(case["category"], 0) + 1
    summary = {
        "dataset": DATASET,
        "cases": len(cases),
        "category_counts": counts,
        "excluded_parent_ids": excluded,
        "split_counts": {name: sum(split == name for split in splits.values()) for name in ("development", "validation", "test")},
    }
    (destination / "manifest.csv").write_text(
        "dataset,version,cases,seed\n"
        f"{DATASET},v1,{len(cases)},{SEED}\n",
        encoding="utf-8",
    )
    return summary
