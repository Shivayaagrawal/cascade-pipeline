"""Local annotation server. It serves only the development pilot."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from annotation.pilot_workflow import PilotWorkflow
from annotation.validate_annotations import ENUMS

FORM = Path(__file__).with_name("pilot_form.html")
ENUM_ORDER = {
    "sentence_type": ["not_annotated", "declarative", "interrogative", "imperative", "exclamatory", "fragment", "unclear"],
    "utterance_completeness": ["not_annotated", "complete", "incomplete", "fragment", "unclear"],
    "semantic_coherence": ["not_annotated", "coherent", "internally_inconsistent", "unclear"],
    "negation_present": ["not_annotated", "present", "absent", "ambiguous"],
    "uncertainty_present": ["not_annotated", "present", "absent", "ambiguous"],
    "temporal_expression_present": ["not_annotated", "present", "absent", "ambiguous"],
    "numerical_expression_present": ["not_annotated", "present", "absent", "ambiguous"],
    "coreference_or_context_dependency": ["not_annotated", "none_observed", "context_dependent", "unclear"],
    "semantic_ambiguity": ["not_annotated", "none_observed", "lexical", "syntactic", "semantic", "context_dependent", "unclear"],
    "task_intent_status": ["not_annotated", "not_applicable", "genuinely_present", "ambiguous"],
    "annotation_confidence": ["not_annotated", "high", "medium", "low"],
    "audio_reviewed": ["not_performed", "yes", "no"],
}


class PilotHandler(BaseHTTPRequestHandler):
    workflow: PilotWorkflow

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._bytes(200, FORM.read_bytes(), "text/html; charset=utf-8")
            return
        if parsed.path == "/api/schema":
            self._json(200, {"enums": ENUM_ORDER})
            return
        if parsed.path == "/api/utterance":
            index = int(parse_qs(parsed.query).get("index", ["0"])[0])
            self._json(200, self._payload(index))
            return
        if parsed.path == "/audio":
            index = int(parse_qs(parsed.query).get("index", ["0"])[0])
            try:
                audio = self.workflow.audio_for(index)
            except (ValueError, IndexError, OSError) as exc:
                self._json(404, {"error": str(exc)})
                return
            self._bytes(200, audio.read_bytes(), "audio/flac")
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/save":
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        try:
            self.workflow.save(int(body["index"]), body["fields"], listened=bool(body.get("listened")))
        except (ValueError, IndexError, KeyError) as exc:
            self._json(400, {"error": str(exc)})
            return
        self._json(200, self._payload(int(body["index"])))

    def log_message(self, format: str, *args) -> None:
        return

    def _payload(self, index: int) -> dict:
        row = self.workflow.public_row(index)
        return {
            "index": index,
            "total": len(self.workflow),
            "completed": self.workflow.completed_count(),
            "row": row,
        }

    def _json(self, status: int, payload: dict) -> None:
        self._bytes(status, json.dumps(payload).encode("utf-8"), "application/json")

    def _bytes(self, status: int, payload: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def serve(workflow: PilotWorkflow, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    handler = type("BoundPilotHandler", (PilotHandler,), {"workflow": workflow})
    server = ThreadingHTTPServer((host, port), handler)
    return server


def enum_order_matches_validator() -> bool:
    for field, values in ENUM_ORDER.items():
        if set(values) != ENUMS[field]:
            return False
    return True
