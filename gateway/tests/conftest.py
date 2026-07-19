import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings
from app.services.conversation import ConversationService
from app.websocket_endpoint import create_router
from tests.fakes.llm import FakeLlmClient
from tests.fakes.stt import FakeSttClient
from tests.fakes.tts import FakeTtsClient


@pytest.fixture
def settings() -> Settings:
    return Settings(max_audio_seconds=1, max_history_messages=20)


@pytest.fixture
def client(settings: Settings) -> TestClient:
    app = FastAPI()
    service = ConversationService(FakeSttClient(), FakeLlmClient(), FakeTtsClient(), settings)
    app.include_router(create_router(service, settings))
    return TestClient(app)
