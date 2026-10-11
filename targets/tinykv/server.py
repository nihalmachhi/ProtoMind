from __future__ import annotations

import argparse
import asyncio


class TinyKV:
    def __init__(self, buggy: bool = False) -> None:
        self.buggy = buggy
        self.values: dict[str, str] = {}
        self.state = "INIT"
        self.failures = 0

    def execute(self, line: str) -> str:
        parts = line.strip().split()
        if not parts:
            return "-ERR EMPTY"
        command, args = parts[0].upper(), parts[1:]
        if command == "QUIT":
            self.state = "CLOSED"
            return "+BYE"
        if command == "HELLO":
            if self.state != "INIT" or len(args) != 1:
                return "-ERR STATE"
            self.state = "GREETED"
            return "+OK"
        if command == "AUTH":
            if self.state != "GREETED" or len(args) != 2:
                return "-ERR STATE"
            if args == ["demo", "demo"]:
                self.state = "AUTHED"
                return "+OK"
            self.failures += 1
            if self.failures >= 3:
                self.state = "LOCKED"
                return "-ERR LOCKED"
            return "-ERR AUTH"
        if command == "GET" and self.buggy and len(args) == 1:
            return "$" + self.values.get(args[0], "nil")
        if self.state != "AUTHED":
            return "-ERR STATE"
        if command == "SET" and len(args) >= 2:
            self.values[args[0]] = " ".join(args[1:])
            return "+OK"
        if command == "GET" and len(args) == 1:
            return "$" + self.values.get(args[0], "nil")
        if command == "DEL" and len(args) == 1:
            return ":" + str(int(self.values.pop(args[0], None) is not None))
        return "-ERR COMMAND"


async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, buggy: bool) -> None:
    protocol = TinyKV(buggy)
    try:
        while line := await reader.readline():
            writer.write((protocol.execute(line.decode("utf-8", "replace")) + "\r\n").encode())
            await writer.drain()
            if protocol.state == "CLOSED":
                break
    finally:
        writer.close()
        await writer.wait_closed()


async def serve(host: str, port: int, buggy: bool) -> None:
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise ValueError("TinyKV lab target binds to loopback only")
    server = await asyncio.start_server(lambda r, w: handle(r, w, buggy), host, port)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9100)
    parser.add_argument("--buggy", action="store_true")
    args = parser.parse_args()
    asyncio.run(serve(args.host, args.port, args.buggy))
