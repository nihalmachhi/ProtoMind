# Privacy

ProtoMind is a local analysis tool. It minimizes derived data, but it cannot make an
uploaded capture anonymous. Read this before using a real capture.

## Stored on disk

| Location | Data | Notes |
|---|---|---|
| `data/captures/{run_id}.pcap` | The uploaded capture bytes | Raw and potentially sensitive. Not redacted. |
| `data/runs/{run_id}/model.json` | Framing, message groups, field hypotheses and the state model | Message examples are redacted for AUTH/LOGIN/PASS. |
| `data/runs/{run_id}/spec.md` | Human-readable spec | Same derived data as the model. |
| `data/runs/{run_id}/machine.mmd` | Mermaid state diagram | Observed transitions only. |
| `data/protomind.sqlite3` | Capture name, SHA-256, status, result JSON, timestamps | No raw capture bytes. |
| `data/protomind.sqlite3` | Experiment target, redacted input and output symbols | Only for `/experiments/query`. |

## Redaction

`redact_message` masks every argument after an `AUTH`, `LOGIN` or `PASS` token with
asterisks of the same length, preserving the trailing CR/LF. It does not claim to
recognize every credential-bearing command. `SET password ...` is not masked.

The capture file itself is never rewritten. If it contains credentials, those bytes
remain in `data/captures/`.

## Not collected

- No telemetry, analytics or outbound upload.
- No DNS names for active targets; the guard requires a literal IP.
- No user accounts or per-analyst identity.
- No packet payloads in the SQLite result beyond redacted message examples.

## Retention

There is no automatic retention or purge command. To remove data, stop the API and
delete `data/captures/`, `data/runs/` and `data/protomind.sqlite3`. Deleting a run
row does not delete its capture or artifact directory.

## Evaluation data

The synthetic evaluation uses hand-written exchanges and demo-only credentials
(`demo` / `demo`). It is generated locally and contains no real traffic.
