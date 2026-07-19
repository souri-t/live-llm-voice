from typing import Protocol

Message = dict[str, str]


class SttClient(Protocol):
    async def transcribe(self, audio_data: bytes) -> str: ...


class LlmClient(Protocol):
    async def complete(self, messages: list[Message]) -> str: ...


class TtsClient(Protocol):
    async def synthesize(self, text: str, speaker_id: int) -> bytes: ...
