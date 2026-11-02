"""Safe tar extraction for the two approved LibriSpeech archives."""

from __future__ import annotations

import tarfile
from pathlib import Path, PurePosixPath


class UnsafeArchive(ValueError):
    """The archive contains a member that must not be written."""


def reject_member_name(name: str) -> None:
    """Reject absolute paths and parent-directory traversal."""

    if not name or name.startswith("/") or name.startswith("\\"):
        raise UnsafeArchive(f"absolute or empty archive path: {name!r}")
    parts = PurePosixPath(name).parts
    if ".." in parts or any(part.startswith("/") for part in parts):
        raise UnsafeArchive(f"path traversal in archive member: {name!r}")


def member_destination(root: Path, name: str) -> Path:
    """Return the destination path, or raise if it would leave root."""

    reject_member_name(name)
    base = root.resolve()
    destination = (base / name).resolve()
    if destination != base and base not in destination.parents:
        raise UnsafeArchive(f"member escapes extraction root: {name!r}")
    return destination


def archive_member_bytes(archive_path: Path) -> int:
    """Sum regular-file sizes from the tar index. Nothing is written."""

    total = 0
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            reject_member_name(member.name)
            if member.issym() or member.islnk():
                raise UnsafeArchive(f"link member is not allowed: {member.name}")
            if member.isfile():
                total += member.size
    return total


def safe_extract(archive_path: Path, destination: Path) -> dict[str, int]:
    """Extract one archive under destination. Existing equal files are kept.

    A file that already exists with a different size is left untouched and
    reported as a conflict. Source archives are not deleted.
    """

    destination.mkdir(parents=True, exist_ok=True)
    written = 0
    kept = 0
    conflicts: list[str] = []
    with tarfile.open(archive_path, "r:gz") as archive:
        members = list(archive)
        for member in members:
            member_destination(destination, member.name)
            if member.issym() or member.islnk():
                raise UnsafeArchive(f"link member is not allowed: {member.name}")
            if not member.isfile() and not member.isdir():
                raise UnsafeArchive(f"unexpected member type: {member.name}")
        for member in members:
            target = member_destination(destination, member.name)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if target.exists():
                if target.is_file() and target.stat().st_size == member.size:
                    kept += 1
                    continue
                conflicts.append(str(target))
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise UnsafeArchive(f"unreadable member: {member.name}")
            with target.open("wb") as handle:
                while True:
                    block = source.read(1024 * 1024)
                    if not block:
                        break
                    handle.write(block)
            written += 1
    if conflicts:
        raise UnsafeArchive("refusing to overwrite existing files: " + "; ".join(conflicts))
    return {"written": written, "kept": kept}
