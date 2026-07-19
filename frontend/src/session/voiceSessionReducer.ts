import type { VoiceSessionAction, VoiceSessionViewState } from "./voiceSession.types";
import type { VoiceState } from "../websocket/events";

export function shouldApplyServerState(state: VoiceState, playbackActive: boolean): boolean {
  return state !== "idle" || !playbackActive;
}

export const initialVoiceSessionState: VoiceSessionViewState = {
  state: "disconnected",
  transcript: "",
  response: "",
  error: null,
};

export function voiceSessionReducer(state: VoiceSessionViewState, action: VoiceSessionAction): VoiceSessionViewState {
  switch (action.type) {
    case "state": return { ...state, state: action.state };
    case "transcript": return { ...state, transcript: action.text };
    case "response": return { ...state, response: action.text };
    case "error": return { ...state, state: "error", error: action.message };
    case "clearError": return { ...state, error: null };
    case "reset": return { ...initialVoiceSessionState, state: state.state === "disconnected" ? "disconnected" : "idle" };
  }
}
