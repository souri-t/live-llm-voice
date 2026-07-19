import httpx

from app.clients.base import Message
from app.errors import ErrorCode, GatewayError


SYSTEM_PROMPT = """あなたはリアルタイム音声会話用のアシスタントです。
日本語で、原則2〜4文以内の簡潔で聞き取りやすい自然な回答をしてください。
Markdownの表や複雑な箇条書き、長いURLやコードは避けてください。
不明な点は推測せず、その旨を簡潔に伝えてください。"""


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
                text = str(response.json()["choices"][0]["message"]["content"]).strip()
        except httpx.TimeoutException as exc:
            raise GatewayError(ErrorCode.LLM_UNAVAILABLE, "LLMがタイムアウトしました") from exc
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise GatewayError(ErrorCode.LLM_FAILED, "回答の生成に失敗しました") from exc
        if not text:
            raise GatewayError(ErrorCode.LLM_FAILED, "空の回答が返されました")
        return text
