import { describe, expect, it } from "vitest";
import { PcmConverter } from "./PcmConverter";

describe("PcmConverter", () => {
  it("converts 48kHz float samples to 16kHz int16", () => {
    const result = new PcmConverter().convert(new Float32Array([1, 1, 1, -1, -1, -1]), 48_000);
    expect(Array.from(result)).toEqual([32767, -32768]);
  });
  it("clips samples", () => {
    const result = new PcmConverter().convert(new Float32Array([2, -2]), 16_000);
    expect(Array.from(result)).toEqual([32767, -32768]);
  });
});
