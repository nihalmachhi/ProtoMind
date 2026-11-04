import { describe, it, expect } from "vitest";
import { bytesToDisplay, bytesToHex, hexToBytes, inferFramingHex } from "./engine";
import fixture from "./__fixtures__/framing.generated.json";

interface Case {
  name: string;
  streams_hex: string[];
  expected: {
    kind: string;
    score: number;
    params: Record<string, string | number>;
    messages_hex: string[];
  };
}

describe("framing parity with the Python segmenters", () => {
  for (const item of fixture as Case[]) {
    it(item.name, () => {
      const got = inferFramingHex(item.streams_hex);
      expect(got.kind).toBe(item.expected.kind);
      expect(got.score).toBeCloseTo(item.expected.score, 6);
      expect(got.params).toEqual(item.expected.params);
      expect(got.messages.map(bytesToHex)).toEqual(item.expected.messages_hex);
    });
  }
});

describe("hex helpers", () => {
  it("round-trips bytes", () => {
    const bytes = hexToBytes("000d0a2b4f4b");
    expect(bytesToHex(bytes)).toBe("000d0a2b4f4b");
    expect(bytesToDisplay(bytes)).toBe("\\0\\r\\n+OK");
  });

  it("rejects odd-length input", () => {
    expect(() => hexToBytes("abc")).toThrow(/even number/);
  });
});
