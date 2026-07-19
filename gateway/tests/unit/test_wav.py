import wave
from io import BytesIO

from app.audio.wav import pcm_to_wav


def test_pcm_to_wav_header() -> None:
    with wave.open(BytesIO(pcm_to_wav(b"\x00\x00" * 160)), "rb") as audio:
        assert (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getnframes()) == (1, 2, 16_000, 160)
