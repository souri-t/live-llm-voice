# WebSocket protocol

Endpoint: `ws://localhost:8000/ws/voice`

JSON control events use text frames. Audio always uses binary frames. Client PCM is mono, 16 kHz, signed 16-bit little-endian.

## Normal sequence

```text
Client session.start          Server session.state(idle)
Client input.start            Server session.state(listening)
Client <PCM binary> ...
Client input.commit           Server session.state(transcribing)
                              Server transcript.final
                              Server session.state(thinking)
                              Server response.text.final
                              Server session.state(synthesizing)
                              Server session.state(speaking)
                              Server response.audio.started
                              Server <WAV binary>
                              Server response.completed
                              Server session.state(idle)
```

`response.cancel` cancels server work and returns to `idle`. `session.reset` additionally clears history. Invalid state transitions return `{type:"error", code, message}` without exposing internal exceptions.
