import { describe, expect, it } from "vitest";
import { PcmChunker } from "./PcmChunker";

describe("PcmChunker", () => {
  it("emits fixed-size chunks and retains the remainder", () => {
    const chunker = new PcmChunker(4);
    expect(chunker.append(new Int16Array([1, 2, 3]))).toHaveLength(0);
    const chunks = chunker.append(new Int16Array([4, 5, 6, 7, 8, 9]));
    expect(chunks.map((chunk) => Array.from(chunk))).toEqual([[1, 2, 3, 4], [5, 6, 7, 8]]);
    expect(Array.from(chunker.flush()!)).toEqual([9]);
  });

  it("clears buffered samples on reset", () => {
    const chunker = new PcmChunker(4);
    chunker.append(new Int16Array([1, 2]));
    chunker.reset();
    expect(chunker.flush()).toBeNull();
  });
});
