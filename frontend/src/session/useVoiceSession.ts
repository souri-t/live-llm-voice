import { useCallback, useEffect, useMemo, useReducer, useRef } from "react";
import { AudioPlayer } from "../audio/AudioPlayer";
import { AudioRecorder } from "../audio/AudioRecorder";
import { PcmChunker } from "../audio/PcmChunker";
import { PcmConverter } from "../audio/PcmConverter";
import { SilenceDetector } from "../audio/SilenceDetector";
import type { ServerEvent } from "../websocket/events";
import { VoiceSocket } from "../websocket/VoiceSocket";
import { initialVoiceSessionState, shouldApplyServerState, voiceSessionReducer } from "./voiceSessionReducer";

const websocketUrl = import.meta.env.VITE_GATEWAY_WS_URL ?? "ws://localhost:8000/ws/voice";
const silenceDuration = Number(import.meta.env.VITE_SILENCE_DURATION_MS ?? 1200);
const silenceThreshold = Number(import.meta.env.VITE_SILENCE_THRESHOLD ?? 0.015);
const maxRecordingMs = 60_000;

export function useVoiceSession() {
  const [view, dispatch] = useReducer(voiceSessionReducer, initialVoiceSessionState);
  const recorder = useMemo(() => new AudioRecorder(), []);
  const player = useMemo(() => new AudioPlayer(), []);
  const converter = useMemo(() => new PcmConverter(), []);
  const chunker = useMemo(() => new PcmChunker(640), []);
  const detector = useMemo(() => new SilenceDetector({ threshold: silenceThreshold, silenceDurationMs: silenceDuration }), []);
  const socketRef = useRef<VoiceSocket | null>(null);
  const recordingRef = useRef(false);
  const playbackRef = useRef(false);
  const timeoutRef = useRef<number | null>(null);

  const clearRecordingTimeout = useCallback(() => {
    if (timeoutRef.current !== null) window.clearTimeout(timeoutRef.current);
    timeoutRef.current = null;
  }, []);

  const abortRecording = useCallback(async () => {
    recordingRef.current = false;
    clearRecordingTimeout();
    chunker.reset();
    await recorder.stop();
  }, [chunker, clearRecordingTimeout, recorder]);

  const stopRecording = useCallback(async () => {
    if (!recordingRef.current) return;
    recordingRef.current = false;
    clearRecordingTimeout();
    const finalChunk = chunker.flush();
    if (finalChunk) socketRef.current?.sendAudio(finalChunk);
    await recorder.stop();
    try { socketRef.current?.sendEvent({ type: "input.commit" }); }
    catch { dispatch({ type: "error", message: "録音を送信できませんでした" }); }
  }, [chunker, clearRecordingTimeout, recorder]);

  const handleEvent = useCallback((event: ServerEvent) => {
    switch (event.type) {
      case "session.state":
        if (shouldApplyServerState(event.state, playbackRef.current)) dispatch({ type: "state", state: event.state });
        break;
      case "transcript.final": dispatch({ type: "transcript", text: event.text }); break;
      case "response.text.final": dispatch({ type: "response", text: event.text }); break;
      case "error": dispatch({ type: "error", message: event.message }); break;
    }
  }, []);

  const connect = useCallback(async () => {
    socketRef.current?.close();
    let socket!: VoiceSocket;
    socket = new VoiceSocket(websocketUrl, {
      onEvent: handleEvent,
      onAudio: (audio) => {
        playbackRef.current = true;
        dispatch({ type: "state", state: "speaking" });
        void player.play(audio, () => {
          playbackRef.current = false;
          dispatch({ type: "state", state: "idle" });
        }).catch(() => {
          playbackRef.current = false;
          dispatch({ type: "error", message: "音声を再生できませんでした" });
        });
      },
      onClose: () => {
        if (socketRef.current !== socket) return;
        void abortRecording();
        playbackRef.current = false;
        player.stop();
        dispatch({ type: "state", state: "disconnected" });
      },
      onError: (message) => dispatch({ type: "error", message }),
    });
    socketRef.current = socket;
    dispatch({ type: "clearError" });
    try { await socket.connect(); }
    catch { /* error handler updates the UI */ }
  }, [abortRecording, handleEvent, player]);

  useEffect(() => {
    void connect();
    return () => { void abortRecording(); playbackRef.current = false; player.stop(); socketRef.current?.close(); };
  }, [abortRecording, connect, player]);

  const startRecording = useCallback(async () => {
    try {
      converter.reset();
      chunker.reset();
      detector.reset();
      playbackRef.current = false;
      player.stop();
      dispatch({ type: "clearError" });
      socketRef.current?.sendEvent({ type: "input.start" });
      recordingRef.current = true;
      await recorder.start((samples, sampleRate) => {
        if (!recordingRef.current) return;
        const pcm = converter.convert(samples, sampleRate);
        for (const chunk of chunker.append(pcm)) socketRef.current?.sendAudio(chunk);
        if (detector.update(samples, performance.now())) void stopRecording();
      });
      timeoutRef.current = window.setTimeout(() => void stopRecording(), maxRecordingMs);
    } catch (error) {
      await abortRecording();
      try { socketRef.current?.sendEvent({ type: "response.cancel" }); } catch { /* connection is already unavailable */ }
      dispatch({ type: "error", message: error instanceof DOMException ? "マイクを利用できません" : "録音を開始できませんでした" });
    }
  }, [abortRecording, chunker, converter, detector, player, recorder, stopRecording]);

  const cancel = useCallback(() => {
    playbackRef.current = false;
    player.stop();
    try { socketRef.current?.sendEvent({ type: "response.cancel" }); }
    catch { dispatch({ type: "error", message: "応答を停止できませんでした" }); }
  }, [player]);

  const reset = useCallback(() => {
    void abortRecording();
    playbackRef.current = false;
    player.stop();
    try { socketRef.current?.sendEvent({ type: "session.reset" }); }
    catch { dispatch({ type: "error", message: "会話をリセットできませんでした" }); return; }
    dispatch({ type: "reset" });
  }, [abortRecording, player]);

  return { view, connect, startRecording, stopRecording, cancel, reset };
}
