# Verification

1. Open `http://127.0.0.1:5173` in the latest Chrome.
2. Confirm the status becomes `待機中`.
3. Select `録音を開始`, allow microphone access, and speak Japanese.
4. Remain silent for about 1.2 seconds. Confirm recording stops automatically.
5. Confirm the transcript appears, followed by the Japanese response and synthesized voice.
6. Repeat with manual recording stop, response cancellation, and conversation reset.
7. Stop each backend service temporarily and confirm the UI shows a safe error.

Audio never goes to the configured LLM endpoint. Inspect browser network traffic and Gateway logs to confirm that only transcript/history text is included in the LLM request.
