from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter


class SessionStart(BaseModel):
    type: Literal["session.start"]


class InputStart(BaseModel):
    type: Literal["input.start"]


class InputCommit(BaseModel):
    type: Literal["input.commit"]


class ResponseCancel(BaseModel):
    type: Literal["response.cancel"]


class SessionReset(BaseModel):
    type: Literal["session.reset"]


ClientEvent = Annotated[
    SessionStart | InputStart | InputCommit | ResponseCancel | SessionReset,
    Field(discriminator="type"),
]
client_event_adapter = TypeAdapter(ClientEvent)


def parse_client_event(data: str) -> ClientEvent:
    return client_event_adapter.validate_json(data)
