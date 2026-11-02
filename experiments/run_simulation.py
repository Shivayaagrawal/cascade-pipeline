#!/usr/bin/env python3
"""Generate the synthetic set, optional local audio, and B0/B1/B2 reports.

This command does not download Common Voice and does not approve Phase 1.
"""

from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cascadeguard.asr.base import Hypothesis, SYNTHETIC_EDIT  # noqa: E402
from cascadeguard.evaluation.cer import corpus_cer  # noqa: E402
from cascadeguard.evaluation.intent_metrics import (  # noqa: E402
    exact_frame_match,
    intent_accuracy,
    semantic_error_rate,
)
from cascadeguard.evaluation.slot_metrics import slot_scores  # noqa: E402
from cascadeguard.evaluation.wer import corpus_wer  # noqa: E402
from cascadeguard.pipeline import run_b0, run_b1, run_b2  # noqa: E402
from cascadeguard.simulation.audio_generator import inspect_audio, synthesize  # noqa: E402
from cascadeguard.simulation.error_injector import generate_variants  # noqa: E402
from cascadeguard.simulation.manifest import (  # noqa: E402
    write_common_voice_placeholder,
    write_manifests,
)
from cascadeguard.simulation.utterance_generator import generate_utterances  # noqa: E402


def _frame_rows(utterances, outputs):
    by_id = {item.utterance_id: item for item in outputs}
    rows = []
    for utterance in utterances:
        output = by_id[utterance.utterance_id]
        rows.append((utterance.intent, utterance.slots, output.intent, output.slots))
    return rows


def _summarize(name, utterances, outputs, transcript_pairs, actions=None):
    frames = _frame_rows(utterances, outputs)
    summary = {
        "system": name,
        "dataset": "synthetic",
        "utterances": len(utterances),
        "wer": corpus_wer(transcript_pairs),
        "cer": corpus_cer(transcript_pairs),
        "intent_accuracy": intent_accuracy([(row[0], row[2]) for row in frames]),
        "slots": slot_scores([(row[1], row[3]) for row in frames]),
        "exact_frame_match": exact_frame_match(frames),
        "semantic_error_rate": semantic_error_rate(frames),
        "mean_latency_seconds": sum(item.elapsed_seconds for item in outputs) / len(outputs),
    }
    if actions is not None:
        summary["actions"] = dict(Counter(actions))
    return summary


def _recovery_rates(b0_frames, b2_frames):
    successes = 0
    failures = 0
    false_recoveries = 0
    b0_correct = 0
    for b0_row, b2_row in zip(b0_frames, b2_frames, strict=True):
        b0_match = b0_row[0] == b0_row[2] and {
            (key.casefold(), value.casefold()) for key, value in b0_row[1].items()
        } == {(key.casefold(), value.casefold()) for key, value in b0_row[3].items()}
        b2_match = b2_row[0] == b2_row[2] and {
            (key.casefold(), value.casefold()) for key, value in b2_row[1].items()
        } == {(key.casefold(), value.casefold()) for key, value in b2_row[3].items()}
        if b0_match:
            b0_correct += 1
            if not b2_match:
                false_recoveries += 1
        else:
            failures += 1
            if b2_match:
                successes += 1
    return {
        "recovery_success_rate": None if failures == 0 else successes / failures,
        "false_recovery_rate": None if b0_correct == 0 else false_recoveries / b0_correct,
        "b0_frame_failures": failures,
        "b0_frame_successes": b0_correct,
        "recovered": successes,
        "harmed": false_recoveries,
    }


def generate_audio(utterances, audio_dir: Path) -> dict[str, str]:
    paths: dict[str, str] = {}
    for utterance in utterances:
        destination = audio_dir / f"{utterance.utterance_id}.aiff"
        synthesize(utterance.text, destination)
        info = inspect_audio(destination)
        paths[utterance.utterance_id] = str(destination.relative_to(ROOT))
        if info.duration_seconds <= 0:
            raise RuntimeError(f"Empty duration for {destination}")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--skip-audio", action="store_true")
    args = parser.parse_args()

    started = time.perf_counter()
    utterances = generate_utterances()
    variants = generate_variants(utterances, args.seed)
    by_utterance: dict[str, list] = {}
    for variant in variants:
        by_utterance.setdefault(variant.utterance_id, []).append(variant)

    audio_dir = ROOT / "data" / "synthetic" / "audio"
    if args.skip_audio:
        audio_paths = {item.utterance_id: "" for item in utterances}
        audio_info = None
    else:
        audio_paths = generate_audio(utterances, audio_dir)
        sample = inspect_audio(audio_dir / "utt-000.aiff")
        audio_info = {
            "files": len(audio_paths),
            "format": sample.format_name,
            "sample_rate_hz": sample.sample_rate_hz,
            "channels": sample.channels,
            "example_duration_seconds": sample.duration_seconds,
        }

    write_manifests(utterances, variants, audio_paths, ROOT)
    write_common_voice_placeholder(ROOT)

    b0_outputs = []
    b1_outputs = []
    b2_outputs = []
    b0_pairs = []
    b1_pairs = []
    b2_pairs = []
    actions = []
    for utterance in utterances:
        choices = by_utterance[utterance.utterance_id]
        hypotheses = tuple(
            Hypothesis(item.text, SYNTHETIC_EDIT, rank)
            for rank, item in enumerate(choices)
        )
        b0 = run_b0(utterance.utterance_id, hypotheses[0])
        b1 = run_b1(utterance.utterance_id, hypotheses)
        b2, decision = run_b2(utterance.utterance_id, hypotheses[0], hypotheses[1:])
        b0_outputs.append(b0)
        b1_outputs.append(b1)
        b2_outputs.append(b2)
        b0_pairs.append((utterance.text, b0.hypothesis_text))
        b1_pairs.append((utterance.text, b1.hypothesis_text))
        b2_pairs.append((utterance.text, b2.hypothesis_text))
        actions.append(decision.action.value)

    b0_summary = _summarize("B0", utterances, b0_outputs, b0_pairs)
    b1_summary = _summarize("B1", utterances, b1_outputs, b1_pairs)
    b2_summary = _summarize("B2", utterances, b2_outputs, b2_pairs, actions)
    recovery = _recovery_rates(
        _frame_rows(utterances, b0_outputs),
        _frame_rows(utterances, b2_outputs),
    )
    b2_summary["recovery"] = recovery
    elapsed = time.perf_counter() - started
    # macOS reports ru_maxrss in bytes.
    peak_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    report = {
        "dataset": "synthetic",
        "common_voice": "not_acquired",
        "phase_1_approved": False,
        "seed": args.seed,
        "utterances": len(utterances),
        "variants": len(variants),
        "audio": audio_info,
        "asr_backend": "synthetic_hypothesis",
        "whisper_executed": False,
        "candidate_provenance": SYNTHETIC_EDIT,
        "normalizer": "NFC, casefold, collapse whitespace, keep punctuation",
        "b0": b0_summary,
        "b1": b1_summary,
        "b2": b2_summary,
        "wall_seconds": elapsed,
        "peak_rss_bytes": peak_bytes,
        "comparison_ids": [item.utterance_id for item in utterances],
        "limitation": (
            "These scores are a closed synthetic grammar with injected transcript "
            "edits. They are not Common Voice, not Whisper, and not a real-world "
            "speech benchmark."
        ),
    }
    for name, summary in ("B0", b0_summary), ("B1", b1_summary), ("B2", b2_summary):
        directory = ROOT / "experiments" / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    artifact_dir = ROOT / "artifacts" / "reports"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "simulation_report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: report[key] for key in ("utterances", "variants", "audio", "b0", "b1", "b2", "wall_seconds", "peak_rss_bytes")}, indent=2))


if __name__ == "__main__":
    main()
