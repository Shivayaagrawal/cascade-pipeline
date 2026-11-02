"""Acquisition manifest checks. This module does not download audio."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

APPROVED_SPLITS = frozenset({"dev-clean", "test-clean"})
STORAGE_CAP_BYTES = 5_000_000_000
NOT_DOWNLOADED = "NOT_DOWNLOADED"
NOT_APPROVED = "NOT_APPROVED"
APPROVED = "APPROVED"
VERIFIED_LOCAL_COPY = "VERIFIED_LOCAL_COPY"
EXTRACTED = "EXTRACTED"
LOCAL_COPY_STATUSES = frozenset({VERIFIED_LOCAL_COPY, EXTRACTED})


def load_acquisition_manifest(path: Path) -> dict:
    """Read the acquisition manifest and reject a record that fails its own rules."""

    manifest = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_acquisition_manifest(manifest)
    if errors:
        raise ValueError("; ".join(errors))
    return manifest


def validate_acquisition_manifest(manifest: dict) -> list[str]:
    """Return problems for either the pre-approval record or the approved record.

    A pre-approval record must leave checksums and measured sizes empty.
    An approved record must name both splits, keep the storage cap, and carry
    measured MD5, SHA-256, and size values. ``downloaded_at`` stays null unless
    a real OpenSLR transfer time is known. This function does not invent one.
    """

    errors: list[str] = []
    if manifest.get("storage_cap_bytes") != STORAGE_CAP_BYTES:
        errors.append("storage_cap_bytes must be 5000000000")
    if manifest.get("kaggle_upload_is_approved_source") is not False:
        errors.append("kaggle upload must not be an approved source")
    archives = manifest.get("archives")
    if not isinstance(archives, list) or not archives:
        errors.append("archives must be a non-empty list")
        return errors
    seen: set[str] = set()
    parsed: list[tuple[str, dict]] = []
    for archive in archives:
        split = archive.get("split")
        if split not in APPROVED_SPLITS:
            errors.append(f"split {split!r} is not an approved split")
            continue
        if split in seen:
            errors.append(f"duplicate split {split}")
            continue
        seen.add(split)
        parsed.append((split, archive))
    if seen != APPROVED_SPLITS:
        errors.append("manifest must name dev-clean and test-clean, and no other split")

    status = manifest.get("approval_status")
    if status == NOT_APPROVED:
        errors.extend(_pending_errors(manifest, parsed))
    elif status == APPROVED:
        errors.extend(_approved_errors(manifest, parsed))
    else:
        errors.append("approval_status must be NOT_APPROVED or APPROVED")
    return errors


def _pending_errors(manifest: dict, archives: list[tuple[str, dict]]) -> list[str]:
    errors: list[str] = []
    if manifest.get("download_status") != NOT_DOWNLOADED:
        errors.append("download_status must be NOT_DOWNLOADED until an approved archive is stored")
    if manifest.get("legal_code_read") is True or manifest.get("owner_decision") == "Accepted":
        errors.append("pending manifest cannot record licence acceptance")
    for split, archive in archives:
        if archive.get("download_status") != NOT_DOWNLOADED:
            errors.append(f"{split} download_status must be NOT_DOWNLOADED")
        if archive.get("approval_status") != NOT_APPROVED:
            errors.append(f"{split} approval_status must be NOT_APPROVED")
        if archive.get("checksum") is not None or archive.get("downloaded_at") is not None:
            errors.append(f"{split} checksum and downloaded_at must stay null before download")
        if archive.get("md5") is not None or archive.get("sha256") is not None:
            errors.append(f"{split} md5 and sha256 must stay null before measurement")
        if archive.get("size_bytes_measured") is not None:
            errors.append(f"{split} size_bytes_measured must stay null before a local measurement")
    return errors


def _approved_errors(manifest: dict, archives: list[tuple[str, dict]]) -> list[str]:
    errors: list[str] = []
    if manifest.get("legal_code_read") is not True:
        errors.append("approved manifest requires legal_code_read true")
    if manifest.get("owner_decision") != "Accepted":
        errors.append("approved manifest requires owner_decision Accepted")
    if manifest.get("download_status") not in LOCAL_COPY_STATUSES:
        errors.append("approved manifest download_status must be VERIFIED_LOCAL_COPY or EXTRACTED")
    for split, archive in archives:
        if archive.get("approval_status") != APPROVED:
            errors.append(f"{split} approval_status must be APPROVED")
        if archive.get("download_status") not in LOCAL_COPY_STATUSES:
            errors.append(f"{split} download_status must be VERIFIED_LOCAL_COPY or EXTRACTED")
        if not archive.get("md5") or not archive.get("sha256"):
            errors.append(f"{split} md5 and sha256 must be measured values")
        if archive.get("size_bytes_measured") in (None, 0):
            errors.append(f"{split} size_bytes_measured must be a measured size")
        if archive.get("md5_match") is not True:
            errors.append(f"{split} official MD5 comparison must be a recorded match")
        if archive.get("downloaded_at") is not None:
            errors.append(f"{split} downloaded_at must stay null without an OpenSLR transfer time")
    return errors


def file_digests(path: Path) -> dict[str, int | str]:
    """Return size, MD5, and SHA-256 for one local file."""

    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            size += len(block)
            md5.update(block)
            sha256.update(block)
    return {"size_bytes": size, "md5": md5.hexdigest(), "sha256": sha256.hexdigest()}


def directory_size(path: Path) -> int:
    """Sum regular-file sizes under path. Missing paths count as zero."""

    if not path.exists():
        return 0
    total = 0
    for child in path.rglob("*"):
        if child.is_file() and not child.is_symlink():
            total += child.stat().st_size
    return total


def assert_within_cap(total_bytes: int, cap_bytes: int = STORAGE_CAP_BYTES) -> None:
    """Stop before stored project data can pass the cap."""

    if total_bytes > cap_bytes:
        raise RuntimeError(f"storage cap exceeded: {total_bytes} > {cap_bytes}")


def parse_md5sum(text: str) -> dict[str, str]:
    """Parse an OpenSLR ``md5sum.txt`` listing. Names stay as published."""

    found: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        found[name.strip()] = digest.strip().lower()
    return found
