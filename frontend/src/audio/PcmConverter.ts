export class PcmConverter {
  private carry = new Float32Array(0);

  constructor(private readonly targetRate = 16_000) {}

  reset(): void {
    this.carry = new Float32Array(0);
  }

  convert(input: Float32Array, inputRate: number): Int16Array {
    if (inputRate < this.targetRate) throw new Error("Input sample rate must be at least 16kHz");
    const joined = new Float32Array(this.carry.length + input.length);
    joined.set(this.carry);
    joined.set(input, this.carry.length);
    const ratio = inputRate / this.targetRate;
    const outputLength = Math.floor(joined.length / ratio);
    const output = new Int16Array(outputLength);
    for (let i = 0; i < outputLength; i += 1) {
      const start = Math.floor(i * ratio);
      const end = Math.max(start + 1, Math.floor((i + 1) * ratio));
      let sum = 0;
      for (let j = start; j < Math.min(end, joined.length); j += 1) sum += joined[j];
      const sample = Math.max(-1, Math.min(1, sum / (end - start)));
      output[i] = sample < 0 ? Math.round(sample * 32768) : Math.round(sample * 32767);
    }
    const consumed = Math.floor(outputLength * ratio);
    this.carry = joined.slice(consumed);
    return output;
  }
}
