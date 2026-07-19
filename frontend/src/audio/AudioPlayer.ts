export class AudioPlayer {
  private audio: HTMLAudioElement | null = null;
  private objectUrl: string | null = null;
  private endedHandler: (() => void) | null = null;

  async play(wav: ArrayBuffer, onEnded: () => void): Promise<void> {
    this.stop();
    this.objectUrl = URL.createObjectURL(new Blob([wav], { type: "audio/wav" }));
    this.audio = new Audio(this.objectUrl);
    this.endedHandler = () => {
      this.stop();
      onEnded();
    };
    this.audio.addEventListener("ended", this.endedHandler, { once: true });
    try {
      await this.audio.play();
    } catch (error) {
      this.stop();
      throw error;
    }
  }

  stop(): void {
    if (this.audio) {
      if (this.endedHandler) this.audio.removeEventListener("ended", this.endedHandler);
      this.audio.pause();
      this.audio.src = "";
      this.audio = null;
    }
    this.endedHandler = null;
    if (this.objectUrl) URL.revokeObjectURL(this.objectUrl);
    this.objectUrl = null;
  }
}
