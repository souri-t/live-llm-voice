export interface SilenceDetectorOptions {
  threshold: number;
  silenceDurationMs: number;
}

export class SilenceDetector {
  private heardSpeech = false;
  private silentSince: number | null = null;
  private committed = false;

  constructor(private readonly options: SilenceDetectorOptions) {}

  reset(): void {
    this.heardSpeech = false;
    this.silentSince = null;
    this.committed = false;
  }

  update(samples: Float32Array, nowMs: number): boolean {
    if (this.committed || samples.length === 0) return false;
    const rms = Math.sqrt(samples.reduce((sum, sample) => sum + sample * sample, 0) / samples.length);
    if (rms >= this.options.threshold) {
      this.heardSpeech = true;
      this.silentSince = null;
      return false;
    }
    if (!this.heardSpeech) return false;
    this.silentSince ??= nowMs;
    if (nowMs - this.silentSince >= this.options.silenceDurationMs) {
      this.committed = true;
      return true;
    }
    return false;
  }
}
