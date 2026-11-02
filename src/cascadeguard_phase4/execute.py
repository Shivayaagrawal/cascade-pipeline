"""Run frozen strategies on Phase 4 bundles. Oracle labels are joined afterwards."""

from __future__ import annotations

import json
from pathlib import Path

from cascadeguard.evaluation.semantic_evidence import lexicon_from_utterances
from cascadeguard_facade.adapters import b0_prefix
from cascadeguard_facade.adapters import b1_forced_lexical
from cascadeguard_facade.adapters import b1_prefix
from cascadeguard_facade.adapters import b2_lexical_v3
from cascadeguard_facade.adapters import b2_prefix_controller
from cascadeguard_facade.commit_policy_v4 import PolicySwitches
from cascadeguard_facade.contracts import CandidateBundle, CandidateRecord
from cascadeguard_facade.risk_assessment_v4 import thresholds, weight_grid
from cascadeguard_facade.semantic_controller_v4 import run_semantic_v4
from cascadeguard_phase4.candidate_provenance import _by_text
from cascadeguard_phase4.candidate_provenance import action_path_consistent
from cascadeguard_phase4.candidate_provenance import lexical_source
from cascadeguard_phase4.candidate_provenance import v4_source
from cascadeguard_phase4.independent_evaluator import judge_output
from cascadeguard_phase4.phase4_metrics import summarize

PHASE3_WEIGHTS = {
    "intent": 0.0,
    "slot": 0.0,
    "polarity": 0.0,
    "ambiguity": 0.0,
    "contradiction": 1.0,
}
PHASE3_THRESHOLD = 0.25


def bundle_from(record: dict[str, object]) -> CandidateBundle:
    candidates = tuple(
        CandidateRecord(
            str(item["candidate_id"]),
            str(item["text"]),
            str(item["provenance"]),
            int(item["rank"]),
            str(record["candidate_source"]),
        )
        for item in record["candidates"]
    )
    return CandidateBundle(
        str(record["case_id"]),
        candidates,
        str(record["generation_method"]),
        str(record["candidate_source"]),
    )


def _frame(intent: str | None, slots: dict[str, str] | None) -> dict[str, object] | None:
    if intent is None and not slots:
        return None
    return {"intent": intent, "slots": dict(slots or {})}


def _raw_dict(raw: object) -> dict[str, object]:
    return {
        "strategy": raw.strategy,
        "utterance_id": raw.utterance_id,
        "invoked": raw.invoked,
        "text": raw.text,
        "intent": raw.intent,
        "slots": dict(raw.slots),
        "action": raw.action,
        "reason": raw.reason,
        "retry_mechanism": raw.retry_mechanism,
        "support": raw.support,
        "retries": raw.retries,
        "elapsed_seconds": raw.elapsed_seconds,
    }


def _finish(
    record: dict[str, object],
    bundle: CandidateBundle,
    *,
    strategy: str,
    action: str | None,
    reason: str,
    raw: dict[str, object],
    committed_intent: str | None,
    committed_slots: dict[str, str],
    answered_intent: str | None,
    answered_slots: dict[str, str],
    selected_id: str | None,
    selected_text: str | None,
    committed_id: str | None,
    risk: dict[str, object] | None,
    polarity: str | None,
    modality: str | None,
    retry_source: str | None,
) -> dict[str, object]:
    committed = committed_intent is not None
    ids = {item.candidate_id for item in bundle.ordered()}
    return {
        "case_id": str(record["case_id"]),
        "strategy_id": strategy,
        "action": action,
        "reason_code": reason,
        "selected_candidate_id": selected_id,
        "selected_candidate_text": selected_text,
        "committed_candidate_id": committed_id if committed else None,
        "retry_source_candidate": retry_source if committed else None,
        "raw_controller_output": raw,
        "answered_frame": _frame(answered_intent, answered_slots),
        "committed_frame": _frame(committed_intent, committed_slots) if committed else None,
        "committed": committed,
        "committed_intent": committed_intent,
        "committed_slots": committed_slots if committed else {},
        "risk_breakdown": risk,
        "candidate_provenance": [item.provenance for item in bundle.ordered()],
        "emitted_polarity": polarity,
        "emitted_modality": modality,
        "action_path_consistent": action_path_consistent(
            strategy, action, committed, committed_id if committed else None, ids
        ),
        "normalized_decision": {"action": action, "reason": reason, "committed": committed},
    }


def _frames_from_normalized(normalized: object) -> tuple[str | None, dict[str, str], str | None, dict[str, str]]:
    committed = normalized.committed_frame
    answered = normalized.answered_frame
    committed_intent = None if committed is None else committed.intent
    committed_slots = {} if committed is None else committed.as_dict()
    answered_intent = None if answered is None else answered.intent
    answered_slots = {} if answered is None else answered.as_dict()
    return committed_intent, committed_slots, answered_intent, answered_slots


def _prefix(record, bundle, adapter, strategy: str) -> dict[str, object]:
    raw, normalized = adapter.execute(bundle)
    committed_intent, committed_slots, answered_intent, answered_slots = _frames_from_normalized(normalized)
    selected_text = raw.text
    selected_id = _by_text(bundle, selected_text)
    if strategy == "b0_prefix" and bundle.candidate_count:
        selected_id = bundle.ordered()[0].candidate_id
        selected_text = bundle.ordered()[0].text
    return _finish(
        record,
        bundle,
        strategy=strategy,
        action=normalized.action,
        reason=normalized.reason,
        raw=_raw_dict(raw),
        committed_intent=committed_intent,
        committed_slots=committed_slots,
        answered_intent=answered_intent,
        answered_slots=answered_slots,
        selected_id=selected_id,
        selected_text=selected_text,
        committed_id=selected_id,
        risk=None,
        polarity=None,
        modality=None,
        retry_source=selected_id if normalized.action == "RETRY" else None,
    )


def _lexical_family(record, bundle, lexicon, strategy: str, forced: bool) -> dict[str, object]:
    if forced:
        raw, normalized = b1_forced_lexical.execute(bundle, lexicon)
    else:
        raw, normalized = b2_lexical_v3.execute(bundle, lexicon)
    committed_intent, committed_slots, answered_intent, answered_slots = _frames_from_normalized(normalized)
    source_intent = committed_intent if committed_intent is not None else answered_intent
    source_slots = committed_slots if committed_intent is not None else answered_slots
    selected_id = lexical_source(bundle, lexicon, source_intent, tuple(sorted(source_slots.items())))
    selected_text = next((item.text for item in bundle.ordered() if item.candidate_id == selected_id), None)
    return _finish(
        record,
        bundle,
        strategy=strategy,
        action=normalized.action,
        reason=normalized.reason,
        raw=_raw_dict(raw),
        committed_intent=committed_intent,
        committed_slots=committed_slots,
        answered_intent=answered_intent,
        answered_slots=answered_slots,
        selected_id=selected_id,
        selected_text=selected_text,
        committed_id=selected_id,
        risk=None,
        polarity=None,
        modality=None,
        retry_source=selected_id if normalized.action == "RETRY" else None,
    )


def jsonable(value):
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    return value


def _modality(raw: dict[str, object], selected_id: str | None) -> str | None:
    assessments = raw.get("assessments") or []
    if not isinstance(assessments, list) or not assessments:
        return None
    for assessment in assessments:
        if isinstance(assessment, dict) and assessment.get("candidate_id") == selected_id:
            return assessment.get("modality")
    first = assessments[0]
    if isinstance(first, dict):
        return first.get("modality")
    return None


def _v4(record, bundle, lexicon, switches: PolicySwitches, weights, threshold, frozen: bool) -> dict[str, object]:
    result = run_semantic_v4(
        bundle,
        lexicon,
        weights=weights,
        threshold=threshold,
        switches=switches,
        frozen_recovery=frozen,
    )
    slots = dict(result.committed_slots)
    if frozen:
        selected_id = lexical_source(bundle, lexicon, result.committed_intent, tuple(result.committed_slots))
    else:
        selected_id = v4_source(bundle, lexicon, result.committed_intent, tuple(result.committed_slots), switches)
    selected_text = next((item.text for item in bundle.ordered() if item.candidate_id == selected_id), None)
    raw = jsonable(result.raw)
    return _finish(
        record,
        bundle,
        strategy="b2_semantic_v4",
        action=result.action,
        reason=result.reason,
        raw=raw,
        committed_intent=result.committed_intent,
        committed_slots=slots,
        answered_intent=result.answered_intent,
        answered_slots=dict(result.answered_slots),
        selected_id=selected_id,
        selected_text=selected_text,
        committed_id=selected_id,
        risk=result.risk,
        polarity=result.polarity,
        modality=_modality(raw, selected_id),
        retry_source=selected_id if result.action == "RETRY" else None,
    )


def run_strategy(record, code, lexicon, *, weights, threshold, switches=None):
    bundle = bundle_from(record)
    switches = switches or PolicySwitches()
    if code == "E0":
        return _prefix(record, bundle, b0_prefix, "b0_prefix")
    if code == "E1":
        return _prefix(record, bundle, b1_prefix, "b1_prefix")
    if code == "E2":
        return _prefix(record, bundle, b2_prefix_controller, "b2_prefix_controller")
    if code == "E3":
        return _lexical_family(record, bundle, lexicon, "b1_forced_lexical", True)
    if code == "E4":
        return _lexical_family(record, bundle, lexicon, "b2_lexical_v3", False)
    if code == "E5":
        decision = _v4(record, bundle, lexicon, switches, weights, threshold, True)
        decision["strategy_id"] = "E5_diagnosis_frozen_action"
        return decision
    if code == "E6":
        held = PolicySwitches(
            polarity=switches.polarity,
            ambiguity=switches.ambiguity,
            critical_slots=switches.critical_slots,
            contradiction=switches.contradiction,
            completeness=switches.completeness,
            modality=switches.modality,
            risk_score=switches.risk_score,
            allow_retry=False,
        )
        decision = _v4(record, bundle, lexicon, held, weights, threshold, False)
        decision["strategy_id"] = "E6_gates_no_retry"
        return decision
    decision = _v4(record, bundle, lexicon, switches, weights, threshold, False)
    decision["strategy_id"] = "b2_semantic_v4"
    return decision


def evaluate_rows(records, labels, code, *, weights, threshold, switches=None):
    lexicon = lexicon_from_utterances()
    decisions = []
    judged = []
    for record in records:
        decision = run_strategy(
            record, code, lexicon, weights=weights, threshold=threshold, switches=switches
        )
        label = dict(labels[str(record["case_id"])])
        label["case_category"] = record["case_category"]
        label["parent_id"] = record["parent_id"]
        row = judge_output(label, decision)
        row["expected_slots"] = label["expected_slots"]
        row["expected_intent"] = label["expected_intent"]
        row["predicted_slots"] = decision["committed_slots"]
        row["expected_action"] = label["expected_action"]
        row["action"] = decision["action"]
        decisions.append(decision)
        judged.append(row)
    return decisions, judged


def selection_record(judged, weights, threshold):
    summary = summarize(judged)
    return {
        "weights": weights,
        "threshold": threshold,
        "weight_tuple": tuple(
            weights[name] for name in ("intent", "slot", "polarity", "ambiguity", "contradiction")
        ),
        "unsafe_count": summary["unsafe_commit_rate"]["numerator"],
        "invalid_count": summary["outcomes"]["INVALID_ACTION_PATH"],
        "safe_accuracy": summary["safe_commitment_accuracy"]["value"],
        "selective_risk": summary["selective_risk"]["value"],
        "coverage": summary["coverage"]["value"] or 0,
        "unnecessary": summary["unnecessary_abstention"]["value"],
        "summary": summary,
    }


def _sort_key(item):
    return (
        item["unsafe_count"],
        item["invalid_count"],
        -1 if item["safe_accuracy"] is None else -float(item["safe_accuracy"]),
        1 if item["selective_risk"] is None else float(item["selective_risk"]),
        -float(item["coverage"]),
        1 if item["unnecessary"] is None else float(item["unnecessary"]),
        item["weight_tuple"],
        item["threshold"],
    )


def search_validation(records, labels):
    rows = []
    for weights in weight_grid():
        for threshold in thresholds():
            _decisions, judged = evaluate_rows(
                records, labels, "E7", weights=weights, threshold=threshold
            )
            rows.append(selection_record(judged, weights, threshold))
    best = min(rows, key=_sort_key)
    head = _sort_key(best)[:6]
    tied = [item for item in rows if _sort_key(item)[:6] == head]
    phase3 = next(
        (
            item
            for item in tied
            if item["weights"] == PHASE3_WEIGHTS and item["threshold"] == PHASE3_THRESHOLD
        ),
        None,
    )
    chosen = phase3 or best
    curve = []
    for threshold in thresholds():
        match = next(
            item
            for item in rows
            if item["weights"] == PHASE3_WEIGHTS and item["threshold"] == threshold
        )
        curve.append(
            {
                "threshold": threshold,
                "weights": PHASE3_WEIGHTS,
                "coverage": match["summary"]["coverage"],
                "unsafe_commit_rate": match["summary"]["unsafe_commit_rate"],
                "path_safety": match["summary"]["path_safety"],
                "unnecessary_abstention": match["summary"]["unnecessary_abstention"],
                "safe_commitment_accuracy": match["summary"]["safe_commitment_accuracy"],
            }
        )
    return {
        "grid_size": len(rows),
        "tie_count": len(tied),
        "chosen_weights": chosen["weights"],
        "chosen_threshold": chosen["threshold"],
        "chosen_summary": chosen["summary"],
        "phase3_in_tie_set": phase3 is not None,
        "curve": curve,
        "rows": [
            {
                "weights": item["weights"],
                "threshold": item["threshold"],
                "unsafe_count": item["unsafe_count"],
                "invalid_count": item["invalid_count"],
                "safe_accuracy": item["safe_accuracy"],
                "selective_risk": item["selective_risk"],
                "coverage": item["coverage"],
                "unnecessary": item["unnecessary"],
            }
            for item in rows
        ],
    }


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
