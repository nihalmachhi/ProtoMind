from __future__ import annotations

from collections import Counter


def printable_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    return sum(32 <= byte < 127 or byte in (9, 10, 13) for byte in data) / len(data)


def infer_fields(messages: list[bytes]) -> list[dict[str, object]]:
    if not messages:
        return []
    width = min(min(map(len, messages)), 64)
    fields: list[dict[str, object]] = []
    offset = 0
    while offset < width:
        column = [message[offset] for message in messages if len(message) > offset]
        values = Counter(column)
        if len(values) == 1:
            value = next(iter(values))
            fields.append(
                {
                    "offset": offset,
                    "length": 1,
                    "kind": "const",
                    "value_hex": f"{value:02x}",
                    "confidence": 1.0,
                }
            )
            offset += 1
        else:
            rest = b"".join(message[offset:] for message in messages)
            kind = "string" if printable_ratio(rest) >= 0.85 else "unknown"
            fields.append(
                {
                    "offset": offset,
                    "length": None,
                    "kind": kind,
                    "confidence": round(max(values.values()) / len(column), 3),
                }
            )
            break
    if any(len(message) > width for message in messages):
        fields.append(
            {"offset": width, "length": None, "kind": "variable_payload", "confidence": 0.5}
        )
    return fields
