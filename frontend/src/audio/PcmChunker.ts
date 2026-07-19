export class PcmChunker {
  private pending = new Int16Array(0);

  constructor(private readonly chunkSamples = 640) {
    if (chunkSamples < 1) throw new Error("chunkSamples must be positive");
  }

  reset(): void {
    this.pending = new Int16Array(0);
  }

  append(samples: Int16Array): Int16Array[] {
    if (samples.length === 0) return [];
    const joined = new Int16Array(this.pending.length + samples.length);
    joined.set(this.pending);
    joined.set(samples, this.pending.length);
    const chunks: Int16Array[] = [];
    let offset = 0;
    while (joined.length - offset >= this.chunkSamples) {
      chunks.push(joined.slice(offset, offset + this.chunkSamples));
      offset += this.chunkSamples;
    }
    this.pending = joined.slice(offset);
    return chunks;
  }

  flush(): Int16Array | null {
    if (this.pending.length === 0) return null;
    const finalChunk = this.pending;
    this.pending = new Int16Array(0);
    return finalChunk;
  }
}
