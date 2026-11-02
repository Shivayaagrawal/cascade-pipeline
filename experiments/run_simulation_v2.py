#!/usr/bin/env python3
"""Simulation Evaluation v2. Does not rewrite the initial B0/B1/B2 summaries."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cascadeguard.asr.base import REFERENCE_PASSTHROUGH, SYNTHETIC_EDIT, Hypothesis  # noqa: E402
from cascadeguard.candidates.candidate_manager import score_hypothesis, select_candidate  # noqa: E402
from cascadeguard.evaluation.cer import corpus_cer  # noqa: E402
from cascadeguard.evaluation.intent_metrics import (  # noqa: E402
    exact_frame_match,
    frames_equal,
    intent_accuracy,
    semantic_error_rate,
)
from cascadeguard.evaluation.latency_stats import summarize_seconds  # noqa: E402
from cascadeguard.evaluation.oracle import oracle_summary  # noqa: E402
from cascadeguard.evaluation.policy_eval import SIMULATED_RETRY, action_report, expected_action  # noqa: E402
from cascadeguard.evaluation.slot_metrics import per_slot_scores, slot_scores  # noqa: E402
from cascadeguard.evaluation.wer import corpus_wer  # noqa: E402
from cascadeguard.nlu.intent_classifier import classify_intent  # noqa: E402
from cascadeguard.nlu.slot_extractor import extract_slots  # noqa: E402
from cascadeguard.recovery.failure_detector import detect_failure  # noqa: E402
from cascadeguard.recovery.recovery_controller import decide  # noqa: E402
from cascadeguard.simulation.error_injector import ERROR_CATEGORIES, generate_variants  # noqa: E402
from cascadeguard.simulation.utterance_generator import generate_utterances  # noqa: E402

PRESERVED = (
    ROOT / "experiments" / "B0" / "summary.json",
    ROOT / "experiments" / "B1" / "summary.json",
    ROOT / "experiments" / "B2" / "summary.json",
    ROOT / "artifacts" / "reports" / "simulation_report.json",
)


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _bundle(name: str, texts: list[tuple[str, str]], frames: list[tuple]) -> dict[str, object]:
    return {
        "system": name,
        "n": len(frames),
        "wer": corpus_wer(texts),
        "cer": corpus_cer(texts),
        "intent_accuracy": intent_accuracy([(row[0], row[2]) for row in frames]),
        "slot_f1": slot_scores([(row[1], row[3]) for row in frames])["f1"],
        "semantic_error_rate": semantic_error_rate(frames),
        "exact_frame_match": exact_frame_match(frames),
    }


def main() -> None:
    before = {str(path.relative_to(ROOT)): _sha256(path) for path in PRESERVED}
    started_at = datetime.now(timezone.utc).isoformat()
    seed = 17
    utterances = generate_utterances()

    generation_started = time.perf_counter()
    variants = generate_variants(utterances, seed)
    candidate_generation_seconds = time.perf_counter() - generation_started
    grouped: dict[str, list] = defaultdict(list)
    for variant in variants:
        grouped[variant.utterance_id].append(variant)

    nlu_times: list[float] = []
    score_times: list[float] = []
    diagnosis_times: list[float] = []
    decision_times: list[float] = []
    text_times: list[float] = []
    records = []

    for utterance in utterances:
        choices = grouped[utterance.utterance_id]
        hypotheses = tuple(
            Hypothesis(item.text, SYNTHETIC_EDIT, index) for index, item in enumerate(choices)
        )
        stage_started = time.perf_counter()
        for hypothesis in hypotheses:
            call_started = time.perf_counter()
            prediction = classify_intent(hypothesis.text)
            if not prediction.ambiguous:
                extract_slots(prediction.intent, hypothesis.text)
            nlu_times.append(time.perf_counter() - call_started)
        score_started = time.perf_counter()
        scored = tuple(score_hypothesis(hypothesis) for hypothesis in hypotheses)
        score_elapsed = time.perf_counter() - score_started
        score_times.append(score_elapsed)
        diagnosis_started = time.perf_counter()
        detect_failure(scored[0])
        diagnosis_elapsed = time.perf_counter() - diagnosis_started
        diagnosis_times.append(diagnosis_elapsed)
        decision_started = time.perf_counter()
        decision = decide(scored[0], hypotheses[1:])
        decision_elapsed = time.perf_counter() - decision_started
        decision_times.append(decision_elapsed)
        text_times.append(time.perf_counter() - stage_started)
        selected = select_candidate(hypotheses)
        records.append(
            {
                "utterance": utterance,
                "choices": choices,
                "hypotheses": hypotheses,
                "scored": scored,
                "b1": selected,
                "decision": decision,
            }
        )

    def frames_for(picker) -> tuple[list[tuple[str, str]], list[tuple]]:
        texts = []
        frames = []
        for record in records:
            utterance = record["utterance"]
            chosen = picker(record)
            texts.append((utterance.text, chosen.hypothesis.text))
            frames.append((utterance.intent, utterance.slots, chosen.intent, chosen.slots))
        return texts, frames

    b0_texts, b0_frames = frames_for(lambda record: record["scored"][0])
    b1_texts, b1_frames = frames_for(lambda record: record["b1"])
    b2_texts, b2_frames = frames_for(lambda record: record["decision"].selected)
    systems = {
        "B0": _bundle("B0", b0_texts, b0_frames),
        "B1": _bundle("B1", b1_texts, b1_frames),
        "B2": _bundle("B2", b2_texts, b2_frames),
    }

    by_category: dict[str, dict[str, list]] = {
        name: {category: [] for category in ERROR_CATEGORIES} for name in ("B0", "B1", "B2")
    }
    text_groups = {"B0": b0_texts, "B1": b1_texts, "B2": b2_texts}
    frame_groups = {"B0": b0_frames, "B1": b1_frames, "B2": b2_frames}
    for index, record in enumerate(records):
        category = record["choices"][0].category
        for name in ("B0", "B1", "B2"):
            by_category[name][category].append(index)
    category_report = {}
    for name in ("B0", "B1", "B2"):
        category_report[name] = {}
        for category in ERROR_CATEGORIES:
            indexes = by_category[name][category]
            texts = [text_groups[name][index] for index in indexes]
            frames = [frame_groups[name][index] for index in indexes]
            category_report[name][category] = _bundle(name, texts, frames)

    variant_rows: dict[str, list[tuple]] = {category: [] for category in ERROR_CATEGORIES}
    variant_texts: dict[str, list[tuple[str, str]]] = {category: [] for category in ERROR_CATEGORIES}
    for record in records:
        utterance = record["utterance"]
        for choice, scored in zip(record["choices"], record["scored"], strict=True):
            variant_texts[choice.category].append((utterance.text, choice.text))
            variant_rows[choice.category].append(
                (utterance.intent, utterance.slots, scored.intent, scored.slots)
            )
    variant_report = {
        category: _bundle("variant", variant_texts[category], variant_rows[category])
        for category in ERROR_CATEGORIES
    }

    oracle_rows = [
        (record["utterance"].intent, record["utterance"].slots, record["scored"])
        for record in records
    ]
    primary_oracle = oracle_summary(oracle_rows)
    gold_rows = []
    for record in records:
        utterance = record["utterance"]
        extra = score_hypothesis(Hypothesis(utterance.text, REFERENCE_PASSTHROUGH, 3))
        gold_rows.append((utterance.intent, utterance.slots, record["scored"] + (extra,)))
    gold_oracle = oracle_summary(gold_rows)
    gold_oracle["gold_transcript_included"] = True
    gold_oracle["label"] = "separate ablation; not part of the primary three-candidate oracle"

    policy_rows = []
    for record in records:
        utterance = record["utterance"]
        one_best = record["scored"][0]
        one_ok = frames_equal(utterance.intent, utterance.slots, one_best.intent, one_best.slots)
        other_ok = any(
            frames_equal(utterance.intent, utterance.slots, item.intent, item.slots)
            for item in record["scored"][1:]
        )
        expected = expected_action(
            category=record["choices"][0].category,
            one_best_ambiguous=one_best.ambiguous,
            one_best_frame_ok=one_ok,
            other_candidate_frame_ok=other_ok,
        )
        action = record["decision"].action.value
        selected = record["decision"].selected
        final_ok = frames_equal(
            utterance.intent, utterance.slots, selected.intent, selected.slots
        )
        policy_rows.append(
            {
                "expected": expected,
                "actual": action,
                "b0_frame_ok": one_ok,
                "b2_frame_ok": final_ok,
                "committed": action in {"CONTINUE", "RETRY"},
            }
        )
    policy = action_report(policy_rows)

    slot_report = {
        "B0": per_slot_scores([(row[1], row[3]) for row in b0_frames]),
        "B1": per_slot_scores([(row[1], row[3]) for row in b1_frames]),
        "B2": per_slot_scores([(row[1], row[3]) for row in b2_frames]),
        "not_in_schema": {
            "location": {"value": None, "reason": "the synthetic schema has no location slot"},
            "negation": {
                "value": None,
                "reason": "negation is an error category, not a gold slot",
            },
        },
    }

    def ablation_b1(limit: int, semantic: bool) -> dict[str, object]:
        texts = []
        frames = []
        for record in records:
            utterance = record["utterance"]
            hypotheses = record["hypotheses"][:limit]
            chosen = select_candidate(hypotheses) if semantic else score_hypothesis(hypotheses[0])
            texts.append((utterance.text, chosen.hypothesis.text))
            frames.append((utterance.intent, utterance.slots, chosen.intent, chosen.slots))
        return _bundle(f"B1-{limit}-semantic-{semantic}", texts, frames)

    def ablation_b2(diagnosis: bool) -> dict[str, object]:
        texts = []
        frames = []
        for record in records:
            utterance = record["utterance"]
            if diagnosis:
                chosen = record["decision"].selected
            else:
                chosen = record["scored"][0]
            texts.append((utterance.text, chosen.hypothesis.text))
            frames.append((utterance.intent, utterance.slots, chosen.intent, chosen.slots))
        return _bundle(f"B2-diagnosis-{diagnosis}", texts, frames)

    ablations = {
        "b1_one_candidate_with_semantic_comparison": ablation_b1(1, True),
        "b1_two_candidates_with_semantic_comparison": ablation_b1(2, True),
        "b1_three_candidates_with_semantic_comparison": ablation_b1(3, True),
        "b1_three_candidates_without_semantic_comparison": ablation_b1(3, False),
        "b2_with_failure_diagnosis": ablation_b2(True),
        "b2_without_failure_diagnosis": ablation_b2(False),
        "oracle_with_gold_transcript": gold_oracle,
    }

    load_times: list[float] = []
    audio_dir = ROOT / "data" / "synthetic" / "audio"
    if any(audio_dir.glob("*.aiff")):
        for utterance in utterances:
            path = audio_dir / f"{utterance.utterance_id}.aiff"
            load_started = time.perf_counter()
            if path.is_file():
                path.read_bytes()
            load_times.append(time.perf_counter() - load_started)
        audio_loading = summarize_seconds(load_times)
    else:
        audio_loading = {
            "n": 0,
            "mean": None,
            "median": None,
            "p95": None,
            "reason": "no local AIFF files were present",
        }

    manifest = ROOT / "data" / "synthetic" / "manifest.csv"
    report = {
        "experiment_id": "sim-eval-v2",
        "dataset": "synthetic",
        "seed": seed,
        "started_at": started_at,
        "git_head": _git(["rev-parse", "HEAD"]),
        "git_status_short": _git(["status", "--short"]),
        "backend": "synthetic_hypothesis",
        "whisper_executed": False,
        "asr_decode": False,
        "candidate_provenance": SYNTHETIC_EDIT,
        "retry_mechanism": SIMULATED_RETRY,
        "phase_1_approved": False,
        "common_voice": "not_acquired",
        "manifest_sha256": _sha256(manifest),
        "variants_sha256": _sha256(ROOT / "data" / "synthetic" / "transcripts" / "variants.csv"),
        "preserved_initial_sha256": before,
        "candidate_oracle": primary_oracle,
        "systems_recomputed_not_a_replacement": systems,
        "by_v0_category": category_report,
        "by_variant_category": variant_report,
        "b2_policy": policy,
        "per_slot": slot_report,
        "ablations": ablations,
        "latency_seconds": {
            "audio_synthesis": {
                "value": None,
                "reason": (
                    "macOS say was not run again. The initial 437.66s wall time "
                    "included synthesis and is not ASR or recovery latency."
                ),
            },
            "asr_decode": {
                "value": None,
                "reason": "no waveform decoder was executed",
            },
            "audio_loading": audio_loading,
            "candidate_generation": {
                "n": 1,
                "mean": candidate_generation_seconds,
                "median": candidate_generation_seconds,
                "p95": candidate_generation_seconds,
            },
            "nlu": summarize_seconds(nlu_times),
            "candidate_scoring": summarize_seconds(score_times),
            "failure_diagnosis": summarize_seconds(diagnosis_times),
            "recovery_decision": summarize_seconds(decision_times),
            "text_pipeline_per_utterance": summarize_seconds(text_times),
        },
        "limitation": (
            "Recomputed scores describe the same unchanged controller and the same "
            "three synthetic candidates. They do not replace experiments/B0, B1, or B2."
        ),
    }
    destination = ROOT / "experiments" / "sim-eval-v2"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    artifact_dir = ROOT / "artifacts" / "reports" / "simulation_v2"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    after = {str(path.relative_to(ROOT)): _sha256(path) for path in PRESERVED}
    if after != before:
        raise SystemExit("Initial experiment files changed")
    print(json.dumps({
        "experiment_id": report["experiment_id"],
        "oracle_frame": primary_oracle["complete_frame_oracle_coverage"],
        "oracle_intent": primary_oracle["candidate_oracle_intent_accuracy"],
        "no_recoverable_frame": primary_oracle["utterances_with_no_recoverable_frame"],
        "action_accuracy": policy["action_accuracy"],
        "preserved": before == after,
    }, indent=2))


if __name__ == "__main__":
    main()
