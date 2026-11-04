import pytest

from protomind.safety.allowlist import LabTargetGuard, TargetRefused


def test_active_guard_allows_loopback_only_by_default():
    guard = LabTargetGuard()
    assert guard.validate("127.0.0.1:9100") == ("127.0.0.1", 9100)
    with pytest.raises(TargetRefused):
        guard.validate("192.168.1.20:9100")
    with pytest.raises(TargetRefused):
        guard.validate("example.com:9100")


def test_guard_rejects_missing_ports_and_non_tcp_schemes():
    guard = LabTargetGuard()
    with pytest.raises(TargetRefused):
        guard.validate("127.0.0.1")
    with pytest.raises(TargetRefused):
        guard.validate("udp://127.0.0.1:9100")


def test_guard_can_allow_an_explicit_lab_cidr():
    guard = LabTargetGuard(extra_cidrs=("192.0.2.0/24",))
    assert guard.validate("192.0.2.10:9100") == ("192.0.2.10", 9100)


def test_guard_enforces_the_query_rate_limit():
    guard = LabTargetGuard(max_queries_per_minute=1)
    guard.validate("127.0.0.1:9100")
    with pytest.raises(TargetRefused):
        guard.validate("127.0.0.1:9100")
