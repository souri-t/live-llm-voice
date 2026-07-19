import httpx

from app.errors import ErrorCode, GatewayError


class WhisperSttClient:
    def __init__(self, base_url: str, language: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.language = language
        self.timeout = timeout

    async def transcribe(self, audio_data: bytes) -> str:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/inference",
                    files={"file": ("recording.wav", audio_data, "audio/wav")},
                    data={"language": self.language, "response_format": "json"},
                )
                response.raise_for_status()
                text = str(response.json().get("text", "")).strip()
        except httpx.TimeoutException as exc:
            raise GatewayError(ErrorCode.STT_UNAVAILABLE, "音声認識がタイムアウトしました") from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise GatewayError(ErrorCode.STT_FAILED, "音声認識に失敗しました") from exc
        if not text:
            raise GatewayError(ErrorCode.STT_FAILED, "発話を認識できませんでした")
        return text
