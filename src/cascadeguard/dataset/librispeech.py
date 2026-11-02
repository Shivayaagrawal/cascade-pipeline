"""LibriSpeech transcript matching and FLAC checks. No ASR is imported."""

from __future__ import annotations

import csv
import os
import re
import subprocess
import tempfile
from pathlib import Path

UTTERANCE_ID = re.compile(r"^\d+-\d+-\d+$")
MANIFEST_FIELDS = (
    "utterance_id",
    "reference_text",
    "audio_path",
    "split",
    "speaker_id",
    "chapter_id",
    "duration_seconds",
    "sample_rate",
    "channels",
    "audio_format",
    "transcript_source_path",
)


def parse_transcript_text(text: str, source: str) -> tuple[list[dict[str, str]], list[str]]:
    """Parse utterance lines. The reference text after the first space is kept."""

    rows: list[dict[str, str]] = []
    problems: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line == "":
            continue
        split_at = len(line)
        for index, character in enumerate(line):
            if character in " \t":
                split_at = index
                break
        utterance_id = line[:split_at]
        reference = line[split_at + 1 :] if split_at < len(line) else ""
        where = f"{source}:{lineno}"
        if not UTTERANCE_ID.fullmatch(utterance_id):
            problems.append(f"malformed utterance id at {where}")
            continue
        if reference == "":
            problems.append(f"empty reference text at {where}")
            continue
        speaker_id, chapter_id, _utterance = utterance_id.split("-")
        rows.append(
            {
                "utterance_id": utterance_id,
                "reference_text": reference,
                "speaker_id": speaker_id,
                "chapter_id": chapter_id,
                "transcript_source_path": source,
            }
        )
    seen: set[str] = set()
    for row in rows:
        if row["utterance_id"] in seen:
            problems.append(f"duplicate utterance id {row['utterance_id']} in {source}")
        seen.add(row["utterance_id"])
    return rows, problems


def read_flac_streaminfo(path: Path) -> dict[str, int | str | float]:
    """Read the FLAC STREAMINFO block. This does not decode audio frames."""

    with path.open("rb") as handle:
        header = handle.read(64)
    if len(header) < 42 or header[:4] != b"fLaC":
        raise ValueError(f"not a FLAC file: {path}")
    block_type = header[4] & 0x7F
    if block_type != 0:
        raise ValueError(f"STREAMINFO is not the first block: {path}")
    size = int.from_bytes(header[5:8], "big")
    if size < 34:
        raise ValueError(f"truncated STREAMINFO: {path}")
    info = header[8:42]
    sample_rate = int.from_bytes(info[10:13], "big") >> 4
    channels = ((info[12] & 0x0E) >> 1) + 1
    bits_per_sample = (((info[12] & 0x01) << 4) | (info[13] >> 4)) + 1
    total_samples = ((info[13] & 0x0F) << 32) | int.from_bytes(info[14:18], "big")
    if sample_rate <= 0 or total_samples <= 0 or bits_per_sample <= 0:
        raise ValueError(f"invalid FLAC stream info: {path}")
    return {
        "sample_rate": sample_rate,
        "channels": channels,
        "bits_per_sample": bits_per_sample,
        "total_samples": total_samples,
        "duration_seconds": total_samples / sample_rate,
    }


def decode_flac_job(path_str: str) -> str | None:
    """Decode one file in a worker process. A string keeps the job picklable."""

    work = Path(tempfile.gettempdir()) / f"cg-flac-{os.getpid()}.wav"
    try:
        decode_flac(Path(path_str), work)
    except ValueError as exc:
        return str(exc)
    return None


def decode_flac(path: Path, work_file: Path) -> None:
    """Decode one FLAC with macOS afconvert. The temporary WAV is removed."""

    work_file.parent.mkdir(parents=True, exist_ok=True)
    if work_file.exists():
        work_file.unlink()
    completed = subprocess.run(
        ["afconvert", "-f", "WAVE", "-d", "LEI16", str(path), str(work_file)],
        check=False,
        capture_output=True,
    )
    try:
        if completed.returncode != 0 or not work_file.is_file() or work_file.stat().st_size <= 44:
            detail = completed.stderr.decode("utf-8", "replace").strip()
            raise ValueError(f"FLAC decode failed: {path} {detail}")
    finally:
        if work_file.exists():
            work_file.unlink()


def collect_split(split_root: Path, split: str, repo_root: Path) -> tuple[list[dict[str, str]], list[str]]:
    """Match transcript rows to FLAC files under one extracted split."""

    problems: list[str] = []
    transcripts: list[dict[str, str]] = []
    trans_files = sorted(split_root.rglob("*.trans.txt"))
    if not trans_files:
        problems.append(f"{split} has no transcript files")
    seen: set[str] = set()
    for trans_path in trans_files:
        source = str(trans_path.relative_to(repo_root))
        rows, row_problems = parse_transcript_text(trans_path.read_text(encoding="utf-8"), source)
        problems.extend(row_problems)
        for row in rows:
            if row["utterance_id"] in seen:
                problems.append(f"duplicate utterance id {row['utterance_id']} in {split}")
            seen.add(row["utterance_id"])
            transcripts.append(row)
    flac_files = sorted(path for path in split_root.rglob("*.flac") if path.is_file())
    flac_by_id = {path.stem: path for path in flac_files}
    if len(flac_by_id) != len(flac_files):
        problems.append(f"{split} has FLAC files that share an utterance id")
    records: list[dict[str, str]] = []
    for row in transcripts:
        audio = flac_by_id.get(row["utterance_id"])
        if audio is None:
            problems.append(f"missing audio for {row['utterance_id']}")
            continue
        if audio.stat().st_size == 0:
            problems.append(f"zero-byte audio for {row['utterance_id']}")
            continue
        try:
            info = read_flac_streaminfo(audio)
        except ValueError as exc:
            problems.append(str(exc))
            continue
        if info["sample_rate"] != 16000:
            problems.append(f"{row['utterance_id']} sample rate is {info['sample_rate']}, expected 16000")
        speaker_id, chapter_id, _utterance = row["utterance_id"].split("-")
        if speaker_id != row["speaker_id"] or chapter_id != row["chapter_id"]:
            problems.append(f"speaker or chapter mismatch for {row['utterance_id']}")
        parent_names = audio.relative_to(split_root).parts
        if speaker_id not in parent_names or chapter_id not in parent_names:
            problems.append(f"path does not contain speaker and chapter for {row['utterance_id']}")
        records.append(
            {
                "utterance_id": row["utterance_id"],
                "reference_text": row["reference_text"],
                "audio_path": str(audio.relative_to(repo_root)),
                "split": split,
                "speaker_id": speaker_id,
                "chapter_id": chapter_id,
                "duration_seconds": f"{info['duration_seconds']:.6f}",
                "sample_rate": str(info["sample_rate"]),
                "channels": str(info["channels"]),
                "audio_format": "FLAC",
                "transcript_source_path": row["transcript_source_path"],
            }
        )
    transcript_ids = {row["utterance_id"] for row in transcripts}
    for utterance_id in sorted(set(flac_by_id) - transcript_ids):
        problems.append(f"missing transcript for {utterance_id}")
    return records, problems


def write_manifest(path: Path, records: list[dict[str, str]]) -> None:
    """Write a manifest. Reference text is not rewritten."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow({field: record[field] for field in MANIFEST_FIELDS})


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != MANIFEST_FIELDS:
            raise ValueError(f"unexpected manifest columns in {path}")
        return list(reader)
