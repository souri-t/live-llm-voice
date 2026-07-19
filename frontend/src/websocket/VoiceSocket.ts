import { parseServerEvent } from "./eventParser";
import type { ClientEvent, ServerEvent } from "./events";

export interface VoiceSocketHandlers {
  onEvent: (event: ServerEvent) => void;
  onAudio: (audio: ArrayBuffer) => void;
  onClose: () => void;
  onError: (message: string) => void;
}

export class VoiceSocket {
  private socket: WebSocket | null = null;

  constructor(private readonly url: string, private readonly handlers: VoiceSocketHandlers) {}

  connect(): Promise<void> {
    this.close();
    return new Promise((resolve, reject) => {
      const socket = new WebSocket(this.url);
      socket.binaryType = "arraybuffer";
      this.socket = socket;
      socket.onopen = () => {
        this.sendEvent({ type: "session.start" });
        resolve();
      };
      socket.onmessage = (message) => {
        try {
          if (typeof message.data === "string") this.handlers.onEvent(parseServerEvent(message.data));
          else this.handlers.onAudio(message.data as ArrayBuffer);
        } catch {
          this.handlers.onError("サーバーから不正な応答を受信しました");
        }
      };
      socket.onerror = () => {
        this.handlers.onError("Gatewayへ接続できませんでした");
        reject(new Error("WebSocket connection failed"));
      };
      socket.onclose = () => this.handlers.onClose();
    });
  }

  sendEvent(event: ClientEvent): void {
    if (this.socket?.readyState !== WebSocket.OPEN) throw new Error("WebSocket is not connected");
    this.socket.send(JSON.stringify(event));
  }

  sendAudio(chunk: Int16Array): void {
    if (this.socket?.readyState !== WebSocket.OPEN) return;
    const copy = new Uint8Array(chunk.byteLength);
    copy.set(new Uint8Array(chunk.buffer, chunk.byteOffset, chunk.byteLength));
    this.socket.send(copy.buffer);
  }

  close(): void {
    this.socket?.close();
    this.socket = null;
  }
}
