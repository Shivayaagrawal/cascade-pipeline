"""ASR result types and the synthetic hypothesis backend."""

from __future__ import annotations

from dataclasses import dataclass, field


NATIVE_NBEST = "native_nbest"
SYNTHETIC_EDIT = "synthetic_edit"
REFERENCE_PASSTHROUGH = "reference_passthrough"


@dataclass(frozen=True)
class Hypothesis:
    """One transcript candidate and where it came from."""

    text: str
    provenance: str
    rank: int

    def __post_init__(self) -> None:
        if self.provenance == NATIVE_NBEST and self.rank < 0:
            raise ValueError("N-best rank must be non-negative")


@dataclass(frozen=True)
class ASRResult:
    """A recognizer call. `backend` names the implementation that produced it."""

    hypotheses: tuple[Hypothesis, ...]
    backend: str
    audio_path: str = ""
    elapsed_seconds: float = 0.0
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def one_best(self) -> Hypothesis:
        if not self.hypotheses:
            raise ValueError("ASR result has no hypothesis")
        return self.hypotheses[0]


class ASRBackend:
    """Interface for a speech recognizer."""

    backend_name = "unspecified"

    def transcribe(self, audio_path: str) -> ASRResult:
        raise NotImplementedError


class SyntheticHypothesisASR(ASRBackend):
    """Return transcripts that were already written by the error injector.

    This backend does not decode audio. It must not be described as Whisper,
    and it must not label its hypotheses as native N-best.
    """

    backend_name = "synthetic_hypothesis"

    def __init__(self, hypotheses_by_id: dict[str, tuple[Hypothesis, ...]]) -> None:
        for hypotheses in hypotheses_by_id.values():
            for hypothesis in hypotheses:
                if hypothesis.provenance == NATIVE_NBEST:
                    raise ValueError(
                        "Synthetic hypotheses cannot use provenance native_nbest"
                    )
        self._hypotheses_by_id = hypotheses_by_id

    def transcribe(self, audio_path: str) -> ASRResult:
        raise NotImplementedError("Use transcribe_id for the synthetic backend")

    def transcribe_id(self, utterance_id: str, audio_path: str = "") -> ASRResult:
        hypotheses = self._hypotheses_by_id.get(utterance_id)
        if not hypotheses:
            raise KeyError(f"No synthetic hypothesis for {utterance_id}")
        return ASRResult(hypotheses, self.backend_name, audio_path)
