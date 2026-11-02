"""Typed records for the synthetic facade.

Raw controller values and normalized decisions are separate objects.
Neither object is a view onto a frozen experiment file.
"""

from __future__ import annotations

from dataclasses import dataclass

STRATEGIES: frozenset[str] = frozenset(
    {
        "b0_prefix",
        "b1_prefix",
        "b2_prefix_controller",
        "b1_forced_lexical",
        "b2_lexical_v3",
    }
)

CONTROLLER_STRATEGIES: frozenset[str] = frozenset(
    {"b2_prefix_controller", "b2_lexical_v3"}
)

ALLOWED_PROVENANCE: frozenset[str] = frozenset(
    {"synthetic_edit", "reference_passthrough"}
)

SINGLE_TRANSCRIPT = "SINGLE_TRANSCRIPT"
SYNTHETIC_PROXY = "SYNTHETIC_PROXY"
ALLOWED_SOURCES: frozenset[str] = frozenset({SINGLE_TRANSCRIPT, SYNTHETIC_PROXY})

RECOVERY_ACTIONS: frozenset[str] = frozenset({"CONTINUE", "RETRY", "CLARIFY", "HOLD"})
COMMITTING_ACTIONS: frozenset[str] = frozenset({"CONTINUE", "RETRY"})


class FacadeError(Exception):
    """Base error for facade validation and adapter failures."""


class UnknownStrategyError(FacadeError):
    """The router was given a name outside the five identities."""


class InvalidProvenanceError(FacadeError):
    """A candidate used a provenance this simulation does not accept."""


class InvalidBundleError(FacadeError):
    """The bundle disagrees with itself."""


class AdapterError(FacadeError):
    """An existing function raised. The facade did not change that function."""

    def __init__(self, strategy: str, message: str) -> None:
        self.strategy = strategy
        super().__init__(f"{strategy}: {message}")


def slot_pairs(slots: dict[str, str] | None) -> tuple[tuple[str, str], ...]:
    if not slots:
        return ()
    return tuple(sorted((str(key), str(value)) for key, value in slots.items()))


@dataclass(frozen=True)
class SemanticFrame:
    """A predicted intent and slot map. Slots are stored as sorted pairs."""

    intent: str | None
    slots: tuple[tuple[str, str], ...]

    def as_dict(self) -> dict[str, str]:
        return dict(self.slots)

    @classmethod
    def from_mapping(cls, intent: str | None, slots: dict[str, str] | None) -> SemanticFrame:
        return cls(intent, slot_pairs(slots))


@dataclass(frozen=True)
class CandidateRecord:
    candidate_id: str
    text: str
    provenance: str
    rank: int
    candidate_source: str

    def __post_init__(self) -> None:
        if self.provenance not in ALLOWED_PROVENANCE:
            raise InvalidProvenanceError(
                f"{self.candidate_id} has provenance {self.provenance!r}. "
                "This simulation accepts synthetic_edit and reference_passthrough."
            )
        if self.candidate_source not in ALLOWED_SOURCES:
            raise InvalidProvenanceError(
                f"{self.candidate_id} has source {self.candidate_source!r}."
            )


@dataclass(frozen=True)
class CandidateBundle:
    utterance_id: str
    candidates: tuple[CandidateRecord, ...]
    generation_method: str
    candidate_source: str

    def __post_init__(self) -> None:
        if self.candidate_source not in ALLOWED_SOURCES:
            raise InvalidBundleError(f"Unknown bundle source {self.candidate_source!r}.")
        ids = [item.candidate_id for item in self.candidates]
        if len(ids) != len(set(ids)):
            raise InvalidBundleError(f"Duplicate candidate ids in {self.utterance_id}.")
        sources = {item.candidate_source for item in self.candidates}
        if sources and sources != {self.candidate_source}:
            raise InvalidBundleError("Candidate source does not match the bundle source.")

    @property
    def candidate_count(self) -> int:
        return len(self.candidates)

    def ordered(self) -> tuple[CandidateRecord, ...]:
        return tuple(sorted(self.candidates, key=lambda item: (item.rank, item.candidate_id)))


@dataclass(frozen=True)
class RawControllerOutput:
    """A copy of what an existing function returned. The facade does not write back."""

    strategy: str
    utterance_id: str
    invoked: bool
    text: str | None
    intent: str | None
    slots: tuple[tuple[str, str], ...]
    action: str | None
    reason: str | None
    retry_mechanism: str | None
    support: int | None
    retries: int | None
    elapsed_seconds: float | None

    def slots_dict(self) -> dict[str, str]:
        return dict(self.slots)


@dataclass(frozen=True)
class NormalizedDecision:
    """Facade commit rule. Independent of the raw object."""

    strategy: str
    utterance_id: str
    action: str | None
    reason: str
    committed_frame: SemanticFrame | None
    answered_frame: SemanticFrame | None
    retry_mechanism: str | None

    @property
    def committed(self) -> bool:
        return self.committed_frame is not None


@dataclass(frozen=True)
class EvaluationResult:
    """Scores one decision. Gold is read here and was not passed to the controller."""

    utterance_id: str
    strategy: str
    intent_correct: bool | None
    exact_frame: bool
    committed: bool
    abstained: bool
    unsafe: bool | None
    slot_reference: tuple[tuple[str, str], ...]
    slot_predicted: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class AuditRecord:
    strategy: str
    utterance_id: str
    candidate_ids: tuple[str, ...]
    candidate_provenance: tuple[str, ...]
    raw: RawControllerOutput
    normalized: NormalizedDecision
    evaluation: EvaluationResult | None
