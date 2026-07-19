import type { VoiceState } from "../websocket/events";

export interface VoiceSessionViewState {
  state: VoiceState;
  transcript: string;
  response: string;
  error: string | null;
}

export type VoiceSessionAction =
  | { type: "state"; state: VoiceState }
  | { type: "transcript"; text: string }
  | { type: "response"; text: string }
  | { type: "error"; message: string }
  | { type: "clearError" }
  | { type: "reset" };
