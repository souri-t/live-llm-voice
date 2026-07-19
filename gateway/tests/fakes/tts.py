class FakeTtsClient:
    async def synthesize(self, text: str, speaker_id: int) -> bytes:
        return b"RIFFfake-wave"
