from pathlib import Path

from scapy.all import IP, TCP, PcapWriter, Raw


def write_tinykv_capture(path: Path) -> Path:
    packets = []
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
        raw = request.encode()
        packet = (
            IP(src="127.0.0.1", dst="127.0.0.2")
            / TCP(sport=41000, dport=9100, seq=client_seq, flags="PA")
            / Raw(raw)
        )
        packet.time = timestamp
        packets.append(packet)
        client_seq += len(raw)
        timestamp += 0.01
        raw = reply.encode()
        packet = (
            IP(src="127.0.0.2", dst="127.0.0.1")
            / TCP(sport=9100, dport=41000, seq=server_seq, flags="PA")
            / Raw(raw)
        )
        packet.time = timestamp
        packets.append(packet)
        server_seq += len(raw)
        timestamp += 0.01
    writer = PcapWriter(str(path), sync=True)
    for packet in packets:
        writer.write(packet)
    writer.close()
    return path
