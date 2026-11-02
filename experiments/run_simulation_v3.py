#!/usr/bin/env python3
"""Simulation Evaluation v3. Does not rewrite v1 summaries or the v2 report."""

from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances  # noqa: E402
from cascadeguard.evaluation.v3_metrics import (  # noqa: E402
    b0_exact_count,
    candidate_information,
    category_selective_report,
    gold_transcript_oracle,
    risk_coverage_curve,
    selective_report,
)
from cascadeguard.simulation.candidate_diversity import (  # noqa: E402
    gold_is_absent,
    gold_is_not_exact,
    paraphrases,
    slot_removed,
    split_evidence,
    v1_candidate_texts,
)
from cascadeguard.simulation.error_injector import (  # noqa: E402
    ERROR_CATEGORIES,
    apply_category,
    categories_for_index,
)
from cascadeguard.simulation.utterance_generator import generate_utterances  # noqa: E402

PRESERVED = (
    ROOT / "experiments" / "B0" / "summary.json",
    ROOT / "experiments" / "B1" / "summary.json",
    ROOT / "experiments" / "B2" / "summary.json",
    ROOT / "artifacts" / "reports" / "simulation_report.json",
    ROOT / "experiments" / "sim-eval-v2" / "report.json",
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


def _grouped(rows: list, builder) -> dict[str, list[str]]:
    grouped = {row.utterance_id: builder(row) for row in rows}
    for row in rows:
        if not gold_is_absent(row.text, grouped[row.utterance_id]):
            raise SystemExit(f"Gold transcript entered a candidate list for {row.utterance_id}")
    return grouped


def _corrupt(text: str, row, category: str) -> str:
    rng = random.Random(f"17:{row.utterance_id}:{category}")
    edited = apply_category(text, row.slots, category, rng)
    if edited.casefold() == row.text.casefold():
        raise SystemExit(f"Corruption copied the gold transcript for {row.utterance_id} {category}")
    # The ambiguous edit appends a fixed balance question. For the one utterance
    # whose gold text is that question, the question is the reference sentence.
    # Every other category must not contain the reference sentence.
    if category != "ambiguous_transcript" and row.text.casefold() in edited.casefold():
        raise SystemExit(f"Corruption copied the gold transcript for {row.utterance_id} {category}")
    return edited


def main() -> None:
    before = {str(path.relative_to(ROOT)): _sha256(path) for path in PRESERVED}
    started_at = datetime.now(timezone.utc).isoformat()
    seed = 17
    utterances = generate_utterances()
    lexicon = lexicon_from_utterances(utterances)
    v0_category = {
        row.utterance_id: categories_for_index(index)[0]
        for index, row in enumerate(utterances)
    }

    methods = {
        "v1_injector": v1_candidate_texts(utterances, seed),
        "paraphrase": _grouped(utterances, paraphrases),
        "slot_removed": _grouped(utterances, slot_removed),
        "split_evidence": _grouped(utterances, split_evidence),
    }
    for row in utterances:
        if not gold_is_not_exact(row.text, methods["v1_injector"][row.utterance_id]):
            raise SystemExit(f"Gold transcript entered the v1 list for {row.utterance_id}")

    one_supported = {}
    for row in utterances:
        clean = methods["paraphrase"][row.utterance_id]
        removed = methods["slot_removed"][row.utterance_id]
        one_supported[row.utterance_id] = [clean[0], removed[0], removed[1]]
        if not gold_is_absent(row.text, one_supported[row.utterance_id]):
            raise SystemExit(f"Gold transcript entered the support curve for {row.utterance_id}")

    information = {
        name: candidate_information(utterances, grouped, lexicon) for name, grouped in methods.items()
    }
    comparisons = {}
    for name, grouped in methods.items():
        comparisons[name] = selective_report(
            utterances,
            grouped,
            lexicon,
            b0_exact=b0_exact_count(utterances, grouped),
        )

    curves = {
        "paraphrase": risk_coverage_curve(utterances, methods["paraphrase"], lexicon),
        "one_clean_candidate": risk_coverage_curve(utterances, one_supported, lexicon),
        "v1_injector": risk_coverage_curve(utterances, methods["v1_injector"], lexicon),
    }

    recovery = selective_report(
        utterances,
        methods["slot_removed"],
        lexicon,
        retry_grouped=methods["paraphrase"],
        b0_exact=b0_exact_count(utterances, methods["slot_removed"]),
    )

    by_v0 = category_selective_report(
        utterances,
        methods["v1_injector"],
        lexicon,
        v0_category,
    )
    single_corrupted: dict[str, dict[str, list[str]]] = {category: {} for category in ERROR_CATEGORIES}
    agreement: dict[str, dict[str, list[str]]] = {category: {} for category in ERROR_CATEGORIES}
    ambiguous_contains_gold = 0
    for row in utterances:
        clean = methods["paraphrase"][row.utterance_id]
        for category in ERROR_CATEGORIES:
            edited = _corrupt(clean[0], row, category)
            if category == "ambiguous_transcript" and row.text.casefold() in edited.casefold():
                ambiguous_contains_gold += 1
            single_corrupted[category][row.utterance_id] = [edited]
            agreement[category][row.utterance_id] = [edited, clean[1], clean[2]]
    corrupted_report = {
        category: category_selective_report(
            utterances,
            single_corrupted[category],
            lexicon,
            {row.utterance_id: category for row in utterances},
        )[category]
        for category in ERROR_CATEGORIES
    }
    agreement_report = {
        category: category_selective_report(
            utterances,
            agreement[category],
            lexicon,
            {row.utterance_id: category for row in utterances},
        )[category]
        for category in ERROR_CATEGORIES
    }

    v2_path = ROOT / "experiments" / "sim-eval-v2" / "report.json"
    unchanged_b2 = None
    if v2_path.is_file():
        v2_report = json.loads(v2_path.read_text(encoding="utf-8"))
        unchanged_b2 = {
            "source": "experiments/sim-eval-v2/report.json",
            "controller_modified": False,
            "thresholds_tuned_on_v1_or_v2": False,
            "unsafe_commitment": v2_report["b2_policy"]["unsafe_commitment"],
            "action_accuracy": v2_report["b2_policy"]["action_accuracy"],
        }

    config_path = ROOT / "configs" / "evaluation_v3.yaml"
    report = {
        "experiment_id": "sim-eval-v3",
        "dataset": "synthetic",
        "seed": seed,
        "started_at": started_at,
        "git_head": _git(["rev-parse", "HEAD"]),
        "git_status_short": _git(["status", "--short"]),
        "backend": "synthetic_hypothesis",
        "whisper_executed": False,
        "asr_decode": False,
        "retry_mechanism": "simulated_candidate_rescore",
        "phase_1_approved": False,
        "common_voice": "not_acquired",
        "b2_thresholds_tuned": False,
        "gold_transcript_in_primary_candidates": False,
        "manifest_sha256": _sha256(ROOT / "data" / "synthetic" / "manifest.csv"),
        "config_sha256": _sha256(config_path),
        "preserved_sha256_before": before,
        "candidate_information": information,
        "selector_comparison": comparisons,
        "risk_coverage": curves,
        "recovery_with_simulated_retry": recovery,
        "by_v0_category_on_v1_candidates": by_v0,
        "ambiguous_edit_contains_reference_sentence": {
            "count": ambiguous_contains_gold,
            "reason": (
                "The ambiguous category appends the fixed question 'What is my account balance?'. "
                "That question is the reference sentence of one balance utterance, so the appended "
                "question is the reference text. It is not added as its own candidate."
            ),
        },
        "by_corruption_of_one_paraphrase": corrupted_report,
        "by_corruption_with_two_clean_paraphrases": agreement_report,
        "gold_transcript_oracle": gold_transcript_oracle(utterances, lexicon),
        "unchanged_b2_recorded_in_v2": unchanged_b2,
        "oracle_definitions": {
            "candidate_oracle_coverage": (
                "Share of utterances whose ordinary candidate list still contains the "
                "gold intent cue, the gold slot values, or both in one candidate. "
                "The gold transcript is not added."
            ),
            "gold_transcript_oracle": (
                "The reference sentence is scored by itself, in a separate condition. "
                "It is not a member of the B0, B1, or selective candidate lists."
            ),
            "achieved_performance": (
                "Frames the selective layer commits. Abstention counts as not correct "
                "in the all-input rate, and selective risk is the error among commits only."
            ),
        },
        "limitation": (
            "Candidate lists are written variants, not recognizer N-best lists. "
            "RETRY rescores a supplied second list. No waveform was decoded."
        ),
    }
    destination = ROOT / "experiments" / "sim-eval-v3"
    destination.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2) + "\n"
    (destination / "report.json").write_text(payload, encoding="utf-8")
    artifact_dir = ROOT / "artifacts" / "reports" / "simulation_v3"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "report.json").write_text(payload, encoding="utf-8")
    after = {str(path.relative_to(ROOT)): _sha256(path) for path in PRESERVED}
    if after != before:
        raise SystemExit("Preserved experiment files changed")
    report["preserved_sha256_after"] = after
    payload = json.dumps(report, indent=2) + "\n"
    (destination / "report.json").write_text(payload, encoding="utf-8")
    (artifact_dir / "report.json").write_text(payload, encoding="utf-8")
    if {str(path.relative_to(ROOT)): _sha256(path) for path in PRESERVED} != before:
        raise SystemExit("Preserved experiment files changed")
    paraphrase = comparisons["paraphrase"]
    v1 = comparisons["v1_injector"]
    print(json.dumps({
        "experiment_id": report["experiment_id"],
        "v1_frame_oracle": information["v1_injector"]["complete_frame_oracle_coverage"],
        "paraphrase_frame_oracle": information["paraphrase"]["complete_frame_oracle_coverage"],
        "v1_coverage": v1["decision_coverage"],
        "v1_selective_risk": v1["selective_risk"],
        "paraphrase_coverage": paraphrase["decision_coverage"],
        "paraphrase_selective_risk": paraphrase["selective_risk"],
        "preserved": True,
    }, indent=2))


if __name__ == "__main__":
    main()
