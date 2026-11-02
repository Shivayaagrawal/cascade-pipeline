"""Bundle-level failure labels. A label is not itself a commit."""

from __future__ import annotations


def diagnose(readings: list[dict[str, object]]) -> dict[str, object]:
    labels: list[str] = []
    frames = [item["frame"] for item in readings if item.get("frame")]
    intents = {frame["intent"] for frame in frames if isinstance(frame, dict)}
    signatures = {
        (
            frame["intent"],
            tuple(sorted(frame["slots"].items())),
        )
        for frame in frames
        if isinstance(frame, dict)
    }
    if any(len(item["intents"]) > 1 for item in readings):
        labels.append("MULTIPLE_INTENTS")
    if len(signatures) > 1 or len(intents) > 1:
        labels.append("CONFLICTING_FRAMES")
    if any(item["unrecognized"] for item in readings):
        labels.append("OUT_OF_INVENTORY")
    if any(item["intents"] and item["frame"] is None for item in readings):
        labels.append("INCOMPLETE_FRAME")
    return {"labels": labels, "frame_count": len(signatures)}
