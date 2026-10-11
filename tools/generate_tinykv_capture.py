from __future__ import annotations

import argparse
from pathlib import Path

from scapy.layers.inet import IP, TCP
from scapy.packet import Raw
from scapy.utils import PcapWriter


def generate(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = PcapWriter(str(path), sync=True)
    client_seq, server_seq = 1000, 9000
    exchanges = [
        ("HELLO demo\r\n", "+OK\r\n"),
        ("AUTH demo demo\r\n", "+OK\r\n"),
        ("SET color blue\r\n", "+OK\r\n"),
        ("GET color\r\n", "$blue\r\n"),
        ("QUIT\r\n", "+BYE\r\n"),
    ]
    timestamp = 1_700_000_000.0
    for request, reply in exchanges:
        data = request.encode()
        packet = (
            IP(src="127.0.0.1", dst="127.0.0.2")
            / TCP(sport=41000, dport=9100, seq=client_seq, flags="PA")
            / Raw(data)
        )
        packet.time = timestamp
        writer.write(packet)
        client_seq += len(data)
        timestamp += 0.01
        data = reply.encode()
        packet = (
            IP(src="127.0.0.2", dst="127.0.0.1")
            / TCP(sport=9100, dport=41000, seq=server_seq, flags="PA")
            / Raw(data)
        )
        packet.time = timestamp
        writer.write(packet)
        server_seq += len(data)
        timestamp += 0.01
    writer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a synthetic TinyKV lab PCAP")
    parser.add_argument(
        "output", type=Path, nargs="?", default=Path("data/captures/tinykv-demo.pcap")
    )
    generate(parser.parse_args().output)
