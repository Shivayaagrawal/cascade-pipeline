"""Validate Phase 1C annotation rows. This module does not read audio."""

from __future__ import annotations

import csv
import json
from pathlib import Path

REQUIRED_COLUMNS = (
    "utterance_id",
    "split",
    "speaker_id",
    "reference_text",
    "sentence_type",
    "utterance_completeness",
    "proposition_summary",
    "semantic_coherence",
    "entities_explicitly_mentioned",
    "negation_present",
    "uncertainty_present",
    "temporal_expression_present",
    "numerical_expression_present",
    "coreference_or_context_dependency",
    "semantic_ambiguity",
    "task_intent_status",
    "task_intent",
    "task_slots",
    "annotation_confidence",
    "annotator_id",
    "annotation_notes",
    "audio_reviewed",
)

JUDGMENT_FIELDS = (
    "sentence_type",
    "utterance_completeness",
    "proposition_summary",
    "semantic_coherence",
    "negation_present",
    "uncertainty_present",
    "temporal_expression_present",
    "numerical_expression_present",
    "coreference_or_context_dependency",
    "semantic_ambiguity",
    "task_intent_status",
    "task_intent",
    "annotation_confidence",
)

ENUMS = {
    "sentence_type": {"declarative", "interrogative", "imperative", "exclamatory", "fragment", "unclear", "not_annotated"},
    "utterance_completeness": {"complete", "incomplete", "fragment", "unclear", "not_annotated"},
    "semantic_coherence": {"coherent", "internally_inconsistent", "unclear", "not_annotated"},
    "negation_present": {"present", "absent", "ambiguous", "not_annotated"},
    "uncertainty_present": {"present", "absent", "ambiguous", "not_annotated"},
    "temporal_expression_present": {"present", "absent", "ambiguous", "not_annotated"},
    "numerical_expression_present": {"present", "absent", "ambiguous", "not_annotated"},
    "coreference_or_context_dependency": {"none_observed", "context_dependent", "unclear", "not_annotated"},
    "semantic_ambiguity": {"none_observed", "lexical", "syntactic", "semantic", "context_dependent", "unclear", "not_annotated"},
    "task_intent_status": {"not_applicable", "genuinely_present", "ambiguous", "not_annotated"},
    "annotation_confidence": {"high", "medium", "low", "not_annotated"},
    "audio_reviewed": {"yes", "no", "not_performed"},
    "split": {"dev-clean", "test-clean"},
}

NOT_ANNOTATED = "not_annotated"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or tuple(reader.fieldnames) != REQUIRED_COLUMNS:
            found = tuple(reader.fieldnames or ())
            raise ValueError(f"annotation columns must be {REQUIRED_COLUMNS}, found {found}")
        return list(reader)


def validate_rows(
    rows: list[dict[str, str]],
    *,
    development_ids: set[str],
    heldout_ids: set[str],
    source_text: dict[str, str],
) -> list[str]:
    """Return problems. An unannotated row must say so in every judgment field."""

    problems: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        utterance_id = row.get("utterance_id", "")
        where = f"row {index} {utterance_id or '(missing id)'}"
        if not utterance_id:
            problems.append(f"{where}: missing utterance_id")
            continue
        if utterance_id in seen:
            problems.append(f"{where}: duplicate utterance_id")
        seen.add(utterance_id)
        if utterance_id in heldout_ids or row.get("split") == "test-clean":
            problems.append(f"{where}: held-out test utterance is not allowed in this pilot")
        if utterance_id not in development_ids:
            problems.append(f"{where}: utterance is not in the development sample")
        if row.get("split") != "dev-clean":
            problems.append(f"{where}: split must be dev-clean")
        if utterance_id in source_text and row.get("reference_text") != source_text[utterance_id]:
            problems.append(f"{where}: reference_text differs from the source manifest")
        for field, allowed in ENUMS.items():
            if field == "split":
                continue
            value = row.get(field, "")
            if value not in allowed:
                problems.append(f"{where}: {field} value {value!r} is not allowed")
        json_problem = _check_json_field(row.get("entities_explicitly_mentioned", ""), where, "entities_explicitly_mentioned")
        if json_problem:
            problems.append(json_problem)
        json_problem = _check_json_field(row.get("task_slots", ""), where, "task_slots")
        if json_problem:
            problems.append(json_problem)
        problems.extend(_check_annotation_state(row, where))
    return problems


def _check_json_field(value: str, where: str, field: str) -> str | None:
    if value == NOT_ANNOTATED:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return f"{where}: {field} is not valid JSON"
    if parsed is not None and not isinstance(parsed, list):
        return f"{where}: {field} must be a JSON list, null, or not_annotated"
    return None


def _check_annotation_state(row: dict[str, str], where: str) -> list[str]:
    problems: list[str] = []
    unannotated = row.get("annotator_id") == NOT_ANNOTATED
    judgments = [row.get(field, "") for field in JUDGMENT_FIELDS]
    entities = row.get("entities_explicitly_mentioned", "")
    slots = row.get("task_slots", "")
    if unannotated:
        if any(value != NOT_ANNOTATED for value in judgments):
            problems.append(f"{where}: an unannotated row cannot contain a judgment")
        if entities != NOT_ANNOTATED or slots != NOT_ANNOTATED:
            problems.append(f"{where}: an unannotated row cannot contain entities or slots")
        if row.get("audio_reviewed") == "yes":
            problems.append(f"{where}: audio_reviewed cannot be yes without an annotator")
        return problems
    if row.get("annotation_confidence") == NOT_ANNOTATED:
        problems.append(f"{where}: an annotated row needs a confidence value")
    if row.get("task_intent_status") == "not_applicable" and row.get("task_intent") not in {NOT_ANNOTATED, "not_applicable"}:
        problems.append(f"{where}: task_intent must stay unset when status is not_applicable")
    if row.get("task_intent_status") == "genuinely_present" and row.get("task_intent") in {"", NOT_ANNOTATED, "not_applicable"}:
        problems.append(f"{where}: a genuinely present intent needs a task_intent name")
    return problems
