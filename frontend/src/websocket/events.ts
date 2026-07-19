export type VoiceState = "disconnected" | "idle" | "listening" | "transcribing" | "thinking" | "synthesizing" | "speaking" | "error";

export type ClientEvent =
  | { type: "session.start" }
  | { type: "input.start" }
  | { type: "input.commit" }
  | { type: "response.cancel" }
  | { type: "session.reset" };

export type ServerEvent =
  | { type: "session.state"; state: Exclude<VoiceState, "disconnected" | "error"> }
  | { type: "transcript.final"; text: string }
  | { type: "response.text.final"; text: string }
  | { type: "response.audio.started" }
  | { type: "response.completed" }
  | { type: "error"; code: string; message: string };
