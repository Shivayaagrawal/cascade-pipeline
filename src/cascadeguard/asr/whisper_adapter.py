"""Optional faster-whisper adapter.

The simulation runner does not call this adapter and does not download a model.
`beam_size` is a search setting. It is not evidence of an N-best list.
"""

from __future__ import annotations

from cascadeguard.asr.base import ASRResult, Hypothesis, NATIVE_NBEST


class WhisperAdapter:
    """Load faster-whisper only when transcribe is called."""

    backend_name = "faster_whisper"

    def __init__(self, model_name: str = "tiny") -> None:
        self.model_name = model_name

    def transcribe(self, audio_path: str) -> ASRResult:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper is not installed. This simulation does not install it "
                "and does not download Common Voice or a Whisper checkpoint."
            ) from exc
        model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, beam_size=1)
        text = " ".join(segment.text.strip() for segment in segments).strip()
        # The installed call returns one string per segment, not an N-best list.
        hypothesis = Hypothesis(text, "single_segment_text", 0)
        if hypothesis.provenance == NATIVE_NBEST:
            raise RuntimeError("Refusing to relabel a 1-best decode as native_nbest")
        return ASRResult(
            (hypothesis,),
            self.backend_name,
            audio_path,
            metadata={"language": str(getattr(info, "language", ""))},
        )
