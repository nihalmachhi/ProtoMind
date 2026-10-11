from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.inet6 import IPv6
from scapy.utils import PcapReader


@dataclass
class Stream:
    session_id: str
    client: str
    server: str
    client_port: int
    server_port: int
    protocol: str
    packets: list[tuple[float, str, int, bytes]] = field(default_factory=list)


@dataclass(frozen=True)
class ByteStream:
    session_id: str
    direction: str
    timestamp: float
    data: bytes


def read_capture(path: str | Path) -> list[ByteStream]:
    """Read a pcap incrementally and assemble directional payload byte streams."""
    flows: dict[tuple, Stream] = {}
    with PcapReader(str(path)) as reader:
        for packet in reader:
            if TCP not in packet and UDP not in packet:
                continue
            layer = packet[IP] if IP in packet else packet[IPv6] if IPv6 in packet else None
            if layer is None:
                continue
            transport = packet[TCP] if TCP in packet else packet[UDP]
            payload = bytes(transport.payload)
            if not payload:
                continue
            src, dst = layer.src, layer.dst
            sport, dport = int(transport.sport), int(transport.dport)
            proto = "tcp" if TCP in packet else "udp"
            forward = (src, sport, dst, dport, proto)
            reverse = (dst, dport, src, sport, proto)
            key = min(forward, reverse)
            flow = flows.get(key)
            if flow is None:
                flow = Stream("-".join(map(str, key)), src, dst, sport, dport, proto)
                flows[key] = flow
            direction = "C2S" if (src, sport) == (flow.client, flow.client_port) else "S2C"
            seq = int(transport.seq) if proto == "tcp" else 0
            flow.packets.append((float(packet.time), direction, seq, payload))
    output: list[ByteStream] = []
    for flow in flows.values():
        for direction in ("C2S", "S2C"):
            packets = sorted(
                (p for p in flow.packets if p[1] == direction), key=lambda p: (p[2], p[0])
            )
            if not packets:
                continue
            chunks: list[bytes] = []
            next_seq: int | None = None
            for _, _, seq, payload in packets:
                if flow.protocol == "udp":
                    chunks.append(payload)
                elif next_seq is None:
                    chunks.append(payload)
                    next_seq = seq + len(payload)
                elif seq + len(payload) <= next_seq:
                    continue
                elif seq < next_seq:
                    overlap = next_seq - seq
                    chunks.append(payload[overlap:])
                    next_seq += len(payload) - overlap
                else:
                    chunks.extend((b"\n", payload))
                    next_seq = seq + len(payload)
            output.append(ByteStream(flow.session_id, direction, packets[0][0], b"".join(chunks)))
    return output
