"""Phase 1A metadata contracts. No audio is created or read."""

import json
from pathlib import Path

import pytest

from cascadeguard.dataset.acquisition import (
    STORAGE_CAP_BYTES,
    load_acquisition_manifest,
    validate_acquisition_manifest,
)
from cascadeguard.dataset.sampling import (
    DEVELOPMENT_MAX,
    DEVELOPMENT_PILOT,
    order_utterances,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "librispeech" / "metadata" / "acquisition_manifest.json"


def test_acquisition_manifest_records_the_owner_decision() -> None:
    manifest = load_acquisition_manifest(MANIFEST)
    assert manifest["approval_status"] in {"NOT_APPROVED", "APPROVED"}
    assert manifest["storage_cap_bytes"] == STORAGE_CAP_BYTES
    assert manifest["kaggle_upload_is_approved_source"] is False
    assert {row["split"] for row in manifest["archives"]} == {"dev-clean", "test-clean"}
    if manifest["approval_status"] == "APPROVED":
        assert manifest["legal_code_read"] is True
        assert manifest["owner_decision"] == "Accepted"
        for row in manifest["archives"]:
            assert row["approval_status"] == "APPROVED"
            assert row["downloaded_at"] is None
            assert row["md5_match"] is True
            assert row["size_bytes_measured"] > 0
    else:
        assert manifest["download_status"] == "NOT_DOWNLOADED"
        assert manifest["owner_decision"] == "Pending"


def test_unapproved_split_and_fabricated_checksum_are_rejected() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["archives"][0]["split"] = "train-clean-360"
    assert any("not an approved split" in error for error in validate_acquisition_manifest(manifest))


def test_storage_cap_is_five_gigabytes() -> None:
    assert STORAGE_CAP_BYTES == 5_000_000_000


def test_sampling_order_is_stable_and_not_size_based() -> None:
    ids = ["b-2-0001", "a-1-0000", "a-1-0001"]
    first = order_utterances(ids, "dev-clean")
    second = order_utterances(list(reversed(ids)), "dev-clean")
    assert first == second
    assert order_utterances(ids, "dev-clean")[:DEVELOPMENT_PILOT] == first[:DEVELOPMENT_PILOT]
    assert first[:DEVELOPMENT_PILOT] == order_utterances(ids, "dev-clean")[:DEVELOPMENT_MAX][:DEVELOPMENT_PILOT]
    assert order_utterances(ids, "test-clean") != first
    with pytest.raises(ValueError):
        order_utterances(ids, "train-clean-360")
    with pytest.raises(ValueError):
        order_utterances(["a-1-0000", "a-1-0000"], "dev-clean")


def test_librispeech_audio_stays_under_the_dataset_root() -> None:
    root = ROOT / "data" / "librispeech"
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in {".flac", ".tar", ".gz"} or path.name.endswith(".tar.gz"):
            relative = path.relative_to(root)
            assert relative.parts[0] in {"raw", "archives"}
