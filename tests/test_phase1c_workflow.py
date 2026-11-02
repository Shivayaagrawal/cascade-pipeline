"""Human annotation workflow checks. Fixtures are not LibriSpeech labels."""

from __future__ import annotations

import csv
import hashlib
import json
import threading
from pathlib import Path
from urllib.request import Request, urlopen

from annotation.pilot_server import enum_order_matches_validator, serve
from annotation.pilot_workflow import PilotWorkflow, resolve_dev_audio, row_is_dirty
from annotation.validate_annotations import REQUIRED_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
FORM = ROOT / "src" / "annotation" / "pilot_form.html"
REAL_HASHES = {
    "data/librispeech/annotations/phase_1c_pilot_30.csv": "56a4dc49b3a2f5add5c361c2b23edde923c8265a998de76c7e5b87462e5d6a5c",
    "data/librispeech/processed/dev-clean/sample-200.csv": "e39f7e78dc93a785ec19915bd9dca928ad77c5791a5dd2632613181101253233",
    "data/librispeech/processed/test-clean/sample-200.csv": "6da39d6d7193bf5f7e17ba91da9a3ce4127c0ebb37fba712efee4aae7828e5cb",
}


def _write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _blank(utterance_id: str, speaker: str, text: str) -> dict[str, str]:
    row = {field: "not_annotated" for field in REQUIRED_COLUMNS}
    row.update(
        {
            "utterance_id": utterance_id,
            "split": "dev-clean",
            "speaker_id": speaker,
            "reference_text": text,
            "audio_reviewed": "not_performed",
            "annotation_notes": "Not annotated.",
        }
    )
    return row


def _fixture(tmp: Path) -> tuple[PilotWorkflow, Path]:
    repo = tmp / "repo"
    audio = repo / "data/librispeech/raw/dev-clean/1272/128104/1272-128104-0000.flac"
    audio.parent.mkdir(parents=True)
    audio.write_bytes(b"fixture-audio")
    other = repo / "data/librispeech/raw/dev-clean/1272/128104/1272-128104-0001.flac"
    other.write_bytes(b"fixture-audio-2")
    sample_fields = ["utterance_id", "reference_text", "audio_path", "split", "speaker_id"]
    dev_rows = [
        {
            "utterance_id": "1272-128104-0000",
            "reference_text": "HELLO THERE",
            "audio_path": "data/librispeech/raw/dev-clean/1272/128104/1272-128104-0000.flac",
            "split": "dev-clean",
            "speaker_id": "1272",
        },
        {
            "utterance_id": "1272-128104-0001",
            "reference_text": "SECOND LINE",
            "audio_path": "data/librispeech/raw/dev-clean/1272/128104/1272-128104-0001.flac",
            "split": "dev-clean",
            "speaker_id": "1272",
        },
    ]
    dev = repo / "sample.csv"
    held = repo / "heldout.csv"
    pilot = repo / "pilot.csv"
    _write_csv(dev, dev_rows, sample_fields)
    _write_csv(
        held,
        [
            {
                "utterance_id": "9999-1-0000",
                "reference_text": "HELD OUT",
                "audio_path": "data/librispeech/raw/test-clean/9999/1/9999-1-0000.flac",
                "split": "test-clean",
                "speaker_id": "9999",
            }
        ],
        sample_fields,
    )
    _write_csv(pilot, [_blank("1272-128104-0000", "1272", "HELLO THERE"), _blank("1272-128104-0001", "1272", "SECOND LINE")], list(REQUIRED_COLUMNS))
    return PilotWorkflow(repo, pilot, dev, held), audio


def _completed_fields() -> dict[str, str]:
    return {
        "sentence_type": "declarative",
        "utterance_completeness": "complete",
        "proposition_summary": "A short gloss of the words that are present.",
        "semantic_coherence": "coherent",
        "entities_explicitly_mentioned": "[]",
        "negation_present": "absent",
        "uncertainty_present": "absent",
        "temporal_expression_present": "absent",
        "numerical_expression_present": "absent",
        "coreference_or_context_dependency": "none_observed",
        "semantic_ambiguity": "none_observed",
        "task_intent_status": "not_applicable",
        "task_intent": "not_applicable",
        "task_slots": "not_annotated",
        "annotation_confidence": "medium",
        "annotator_id": "reviewer-a",
        "annotation_notes": "Heard the fixture. No discrepancy.",
        "audio_reviewed": "yes",
    }


def test_blank_rows_stay_unannotated_until_a_listened_save(tmp_path: Path) -> None:
    workflow, audio = _fixture(tmp_path)
    before = audio.read_bytes()
    try:
        workflow.save(0, _completed_fields(), listened=False)
        assert False, "save without listening should fail"
    except ValueError as exc:
        assert "listen" in str(exc)
    assert workflow.rows[0]["annotator_id"] == "not_annotated"
    workflow.save(0, _completed_fields(), listened=True)
    resumed = PilotWorkflow(workflow.repo_root, workflow.pilot_csv, workflow.repo_root / "sample.csv", workflow.repo_root / "heldout.csv")
    assert resumed.rows[0]["annotator_id"] == "reviewer-a"
    assert resumed.rows[1]["annotator_id"] == "not_annotated"
    assert resumed.completed_count() == 1
    assert audio.read_bytes() == before
    assert resumed.rows[0]["reference_text"] == "HELLO THERE"


def test_bad_values_and_heldout_audio_are_rejected(tmp_path: Path) -> None:
    workflow, _audio = _fixture(tmp_path)
    fields = _completed_fields()
    fields["sentence_type"] = "command"
    try:
        workflow.save(0, fields, listened=True)
        assert False, "invalid enumeration should fail"
    except ValueError as exc:
        assert "sentence_type" in str(exc)
    fields = _completed_fields()
    del fields["annotation_notes"]
    try:
        workflow.save(0, fields, listened=True)
        assert False, "missing field should fail"
    except ValueError as exc:
        assert "missing field" in str(exc)
    try:
        resolve_dev_audio(workflow.repo_root, "data/librispeech/raw/test-clean/9999/1/9999-1-0000.flac")
        assert False, "held-out audio should be refused"
    except ValueError as exc:
        assert "held-out" in str(exc)
    changed = _completed_fields()
    changed["reference_text"] = "EDITED"
    try:
        workflow.save(0, changed, listened=True)
        assert False, "source text should be immutable"
    except ValueError as exc:
        assert "reference_text" in str(exc)


def test_unsaved_change_detection_and_page_guard() -> None:
    saved = {"annotation_notes": "Not annotated.", "sentence_type": "not_annotated"}
    assert row_is_dirty(saved, dict(saved)) is False
    changed = dict(saved)
    changed["sentence_type"] = "declarative"
    assert row_is_dirty(saved, changed) is True
    page = FORM.read_text(encoding="utf-8")
    assert "beforeunload" in page
    assert "unsaved changes" in page
    assert "not_annotated" in page


def test_enumeration_order_matches_the_validator() -> None:
    assert enum_order_matches_validator()


def test_http_save_resumes_and_does_not_offer_heldout_audio(tmp_path: Path) -> None:
    workflow, audio = _fixture(tmp_path)
    server = serve(workflow, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        with urlopen(f"http://127.0.0.1:{port}/api/utterance?index=0") as response:
            body = json.load(response)
        assert body["row"]["split"] == "dev-clean"
        assert "9999-1-0000" not in json.dumps(body)
        request = Request(
            f"http://127.0.0.1:{port}/api/save",
            data=json.dumps({"index": 0, "listened": True, "fields": _completed_fields()}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            saved = json.load(response)
        assert saved["completed"] == 1
        with urlopen(f"http://127.0.0.1:{port}/audio?index=0") as response:
            assert response.read() == audio.read_bytes()
    finally:
        server.shutdown()


def test_real_pilot_files_remain_unannotated() -> None:
    for relative, digest in REAL_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    workflow = PilotWorkflow(
        ROOT,
        ROOT / "data/librispeech/annotations/phase_1c_pilot_30.csv",
        ROOT / "data/librispeech/processed/dev-clean/sample-200.csv",
        ROOT / "data/librispeech/processed/test-clean/sample-200.csv",
    )
    assert len(workflow) == 30
    assert workflow.completed_count() == 0
    assert all(row["audio_reviewed"] == "not_performed" for row in workflow.rows)
