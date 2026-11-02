"""Write synthetic manifests. Does not write Common Voice rows."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from cascadeguard.simulation.error_injector import TranscriptVariant
from cascadeguard.simulation.utterance_generator import Utterance


def write_manifests(
    utterances: list[Utterance],
    variants: list[TranscriptVariant],
    audio_paths: dict[str, str],
    root: Path,
) -> dict[str, Path]:
    """Write text manifests under data/synthetic. Audio bytes stay elsewhere."""

    synthetic = root / "data" / "synthetic"
    transcript_dir = synthetic / "transcripts"
    annotation_dir = synthetic / "annotations"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    annotation_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = synthetic / "manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "utterance_id",
                "intent",
                "text",
                "slots",
                "audio_path",
                "dataset",
                "synthetic",
            ],
        )
        writer.writeheader()
        for utterance in utterances:
            row = utterance.to_row()
            row["audio_path"] = audio_paths.get(utterance.utterance_id, "")
            writer.writerow(row)

    variant_path = transcript_dir / "variants.csv"
    with variant_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "utterance_id",
                "variant_id",
                "category",
                "text",
                "provenance",
                "synthetic",
            ],
        )
        writer.writeheader()
        for variant in variants:
            writer.writerow(variant.to_row())

    annotation_path = annotation_dir / "annotations.jsonl"
    with annotation_path.open("w", encoding="utf-8") as handle:
        for utterance in utterances:
            record = {
                "utterance_id": utterance.utterance_id,
                "intent": utterance.intent,
                "slots": utterance.slots,
                "text": utterance.text,
                "dataset": "synthetic",
                "synthetic": True,
            }
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")

    return {
        "manifest": manifest_path,
        "variants": variant_path,
        "annotations": annotation_path,
    }


def write_common_voice_placeholder(root: Path) -> Path:
    """Record that no Common Voice file has been acquired.

    The columns are project status fields. They are not a Common Voice schema.
    """

    directory = root / "data" / "common_voice"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "manifest.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["project_status", "row_count"])
        writer.writeheader()
        writer.writerow({"project_status": "not_acquired", "row_count": "0"})
    return path
