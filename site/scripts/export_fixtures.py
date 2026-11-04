"""Export site fixtures from the Python pipeline.

Run from the repository root:

    uv run python site/scripts/export_fixtures.py

The generated JSON files are committed so the site builds without Python.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from protomind.evaluation import evaluate, framing_fixtures

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(__file__).resolve().parents[1]
DATA = SITE / "src" / "data"
SIM = SITE / "src" / "features" / "simulator" / "__fixtures__"


def _dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    _dump(DATA / "results.generated.json", evaluate())
    _dump(SIM / "framing.generated.json", framing_fixtures())
    print(f"wrote fixtures under {DATA} and {SIM}")


if __name__ == "__main__":
    main()
