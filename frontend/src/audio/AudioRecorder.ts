import workletUrl from "./recorder.worklet.ts?worker&url";
import type { AudioChunkHandler } from "./audio.types";

export class AudioRecorder {
  private context: AudioContext | null = null;
  private stream: MediaStream | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private worklet: AudioWorkletNode | null = null;

  async start(onChunk: AudioChunkHandler): Promise<void> {
    if (this.context) return;
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true, autoGainControl: true },
    });
    this.context = new AudioContext();
    await this.context.audioWorklet.addModule(workletUrl);
    this.source = this.context.createMediaStreamSource(this.stream);
    this.worklet = new AudioWorkletNode(this.context, "live-llm-recorder");
    this.worklet.port.onmessage = (event: MessageEvent<Float32Array>) => onChunk(event.data, this.context!.sampleRate);
    this.source.connect(this.worklet);
    this.worklet.connect(this.context.destination);
  }

  async stop(): Promise<void> {
    this.worklet?.disconnect();
    this.source?.disconnect();
    this.stream?.getTracks().forEach((track) => track.stop());
    await this.context?.close();
    this.context = null;
    this.stream = null;
    this.source = null;
    this.worklet = null;
  }
}
