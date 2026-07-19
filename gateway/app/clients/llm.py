import re

import httpx

from app.clients.base import Message
from app.errors import ErrorCode, GatewayError


SYSTEM_PROMPT = """あなたはリアルタイム音声会話用の日本語アシスタントです。
出力するのは、利用者へそのまま読み上げる最終回答だけです。

分析、推論、思考過程、発話内容の要約、意図の説明、回答候補、
番号付きリスト、回答方針、前置きは絶対に出力しないでください。
内部で検討しても、その内容を回答本文に含めないでください。

自然で簡潔な日本語で、原則1〜2文で回答してください。
不明な点は推測せず、短く確認してください。
Markdown、箇条書き、長いURL、コードは使わないでください。"""

_REASONING_BLOCK = re.compile(r"<(?:think|analysis)>.*?</(?:think|analysis)>\s*", re.IGNORECASE | re.DOTALL)
_UNCLOSED_REASONING_BLOCK = re.compile(r"<(?:think|analysis)>.*", re.IGNORECASE | re.DOTALL)


def strip_reasoning_blocks(text: str) -> str:
    """Remove explicit reasoning tags that some local models emit despite instructions."""
    return _UNCLOSED_REASONING_BLOCK.sub("", _REASONING_BLOCK.sub("", text)).strip()


class OpenAiCompatibleLlmClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float, temperature: float, max_tokens: int) -> None:
        self.url = f"{base_url.rstrip('/')}/chat/completions"
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def complete(self, messages: list[Message]) -> str:
        if not self.api_key or not self.model:
            raise GatewayError(ErrorCode.LLM_UNAVAILABLE, "LLMの設定が不足しています")
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.url, headers={"Authorization": f"Bearer {self.api_key}"}, json=payload)
                response.raise_for_status()
                text = strip_reasoning_blocks(str(response.json()["choices"][0]["message"]["content"]))
        except httpx.TimeoutException as exc:
            raise GatewayError(ErrorCode.LLM_UNAVAILABLE, "LLMがタイムアウトしました") from exc
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise GatewayError(ErrorCode.LLM_FAILED, "回答の生成に失敗しました") from exc
        if not text:
            raise GatewayError(ErrorCode.LLM_FAILED, "空の回答が返されました")
        return text
