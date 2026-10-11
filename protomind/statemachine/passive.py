from __future__ import annotations


def learn_prefix_tree(traces: list[list[tuple[str, str]]]) -> dict[str, object]:
    """Build a prefix-tree Mealy hypothesis from observed request/reply traces."""
    transitions: dict[tuple[str, str], tuple[str, str, int]] = {}
    states = {"S0"}
    for trace in traces:
        state = "S0"
        for symbol_in, symbol_out in trace:
            key = (state, symbol_in)
            existing = transitions.get(key)
            if existing and existing[1] != symbol_out:
                output = "|".join(sorted(set(existing[1].split("|") + [symbol_out])))
                destination, count = existing[0], existing[2] + 1
            elif existing:
                destination, output, count = existing[0], existing[1], existing[2] + 1
            else:
                destination, output, count = f"S{len(states)}", symbol_out, 1
                states.add(destination)
            transitions[key] = (destination, output, count)
            state = destination
    edges = [
        {"from": src, "input": symbol, "output": out, "to": dst, "count": count}
        for (src, symbol), (dst, out, count) in sorted(transitions.items())
    ]
    return {
        "initial": "S0",
        "states": sorted(states, key=lambda value: int(value[1:])),
        "transitions": edges,
    }
