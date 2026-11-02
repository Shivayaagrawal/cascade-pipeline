"""Local review store for the 30-utterance pilot. It does not invent labels."""

from __future__ import annotations

import csv
from pathlib import Path

from annotation.validate_annotations import (
    JUDGMENT_FIELDS,
    NOT_ANNOTATED,
    REQUIRED_COLUMNS,
    load_rows,
    validate_rows,
)

LOCKED_FIELDS = ("utterance_id", "split", "speaker_id", "reference_text")
EDITABLE_FIELDS = tuple(field for field in REQUIRED_COLUMNS if field not in LOCKED_FIELDS)


def row_is_dirty(saved: dict[str, str], current: dict[str, str]) -> bool:
    """True when the form differs from the last saved row."""

    return any(saved.get(field, "") != current.get(field, "") for field in EDITABLE_FIELDS)


def resolve_dev_audio(repo_root: Path, relative_path: str) -> Path:
    """Return a development FLAC. Held-out paths are refused."""

    parts = Path(relative_path).parts
    if "test-clean" in parts or relative_path.startswith("/") or ".." in parts:
        raise ValueError("held-out or unsafe audio is not available in this workflow")
    if "dev-clean" not in parts or not relative_path.endswith(".flac"):
        raise ValueError("audio must be a dev-clean FLAC")
    root = (repo_root / "data" / "librispeech" / "raw" / "dev-clean").resolve()
    candidate = (repo_root / relative_path).resolve()
    if root != candidate and root not in candidate.parents:
        raise ValueError("audio path leaves the development directory")
    return candidate


class PilotWorkflow:
    """Read and save the development pilot. Source text and audio are not rewritten."""

    def __init__(self, repo_root: Path, pilot_csv: Path, dev_sample_csv: Path, heldout_csv: Path) -> None:
        self.repo_root = repo_root
        self.pilot_csv = pilot_csv
        self.rows = load_rows(pilot_csv)
        development = load_sample(dev_sample_csv)
        heldout = load_sample(heldout_csv)
        development_ids = [row["utterance_id"] for row in development]
        pilot_ids = [row["utterance_id"] for row in self.rows]
        if pilot_ids != development_ids[: len(pilot_ids)]:
            raise ValueError("pilot selection is not the development-sample prefix")
        heldout_ids = {row["utterance_id"] for row in heldout}
        if set(pilot_ids) & heldout_ids:
            raise ValueError("held-out utterance in the pilot")
        self.development_ids = set(development_ids)
        self.heldout_ids = heldout_ids
        self.source_text = {row["utterance_id"]: row["reference_text"] for row in development}
        self.audio_paths = {row["utterance_id"]: row["audio_path"] for row in development}

    def __len__(self) -> int:
        return len(self.rows)

    def completed_count(self) -> int:
        return sum(1 for row in self.rows if row["annotator_id"] != NOT_ANNOTATED)

    def public_row(self, index: int) -> dict[str, str]:
        row = self.rows[index]
        shown = {field: row[field] for field in REQUIRED_COLUMNS}
        return shown

    def audio_for(self, index: int) -> Path:
        utterance_id = self.rows[index]["utterance_id"]
        return resolve_dev_audio(self.repo_root, self.audio_paths[utterance_id])

    def save(self, index: int, fields: dict[str, str], *, listened: bool) -> None:
        """Write one human submission. A blank row is left untouched."""

        current = self.rows[index]
        updated = dict(current)
        for field in LOCKED_FIELDS:
            if fields.get(field, current[field]) != current[field]:
                raise ValueError(f"{field} cannot be changed")
        for field in EDITABLE_FIELDS:
            if field not in fields:
                raise ValueError(f"missing field {field}")
            updated[field] = fields[field]
        if not row_is_dirty(current, updated):
            raise ValueError("nothing new to save")
        if updated["annotator_id"].strip() in {"", NOT_ANNOTATED}:
            raise ValueError("annotator_id must be supplied by the reviewer")
        if not listened:
            raise ValueError("listen to the whole recording before saving a judgment")
        if updated["audio_reviewed"] != "yes":
            raise ValueError("audio_reviewed must be yes after the recording is heard")
        for field in JUDGMENT_FIELDS:
            if field == "task_intent":
                continue
            if updated[field] == NOT_ANNOTATED:
                raise ValueError(f"{field} still says not_annotated")
        if updated["proposition_summary"].strip() in {"", NOT_ANNOTATED}:
            raise ValueError("proposition_summary still says not_annotated")
        if updated["entities_explicitly_mentioned"] == NOT_ANNOTATED:
            raise ValueError("entities_explicitly_mentioned still says not_annotated")
        status = updated["task_intent_status"]
        intent = updated["task_intent"]
        if status == "not_applicable" and intent != "not_applicable":
            raise ValueError("task_intent must be not_applicable when status is not_applicable")
        if status == "genuinely_present" and intent in {"", NOT_ANNOTATED, "not_applicable"}:
            raise ValueError("a genuinely present intent needs a task_intent name")
        if status == "ambiguous" and intent != NOT_ANNOTATED:
            raise ValueError("an ambiguous task leaves task_intent not_annotated")
        if status in {"not_applicable", "ambiguous"} and updated["task_slots"] != NOT_ANNOTATED:
            raise ValueError("task_slots stay not_annotated unless a task intent is genuinely present")
        proposed = list(self.rows)
        proposed[index] = updated
        problems = validate_rows(
            proposed,
            development_ids=self.development_ids,
            heldout_ids=self.heldout_ids,
            source_text=self.source_text,
        )
        if problems:
            raise ValueError("; ".join(problems))
        self.rows = proposed
        self._write()

    def _write(self) -> None:
        with self.pilot_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS, lineterminator="\n")
            writer.writeheader()
            for row in self.rows:
                writer.writerow({field: row[field] for field in REQUIRED_COLUMNS})


def load_sample(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))
