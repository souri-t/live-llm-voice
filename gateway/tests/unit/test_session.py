from app.session import SessionState, VoiceSession


def test_session_history_is_bounded() -> None:
    session = VoiceSession(60, 2)
    for index in range(3): session.add_message("user", str(index))
    assert [message["content"] for message in session.messages] == ["1", "2"]


def test_reset_clears_state() -> None:
    session = VoiceSession(60, 20)
    session.add_message("user", "hello")
    session.start_input()
    session.reset()
    assert session.state is SessionState.IDLE and not session.messages
