import pytest

from protomind.safety.allowlist import LabTargetGuard, TargetRefused


def test_active_guard_allows_loopback_only_by_default():
    guard = LabTargetGuard()
    assert guard.validate("127.0.0.1:9100") == ("127.0.0.1", 9100)
    with pytest.raises(TargetRefused):
        guard.validate("192.168.1.20:9100")
    with pytest.raises(TargetRefused):
        guard.validate("example.com:9100")
