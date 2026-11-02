"""One local TTS file. The full 200-file set is produced by the experiment runner."""

from pathlib import Path

from cascadeguard.simulation.audio_generator import synthesize


def test_say_writes_aiff(tmp_path: Path) -> None:
    info = synthesize("Book an appointment for tomorrow", tmp_path / "sample.aiff")
    assert info.path.is_file()
    assert info.path.stat().st_size > 0
    assert info.sample_rate_hz > 0
    assert info.duration_seconds > 0
    assert info.channels == 1
