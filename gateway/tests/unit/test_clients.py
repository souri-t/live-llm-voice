import httpx
import pytest

from app.clients.stt import WhisperSttClient


@pytest.mark.asyncio
async def test_stt_response_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"text": " こんにちは "})
    transport = httpx.MockTransport(handler)
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    assert await WhisperSttClient("http://stt", "ja", 1).transcribe(b"wav") == "こんにちは"
