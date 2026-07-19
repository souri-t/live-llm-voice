import { describe, expect, it } from "vitest";
import { initialVoiceSessionState, shouldApplyServerState, voiceSessionReducer } from "./voiceSessionReducer";

describe("voiceSessionReducer", () => {
  it("stores transcript and response", () => {
    const transcript = voiceSessionReducer(initialVoiceSessionState, { type: "transcript", text: "こんにちは" });
    expect(voiceSessionReducer(transcript, { type: "response", text: "はい" })).toMatchObject({ transcript: "こんにちは", response: "はい" });
  });
  it("keeps an error across state updates until explicitly cleared", () => {
    const failed = voiceSessionReducer(initialVoiceSessionState, { type: "error", message: "失敗しました" });
    const idle = voiceSessionReducer(failed, { type: "state", state: "idle" });
    expect(idle).toMatchObject({ state: "idle", error: "失敗しました" });
    expect(voiceSessionReducer(idle, { type: "clearError" }).error).toBeNull();
  });
  it("keeps speaking state while browser playback is active", () => {
    expect(shouldApplyServerState("idle", true)).toBe(false);
    expect(shouldApplyServerState("idle", false)).toBe(true);
    expect(shouldApplyServerState("thinking", true)).toBe(true);
  });
});
