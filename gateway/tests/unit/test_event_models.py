import pytest
from pydantic import ValidationError

from app.event_models import InputStart, parse_client_event


def test_parse_client_event() -> None:
    assert isinstance(parse_client_event('{"type":"input.start"}'), InputStart)


def test_reject_unknown_event() -> None:
    with pytest.raises(ValidationError):
        parse_client_event('{"type":"unknown"}')
