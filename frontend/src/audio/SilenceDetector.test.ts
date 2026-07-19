import { describe, expect, it } from "vitest";
import { quietSamples, speechSamples } from "../test/fixtures";
import { SilenceDetector } from "./SilenceDetector";

describe("SilenceDetector", () => {
  it("does not commit before speech", () => {
    const detector = new SilenceDetector({ threshold: 0.01, silenceDurationMs: 1200 });
    expect(detector.update(quietSamples, 2000)).toBe(false);
  });
  it("commits once after sustained silence", () => {
    const detector = new SilenceDetector({ threshold: 0.01, silenceDurationMs: 1200 });
    detector.update(speechSamples, 0);
    detector.update(quietSamples, 100);
    expect(detector.update(quietSamples, 1300)).toBe(true);
    expect(detector.update(quietSamples, 1400)).toBe(false);
  });
});
