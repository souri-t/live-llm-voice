class FakeLlmClient:
    async def complete(self, messages: list[dict[str, str]]) -> str:
        return "テスト回答です"
