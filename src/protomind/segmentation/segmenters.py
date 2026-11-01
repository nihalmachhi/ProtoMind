from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Segmentation:
    kind: str
    messages: list[bytes]
    score: float
    params: dict[str, object]


class Segmenter(Protocol):
    def fit(self, streams: list[bytes]) -> Segmentation: ...


def split_delimited(stream: bytes, delimiter: bytes) -> list[bytes]:
    if not delimiter:
        return [stream] if stream else []
    parts = stream.split(delimiter)
    result = [part + delimiter for part in parts[:-1] if part]
    if parts[-1]:
        result.append(parts[-1])
    return result


def delimiter_candidate(streams: list[bytes]) -> Segmentation | None:
    best: Segmentation | None = None
    for delimiter in (b"\r\n", b"\n", b"\x00"):
        messages = [msg for stream in streams for msg in split_delimited(stream, delimiter)]
        terminated = sum(stream.count(delimiter) for stream in streams)
        total = len(messages)
        if not terminated or not total:
            continue
        score = min(1.0, terminated / max(1, total))
        candidate = Segmentation("delimiter", messages, score, {"delimiter_hex": delimiter.hex()})
        if best is None or candidate.score > best.score:
            best = candidate
    return best


def length_prefix_candidate(streams: list[bytes], threshold: float = 0.95) -> Segmentation | None:
    best: Segmentation | None = None
    for offset in range(9):
        for width in (1, 2, 4):
            for endian in ("big", "little"):
                messages: list[bytes] = []
                complete = total = 0
                for stream in streams:
                    pos = 0
                    while pos + offset + width <= len(stream):
                        size = int.from_bytes(stream[pos + offset : pos + offset + width], endian)
                        end = pos + offset + width + size
                        if end > len(stream) or end <= pos + offset + width:
                            break
                        messages.append(stream[pos:end])
                        complete += 1
                        total += 1
                        pos = end
                    if pos < len(stream):
                        total += 1
                score = complete / total if total else 0.0
                if best is None or score > best.score:
                    best = Segmentation(
                        "length_prefix",
                        messages,
                        score,
                        {"offset": offset, "width": width, "endian": endian},
                    )
    return best if best and best.score >= threshold else None


def fixed_size_candidate(streams: list[bytes]) -> Segmentation | None:
    lengths = [len(stream) for stream in streams if stream]
    if len(lengths) < 2 or len(set(lengths)) != 1:
        return None
    return Segmentation("fixed_size", list(streams), 1.0, {"size": lengths[0]})


def infer_framing(streams: list[bytes]) -> Segmentation:
    candidates = [
        candidate
        for candidate in (
            delimiter_candidate(streams),
            length_prefix_candidate(streams),
            fixed_size_candidate(streams),
        )
        if candidate
    ]
    if not candidates:
        return Segmentation("whole_stream", [stream for stream in streams if stream], 0.0, {})
    return max(candidates, key=lambda item: (item.score, item.kind == "delimiter"))
