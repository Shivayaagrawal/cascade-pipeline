"""Audit records for the frozen sim-eval-v3 run.

This module calls the existing v3 functions and writes nothing.
It does not add a negation reader, an uncertainty reader, or a new selector.
"""

from __future__ import annotations

import time
from pathlib import Path

from cascadeguard.evaluation.intent_metrics import frames_equal
from cascadeguard.evaluation.latency_stats import summarize_seconds
from cascadeguard.evaluation.semantic_evidence import assess
from cascadeguard.evaluation.selective import recovery_action
from cascadeguard.evaluation.v3_metrics import expected_recovery, slot_critical_mismatch
from cascadeguard.simulation.utterance_generator import Utterance

OUTPUT_DIR_NAME = "sim-eval-v3b"
AUTHORITATIVE_EXPERIMENT = "sim-eval-v3"
AUTHORITATIVE_REPORT = "experiments/sim-eval-v3/report.json"

NEGATION_UNAVAILABLE = {
    "available": False,
    "reason": (
        "assess() returns intent cues and lexicon slot values. "
        "No existing function returns a negation finding for a candidate string."
    ),
}
UNCERTAINTY_UNAVAILABLE = {
    "available": False,
    "reason": "No existing function returns an uncertainty finding for a candidate string.",
}
RECOVERY_IMPROVEMENT_UNAVAILABLE = {
    "available": False,
    "reason": (
        "The authoritative v1 condition supplies no second candidate bundle. "
        "recovery_action is called with retry_candidates omitted, so this audit "
        "cannot score whether a retry changed frame correctness. A retry is not "
        "treated as correct."
    ),
}

REQUESTED_CONDITIONS = (
    "existing_baseline_candidate_selection",
    "semantic_evidence_preservation_disabled",
    "slot_aware_selection_disabled",
    "selective_prediction_disabled",
    "recovery_disabled",
    "full_synthetic_v3",
)


def assert_audit_destination(path: Path) -> None:
    """v3b may write only to a directory named sim-eval-v3b."""

    if path.name != OUTPUT_DIR_NAME:
        raise ValueError("v3b can write only to a directory named sim-eval-v3b")


def candidate_evidence_record(text: str, lexicon: dict[str, tuple[str, ...]]) -> dict[str, object]:
    """Intent and slot evidence from assess(). Negation and uncertainty stay unavailable."""

    evidence = assess(text, lexicon)
    return {
        "transcript": text,
        "intent_evidence": list(evidence.intents),
        "slot_evidence": {name: list(values) for name, values in evidence.slots.items()},
        "negation_evidence": dict(NEGATION_UNAVAILABLE),
        "uncertainty_evidence": dict(UNCERTAINTY_UNAVAILABLE),
    }


def decision_log_row(
    utterance: Utterance,
    candidates: list[str],
    lexicon: dict[str, tuple[str, ...]],
) -> dict[str, object]:
    """One audit row. Expected action is fixed before the selective decision is read."""

    expected = expected_recovery(utterance, candidates)
    action, decision, mechanism = recovery_action(candidates, lexicon)
    committed = action.value in {"CONTINUE", "RETRY"}
    if committed:
        frame_matches = frames_equal(
            utterance.intent,
            utterance.slots,
            decision.intent,
            decision.slots,
        )
        unsafe = not frame_matches
    else:
        frame_matches = None
        unsafe = False
    return {
        "experiment_id": OUTPUT_DIR_NAME,
        "authoritative_experiment": AUTHORITATIVE_EXPERIMENT,
        "utterance_id": utterance.utterance_id,
        "min_support": 1,
        "triggering_evidence": {
            "reason": decision.reason,
            "support": decision.support,
            "mechanism": mechanism,
            "candidates": [
                {"index": index, **candidate_evidence_record(text, lexicon)}
                for index, text in enumerate(candidates)
            ],
        },
        "selected_action": action.value,
        "selected_intent": decision.intent,
        "selected_slots": decision.slots,
        "expected_action": expected,
        "safety_outcome": {
            "action_matches_expected": action.value == expected,
            "committed": committed,
            "frame_matches_reference": frame_matches,
            "unsafe_decision": unsafe,
            "slot_critical_unsafe": slot_critical_mismatch(utterance, decision),
            "recovery_improved_semantic_correctness": dict(RECOVERY_IMPROVEMENT_UNAVAILABLE),
            "reference_frame_for_scoring": {
                "intent": utterance.intent,
                "slots": dict(utterance.slots),
                "note": (
                    "Used only to score the decision. assess(), decide_selective(), "
                    "and recovery_action() do not receive this frame."
                ),
            },
        },
    }


def decision_log(
    utterances: list[Utterance],
    grouped: dict[str, list[str]],
    lexicon: dict[str, tuple[str, ...]],
) -> list[dict[str, object]]:
    """One row per utterance, in the supplied order."""

    return [
        decision_log_row(utterance, grouped[utterance.utterance_id], lexicon)
        for utterance in utterances
    ]


def log_mismatches(rows: list[dict[str, object]], selective: dict[str, object]) -> list[str]:
    """The per-utterance log has to add up to the existing aggregate."""

    errors = []
    action_counts = selective["action_counts"]
    if not isinstance(action_counts, dict):
        return ["action_counts missing"]
    for action, count in action_counts.items():
        found = sum(1 for row in rows if row["selected_action"] == action)
        if found != count:
            errors.append(f"{action} log count {found} aggregate {count}")
    coverage = selective["decision_coverage"]
    risk = selective["selective_risk"]
    if isinstance(coverage, dict):
        committed = sum(1 for row in rows if row["safety_outcome"]["committed"] is True)  # type: ignore[index]
        if committed != coverage["numerator"]:
            errors.append(f"committed log count {committed} coverage {coverage['numerator']}")
    if isinstance(risk, dict):
        unsafe = sum(1 for row in rows if row["safety_outcome"]["unsafe_decision"] is True)  # type: ignore[index]
        if unsafe != risk["numerator"]:
            errors.append(f"unsafe log count {unsafe} selective risk {risk['numerator']}")
    return errors


def published_slot_metrics(selective: dict[str, object]) -> dict[str, object]:
    """Precision, recall, and F1 from the existing slot_scores() values."""

    def one(block: dict[str, object] | None) -> dict[str, object] | None:
        if block is None:
            return None
        scores = block["slot_scores"]
        if not isinstance(scores, dict):
            return {"available": False, "reason": "slot_scores missing"}
        return {
            "precision": scores["precision"],
            "recall": scores["recall"],
            "f1": scores["f1"],
            "matched_pairs": scores["matched_pairs"],
            "predicted_pairs": scores["predicted_pairs"],
            "reference_pairs": scores["reference_pairs"],
            "precision_denominator": "predicted_pairs",
            "recall_denominator": "reference_pairs",
            "function": "cascadeguard.evaluation.slot_metrics.slot_scores",
        }

    abstaining = selective["accuracy_counting_abstention_as_incorrect"]
    committed = selective["accuracy_on_committed_decisions"]
    return {
        "definition": (
            "Micro-average over (slot name, value) pairs from slot_scores(). "
            "An empty gold slot set and an empty prediction count as one matched pair-set. "
            "These are the scores already stored by selective_report(), not a new metric."
        ),
        "b1_selector_all_inputs": one(selective["b1_selector"]),  # type: ignore[arg-type]
        "forced_selector_all_inputs": one(selective["forced_slot_aware_selector"]),  # type: ignore[arg-type]
        "selective_all_inputs_abstention_is_empty_prediction": one(abstaining),  # type: ignore[arg-type]
        "selective_committed_decisions_only": one(committed),  # type: ignore[arg-type]
    }


def lexical_timing(
    utterances: list[Utterance],
    grouped: dict[str, list[str]],
    lexicon: dict[str, tuple[str, ...]],
) -> dict[str, object]:
    """Wall time of the lexical calls. This is not ASR latency."""

    assess_samples: list[float] = []
    decide_samples: list[float] = []
    for utterance in utterances:
        texts = grouped[utterance.utterance_id]
        started = time.perf_counter()
        for text in texts:
            assess(text, lexicon)
        assess_samples.append(time.perf_counter() - started)
        started = time.perf_counter()
        recovery_action(texts, lexicon)
        decide_samples.append(time.perf_counter() - started)
    return {
        "measure": "lexical_processing_only",
        "asr_latency": False,
        "audio_decoded": False,
        "what_was_timed": (
            "Wall time of assess() over one utterance's v1 candidate strings, "
            "then wall time of recovery_action() on that same list. "
            "No waveform was decoded. This is not ASR latency."
        ),
        "assess_seconds": summarize_seconds(assess_samples),
        "recovery_action_seconds": summarize_seconds(decide_samples),
    }


def _selector_metrics(block: dict[str, object]) -> dict[str, object]:
    return {
        "intent_accuracy": block["intent_accuracy"],
        "slot_scores": block["slot_scores"],
        "exact_frame_accuracy": block["exact_frame_accuracy"],
    }


def ablation_table(
    selective: dict[str, object],
    frozen_recovery: dict[str, object] | None,
) -> dict[str, object]:
    """Map the six requested names onto functions that already exist."""

    baseline = _selector_metrics(selective["b1_selector"])  # type: ignore[arg-type]
    forced = _selector_metrics(selective["forced_slot_aware_selector"])  # type: ignore[arg-type]
    primary = {
        "decision_coverage": selective["decision_coverage"],
        "selective_risk": selective["selective_risk"],
        "unsafe_commitment": selective["unsafe_commitment"],
        "action_counts": selective["action_counts"],
        "action_accuracy": selective["action_accuracy"],
        "slot_scores_counting_abstention_as_empty": selective["accuracy_counting_abstention_as_incorrect"][  # type: ignore[index]
            "slot_scores"
        ],
        "exact_frame_counting_abstention_as_incorrect": selective["accuracy_counting_abstention_as_incorrect"][  # type: ignore[index]
            "exact_frame_accuracy"
        ],
    }
    cited = None
    if frozen_recovery is not None:
        cited = {
            "source": AUTHORITATIVE_REPORT,
            "key": "recovery_with_simulated_retry",
            "recomputed": False,
            "action_counts": frozen_recovery.get("action_counts"),
            "decision_coverage": frozen_recovery.get("decision_coverage"),
            "selective_risk": frozen_recovery.get("selective_risk"),
        }
    return {
        "role": "map of requested names onto existing functions",
        "not_a_new_performance_experiment": True,
        "authoritative_results": AUTHORITATIVE_REPORT,
        "input": (
            "v1 injector candidate lists, seed 17, utt-000 through utt-199, "
            "min_support 1, no retry bundle"
        ),
        "rows": [
            {
                "requested_condition": "existing_baseline_candidate_selection",
                "implementation": "cascadeguard.candidates.candidate_manager.select_candidate",
                "called_through": "cascadeguard.evaluation.v3_metrics.b1_frames",
                "distinct_from_another_row": True,
                "metrics": baseline,
            },
            {
                "requested_condition": "semantic_evidence_preservation_disabled",
                "implementation": "cascadeguard.candidates.candidate_manager.select_candidate",
                "distinct_from_another_row": False,
                "same_implementation_as": "existing_baseline_candidate_selection",
                "reason": (
                    "The prefix selector never calls assess(). v3 has no switch that "
                    "turns evidence preservation off while leaving another selector in place."
                ),
                "metrics": "same_as_existing_baseline_candidate_selection",
            },
            {
                "requested_condition": "slot_aware_selection_disabled",
                "implementation": "cascadeguard.candidates.candidate_manager.select_candidate",
                "distinct_from_another_row": False,
                "same_implementation_as": "existing_baseline_candidate_selection",
                "reason": (
                    "Slot-aware selection is forced_selection(). Turning it off leaves "
                    "the prefix selector. There is no third selector."
                ),
                "metrics": "same_as_existing_baseline_candidate_selection",
            },
            {
                "requested_condition": "selective_prediction_disabled",
                "implementation": "cascadeguard.evaluation.selective.forced_selection",
                "distinct_from_another_row": True,
                "reason": "This selector always returns one frame. It is not a safety decision.",
                "metrics": forced,
            },
            {
                "requested_condition": "recovery_disabled",
                "implementation": "cascadeguard.evaluation.selective.recovery_action",
                "call": "retry_candidates omitted",
                "distinct_from_another_row": False,
                "same_implementation_as": "full_synthetic_v3_on_the_v1_list",
                "reason": (
                    "The published v1 condition also omits the retry bundle. "
                    "On this input, recovery disabled and full v3 are the same call."
                ),
                "metrics": primary,
            },
            {
                "requested_condition": "full_synthetic_v3",
                "implementation": "cascadeguard.evaluation.selective.recovery_action",
                "call": "retry_candidates omitted, min_support 1, v1 injector list",
                "distinct_from_another_row": False,
                "same_recomputed_call_as": "recovery_disabled",
                "metrics": "same_as_recovery_disabled",
                "cited_recovery_condition_not_recomputed": cited,
            },
        ],
    }


def mismatches_against_frozen(recomputed: dict[str, object], frozen: dict[str, object]) -> list[str]:
    """The audit has to reproduce the frozen v1 section. A difference stops the run."""

    errors: list[str] = []

    def expect(actual: object, reference: object, path: str) -> None:
        if actual != reference:
            errors.append(f"{path}: recomputed {actual!r} frozen {reference!r}")

    for key in (
        "decision_coverage",
        "selective_risk",
        "unsafe_commitment",
        "slot_critical_unsafe_commitment",
        "action_accuracy",
    ):
        for field in ("numerator", "denominator", "value"):
            expect(recomputed[key][field], frozen[key][field], f"{key}.{field}")  # type: ignore[index]
    expect(recomputed["action_counts"], frozen["action_counts"], "action_counts")
    expect(recomputed["retry_mechanism_counts"], frozen["retry_mechanism_counts"], "retry_mechanism_counts")
    for block in (
        "b1_selector",
        "forced_slot_aware_selector",
        "accuracy_counting_abstention_as_incorrect",
    ):
        expect(recomputed[block]["slot_scores"], frozen[block]["slot_scores"], f"{block}.slot_scores")  # type: ignore[index]
        expect(
            recomputed[block]["exact_frame_accuracy"],  # type: ignore[index]
            frozen[block]["exact_frame_accuracy"],  # type: ignore[index]
            f"{block}.exact_frame_accuracy",
        )
        expect(
            recomputed[block]["intent_accuracy"],  # type: ignore[index]
            frozen[block]["intent_accuracy"],  # type: ignore[index]
            f"{block}.intent_accuracy",
        )
    committed = recomputed["accuracy_on_committed_decisions"]
    frozen_committed = frozen["accuracy_on_committed_decisions"]
    if isinstance(committed, dict) and isinstance(frozen_committed, dict):
        expect(committed["slot_scores"], frozen_committed["slot_scores"], "committed.slot_scores")
        expect(committed["intent_accuracy"], frozen_committed["intent_accuracy"], "committed.intent_accuracy")
    else:
        errors.append("accuracy_on_committed_decisions missing")
    return errors


def assemble_audit_report(
    selective: dict[str, object],
    rows: list[dict[str, object]],
    timing: dict[str, object],
    frozen_recovery: dict[str, object] | None,
    *,
    seed: int,
    utterance_ids: list[str],
) -> dict[str, object]:
    """Summary report. The caller writes it under sim-eval-v3b."""

    if not utterance_ids:
        raise ValueError("utterance_ids is empty")
    return {
        "experiment_id": OUTPUT_DIR_NAME,
        "role": "audit_and_reporting_extension",
        "authoritative_experiment": AUTHORITATIVE_EXPERIMENT,
        "authoritative_report": AUTHORITATIVE_REPORT,
        "not_a_new_performance_experiment": True,
        "real_speech_validation": False,
        "asr_decode": False,
        "librispeech_used": False,
        "test_clean_accessed": False,
        "phase_1c": "blocked",
        "dataset": "synthetic",
        "seed": seed,
        "utterance_count": len(utterance_ids),
        "utterance_id_first": utterance_ids[0],
        "utterance_id_last": utterance_ids[-1],
        "backend": "synthetic_hypothesis",
        "retry_mechanism": "simulated_candidate_rescore",
        "candidate_evidence": {
            "location": "experiments/sim-eval-v3b/decision_log.jsonl",
            "fields_from_assess": ["intent_evidence", "slot_evidence"],
            "negation_evidence": dict(NEGATION_UNAVAILABLE),
            "uncertainty_evidence": dict(UNCERTAINTY_UNAVAILABLE),
        },
        "decision_log": {
            "path": "experiments/sim-eval-v3b/decision_log.jsonl",
            "rows": len(rows),
            "one_row_per_utterance": True,
        },
        "slot_metrics": published_slot_metrics(selective),
        "lexical_processing_timing": timing,
        "ablation": ablation_table(selective, frozen_recovery),
        "limitation": (
            "v3b repeats the frozen v3 functions on the same 200 synthetic transcripts. "
            "It does not show that the method works on real speech. "
            "The authoritative numbers remain experiments/sim-eval-v3/report.json."
        ),
    }
