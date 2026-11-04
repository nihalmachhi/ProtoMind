"""Deterministic synthetic evaluation for the ProtoMind pipeline.

The captures are generated locally from hand-written exchanges. They exercise
reassembly, framing inference, message grouping, field hypotheses, state-machine
learning and redaction. The report is a pipeline check, not a benchmark against
real protocols.
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from scapy.layers.inet import IP, TCP, UDP
from scapy.packet import Raw
from scapy.utils import PcapWriter

from protomind.pipeline import analyze_capture
from protomind.segmentation.segmenters import infer_framing

BASE_TIME = 1_700_000_000.0


@dataclass(frozen=True)
class Exchange:
    request: bytes
    reply: bytes


TINYKV_EXCHANGES = [
    Exchange(b"HELLO demo\r\n", b"+OK\r\n"),
    Exchange(b"AUTH demo demo\r\n", b"+OK\r\n"),
    Exchange(b"SET color blue\r\n", b"+OK\r\n"),
    Exchange(b"GET color\r\n", b"$blue\r\n"),
    Exchange(b"QUIT\r\n", b"+BYE\r\n"),
]

CREDENTIAL_EXCHANGES = [
    Exchange(b"HELLO demo\r\n", b"+OK\r\n"),
    Exchange(b"AUTH alice secret\r\n", b"+OK\r\n"),
    Exchange(b"QUIT\r\n", b"+BYE\r\n"),
]


def _frame(payload: bytes) -> bytes:
    return len(payload).to_bytes(2, "big") + payload


LENGTH_PREFIX_EXCHANGES = [
    Exchange(_frame(b"GET alpha"), _frame(b"VALUE one")),
    Exchange(_frame(b"SET beta two"), _frame(b"OK")),
    Exchange(_frame(b"DEL alpha"), _frame(b"OK")),
]

FIXED_SIZE_EXCHANGES = [Exchange(b"ABCDEFGH", b"IJKLMNOP")]
OPAQUE_EXCHANGES = [Exchange(b"\xff\x01\x02\x03", b"\xfe\x04\x05")]


def write_tcp_capture(
    path: Path,
    sessions: list[list[Exchange]],
    *,
    client_port: int = 41000,
    server_port: int = 9100,
) -> Path:
    """Write a deterministic loopback PCAP for the supplied exchanges."""
    writer = PcapWriter(str(path), sync=True)
    try:
        for session_index, exchanges in enumerate(sessions):
            client_seq = 1000 + session_index * 100_000
            server_seq = 9000 + session_index * 100_000
            sport = client_port + session_index
            timestamp = BASE_TIME + session_index * 10
            for exchange in exchanges:
                for source, destination, source_port, destination_port, seq, payload in (
                    ("127.0.0.1", "127.0.0.2", sport, server_port, client_seq, exchange.request),
                    ("127.0.0.2", "127.0.0.1", server_port, sport, server_seq, exchange.reply),
                ):
                    packet = (
                        IP(src=source, dst=destination)
                        / TCP(sport=source_port, dport=destination_port, seq=seq, flags="PA")
                        / Raw(payload)
                    )
                    packet.time = timestamp
                    writer.write(packet)
                    timestamp += 0.01
                client_seq += len(exchange.request)
                server_seq += len(exchange.reply)
    finally:
        writer.close()
    return path


def write_udp_capture(path: Path) -> Path:
    writer = PcapWriter(str(path), sync=True)
    try:
        packets = [
            ("127.0.0.1", "127.0.0.2", 42000, 9101, b"\x01\x02\x03"),
            ("127.0.0.2", "127.0.0.1", 9101, 42000, b"\x04\x05"),
        ]
        for index, (source, destination, sport, dport, payload) in enumerate(packets):
            packet = IP(src=source, dst=destination) / UDP(sport=sport, dport=dport) / Raw(payload)
            packet.time = BASE_TIME + index * 0.01
            writer.write(packet)
    finally:
        writer.close()
    return path


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    expected_framing: str
    expected_messages: int
    expected_sessions: int
    expected_transitions: int


SCENARIOS = [
    Scenario(
        "tinykv_delimiter",
        "Five request/reply exchanges with CRLF-delimited text.",
        "delimiter",
        10,
        1,
        5,
    ),
    Scenario(
        "tinykv_two_sessions",
        "Two independent TinyKV sessions in one capture.",
        "delimiter",
        20,
        2,
        5,
    ),
    Scenario(
        "length_prefix",
        "Three exchanges framed by a two-byte big-endian length.",
        "length_prefix",
        6,
        1,
        3,
    ),
    Scenario(
        "fixed_size",
        "One request/reply pair where both streams are eight bytes.",
        "fixed_size",
        2,
        1,
        1,
    ),
    Scenario(
        "opaque_binary",
        "Binary payloads with no delimiter or length structure.",
        "whole_stream",
        2,
        1,
        1,
    ),
]


def _redaction_ok(model: dict[str, Any]) -> bool:
    for message_type in model["message_types"]:
        for example in message_type["examples_hex"]:
            decoded = bytes.fromhex(example)
            if b"secret" in decoded or b"alice" in decoded:
                return False
    return True


def evaluate() -> dict[str, Any]:
    """Run the deterministic scenarios and return a serializable report."""
    details: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="protomind-eval-") as directory:
        root = Path(directory)
        builders = {
            "tinykv_delimiter": lambda path: write_tcp_capture(path, [TINYKV_EXCHANGES]),
            "tinykv_two_sessions": lambda path: write_tcp_capture(
                path, [TINYKV_EXCHANGES, TINYKV_EXCHANGES]
            ),
            "length_prefix": lambda path: write_tcp_capture(path, [LENGTH_PREFIX_EXCHANGES]),
            "fixed_size": lambda path: write_tcp_capture(path, [FIXED_SIZE_EXCHANGES]),
            "opaque_binary": lambda path: write_tcp_capture(path, [OPAQUE_EXCHANGES]),
        }
        for scenario in SCENARIOS:
            capture = builders[scenario.name](root / f"{scenario.name}.pcap")
            model = cast(dict[str, Any], analyze_capture(capture, root / f"{scenario.name}-run"))
            predicted_framing = str(model["framing"]["kind"])
            predicted_messages = int(model["message_count"])
            predicted_sessions = int(model["sessions"])
            predicted_transitions = len(model["machine"]["transitions"])
            passed = (
                predicted_framing == scenario.expected_framing
                and predicted_messages == scenario.expected_messages
                and predicted_sessions == scenario.expected_sessions
                and predicted_transitions == scenario.expected_transitions
            )
            details.append(
                {
                    "scenario": scenario.name,
                    "description": scenario.description,
                    "expected_framing": scenario.expected_framing,
                    "predicted_framing": predicted_framing,
                    "framing_confidence": model["framing"]["confidence"],
                    "expected_messages": scenario.expected_messages,
                    "predicted_messages": predicted_messages,
                    "expected_sessions": scenario.expected_sessions,
                    "predicted_sessions": predicted_sessions,
                    "expected_transitions": scenario.expected_transitions,
                    "predicted_transitions": predicted_transitions,
                    "passed": passed,
                }
            )

        credential_capture = write_tcp_capture(root / "credentials.pcap", [CREDENTIAL_EXCHANGES])
        credential_model = cast(
            dict[str, Any], analyze_capture(credential_capture, root / "credentials-run")
        )
        redaction_ok = _redaction_ok(credential_model)
        udp_capture = write_udp_capture(root / "udp.pcap")
        udp_model = cast(dict[str, Any], analyze_capture(udp_capture, root / "udp-run"))

    total = len(details)
    metrics = {
        "framing_accuracy": round(
            sum(item["predicted_framing"] == item["expected_framing"] for item in details) / total,
            4,
        ),
        "message_count_accuracy": round(
            sum(item["predicted_messages"] == item["expected_messages"] for item in details)
            / total,
            4,
        ),
        "session_accuracy": round(
            sum(item["predicted_sessions"] == item["expected_sessions"] for item in details)
            / total,
            4,
        ),
        "transition_accuracy": round(
            sum(item["predicted_transitions"] == item["expected_transitions"] for item in details)
            / total,
            4,
        ),
        "pass_rate": round(sum(item["passed"] for item in details) / total, 4),
    }
    return {
        "kind": "synthetic",
        "description": (
            "Deterministic captures generated from hand-written exchanges. They validate "
            "the pipeline; they are not a benchmark against real-world protocols."
        ),
        "scenarios": total,
        "metrics": metrics,
        "redaction": {
            "checked": True,
            "passed": redaction_ok,
            "capture": "credentials.pcap",
        },
        "udp": {
            "sessions": udp_model["sessions"],
            "messages": udp_model["message_count"],
            "framing": udp_model["framing"]["kind"],
        },
        "details": details,
        "boundary_case": {
            "scenario": "opaque_binary",
            "note": "No delimiter, length prefix or fixed size was found; the stream stays opaque.",
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    lines = [
        "# Synthetic evaluation",
        "",
        "> **Synthetic data.** This report is generated from hand-written captures. It",
        "> verifies the pipeline; it is not evidence of real-world protocol accuracy.",
        "",
        f"- Scenarios: **{report['scenarios']}**",
        f"- Framing accuracy: **{metrics['framing_accuracy']:.2%}**",
        f"- Message-count accuracy: **{metrics['message_count_accuracy']:.2%}**",
        f"- Session accuracy: **{metrics['session_accuracy']:.2%}**",
        f"- Transition accuracy: **{metrics['transition_accuracy']:.2%}**",
        f"- Full pipeline pass rate: **{metrics['pass_rate']:.2%}**",
        f"- Credential redaction: **{'pass' if report['redaction']['passed'] else 'FAIL'}**",
        "",
        "## Per-scenario results",
        "",
        "| Scenario | Framing | Messages | Sessions | Transitions | Pass |",
        "|---|---|---:|---:|---:|:---:|",
    ]
    for item in report["details"]:
        lines.append(
            f"| `{item['scenario']}` | `{item['predicted_framing']}` "
            f"| {item['predicted_messages']}/{item['expected_messages']} "
            f"| {item['predicted_sessions']}/{item['expected_sessions']} "
            f"| {item['predicted_transitions']}/{item['expected_transitions']} "
            f"| {'yes' if item['passed'] else 'no'} |"
        )
    lines += [
        "",
        "## UDP smoke check",
        "",
        f"- Sessions: {report['udp']['sessions']}",
        f"- Messages: {report['udp']['messages']}",
        f"- Framing: `{report['udp']['framing']}`",
        "",
        "## Known boundary",
        "",
        f"- `{report['boundary_case']['scenario']}`: {report['boundary_case']['note']}",
        "",
    ]
    return "\n".join(lines)


def framing_fixtures() -> list[dict[str, Any]]:
    """Return browser-sized framing cases exported from the Python implementation."""
    cases = [
        (
            "tinykv_delimiter",
            [b"HELLO demo\r\nAUTH demo demo\r\nQUIT\r\n", b"+OK\r\n+OK\r\n+BYE\r\n"],
        ),
        ("length_prefix", [_frame(b"GET alpha") + _frame(b"SET beta two"), _frame(b"OK")]),
        ("fixed_size", [b"ABCDEFGH", b"IJKLMNOP"]),
        ("opaque_binary", [b"\xff\x01\x02\x03", b"\xfe\x04\x05"]),
    ]
    output: list[dict[str, Any]] = []
    for name, streams in cases:
        result = infer_framing(streams)
        output.append(
            {
                "name": name,
                "streams_hex": [stream.hex() for stream in streams],
                "expected": {
                    "kind": result.kind,
                    "score": round(result.score, 4),
                    "params": result.params,
                    "messages_hex": [message.hex() for message in result.messages],
                },
            }
        )
    return output


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    report = evaluate()
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs" / "evaluation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (root / "docs" / "evaluation.md").write_text(render_markdown(report), encoding="utf-8")
    print(
        "wrote docs/evaluation.json and docs/evaluation.md "
        f"(framing={report['metrics']['framing_accuracy']:.2%}, "
        f"pass={report['metrics']['pass_rate']:.2%})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
