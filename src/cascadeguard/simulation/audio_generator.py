"""Local macOS text-to-speech. No network and no external dataset."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AudioInfo:
    path: Path
    format_name: str
    sample_rate_hz: int
    duration_seconds: float
    channels: int


def synthesize(text: str, destination: Path) -> AudioInfo:
    """Write one AIFF file with the macOS `say` command."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    completed = subprocess.run(
        ["say", "-o", str(destination), text],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "macOS say failed")
    return inspect_audio(destination)


def inspect_audio(path: Path) -> AudioInfo:
    """Read format, rate, and duration with `afinfo`. Fail on empty or missing files."""

    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size == 0:
        raise ValueError(f"Empty audio file: {path}")
    completed = subprocess.run(
        ["afinfo", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"afinfo failed for {path}")
    report = completed.stdout
    format_match = re.search(r"Data format:\s+(\d+)\s+ch,\s+(\d+)\s+Hz", report)
    duration_match = re.search(r"estimated duration:\s+([0-9.]+)\s+sec", report)
    file_match = re.search(r"File type ID:\s+(\S+)", report)
    if format_match is None or duration_match is None:
        raise ValueError(f"Could not read audio metadata for {path}")
    duration = float(duration_match.group(1))
    if duration <= 0:
        raise ValueError(f"Non-positive duration for {path}")
    return AudioInfo(
        path=path,
        format_name=file_match.group(1) if file_match else "unknown",
        sample_rate_hz=int(format_match.group(2)),
        duration_seconds=duration,
        channels=int(format_match.group(1)),
    )
