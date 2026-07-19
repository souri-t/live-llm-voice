import type { VoiceState } from "../websocket/events";

const labels: Record<VoiceState, string> = {
  disconnected: "未接続", idle: "待機中", listening: "聞いています", transcribing: "文字起こし中",
  thinking: "考えています", synthesizing: "音声を生成中", speaking: "再生中", error: "エラー",
};

export function StatusIndicator({ state }: { state: VoiceState }) {
  return <div className={`status status--${state}`}><span />{labels[state]}</div>;
}
