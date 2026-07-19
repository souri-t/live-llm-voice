from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    stt_base_url: str = "http://whisper:8080"
    stt_language: str = "ja"
    stt_timeout_seconds: float = 60

    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = ""
    llm_timeout_seconds: float = 60
    llm_temperature: float = 0.6
    llm_max_tokens: int = 256

    tts_base_url: str = "http://voicevox:50021"
    tts_speaker_id: int = 1
    tts_speed_scale: float = 1.0
    tts_timeout_seconds: float = 60

    max_audio_seconds: int = 60
    max_history_messages: int = 20
    websocket_max_message_bytes: int = 2_000_000
    log_level: str = "INFO"
    log_conversation_text: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str) and not value.startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
