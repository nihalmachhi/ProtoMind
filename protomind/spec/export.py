from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_artifacts(run_dir: str | Path, model: dict[str, Any]) -> dict[str, str]:
    output = Path(run_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path, mermaid_path, markdown_path = (
        output / "model.json",
        output / "machine.mmd",
        output / "spec.md",
    )
    json_path.write_text(json.dumps(model, indent=2, sort_keys=True), encoding="utf-8")
    machine = model.get("machine", {})
    lines = ["stateDiagram-v2", "    [*] --> " + str(machine.get("initial", "S0"))]
    for edge in machine.get("transitions", []):
        label = str(edge["input"]).replace('"', "'") + " / " + str(edge["output"]).replace('"', "'")
        lines.append(f"    {edge['from']} --> {edge['to']}: {label}")
    mermaid_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    markdown = [
        f"# Inferred protocol: {model.get('protocol', 'unknown')}",
        "",
        "> Inferences are hypotheses from the capture. Review confidence and unknown fields.",
        "",
        "## Framing",
        "",
        f"- Kind: `{model.get('framing', {}).get('kind', 'unknown')}`",
        f"- Confidence: {model.get('framing', {}).get('confidence', 0):.3f}",
        "",
        "## Message types",
        "",
    ]
    for message_type in model.get("message_types", []):
        markdown += [
            f"### {message_type['id']}",
            "",
            f"- Direction: {message_type['direction']}",
            f"- Observed count: {message_type['support_count']}",
            "",
            "| Offset | Length | Kind | Confidence |",
            "|---:|---:|---|---:|",
        ]
        for field in message_type["fields"]:
            row = f"| {field['offset']} | {field.get('length', 'variable')} "
            row += f"| {field['kind']} | {field['confidence']} |"
            markdown.append(row)
        markdown.append("")
    markdown += ["## State machine", "", "```mermaid", *lines, "```", ""]
    markdown_path.write_text("\n".join(markdown), encoding="utf-8")
    return {"json": json_path.name, "mermaid": mermaid_path.name, "markdown": markdown_path.name}
