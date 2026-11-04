export interface Segmentation {
  kind: string;
  messages: Uint8Array[];
  score: number;
  params: Record<string, string | number>;
}

export interface FramingCase {
  name: string;
  streams_hex: string[];
  expected: {
    kind: string;
    score: number;
    params: Record<string, string | number>;
    messages_hex: string[];
  };
}

const DELIMITERS = [new Uint8Array([13, 10]), new Uint8Array([10]), new Uint8Array([0])];

export function hexToBytes(hex: string): Uint8Array {
  const cleaned = hex.replace(/[^0-9a-fA-F]/g, "");
  if (cleaned.length % 2 !== 0) {
    throw new Error("Hex input must contain an even number of digits");
  }
  const output = new Uint8Array(cleaned.length / 2);
  for (let i = 0; i < output.length; i += 1) {
    output[i] = Number.parseInt(cleaned.slice(i * 2, i * 2 + 2), 16);
  }
  return output;
}

export function bytesToHex(bytes: Uint8Array): string {
  return Array.from(bytes, (value) => value.toString(16).padStart(2, "0")).join("");
}

export function bytesToDisplay(bytes: Uint8Array): string {
  return Array.from(bytes, (value) => {
    if (value === 13) return "\\r";
    if (value === 10) return "\\n";
    if (value === 0) return "\\0";
    if (value >= 32 && value < 127) return String.fromCharCode(value);
    return `\\x${value.toString(16).padStart(2, "0")}`;
  }).join("");
}

function concat(left: Uint8Array, right: Uint8Array): Uint8Array {
  const output = new Uint8Array(left.length + right.length);
  output.set(left);
  output.set(right, left.length);
  return output;
}

function countOccurrences(stream: Uint8Array, needle: Uint8Array): number {
  let count = 0;
  let position = 0;
  while (position <= stream.length - needle.length) {
    let match = true;
    for (let i = 0; i < needle.length; i += 1) {
      if (stream[position + i] !== needle[i]) {
        match = false;
        break;
      }
    }
    if (match) {
      count += 1;
      position += needle.length;
    } else {
      position += 1;
    }
  }
  return count;
}

function splitBytes(stream: Uint8Array, delimiter: Uint8Array): Uint8Array[] {
  if (delimiter.length === 0) return stream.length ? [stream] : [];
  const parts: Uint8Array[] = [];
  let start = 0;
  let position = 0;
  while (position <= stream.length - delimiter.length) {
    let match = true;
    for (let i = 0; i < delimiter.length; i += 1) {
      if (stream[position + i] !== delimiter[i]) {
        match = false;
        break;
      }
    }
    if (match) {
      parts.push(stream.slice(start, position));
      position += delimiter.length;
      start = position;
    } else {
      position += 1;
    }
  }
  parts.push(stream.slice(start));
  return parts;
}

export function splitDelimited(stream: Uint8Array, delimiter: Uint8Array): Uint8Array[] {
  const parts = splitBytes(stream, delimiter);
  const result: Uint8Array[] = [];
  for (const part of parts.slice(0, -1)) {
    if (part.length) result.push(concat(part, delimiter));
  }
  const last = parts[parts.length - 1];
  if (last.length) result.push(last);
  return result;
}

export function printableRatio(data: Uint8Array): number {
  if (data.length === 0) return 0;
  let printable = 0;
  for (const value of data) {
    if ((value >= 32 && value < 127) || value === 9 || value === 10 || value === 13) {
      printable += 1;
    }
  }
  return printable / data.length;
}

function isNul(delimiter: Uint8Array): boolean {
  return delimiter.length === 1 && delimiter[0] === 0;
}

function delimiterCandidate(streams: Uint8Array[]): Segmentation | null {
  let best: Segmentation | null = null;
  const combined = streams.reduce((all, stream) => concat(all, stream), new Uint8Array());
  for (const delimiter of DELIMITERS) {
    if (isNul(delimiter) && printableRatio(combined) < 0.85) continue;
    const messages = streams.flatMap((stream) => splitDelimited(stream, delimiter));
    const terminated = streams.reduce((sum, stream) => sum + countOccurrences(stream, delimiter), 0);
    if (!terminated || !messages.length) continue;
    const score = Math.min(1, terminated / Math.max(1, messages.length));
    const candidate: Segmentation = {
      kind: "delimiter",
      messages,
      score,
      params: { delimiter_hex: bytesToHex(delimiter) },
    };
    if (!best || candidate.score > best.score) best = candidate;
  }
  return best;
}

function readUint(stream: Uint8Array, start: number, width: number, littleEndian: boolean): number {
  let value = 0;
  for (let i = 0; i < width; i += 1) {
    const byte = stream[start + (littleEndian ? width - 1 - i : i)];
    value = value * 256 + byte;
  }
  return value;
}

function lengthPrefixCandidate(streams: Uint8Array[], threshold = 0.95): Segmentation | null {
  let best: Segmentation | null = null;
  for (let offset = 0; offset < 9; offset += 1) {
    for (const width of [1, 2, 4]) {
      for (const littleEndian of [false, true]) {
        const messages: Uint8Array[] = [];
        let complete = 0;
        let total = 0;
        for (const stream of streams) {
          let position = 0;
          while (position + offset + width <= stream.length) {
            const size = readUint(stream, position + offset, width, littleEndian);
            const end = position + offset + width + size;
            if (end > stream.length || end <= position + offset + width) break;
            messages.push(stream.slice(position, end));
            complete += 1;
            total += 1;
            position = end;
          }
          if (position < stream.length) total += 1;
        }
        const score = total ? complete / total : 0;
        if (!best || score > best.score) {
          best = {
            kind: "length_prefix",
            messages,
            score,
            params: { offset, width, endian: littleEndian ? "little" : "big" },
          };
        }
      }
    }
  }
  return best && best.score >= threshold ? best : null;
}

function fixedSizeCandidate(streams: Uint8Array[]): Segmentation | null {
  const lengths = streams.filter((stream) => stream.length > 0).map((stream) => stream.length);
  if (lengths.length < 2 || new Set(lengths).size !== 1) return null;
  return {
    kind: "fixed_size",
    messages: streams.slice(),
    score: 1,
    params: { size: lengths[0] },
  };
}

export function inferFraming(streams: Uint8Array[]): Segmentation {
  const candidates = [delimiterCandidate(streams), lengthPrefixCandidate(streams), fixedSizeCandidate(streams)]
    .filter((candidate): candidate is Segmentation => candidate !== null);
  if (!candidates.length) {
    return {
      kind: "whole_stream",
      messages: streams.filter((stream) => stream.length > 0),
      score: 0,
      params: {},
    };
  }
  return candidates.reduce((best, candidate) => {
    const candidateKey = [candidate.score, candidate.kind === "delimiter" ? 1 : 0] as const;
    const bestKey = [best.score, best.kind === "delimiter" ? 1 : 0] as const;
    if (candidateKey[0] > bestKey[0]) return candidate;
    if (candidateKey[0] === bestKey[0] && candidateKey[1] > bestKey[1]) return candidate;
    return best;
  });
}

export function inferFramingHex(streamsHex: string[]): Segmentation {
  return inferFraming(streamsHex.map(hexToBytes));
}
