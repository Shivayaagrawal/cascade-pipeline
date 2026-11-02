"""Write stored LLM provisional labels. This script does not infer labels.

The judgments were produced by reading data/manual_audit/annotations.csv.
It does not read gold intent, gold slots, or experiment outputs.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/manual_audit/annotations.csv"
DESTINATION = ROOT / "data/manual_audit/llm_provisional_annotations.csv"

MODEL_NAME = "Cursor Auto"
PROMPT_VERSION = "llm-audit-v1"
ORDER_SEED = "20261102"
ANNOTATOR_ID = "cursor-auto-llm-provisional"

FIELDS = (
    "utterance_id",
    "candidate_id",
    "transcript",
    "llm_intent",
    "llm_slots",
    "negation_present",
    "uncertainty_present",
    "temporal_expression",
    "numerical_expression",
    "semantic_completeness",
    "semantic_ambiguity",
    "coreference_dependency",
    "commit_safety",
    "annotation_confidence",
    "explanation",
    "annotator_id",
    "label_status",
    "model_name",
    "prompt_version",
    "annotation_order_seed",
    "presentation_order",
    "generated_at",
)


def row(
    intent: str,
    slots: str,
    negation: str,
    temporal: str,
    numerical: str,
    completeness: str,
    ambiguity: str,
    commit: str,
    confidence: str,
    explanation: str,
    uncertainty: str = "no",
    coreference: str = "no",
) -> dict[str, str]:
    return {
        "llm_intent": intent,
        "llm_slots": slots,
        "negation_present": negation,
        "uncertainty_present": uncertainty,
        "temporal_expression": temporal,
        "numerical_expression": numerical,
        "semantic_completeness": completeness,
        "semantic_ambiguity": ambiguity,
        "coreference_dependency": coreference,
        "commit_safety": commit,
        "annotation_confidence": confidence,
        "explanation": explanation,
    }


WAREHOUSE = row(
    "unknown",
    "not_applicable",
    "no",
    "today",
    "not_applicable",
    "uncertain",
    "no",
    "unsafe",
    "high",
    "The sentence is not one of the ten tasks. 'closed' is not a task negation.",
)

LABELS: dict[str, dict[str, str]] = {
    "utt-041-v0": row(
        "unknown", "uncertain", "no", "Friday", "not_applicable", "incomplete", "no", "unsafe", "medium",
        "'When is my' does not name an appointment; the object is banana.",
    ),
    "utt-076-v2": row(
        "check_balance", "account=expense account", "no", "not_applicable", "not_applicable", "incomplete", "no", "unsafe", "medium",
        "The account is named, but the sentence ends in banana instead of asking for a balance.",
    ),
    "utt-041-v2": row(
        "unknown", "uncertain", "no", "Friday", "not_applicable", "uncertain", "yes", "unsafe", "high",
        "Two requests are present: an appointment question and a balance question. The account is unnamed.",
    ),
    "utt-157-v0": row(
        "weather_query", "date=August 12", "yes", "August 12", "12", "complete", "no", "unsafe", "high",
        "Negation reverses the weather question. The weather subject 'it' is not discourse coreference.",
    ),
    "utt-157-v2": row(
        "weather_query", "date=August 12", "no", "August 12", "12", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The date is August 12.",
    ),
    "utt-196-v2": row(
        "general_information", "topic=closing time", "no", "not_applicable", "not_applicable", "complete", "no", "uncertain", "medium",
        "The topic closing time is readable, but the question word is banana.",
    ),
    "utt-130-v1": row(
        "set_reminder", "time=3 PM", "yes", "3 PM", "3", "complete", "no", "unsafe", "high",
        "Negation reverses the reminder.",
    ),
    "utt-163-v1": row(
        "unknown", "uncertain", "no", "not_applicable", "not_applicable", "uncertain", "yes", "unsafe", "high",
        "Play pop music and an unnamed balance question are both present.",
    ),
    "utt-085-gold": row(
        "transfer_money", "amount=75|currency=rupees", "no", "not_applicable", "75", "complete", "no", "safe", "high",
        "Amount and currency are both stated.",
    ),
    "utt-085-v1": row(
        "transfer_money", "amount=75|currency=uncertain", "no", "not_applicable", "75", "incomplete", "no", "unsafe", "high",
        "The amount is present and the currency is missing.",
    ),
    "utt-018-v2": WAREHOUSE,
    "utt-002-v2": WAREHOUSE,
    "utt-197-v2": row(
        "general_information", "topic=opening time", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The topic is opening time.",
    ),
    "utt-012-v0": row(
        "unknown", "uncertain", "no", "today", "9", "incomplete", "yes", "unsafe", "medium",
        "An appointment and today are present, but the verb is the digit 9, so booking, cancelling, or checking are possible.",
    ),
    "utt-097-v0": row(
        "unknown", "uncertain", "no", "not_applicable", "180", "incomplete", "no", "unsafe", "medium",
        "An amount and rupees appear, but there is no transfer verb.",
    ),
    "utt-074-gold": row(
        "check_balance", "account=deposit account", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "The account is named and a balance is requested.",
    ),
    "utt-163-gold": row(
        "play_music", "genre=pop", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "A play request names the genre pop.",
    ),
    "utt-162-v2": WAREHOUSE,
    "utt-118-v0": row(
        "unknown", "uncertain", "no", "yesterday", "not_applicable", "uncertain", "yes", "unsafe", "high",
        "A transaction request and an unnamed balance request are combined.",
    ),
    "utt-113-gold": row(
        "check_transaction", "recency=card", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "'card' is the transaction qualifier in the closed schema.",
    ),
    "utt-018-v0": row(
        "book_appointment", "date=September 9", "no", "September 9", "9", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The date is September 9.",
    ),
    "utt-052-v2": row(
        "check_appointment", "date=today", "no", "today", "not_applicable", "complete", "no", "uncertain", "medium",
        "A today appointment question is readable, but the question word is banana.",
    ),
    "utt-099-gold": row(
        "transfer_money", "amount=650|currency=rupees", "no", "not_applicable", "650", "complete", "no", "safe", "high",
        "Amount and currency are both stated.",
    ),
    "utt-179-gold": row(
        "play_music", "genre=instrumental", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "A play request names the genre instrumental.",
    ),
    "utt-130-v0": row(
        "set_reminder", "time=3 PM", "no", "3 PM", "3", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The time is 3 PM.",
    ),
    "utt-074-v1": row(
        "check_balance", "account=deposit account", "yes", "not_applicable", "not_applicable", "complete", "no", "unsafe", "high",
        "Negation changes the balance question.",
    ),
    "utt-033-v1": row(
        "cancel_appointment", "date=April 3", "no", "April 3", "3", "complete", "no", "safe", "high",
        "The cancellation date is written as April 3.",
    ),
    "utt-156-v2": row(
        "weather_query", "date=uncertain", "no", "July banana", "not_applicable", "incomplete", "no", "unsafe", "medium",
        "The month July is present, but the day is banana.",
    ),
    "utt-025-v0": row(
        "unknown", "uncertain", "no", "Thursday", "not_applicable", "incomplete", "yes", "unsafe", "medium",
        "An appointment and Thursday are present, but the verb is banana, so booking, cancelling, or checking are possible.",
    ),
    "utt-099-v1": row(
        "unknown", "uncertain", "no", "not_applicable", "650", "uncertain", "yes", "unsafe", "high",
        "A transfer and an unnamed balance question are both present.",
    ),
    "utt-023-v2": row(
        "unknown", "uncertain", "no", "Tuesday", "9", "incomplete", "yes", "unsafe", "medium",
        "The verb is the digit 9, so booking, cancelling, or checking the Tuesday appointment are possible.",
    ),
    "utt-046-v1": row(
        "check_appointment", "date=Saturday", "no", "Saturday", "not_applicable", "complete", "no", "uncertain", "medium",
        "A Saturday appointment question is readable, but the question word is banana.",
    ),
    "utt-141-v0": row(
        "weather_query", "date=Friday", "yes", "Friday", "not_applicable", "complete", "no", "unsafe", "high",
        "Negation reverses the weather question. The weather subject 'it' is not discourse coreference.",
    ),
    "utt-163-v2": row(
        "play_music", "genre=uncertain", "no", "not_applicable", "not_applicable", "incomplete", "no", "unsafe", "high",
        "A play request is present and the genre is missing.",
    ),
    "utt-041-v1": row(
        "check_appointment", "date=Friday", "no", "Friday", "9", "complete", "no", "uncertain", "medium",
        "A Friday appointment question is readable, but the question word is the digit 9.",
    ),
    "utt-162-gold": row(
        "play_music", "genre=rock", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "A play request names the genre rock.",
    ),
    "utt-113-v2": row(
        "unknown", "uncertain", "no", "not_applicable", "not_applicable", "uncertain", "yes", "unsafe", "high",
        "A card transaction request and an unnamed balance question are both present.",
    ),
    "utt-156-v1": WAREHOUSE,
    "utt-180-v0": row(
        "general_information", "topic=working hours", "no", "not_applicable", "9", "complete", "no", "uncertain", "medium",
        "The topic working hours is readable, but the question word is the digit 9.",
    ),
    "utt-033-v2": row(
        "unknown", "uncertain", "no", "April 2", "2", "uncertain", "yes", "unsafe", "high",
        "A cancellation and an unnamed balance question are both present.",
    ),
    "utt-179-v1": row(
        "unknown", "uncertain", "no", "not_applicable", "not_applicable", "uncertain", "yes", "unsafe", "high",
        "A play request and an unnamed balance question are both present.",
    ),
    "utt-041-gold": row(
        "check_appointment", "date=Friday", "no", "Friday", "not_applicable", "complete", "no", "safe", "high",
        "The question asks when a Friday appointment is.",
    ),
    "utt-179-v0": row(
        "play_music", "genre=other", "no", "not_applicable", "not_applicable", "complete", "no", "unsafe", "high",
        "The genre position contains the placeholder other.",
    ),
    "utt-012-v1": WAREHOUSE,
    "utt-066-v1": row(
        "check_balance", "account=travel account", "yes", "not_applicable", "not_applicable", "complete", "no", "unsafe", "high",
        "Negation changes the balance question.",
    ),
    "utt-033-v0": row(
        "unknown", "uncertain", "no", "April 2", "2", "incomplete", "yes", "unsafe", "medium",
        "The verb is banana, so booking, cancelling, or checking the April 2 appointment are possible.",
    ),
    "utt-066-v2": WAREHOUSE,
    "utt-196-v0": row(
        "general_information", "topic=closing time", "no", "not_applicable", "9", "complete", "no", "uncertain", "medium",
        "The topic closing time is readable, but the question word is the digit 9.",
    ),
    "utt-025-v1": row(
        "unknown", "uncertain", "no", "Thursday", "9", "incomplete", "yes", "unsafe", "medium",
        "The verb is the digit 9, so booking, cancelling, or checking the Thursday appointment are possible.",
    ),
    "utt-197-v1": row(
        "general_information", "topic=uncertain", "no", "not_applicable", "not_applicable", "incomplete", "no", "unsafe", "medium",
        "'opening' does not state the full topic opening time.",
    ),
    "utt-130-v2": WAREHOUSE,
    "utt-002-v1": row(
        "book_appointment", "date=Monday", "yes", "Monday", "not_applicable", "complete", "no", "unsafe", "high",
        "Negation reverses the booking.",
    ),
    "utt-002-v0": row(
        "book_appointment", "date=Monday", "no", "Monday", "not_applicable", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The date is Monday.",
    ),
    "utt-126-v2": row(
        "set_reminder", "time=other", "no", "uncertain", "not_applicable", "complete", "no", "unsafe", "high",
        "The time position contains the placeholder other.",
    ),
    "utt-002-gold": row(
        "book_appointment", "date=Monday", "no", "Monday", "not_applicable", "complete", "no", "safe", "high",
        "The request books an appointment for Monday.",
    ),
    "utt-180-v1": WAREHOUSE,
    "utt-138-v0": row(
        "set_reminder", "time=noon", "no", "noon", "not_applicable", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The time is noon.",
    ),
    "utt-052-gold": row(
        "check_appointment", "date=today", "no", "today", "not_applicable", "complete", "no", "safe", "high",
        "The question asks when today's appointment is.",
    ),
    "utt-046-v2": row(
        "check_appointment", "date=other", "no", "uncertain", "not_applicable", "complete", "no", "unsafe", "high",
        "The date position contains the placeholder other.",
    ),
    "utt-138-v1": row(
        "set_reminder", "time=noon", "yes", "noon", "not_applicable", "complete", "no", "unsafe", "high",
        "Negation reverses the reminder.",
    ),
    "utt-023-gold": row(
        "cancel_appointment", "date=Tuesday", "no", "Tuesday", "not_applicable", "complete", "no", "safe", "high",
        "The request cancels an appointment for Tuesday.",
    ),
    "utt-097-v2": row(
        "unknown", "uncertain", "no", "not_applicable", "180", "uncertain", "yes", "unsafe", "high",
        "A transfer and an unnamed balance question are both present.",
    ),
    "utt-099-v0": row(
        "transfer_money", "amount=650|currency=other", "no", "not_applicable", "650", "complete", "no", "unsafe", "high",
        "The currency position contains the placeholder other.",
    ),
    "utt-023-v1": row(
        "cancel_appointment", "date=Tuesday", "no", "Tuesday", "not_applicable", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The date is Tuesday.",
    ),
    "utt-114-v1": row(
        "check_transaction", "recency=cash", "yes", "not_applicable", "not_applicable", "complete", "no", "unsafe", "high",
        "Negation changes the transaction request.",
    ),
    "utt-196-v1": WAREHOUSE,
    "utt-138-v2": WAREHOUSE,
    "utt-076-v1": WAREHOUSE,
    "utt-114-v2": WAREHOUSE,
    "utt-018-gold": row(
        "book_appointment", "date=September 9", "no", "September 9", "9", "complete", "no", "safe", "high",
        "The request books an appointment for September 9.",
    ),
    "utt-052-v0": row(
        "check_appointment", "date=today", "no", "today", "9", "complete", "no", "uncertain", "medium",
        "A today appointment question is readable, but the question word is the digit 9.",
    ),
    "utt-156-gold": row(
        "weather_query", "date=July 1", "no", "July 1", "1", "complete", "no", "safe", "high",
        "The question asks whether it will rain on July 1. The weather subject 'it' is not discourse coreference.",
    ),
    "utt-085-v0": row(
        "transfer_money", "amount=75|currency=rupees", "yes", "not_applicable", "75", "complete", "no", "unsafe", "high",
        "Negation reverses the transfer.",
    ),
    "utt-097-gold": row(
        "transfer_money", "amount=180|currency=rupees", "no", "not_applicable", "180", "complete", "no", "safe", "high",
        "Amount and currency are both stated.",
    ),
    "utt-046-v0": row(
        "unknown", "uncertain", "no", "Saturday", "not_applicable", "uncertain", "yes", "unsafe", "high",
        "An appointment question and an unnamed balance question are both present.",
    ),
    "utt-012-v2": row(
        "book_appointment", "date=today", "no", "today", "not_applicable", "incomplete", "no", "unsafe", "medium",
        "A booking and a date are present, but the object is banana rather than an appointment.",
    ),
    "utt-099-v2": row(
        "transfer_money", "amount=uncertain|currency=rupees", "no", "not_applicable", "not_applicable", "incomplete", "no", "unsafe", "high",
        "The currency is present and the amount is missing.",
    ),
    "utt-023-v0": WAREHOUSE,
    "utt-141-v2": row(
        "weather_query", "date=Friday", "no", "Friday", "not_applicable", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The date is Friday.",
    ),
    "utt-118-v2": row(
        "check_transaction", "recency=other", "no", "not_applicable", "not_applicable", "complete", "no", "unsafe", "high",
        "The transaction qualifier is the placeholder other.",
    ),
    "utt-074-v2": WAREHOUSE,
    "utt-066-gold": row(
        "check_balance", "account=travel account", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "The account is named and a balance is requested.",
    ),
    "utt-156-v0": row(
        "weather_query", "date=July 2", "no", "July 2", "2", "complete", "no", "safe", "high",
        "The rain date is written as July 2. The weather subject 'it' is not discourse coreference.",
    ),
    "utt-113-v1": row(
        "check_transaction", "recency=card", "no", "not_applicable", "9", "complete", "no", "uncertain", "medium",
        "The qualifier card is present, but the verb is the digit 9.",
    ),
    "utt-180-v2": row(
        "general_information", "topic=working hours", "no", "not_applicable", "not_applicable", "complete", "no", "uncertain", "medium",
        "The topic working hours is readable, but the question word is banana.",
    ),
    "utt-113-v0": row(
        "check_transaction", "recency=card", "no", "not_applicable", "not_applicable", "complete", "no", "uncertain", "medium",
        "The qualifier card is present, but the verb is banana.",
    ),
    "utt-141-v1": row(
        "weather_query", "date=Friday", "no", "Friday", "not_applicable", "complete", "no", "safe", "high",
        "The weather subject is omitted. The request is still a Friday rain question.",
    ),
    "utt-074-v0": row(
        "check_balance", "account=deposit account", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The account is deposit account.",
    ),
    "utt-052-v1": WAREHOUSE,
    "utt-033-gold": row(
        "cancel_appointment", "date=April 2", "no", "April 2", "2", "complete", "no", "safe", "high",
        "The request cancels an appointment for April 2.",
    ),
    "utt-162-v1": row(
        "play_music", "genre=rock", "yes", "not_applicable", "not_applicable", "complete", "no", "unsafe", "high",
        "Negation reverses the play request.",
    ),
    "utt-126-v0": row(
        "unknown", "uncertain", "no", "10 AM", "10", "uncertain", "yes", "unsafe", "high",
        "A reminder and an unnamed balance question are both present.",
    ),
    "utt-126-v1": row(
        "set_reminder", "time=10 AM", "no", "10 AM", "10", "complete", "no", "uncertain", "medium",
        "The time 10 AM is present, but the reminder verb is banana.",
    ),
    "utt-076-gold": row(
        "check_balance", "account=expense account", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "The account is named and a balance is requested.",
    ),
    "utt-179-v2": row(
        "play_music", "genre=instrumental", "no", "not_applicable", "not_applicable", "incomplete", "no", "unsafe", "medium",
        "The genre is named, but there is no play request.",
    ),
    "utt-197-v0": row(
        "general_information", "topic=opening time", "yes", "not_applicable", "not_applicable", "complete", "no", "unsafe", "high",
        "Negation changes the information request.",
    ),
    "utt-114-gold": row(
        "check_transaction", "recency=cash", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "'cash' is the transaction qualifier in the closed schema.",
    ),
    "utt-118-v1": row(
        "check_transaction", "recency=yesterday", "no", "yesterday", "not_applicable", "complete", "no", "uncertain", "medium",
        "Yesterday is present, but the verb is banana.",
    ),
    "utt-180-gold": row(
        "general_information", "topic=working hours", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "The topic is working hours.",
    ),
    "utt-076-v0": row(
        "check_balance", "account=expense account", "no", "not_applicable", "9", "complete", "no", "uncertain", "medium",
        "The account and balance are present, but the question word is the digit 9.",
    ),
    "utt-025-gold": row(
        "cancel_appointment", "date=Thursday", "no", "Thursday", "not_applicable", "complete", "no", "safe", "high",
        "The request cancels an appointment for Thursday.",
    ),
    "utt-197-gold": row(
        "general_information", "topic=opening time", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "The topic is opening time.",
    ),
    "utt-163-v0": row(
        "play_music", "genre=other", "no", "not_applicable", "not_applicable", "complete", "no", "unsafe", "high",
        "The genre position contains the placeholder other.",
    ),
    "utt-118-gold": row(
        "check_transaction", "recency=yesterday", "no", "yesterday", "not_applicable", "complete", "no", "safe", "high",
        "'yesterday' is the transaction qualifier.",
    ),
    "utt-157-v1": row(
        "weather_query", "date=August 12", "no", "August 12", "12", "complete", "no", "uncertain", "medium",
        "The date and rain are present, but the auxiliary 'will' is missing. 'it' is a weather subject, not discourse coreference.",
    ),
    "utt-046-gold": row(
        "check_appointment", "date=Saturday", "no", "Saturday", "not_applicable", "complete", "no", "safe", "high",
        "The question asks when a Saturday appointment is.",
    ),
    "utt-157-gold": row(
        "weather_query", "date=August 12", "no", "August 12", "12", "complete", "no", "safe", "high",
        "The question asks whether it will rain on August 12. The weather subject 'it' is not discourse coreference.",
    ),
    "utt-025-v2": row(
        "unknown", "uncertain", "no", "Thursday", "not_applicable", "uncertain", "yes", "unsafe", "high",
        "A cancellation and an unnamed balance question are both present.",
    ),
    "utt-130-gold": row(
        "set_reminder", "time=3 PM", "no", "3 PM", "3", "complete", "no", "safe", "high",
        "The reminder time is 3 PM.",
    ),
    "utt-162-v0": row(
        "play_music", "genre=rock", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The genre is rock.",
    ),
    "utt-141-gold": row(
        "weather_query", "date=Friday", "no", "Friday", "not_applicable", "complete", "no", "safe", "high",
        "The question asks whether it will rain on Friday. The weather subject 'it' is not discourse coreference.",
    ),
    "utt-126-gold": row(
        "set_reminder", "time=10 AM", "no", "10 AM", "10", "complete", "no", "safe", "high",
        "The reminder time is 10 AM.",
    ),
    "utt-196-gold": row(
        "general_information", "topic=closing time", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "The topic is closing time.",
    ),
    "utt-085-v2": row(
        "transfer_money", "amount=75|currency=rupees", "no", "not_applicable", "75", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. Amount and currency are both stated.",
    ),
    "utt-012-gold": row(
        "book_appointment", "date=today", "no", "today", "not_applicable", "complete", "no", "safe", "high",
        "The request books an appointment for today.",
    ),
    "utt-114-v0": row(
        "check_transaction", "recency=cash", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The qualifier is cash.",
    ),
    "utt-138-gold": row(
        "set_reminder", "time=noon", "no", "noon", "not_applicable", "complete", "no", "safe", "high",
        "The reminder time is noon.",
    ),
    "utt-066-v0": row(
        "check_balance", "account=travel account", "no", "not_applicable", "not_applicable", "complete", "no", "safe", "high",
        "'please' is politeness, not uncertainty. The account is travel account.",
    ),
    "utt-097-v1": row(
        "transfer_money", "amount=181|currency=rupees", "no", "not_applicable", "181", "complete", "no", "safe", "high",
        "The amount is written as 181 and the currency is rupees.",
    ),
    "utt-018-v1": row(
        "book_appointment", "date=September 9", "yes", "September 9", "9", "complete", "no", "unsafe", "high",
        "Negation reverses the booking.",
    ),
}


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle))
    source_ids = [item["candidate_id"] for item in source_rows]
    missing = [item for item in source_ids if item not in LABELS]
    extra = sorted(set(LABELS) - set(source_ids))
    if missing or extra or len(source_ids) != len(set(source_ids)):
        raise SystemExit(f"Label keys do not match the sheet. missing={missing} extra={extra}")
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    with DESTINATION.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for index, source in enumerate(source_rows, start=1):
            label = LABELS[source["candidate_id"]]
            writer.writerow(
                {
                    "utterance_id": source["utterance_id"],
                    "candidate_id": source["candidate_id"],
                    "transcript": source["transcript"],
                    "annotator_id": ANNOTATOR_ID,
                    "label_status": "llm_provisional",
                    "model_name": MODEL_NAME,
                    "prompt_version": PROMPT_VERSION,
                    "annotation_order_seed": ORDER_SEED,
                    "presentation_order": str(index),
                    "generated_at": generated_at,
                    **label,
                }
            )
    print(f"wrote {len(source_rows)} rows to {DESTINATION}")
    print(f"generated_at {generated_at}")


if __name__ == "__main__":
    main()
