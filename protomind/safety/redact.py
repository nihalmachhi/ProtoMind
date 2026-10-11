from __future__ import annotations


def redact_message(message: bytes) -> bytes:
    """Mask credential arguments for known plaintext login commands without changing lengths."""
    suffix = b""
    body = message
    for ending in (b"\r\n", b"\n", b"\r"):
        if body.endswith(ending):
            body, suffix = body[: -len(ending)], ending
            break
    parts = body.split(b" ")
    if parts and parts[0].upper() in {b"AUTH", b"LOGIN", b"PASS"}:
        parts = [parts[0], *(b"*" * len(part) for part in parts[1:])]
    return b" ".join(parts) + suffix
