# API

The API is a FastAPI app. It has no authentication and is intended for loopback use.
Run it with:

```bash
uv run uvicorn protomind.api.main:app --reload
```

Interactive docs: <http://127.0.0.1:8000/docs>.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness and project name. |
| `POST` | `/captures` | Upload a `.pcap` or `.pcapng`, run the pipeline, return the result. |
| `GET` | `/runs/{run_id}` | Run metadata, status, result and error. |
| `GET` | `/runs/{run_id}/artifacts/json` | Download `model.json`. |
| `GET` | `/runs/{run_id}/artifacts/markdown` | Download `spec.md`. |
| `GET` | `/runs/{run_id}/artifacts/mermaid` | Download `machine.mmd`. |
| `POST` | `/experiments/query` | Send one symbol to a loopback lab target. |

## Upload

```bash
curl -F "file=@data/captures/tinykv-demo.pcap" http://127.0.0.1:8000/captures
```

- Accepted extensions: `.pcap`, `.pcapng`.
- Maximum size: `PROTOMIND_MAX_UPLOAD_MB` (default 50, range 1–250).
- Empty files return `400`; unsupported extensions return `415`; oversized files
  return `413`.
- Analysis failures return `422` and the run is marked `failed`.
- Success returns `201` with `run_id`, `sha256`, `status` and `result`.

## Run lookup

`GET /runs/{run_id}` returns `run_id`, `capture_name`, `sha256`, `status`,
`created_at`, `result` and `error`. Unknown IDs return `404`.

Artifacts are only served for known names and existing files; anything else returns
`404`.

## Active experiment

```bash
curl -X POST http://127.0.0.1:8000/experiments/query \
  -H "Content-Type: application/json" \
  -d '{"target":"127.0.0.1:9100","message":"HELLO demo"}'
```

- `target` must be an explicit `host:port` with a literal IP.
- Loopback is allowed by default. DNS names and external addresses return `403`.
- One protocol symbol per request; CR or LF returns `400`.
- Timeout is two seconds; failures return `502`.
- Rate limit is 30 requests per minute.
- Input and output are redacted before the experiment row is written.

## Settings

Environment variables use the `PROTOMIND_` prefix:

| Variable | Default | Meaning |
|---|---|---|
| `PROTOMIND_DATABASE` | `data/protomind.sqlite3` | SQLite path. |
| `PROTOMIND_CAPTURE_DIR` | `data/captures` | Uploaded capture directory. |
| `PROTOMIND_RUN_DIR` | `data/runs` | Artifact directory. |
| `PROTOMIND_MAX_UPLOAD_MB` | `50` | Upload limit, 1–250. |
| `PROTOMIND_CORS_ORIGIN` | `http://localhost:5173` | Comma-separated allowed origins. |

## CORS

The API allows the configured origins with all methods and headers. This is a local
development convenience, not an authentication boundary.
