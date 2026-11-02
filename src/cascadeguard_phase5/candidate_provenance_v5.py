"""Candidate identity records emitted by the controller.

The evaluator reads these ids. It does not infer them from a matching frame.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProvenanceRecord:
    candidate_bundle_id: str
    candidate_id: str | None
    candidate_index: int | None
    candidate_text: str | None
    candidate_source: str | None
    selection_reason: str
    selected_candidate_id: str | None
    committed_candidate_id: str | None
    committed_frame: dict[str, str] | None
    provenance_status: str

    def as_dict(self) -> dict[str, object]:
        return {
            "candidate_bundle_id": self.candidate_bundle_id,
            "candidate_id": self.candidate_id,
            "candidate_index": self.candidate_index,
            "candidate_text": self.candidate_text,
            "candidate_source": self.candidate_source,
            "selection_reason": self.selection_reason,
            "selected_candidate_id": self.selected_candidate_id,
            "committed_candidate_id": self.committed_candidate_id,
            "committed_frame": None if self.committed_frame is None else dict(self.committed_frame),
            "provenance_status": self.provenance_status,
        }


def validate_bundle(candidates: list[dict[str, object]]) -> tuple[bool, str]:
    ids = [str(item.get("candidate_id") or "") for item in candidates]
    if any(not item for item in ids):
        return False, "MISSING_CANDIDATE_ID"
    if len(ids) != len(set(ids)):
        return False, "DUPLICATE_CANDIDATE_ID"
    return True, "VALID"


def lookup(candidates: list[dict[str, object]], candidate_id: str | None) -> dict[str, object] | None:
    if candidate_id is None:
        return None
    for index, item in enumerate(candidates):
        if item.get("candidate_id") == candidate_id:
            found = dict(item)
            found["candidate_index"] = index
            return found
    return None
