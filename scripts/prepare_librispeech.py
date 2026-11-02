"""Copy, verify, extract, and manifest the two authorized LibriSpeech archives.

This script does not download the archives and does not run ASR.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cascadeguard.dataset.acquisition import (  # noqa: E402
    EXTRACTED,
    STORAGE_CAP_BYTES,
    VERIFIED_LOCAL_COPY,
    assert_within_cap,
    directory_size,
    file_digests,
    parse_md5sum,
)
from cascadeguard.dataset.extract import archive_member_bytes, safe_extract  # noqa: E402
from cascadeguard.dataset.librispeech import (  # noqa: E402
    collect_split,
    decode_flac_job,
    write_manifest,
)
from cascadeguard.dataset.sampling import DEFAULT_SEED, DEVELOPMENT_PILOT, order_utterances  # noqa: E402

DOWNLOADS = {
    "dev-clean": Path.home() / "Downloads" / "dev-clean.tar.gz",
    "test-clean": Path.home() / "Downloads" / "test-clean.tar.gz",
}
DECLARED_URLS = {
    "dev-clean": "https://openslr.trmal.net/resources/12/dev-clean.tar.gz",
    "test-clean": "https://openslr.trmal.net/resources/12/test-clean.tar.gz",
}
MD5_URL = "https://openslr.trmal.net/resources/12/md5sum.txt"
MANIFEST_PATH = ROOT / "data" / "librispeech" / "metadata" / "acquisition_manifest.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fetch_md5sum(destination: Path) -> str:
    completed = subprocess.run(
        ["curl", "-fsSL", "--max-time", "30", MD5_URL],
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0 or not completed.stdout:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"could not retrieve official md5sum.txt: {detail}")
    text = completed.stdout.decode("utf-8")
    destination.write_text(text, encoding="utf-8")
    return text


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _apply_verification(manifest: dict, measurements: dict[str, dict], status: str, recorded_at: str) -> None:
    manifest["legal_code_read"] = True
    manifest["owner_decision"] = "Accepted"
    manifest["approval_status"] = "APPROVED"
    manifest["download_status"] = status
    manifest["decision_id"] = "D-LS-001"
    manifest["decision_source"] = "explicit owner statement in the current conversation"
    manifest["decision_statement"] = (
        "I explicitly authorize both dev-clean.tar.gz and test-clean.tar.gz for "
        "Cascade Pipeline research, including extraction into the project dataset directory. "
        "I have already read and accepted CC BY 4.0."
    )
    manifest["decision_communicated_at"] = "2026-11-02T10:36:00+05:30"
    manifest["decision_communicated_at_precision"] = "minute; taken from the conversation timestamp"
    manifest["decision_recorded_at"] = "2026-11-02T10:42:27Z"
    manifest["manifest_updated_at"] = recorded_at
    manifest["extraction_authorized"] = True
    manifest["storage_cap_bytes"] = STORAGE_CAP_BYTES
    manifest["kaggle_upload_is_approved_source"] = False
    manifest["provenance_limitation"] = (
        "The browser download attribute kMDItemWhereFroms on both Downloads files was "
        "https://chatgpt.com/ via Brave on 2026-11-02. That is not an OpenSLR host. "
        "Filesystem created and modified times are local file dates, not an OpenSLR "
        "transfer timestamp. downloaded_at stays null. Declared archive URLs are the "
        "official OpenSLR file URLs. Integrity rests on the MD5 comparison with md5sum.txt."
    )
    by_split = {row["split"]: row for row in manifest["archives"]}
    for split, measured in measurements.items():
        row = by_split[split]
        row["approval_status"] = "APPROVED"
        row["download_status"] = status
        row["declared_source_url"] = DECLARED_URLS[split]
        row["local_source_path"] = str(DOWNLOADS[split])
        row["project_archive_path"] = str(
            (ROOT / "data" / "librispeech" / "archives" / f"{split}.tar.gz").relative_to(ROOT)
        )
        row["size_bytes_measured"] = measured["size_bytes"]
        row["md5"] = measured["md5"]
        row["sha256"] = measured["sha256"]
        row["checksum"] = measured["md5"]
        row["checksum_algorithm"] = "MD5"
        row["md5_official"] = measured["md5_official"]
        row["md5_match"] = measured["md5"] == measured["md5_official"]
        row["official_checksum_url"] = MD5_URL
        row["observed_transfer_url"] = "https://chatgpt.com/"
        row["downloaded_at"] = None
        row["filesystem_created_at"] = measured["filesystem_created_at"]
        row["filesystem_modified_at"] = measured["filesystem_modified_at"]
        row["filesystem_time_meaning"] = "local file dates, not an OpenSLR download timestamp"


def main() -> int:
    recorded_at = _utc_now()
    for split, path in DOWNLOADS.items():
        if not path.is_file():
            print(f"missing archive for {split}: {path}", file=sys.stderr)
            return 1
    md5_path = ROOT / "data" / "librispeech" / "metadata" / "openslr_md5sum.txt"
    md5_text = _fetch_md5sum(md5_path)
    official = parse_md5sum(md5_text)
    measurements: dict[str, dict] = {}
    for split, path in DOWNLOADS.items():
        digest = file_digests(path)
        created = datetime.fromtimestamp(path.stat().st_birthtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        expected = official.get(path.name)
        if expected is None:
            print(f"official MD5 missing for {path.name}", file=sys.stderr)
            return 1
        if digest["md5"] != expected:
            print(f"MD5 mismatch for {path.name}: {digest['md5']} != {expected}", file=sys.stderr)
            return 1
        measurements[split] = {
            **digest,
            "md5_official": expected,
            "filesystem_created_at": created,
            "filesystem_modified_at": modified,
        }
        print(f"verified {path.name} md5={digest['md5']} bytes={digest['size_bytes']}")

    member_bytes = {split: archive_member_bytes(path) for split, path in DOWNLOADS.items()}
    archive_dir = ROOT / "data" / "librispeech" / "archives"
    raw_root = ROOT / "data" / "librispeech" / "raw"
    existing = directory_size(ROOT / "data")
    additional_archives = 0
    for split, measured in measurements.items():
        if not (archive_dir / f"{split}.tar.gz").is_file():
            additional_archives += int(measured["size_bytes"])
    additional_extract = 0
    for split, size in member_bytes.items():
        present = directory_size(raw_root / split)
        if present < size:
            additional_extract += size - present
    projected = existing + additional_archives + additional_extract
    free = shutil.disk_usage(ROOT).free
    print(f"projected_bytes={projected} free_bytes={free} cap={STORAGE_CAP_BYTES}")
    if free < sum(member_bytes.values()):
        print("not enough free disk for extraction", file=sys.stderr)
        return 1
    assert_within_cap(projected)

    archive_dir = ROOT / "data" / "librispeech" / "archives"
    archive_dir.mkdir(parents=True, exist_ok=True)
    for split, source in DOWNLOADS.items():
        destination = archive_dir / f"{split}.tar.gz"
        if destination.exists():
            current = file_digests(destination)
            if current["sha256"] != measurements[split]["sha256"]:
                print(f"project archive differs and was not overwritten: {destination}", file=sys.stderr)
                return 1
        else:
            shutil.copy2(source, destination)
            copied = file_digests(destination)
            if copied["sha256"] != measurements[split]["sha256"] or copied["size_bytes"] != measurements[split]["size_bytes"]:
                print(f"copied archive does not match source: {destination}", file=sys.stderr)
                return 1
        print(f"project archive ready {destination}")

    manifest = _load_manifest()
    _apply_verification(manifest, measurements, VERIFIED_LOCAL_COPY, recorded_at)
    _save_manifest(manifest)

    extracted_bytes: dict[str, int] = {}
    for split in ("dev-clean", "test-clean"):
        target = ROOT / "data" / "librispeech" / "raw" / split
        started = _utc_now()
        counts = safe_extract(archive_dir / f"{split}.tar.gz", target)
        extracted_bytes[split] = directory_size(target)
        print(f"extracted {split} at {started} written={counts['written']} kept={counts['kept']} bytes={extracted_bytes[split]}")

    all_problems: list[str] = []
    manifests: dict[str, list[dict[str, str]]] = {}
    for split in ("dev-clean", "test-clean"):
        records, problems = collect_split(ROOT / "data" / "librispeech" / "raw" / split, split, ROOT)
        audio_paths = [str(ROOT / row["audio_path"]) for row in records]
        failures: list[str] = []
        workers = min(8, os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for failure in pool.map(decode_flac_job, audio_paths, chunksize=8):
                if failure:
                    failures.append(failure)
        problems.extend(failures)
        all_problems.extend(problems)
        manifests[split] = records
        print(f"{split} records={len(records)} problems={len(problems)} decode_failures={len(failures)}")

    if all_problems:
        report = ROOT / "data" / "librispeech" / "metadata" / "phase1b_problems.txt"
        report.write_text("\n".join(all_problems) + "\n", encoding="utf-8")
        print(f"validation failed, see {report}", file=sys.stderr)
        return 1

    for split in ("dev-clean", "test-clean"):
        records = manifests[split]
        records.sort(key=lambda row: row["utterance_id"])
        write_manifest(ROOT / "data" / "librispeech" / "processed" / split / "manifest.csv", records)
        ordered = order_utterances([row["utterance_id"] for row in records], split, DEFAULT_SEED)
        rank = {utterance_id: index for index, utterance_id in enumerate(ordered)}
        chosen = set(ordered[:DEVELOPMENT_PILOT])
        sample = [row for row in records if row["utterance_id"] in chosen]
        sample.sort(key=lambda row: rank[row["utterance_id"]])
        write_manifest(ROOT / "data" / "librispeech" / "processed" / split / "sample-200.csv", sample)
        manifests[split + "-sample"] = sample

    dev_speakers = {row["speaker_id"] for row in manifests["dev-clean-sample"]}
    test_speakers = {row["speaker_id"] for row in manifests["test-clean-sample"]}
    overlap = sorted(dev_speakers & test_speakers)
    dev_ids = {row["utterance_id"] for row in manifests["dev-clean-sample"]}
    test_ids = {row["utterance_id"] for row in manifests["test-clean-sample"]}
    if overlap or (dev_ids & test_ids):
        print(f"split isolation failed speakers={overlap}", file=sys.stderr)
        return 1

    sampling = {
        "seed": DEFAULT_SEED,
        "expression": "17:{split}:{utterance_id}",
        "algorithm": "SHA-256 hex digest ascending, then utterance_id ascending",
        "development_sample_size": len(manifests["dev-clean-sample"]),
        "test_sample_size": len(manifests["test-clean-sample"]),
        "development_ids": [row["utterance_id"] for row in manifests["dev-clean-sample"]],
        "test_ids": [row["utterance_id"] for row in manifests["test-clean-sample"]],
        "development_speakers": sorted(dev_speakers),
        "test_speakers": sorted(test_speakers),
        "speaker_overlap": overlap,
        "utterance_overlap": sorted(dev_ids & test_ids),
        "recorded_at": _utc_now(),
        "git_commit": "f55b5bd5b74d760e00f3178a35cd9b9512fd1ccf",
    }
    sampling_path = ROOT / "data" / "librispeech" / "metadata" / "sampling_manifest.json"
    sampling_path.write_text(json.dumps(sampling, indent=2) + "\n", encoding="utf-8")

    manifest = _load_manifest()
    _apply_verification(manifest, measurements, EXTRACTED, recorded_at)
    manifest["extraction"] = {
        "extracted_at": _utc_now(),
        "dev_clean_bytes": extracted_bytes["dev-clean"],
        "test_clean_bytes": extracted_bytes["test-clean"],
        "dev_clean_utterances": len(manifests["dev-clean"]),
        "test_clean_utterances": len(manifests["test-clean"]),
        "member_bytes": member_bytes,
    }
    _save_manifest(manifest)
    total_data = directory_size(ROOT / "data")
    summary = {
        "recorded_at": recorded_at,
        "archive_bytes": {split: measurements[split]["size_bytes"] for split in measurements},
        "extracted_bytes": extracted_bytes,
        "data_directory_bytes": total_data,
        "cap_remaining": STORAGE_CAP_BYTES - total_data,
        "utterances": {split: len(manifests[split]) for split in ("dev-clean", "test-clean")},
        "problems": 0,
    }
    (ROOT / "data" / "librispeech" / "metadata" / "phase1b_run.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
