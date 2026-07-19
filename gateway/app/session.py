import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4

from app.audio.buffer import AudioBuffer
from app.clients.base import Message
from app.errors import ErrorCode, GatewayError


class SessionState(StrEnum):
    IDLE = "idle"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    THINKING = "thinking"
    SYNTHESIZING = "synthesizing"
    SPEAKING = "speaking"


@dataclass
class VoiceSession:
    max_audio_seconds: int
    max_history_messages: int
    session_id: str = field(default_factory=lambda: str(uuid4()))
    state: SessionState = SessionState.IDLE
    messages: list[Message] = field(default_factory=list)
    current_task: asyncio.Task[None] | None = None
    generation: int = 0

    def __post_init__(self) -> None:
        self.audio = AudioBuffer(self.max_audio_seconds)

    def start_input(self) -> None:
        if self.state is not SessionState.IDLE:
            raise GatewayError(ErrorCode.INVALID_EVENT, "現在は録音を開始できません")
        self.audio.clear()
        self.state = SessionState.LISTENING

    def commit_input(self) -> bytes:
        if self.state is not SessionState.LISTENING:
            raise GatewayError(ErrorCode.INVALID_EVENT, "録音中ではありません")
        return self.audio.take()

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        self.messages = self.messages[-self.max_history_messages :]

    def cancel(self) -> None:
        self.generation += 1
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
        self.current_task = None
        self.audio.clear()
        self.state = SessionState.IDLE

    def reset(self) -> None:
        self.cancel()
        self.messages.clear()
