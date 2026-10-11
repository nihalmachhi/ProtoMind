from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from protomind.capture.pcap_reader import read_capture
from protomind.clustering.types import cluster
from protomind.fields.inference import infer_fields
from protomind.safety.redact import redact_message
from protomind.segmentation.segmenters import infer_framing
from protomind.spec.export import write_artifacts
from protomind.statemachine.passive import learn_prefix_tree


def analyze_capture(path: str | Path, output_dir: str | Path) -> dict[str, object]:
    streams = read_capture(path)
    if not streams:
        raise ValueError("Capture contains no supported TCP/UDP payloads")
    framing = infer_framing([stream.data for stream in streams])
    messages: list[tuple[str, int, str, float, bytes]] = []
    by_session: dict[str, dict[str, list[str]]] = defaultdict(lambda: {"C2S": [], "S2C": []})
    for stream in streams:
        split = infer_framing([stream.data])
        for index, raw in enumerate(split.messages):
            messages.append((stream.session_id, index, stream.direction, stream.timestamp, raw))
    typed = cluster(messages)
    for message in typed:
        by_session[message.session_id][message.direction].append(message.type_id)
    examples: dict[str, list[bytes]] = defaultdict(list)
    for message in typed:
        examples[message.type_id].append(message.raw)
    type_items = [
        {
            "id": type_id,
            "direction": type_id.split("_", 1)[0],
            "support_count": len(samples),
            "examples_hex": [redact_message(sample[:128]).hex() for sample in samples[:5]],
            "fields": infer_fields(samples),
        }
        for type_id, samples in sorted(examples.items())
    ]
    traces = []
    for directions in by_session.values():
        pairs = [
            (symbol, directions["S2C"][i] if i < len(directions["S2C"]) else "NO_REPLY")
            for i, symbol in enumerate(directions["C2S"])
        ]
        if pairs:
            traces.append(pairs)
    machine = learn_prefix_tree(traces)
    model: dict[str, object] = {
        "protocol": Path(path).stem,
        "framing": {"kind": framing.kind, "confidence": framing.score, **framing.params},
        "sessions": len(by_session),
        "message_count": len(typed),
        "message_types": type_items,
        "machine": machine,
        "notes": [
            "Passive model from observed traces only.",
            "Field kinds are statistical hypotheses, not confirmed semantics.",
        ],
    }
    model["artifacts"] = write_artifacts(output_dir, model)
    return model
