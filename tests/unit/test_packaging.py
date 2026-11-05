from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_compose_tmpfs_options_stay_one_mount() -> None:
    """Unquoted comma-separated YAML splits the options into fake mounts."""
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    for name, service in compose["services"].items():
        for mount in service.get("tmpfs", []):
            assert mount.startswith("/tmp:"), f"{name}: {mount!r}"  # noqa: S108
            assert "size=" in mount, f"{name}: {mount!r}"
            assert "," in mount, f"{name}: {mount!r}"
