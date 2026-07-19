from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.clients.llm import OpenAiCompatibleLlmClient
from app.clients.stt import WhisperSttClient
from app.clients.tts import VoicevoxTtsClient
from app.config import get_settings
from app.logging import configure_logging
from app.services.conversation import ConversationService
from app.websocket_endpoint import create_router

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title="LiveLLM Voice Gateway", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

service = ConversationService(
    WhisperSttClient(settings.stt_base_url, settings.stt_language, settings.stt_timeout_seconds),
    OpenAiCompatibleLlmClient(
        settings.llm_base_url,
        settings.llm_api_key,
        settings.llm_model,
        settings.llm_timeout_seconds,
        settings.llm_temperature,
        settings.llm_max_tokens,
    ),
    VoicevoxTtsClient(settings.tts_base_url, settings.tts_timeout_seconds, settings.tts_speed_scale),
    settings,
)
app.include_router(create_router(service, settings))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
