import httpx
import pytest

from app.clients.llm import SYSTEM_PROMPT, strip_reasoning_blocks
from app.clients.stt import WhisperSttClient


@pytest.mark.asyncio
async def test_stt_response_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"text": " こんにちは "})
    transport = httpx.MockTransport(handler)
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    assert await WhisperSttClient("http://stt", "ja", 1).transcribe(b"wav") == "こんにちは"


def test_reasoning_tags_are_not_in_final_answer() -> None:
    assert strip_reasoning_blocks("<think>回答を考えます。</think>今日は暑いですね。水分を取ってください。") == (
        "今日は暑いですね。水分を取ってください。"
    )
    assert strip_reasoning_blocks("<analysis>候補を比較します。") == ""


def test_system_prompt_requires_final_answer_only() -> None:
    assert "最終回答だけ" in SYSTEM_PROMPT
    assert "思考過程" in SYSTEM_PROMPT
