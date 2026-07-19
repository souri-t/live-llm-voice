class FakeSttClient:
    async def transcribe(self, audio_data: bytes) -> str:
        return "テスト音声です"
