from __future__ import annotations

import ipaddress
import time
from collections import deque
from urllib.parse import urlparse


class TargetRefused(ValueError):
    pass


class LabTargetGuard:
    """Fail-closed active-target guard; loopback only unless private lab CIDRs are configured."""

    def __init__(self, extra_cidrs: tuple[str, ...] = (), max_queries_per_minute: int = 30) -> None:
        self.networks = tuple(ipaddress.ip_network(cidr, strict=False) for cidr in extra_cidrs)
        self.limit = max_queries_per_minute
        self.timestamps: deque[float] = deque()

    def validate(self, target: str) -> tuple[str, int]:
        parsed = urlparse(target if "://" in target else "tcp://" + target)
        if parsed.scheme not in {"tcp", "http"} or not parsed.hostname or not parsed.port:
            raise TargetRefused("Target must be an explicit host:port lab endpoint")
        try:
            address = ipaddress.ip_address(parsed.hostname)
        except ValueError as exc:
            raise TargetRefused("Use an IP address; DNS names are not permitted") from exc
        if not (address.is_loopback or any(address in network for network in self.networks)):
            raise TargetRefused("Active learning is restricted to loopback or configured lab CIDRs")
        self._rate_limit()
        return str(address), parsed.port

    def _rate_limit(self) -> None:
        now = time.monotonic()
        while self.timestamps and self.timestamps[0] <= now - 60:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.limit:
            raise TargetRefused("Active query rate limit exceeded")
        self.timestamps.append(now)
