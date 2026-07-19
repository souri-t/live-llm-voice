import json
import time

from fastapi.testclient import TestClient


def receive_json_until(socket, expected_type: str) -> dict:
    for _ in range(10):
        event = socket.receive_json()
        if event["type"] == expected_type:
            return event
    raise AssertionError(f"Did not receive {expected_type}")


def test_complete_websocket_round_trip(client: TestClient) -> None:
    with client.websocket_connect("/ws/voice") as socket:
        socket.send_json({"type": "session.start"})
        assert socket.receive_json() == {"type": "session.state", "state": "idle"}
        socket.send_json({"type": "input.start"})
        assert socket.receive_json()["state"] == "listening"
        socket.send_bytes(b"\x00\x00" * 160)
        socket.send_json({"type": "input.commit"})
        assert receive_json_until(socket, "transcript.final")["text"] == "テスト音声です"
        assert receive_json_until(socket, "response.text.final")["text"] == "テスト回答です"
        receive_json_until(socket, "response.audio.started")
        assert socket.receive_bytes() == b"RIFFfake-wave"
        assert socket.receive_json()["type"] == "response.completed"
