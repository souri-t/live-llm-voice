import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.config import Settings
from app.errors import ErrorCode, GatewayError
from app.event_models import InputCommit, InputStart, ResponseCancel, SessionReset, SessionStart, parse_client_event
from app.services.conversation import ConversationService
from app.session import SessionState, VoiceSession

logger = logging.getLogger(__name__)


def create_router(service: ConversationService, settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.websocket("/ws/voice")
    async def voice_socket(websocket: WebSocket) -> None:
        origin = websocket.headers.get("origin")
        if origin and origin not in settings.cors_origins:
            await websocket.close(code=1008, reason="Origin not allowed")
            return
        await websocket.accept()
        session = VoiceSession(settings.max_audio_seconds, settings.max_history_messages)

        async def send_error(error: GatewayError) -> None:
            await websocket.send_json({"type": "error", "code": error.code, "message": error.message})
            await websocket.send_json({"type": "session.state", "state": session.state})

        async def run_conversation(pcm: bytes, generation: int) -> None:
            try:
                await service.run(session, pcm, generation, websocket.send_json, websocket.send_bytes)
            except GatewayError as error:
                await send_error(error)
            except asyncio.CancelledError:
                return

        try:
            while True:
                message = await websocket.receive()
                if message["type"] == "websocket.disconnect":
                    break
                try:
                    if message.get("bytes") is not None:
                        if session.state is not SessionState.LISTENING:
                            raise GatewayError(ErrorCode.INVALID_EVENT, "録音中ではありません")
                        if len(message["bytes"]) > settings.websocket_max_message_bytes:
                            raise GatewayError(ErrorCode.INVALID_AUDIO_FORMAT, "音声チャンクが大きすぎます")
                        session.audio.append(message["bytes"])
                        continue

                    event = parse_client_event(message.get("text") or "")
                    if isinstance(event, SessionStart):
                        await websocket.send_json({"type": "session.state", "state": session.state})
                    elif isinstance(event, InputStart):
                        session.start_input()
                        await websocket.send_json({"type": "session.state", "state": session.state})
                    elif isinstance(event, InputCommit):
                        pcm = session.commit_input()
                        generation = session.generation
                        session.current_task = asyncio.create_task(run_conversation(pcm, generation))
                    elif isinstance(event, ResponseCancel):
                        session.cancel()
                        await websocket.send_json({"type": "session.state", "state": session.state})
                    elif isinstance(event, SessionReset):
                        session.reset()
                        await websocket.send_json({"type": "session.state", "state": session.state})
                except ValidationError:
                    await send_error(GatewayError(ErrorCode.INVALID_EVENT, "不正なイベントです"))
                except GatewayError as error:
                    session.cancel()
                    await send_error(error)
        except WebSocketDisconnect:
            pass
        finally:
            session.cancel()
            logger.info("WebSocket disconnected", extra={"session_id": session.session_id})

    return router
