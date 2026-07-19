import type { VoiceState } from "../websocket/events";

interface Props {
  state: VoiceState;
  onStart: () => void;
  onStop: () => void;
  onCancel: () => void;
  onReset: () => void;
  onReconnect: () => void;
}

export function VoiceControl({ state, onStart, onStop, onCancel, onReset, onReconnect }: Props) {
  const active = ["transcribing", "thinking", "synthesizing", "speaking"].includes(state);
  return <div className="controls">
    {state === "disconnected" ? <button className="primary" onClick={onReconnect}>再接続</button> :
      state === "listening" ? <button className="stop" onClick={onStop}>録音を停止</button> :
      <button className="primary" disabled={state !== "idle" && state !== "error"} onClick={onStart}>録音を開始</button>}
    <button disabled={!active} onClick={onCancel}>応答を停止</button>
    <button onClick={onReset}>会話をリセット</button>
  </div>;
}
