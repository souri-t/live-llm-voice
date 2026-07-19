from dataclasses import dataclass, field

from app.errors import ErrorCode, GatewayError


@dataclass
class AudioBuffer:
    max_seconds: int
    sample_rate: int = 16_000
    sample_width: int = 2
    channels: int = 1
    data: bytearray = field(default_factory=bytearray)

    @property
    def max_bytes(self) -> int:
        return self.max_seconds * self.sample_rate * self.sample_width * self.channels

    @property
    def duration_seconds(self) -> float:
        return len(self.data) / (self.sample_rate * self.sample_width * self.channels)

    def append(self, chunk: bytes) -> None:
        if not chunk or len(chunk) % self.sample_width:
            raise GatewayError(ErrorCode.INVALID_AUDIO_FORMAT, "音声形式が正しくありません")
        if len(self.data) + len(chunk) > self.max_bytes:
            raise GatewayError(ErrorCode.AUDIO_TOO_LONG, "録音時間が上限を超えました")
        self.data.extend(chunk)

    def clear(self) -> None:
        self.data.clear()

    def take(self) -> bytes:
        if not self.data:
            raise GatewayError(ErrorCode.INVALID_AUDIO_FORMAT, "音声が入力されていません")
        value = bytes(self.data)
        self.clear()
        return value
