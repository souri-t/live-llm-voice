from app.errors import ErrorCode, GatewayError


def test_gateway_error_keeps_public_code() -> None:
    error = GatewayError(ErrorCode.INVALID_EVENT, "bad")
    assert error.code == ErrorCode.INVALID_EVENT
