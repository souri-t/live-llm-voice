import httpx

from app.errors import ErrorCode, GatewayError


class VoicevoxTtsClient:
    def __init__(self, base_url: str, timeout: float, speed_scale: float = 1.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.speed_scale = speed_scale

    async def synthesize(self, text: str, speaker_id: int) -> bytes:
        params = {"text": text, "speaker": speaker_id}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                query_response = await client.post(f"{self.base_url}/audio_query", params=params)
                query_response.raise_for_status()
                query = query_response.json()
                query["speedScale"] = self.speed_scale
                audio_response = await client.post(
                    f"{self.base_url}/synthesis", params={"speaker": speaker_id}, json=query
                )
                audio_response.raise_for_status()
                return audio_response.content
        except httpx.TimeoutException as exc:
            raise GatewayError(ErrorCode.TTS_UNAVAILABLE, "音声合成がタイムアウトしました") from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise GatewayError(ErrorCode.TTS_FAILED, "音声合成に失敗しました") from exc
