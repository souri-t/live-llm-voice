from enum import StrEnum


class ErrorCode(StrEnum):
    INVALID_EVENT = "INVALID_EVENT"
    INVALID_AUDIO_FORMAT = "INVALID_AUDIO_FORMAT"
    AUDIO_TOO_LONG = "AUDIO_TOO_LONG"
    STT_UNAVAILABLE = "STT_UNAVAILABLE"
    STT_FAILED = "STT_FAILED"
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    LLM_FAILED = "LLM_FAILED"
    TTS_UNAVAILABLE = "TTS_UNAVAILABLE"
    TTS_FAILED = "TTS_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class GatewayError(Exception):
    def __init__(self, code: ErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
