import pytest

from app.audio.buffer import AudioBuffer
from app.errors import ErrorCode, GatewayError


def test_audio_buffer_duration_and_take() -> None:
    buffer = AudioBuffer(max_seconds=1)
    buffer.append(b"\x00\x00" * 16_000)
    assert buffer.duration_seconds == 1
    assert len(buffer.take()) == 32_000


def test_audio_buffer_rejects_too_long_audio() -> None:
    with pytest.raises(GatewayError) as error:
        AudioBuffer(max_seconds=1).append(b"\x00\x00" * 16_001)
    assert error.value.code == ErrorCode.AUDIO_TOO_LONG
