import asyncio
import logging
from time import perf_counter
from collections.abc import Awaitable, Callable

from app.audio.wav import pcm_to_wav
from app.clients.base import LlmClient, SttClient, TtsClient
from app.config import Settings
from app.errors import ErrorCode, GatewayError
from app.session import SessionState, VoiceSession

SendJson = Callable[[dict[str, object]], Awaitable[None]]
SendBytes = Callable[[bytes], Awaitable[None]]
logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(self, stt: SttClient, llm: LlmClient, tts: TtsClient, settings: Settings) -> None:
        self.stt, self.llm, self.tts, self.settings = stt, llm, tts, settings

    async def run(self, session: VoiceSession, pcm: bytes, generation: int, send_json: SendJson, send_bytes: SendBytes) -> None:
        started_at = perf_counter()
        try:
            session.state = SessionState.TRANSCRIBING
            await send_json({"type": "session.state", "state": session.state})
            transcript = await self.stt.transcribe(pcm_to_wav(pcm))
            if generation != session.generation:
                return
            await send_json({"type": "transcript.final", "text": transcript})

            session.state = SessionState.THINKING
            await send_json({"type": "session.state", "state": session.state})
            prompt = [*session.messages, {"role": "user", "content": transcript}]
            response = await self.llm.complete(prompt)
            if generation != session.generation:
                return
            session.add_message("user", transcript)
            session.add_message("assistant", response)
            await send_json({"type": "response.text.final", "text": response})

            session.state = SessionState.SYNTHESIZING
            await send_json({"type": "session.state", "state": session.state})
            audio = await self.tts.synthesize(response, self.settings.tts_speaker_id)
            if generation != session.generation:
                return
            session.state = SessionState.SPEAKING
            await send_json({"type": "session.state", "state": session.state})
            await send_json({"type": "response.audio.started"})
            await send_bytes(audio)
            await send_json({"type": "response.completed"})
            session.state = SessionState.IDLE
            await send_json({"type": "session.state", "state": session.state})
            logger.info(
                "Conversation completed",
                extra={
                    "session_id": session.session_id,
                    "duration_ms": round((perf_counter() - started_at) * 1000),
                    "audio_seconds": len(pcm) / 32_000,
                    "transcript_length": len(transcript),
                    "response_length": len(response),
                },
            )
        except asyncio.CancelledError:
            raise
        except GatewayError:
            session.state = SessionState.IDLE
            raise
        except Exception as exc:
            session.state = SessionState.IDLE
            logger.exception("Unexpected conversation error", extra={"session_id": session.session_id})
            raise GatewayError(ErrorCode.INTERNAL_ERROR, "内部エラーが発生しました") from exc
