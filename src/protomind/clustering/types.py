from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ObservedMessage:
    session_id: str
    index: int
    direction: str
    timestamp: float
    raw: bytes
    type_id: str


def infer_type_name(raw: bytes) -> str:
    token = raw.split(None, 1)[0].strip(b"\r\n") if raw else b"EMPTY"
    try:
        label = token.decode("ascii")
    except UnicodeDecodeError:
        label = "OP_" + token[:4].hex().upper()
    return "".join(char if char.isalnum() else "_" for char in label.upper())[:32] or "UNKNOWN"


def cluster(messages: list[tuple[str, int, str, float, bytes]]) -> list[ObservedMessage]:
    return [
        ObservedMessage(
            session, index, direction, timestamp, raw, f"{direction}_{infer_type_name(raw)}"
        )
        for session, index, direction, timestamp, raw in messages
    ]
