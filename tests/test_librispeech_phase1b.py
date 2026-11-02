"""Phase 1B archive, transcript, extraction, and sampling checks.

Synthetic fixtures are generated in temporary directories. They are not LibriSpeech
recordings and are not research results.
"""

from __future__ import annotations

import hashlib
import io
import tarfile
import wave
from pathlib import Path

import pytest

from cascadeguard.dataset.acquisition import (
    STORAGE_CAP_BYTES,
    assert_within_cap,
    file_digests,
    parse_md5sum,
    validate_acquisition_manifest,
)
from cascadeguard.dataset.extract import UnsafeArchive, member_destination, safe_extract
from cascadeguard.dataset.librispeech import (
    MANIFEST_FIELDS,
    decode_flac,
    parse_transcript_text,
    read_flac_streaminfo,
    read_manifest,
    write_manifest,
)
from cascadeguard.dataset.sampling import order_utterances

ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "experiments/B0/summary.json": "3873057391b2f36727f503a4d504ddea9453472e6d518a63a2fef2481ae850ee",
    "experiments/B1/summary.json": "597a2800c946018467865dfcf3d8e547bc51c10487596cc134ca2181fee695b2",
    "experiments/B2/summary.json": "34a40fdd233f5d4faa00af73c26f1afcc32c4d83922db8df57b7a7184dce0e5d",
    "artifacts/reports/simulation_report.json": "7adf69ee6ac344e7ef205099af3686ddf7cceaffa111a8789f03b83ed8319856",
    "experiments/sim-eval-v2/report.json": "74499b716103e26ef829cb56816bf738d67d3d3e5961848c4cfe37f2e8f4f77d",
}


def _pending_manifest() -> dict:
    return {
        "approval_status": "NOT_APPROVED",
        "download_status": "NOT_DOWNLOADED",
        "owner_decision": "Pending",
        "legal_code_read": False,
        "storage_cap_bytes": STORAGE_CAP_BYTES,
        "kaggle_upload_is_approved_source": False,
        "archives": [
            {
                "split": "dev-clean",
                "approval_status": "NOT_APPROVED",
                "download_status": "NOT_DOWNLOADED",
                "checksum": None,
                "downloaded_at": None,
                "md5": None,
                "sha256": None,
                "size_bytes_measured": None,
            },
            {
                "split": "test-clean",
                "approval_status": "NOT_APPROVED",
                "download_status": "NOT_DOWNLOADED",
                "checksum": None,
                "downloaded_at": None,
                "md5": None,
                "sha256": None,
                "size_bytes_measured": None,
            },
        ],
    }


def _wav_bytes(rate: int = 16000) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(b"\x00\x00" * rate)
    return buffer.getvalue()


def _flac_from_wav(tmp: Path, rate: int = 16000) -> Path:
    wav_path = tmp / f"tone-{rate}.wav"
    flac_path = tmp / f"tone-{rate}.flac"
    wav_path.write_bytes(_wav_bytes(rate))
    completed = __import__("subprocess").run(
        ["afconvert", "-f", "flac", str(wav_path), str(flac_path)],
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        pytest.skip("afconvert could not write a fixture FLAC")
    return flac_path


def test_missing_archive_is_detected(tmp_path: Path) -> None:
    missing = tmp_path / "dev-clean.tar.gz"
    with pytest.raises(FileNotFoundError):
        file_digests(missing)


def test_partial_download_name_is_not_an_archive(tmp_path: Path) -> None:
    partial = tmp_path / "dev-clean.tar.gz.part"
    partial.write_bytes(b"not-complete")
    assert partial.suffix == ".part"
    with pytest.raises(tarfile.ReadError):
        safe_extract(partial, tmp_path / "out")


def test_corrupt_archive_is_rejected(tmp_path: Path) -> None:
    bad = tmp_path / "dev-clean.tar.gz"
    bad.write_bytes(b"this is not gzip")
    with pytest.raises(tarfile.ReadError):
        safe_extract(bad, tmp_path / "out")


def test_official_md5_parser_keeps_published_names() -> None:
    parsed = parse_md5sum("42e2234ba48799c1f50f24a7926300a1  dev-clean.tar.gz\n")
    assert parsed["dev-clean.tar.gz"] == "42e2234ba48799c1f50f24a7926300a1"


def test_wrong_md5_is_not_a_match() -> None:
    official = parse_md5sum("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  dev-clean.tar.gz\n")
    assert official["dev-clean.tar.gz"] != "42e2234ba48799c1f50f24a7926300a1"


def test_storage_cap_rejects_an_over_budget_total() -> None:
    assert_within_cap(STORAGE_CAP_BYTES)
    with pytest.raises(RuntimeError):
        assert_within_cap(STORAGE_CAP_BYTES + 1)


def test_path_traversal_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(UnsafeArchive):
        member_destination(tmp_path, "../escape.txt")
    with pytest.raises(UnsafeArchive):
        member_destination(tmp_path, "/tmp/escape.txt")


def test_safe_extract_writes_only_inside_destination(tmp_path: Path) -> None:
    archive_path = tmp_path / "sample.tar.gz"
    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "note.txt").write_text("synthetic fixture\n", encoding="utf-8")
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(payload / "note.txt", arcname="note.txt")
        info = tarfile.TarInfo("../escape.txt")
        info.size = 4
        archive.addfile(info, io.BytesIO(b"nope"))
    with pytest.raises(UnsafeArchive):
        safe_extract(archive_path, tmp_path / "dest")
    assert not (tmp_path / "escape.txt").exists()
    assert not (tmp_path.parent / "escape.txt").exists()


def test_transcript_parser_preserves_text_and_finds_duplicates() -> None:
    text = "1272-128104-0000 A MAN SAID  HELLO\n1272-128104-0000 AGAIN\n\nnot-an-id hello\n1272-128104-0001 \n"
    rows, problems = parse_transcript_text(text, "fixture.trans.txt")
    assert rows[0]["reference_text"] == "A MAN SAID  HELLO"
    assert rows[0]["speaker_id"] == "1272"
    assert rows[0]["chapter_id"] == "128104"
    assert any("duplicate" in problem for problem in problems)
    assert any("malformed" in problem for problem in problems)
    assert any("empty reference" in problem for problem in problems)


def test_missing_audio_and_transcript_are_reported(tmp_path: Path) -> None:
    from cascadeguard.dataset.librispeech import collect_split

    root = tmp_path / "split"
    chapter = root / "LibriSpeech" / "dev-clean" / "1272" / "128104"
    chapter.mkdir(parents=True)
    (chapter / "1272-128104.trans.txt").write_text(
        "1272-128104-0000 HELLO THERE\n1272-128104-0001 SECOND LINE\n",
        encoding="utf-8",
    )
    flac = _flac_from_wav(tmp_path)
    (chapter / "1272-128104-0000.flac").write_bytes(flac.read_bytes())
    (chapter / "1272-128104-0002.flac").write_bytes(flac.read_bytes())
    records, problems = collect_split(root, "dev-clean", tmp_path)
    assert [row["utterance_id"] for row in records] == ["1272-128104-0000"]
    assert any("missing audio for 1272-128104-0001" in problem for problem in problems)
    assert any("missing transcript for 1272-128104-0002" in problem for problem in problems)


def test_non_16khz_audio_is_reported(tmp_path: Path) -> None:
    from cascadeguard.dataset.librispeech import collect_split

    root = tmp_path / "split"
    chapter = root / "LibriSpeech" / "dev-clean" / "1272" / "128104"
    chapter.mkdir(parents=True)
    (chapter / "1272-128104.trans.txt").write_text("1272-128104-0000 HELLO\n", encoding="utf-8")
    flac = _flac_from_wav(tmp_path, rate=8000)
    info = read_flac_streaminfo(flac)
    assert info["sample_rate"] == 8000
    (chapter / "1272-128104-0000.flac").write_bytes(flac.read_bytes())
    _records, problems = collect_split(root, "dev-clean", tmp_path)
    assert any("sample rate is 8000" in problem for problem in problems)


def test_truncated_flac_fails_decode(tmp_path: Path) -> None:
    flac = _flac_from_wav(tmp_path)
    broken = tmp_path / "broken.flac"
    broken.write_bytes(flac.read_bytes()[:20])
    with pytest.raises(ValueError):
        read_flac_streaminfo(broken)
    with pytest.raises(ValueError):
        decode_flac(broken, tmp_path / "out.wav")


def test_manifest_round_trip_keeps_reference_text(tmp_path: Path) -> None:
    record = {field: "x" for field in MANIFEST_FIELDS}
    record["reference_text"] = "KEEP  SPACES"
    record["split"] = "dev-clean"
    path = tmp_path / "manifest.csv"
    write_manifest(path, [record])
    loaded = read_manifest(path)
    assert loaded[0]["reference_text"] == "KEEP  SPACES"
    assert tuple(loaded[0]) == MANIFEST_FIELDS


def test_sampling_uses_seed_17_expression() -> None:
    utterance_id = "1272-128104-0000"
    digest = hashlib.sha256(f"17:dev-clean:{utterance_id}".encode("utf-8")).hexdigest()
    ordered = order_utterances([utterance_id, "1272-128104-0001"], "dev-clean", 17)
    assert ordered[0] == min(
        ["1272-128104-0000", "1272-128104-0001"],
        key=lambda item: hashlib.sha256(f"17:dev-clean:{item}".encode("utf-8")).hexdigest(),
    )
    assert digest == hashlib.sha256(b"17:dev-clean:1272-128104-0000").hexdigest()


def test_pending_manifest_still_rejects_a_fabricated_checksum() -> None:
    manifest = _pending_manifest()
    assert validate_acquisition_manifest(manifest) == []
    manifest["archives"][0]["checksum"] = "0" * 32
    manifest["archives"][0]["downloaded_at"] = "2026-11-02T00:00:00Z"
    assert any("must stay null" in error for error in validate_acquisition_manifest(manifest))
    manifest = _pending_manifest()
    manifest["archives"][0]["split"] = "train-clean-360"
    assert any("not an approved split" in error for error in validate_acquisition_manifest(manifest))


def test_approved_manifest_requires_measured_checksums() -> None:
    manifest = _pending_manifest()
    manifest["approval_status"] = "APPROVED"
    manifest["owner_decision"] = "Accepted"
    manifest["legal_code_read"] = True
    manifest["download_status"] = "VERIFIED_LOCAL_COPY"
    for archive in manifest["archives"]:
        archive["approval_status"] = "APPROVED"
        archive["download_status"] = "VERIFIED_LOCAL_COPY"
    assert any("must be measured" in error for error in validate_acquisition_manifest(manifest))


def test_historical_simulation_hashes_are_unchanged() -> None:
    for relative, expected in FROZEN.items():
        digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert digest == expected


def test_phase1b_code_does_not_import_an_asr_engine() -> None:
    package = ROOT / "src" / "cascadeguard" / "dataset"
    script = (ROOT / "scripts" / "prepare_librispeech.py").read_text(encoding="utf-8")
    combined = script + "\n".join(path.read_text(encoding="utf-8") for path in package.glob("*.py"))
    assert "faster_whisper" not in combined
    assert "import whisper" not in combined


def test_project_archives_match_official_md5_when_present() -> None:
    md5_path = ROOT / "data" / "librispeech" / "metadata" / "openslr_md5sum.txt"
    if not md5_path.is_file():
        pytest.skip("official checksum file is not in the repository yet")
    official = parse_md5sum(md5_path.read_text(encoding="utf-8"))
    for name in ("dev-clean.tar.gz", "test-clean.tar.gz"):
        archive = ROOT / "data" / "librispeech" / "archives" / name
        if not archive.is_file():
            pytest.skip("project archive has not been copied yet")
        measured = file_digests(archive)
        assert measured["md5"] == official[name]
        assert measured["sha256"]


def test_prepared_samples_are_isolated() -> None:
    dev = ROOT / "data" / "librispeech" / "processed" / "dev-clean" / "sample-200.csv"
    test = ROOT / "data" / "librispeech" / "processed" / "test-clean" / "sample-200.csv"
    if not dev.is_file() or not test.is_file():
        pytest.skip("samples have not been written yet")
    dev_rows = read_manifest(dev)
    test_rows = read_manifest(test)
    assert len(dev_rows) == 200
    assert len(test_rows) == 200
    assert {row["split"] for row in dev_rows} == {"dev-clean"}
    assert {row["split"] for row in test_rows} == {"test-clean"}
    assert not ({row["utterance_id"] for row in dev_rows} & {row["utterance_id"] for row in test_rows})
    assert not ({row["speaker_id"] for row in dev_rows} & {row["speaker_id"] for row in test_rows})
    dev_ids = [row["utterance_id"] for row in dev_rows]
    test_ids = [row["utterance_id"] for row in test_rows]
    dev_all = [row["utterance_id"] for row in read_manifest(ROOT / "data" / "librispeech" / "processed" / "dev-clean" / "manifest.csv")]
    test_all = [row["utterance_id"] for row in read_manifest(ROOT / "data" / "librispeech" / "processed" / "test-clean" / "manifest.csv")]
    assert dev_ids == order_utterances(dev_all, "dev-clean")[:200]
    assert test_ids == order_utterances(test_all, "test-clean")[:200]
    assert dev_ids == order_utterances(dev_all, "dev-clean")[:500][:200]
