# Testing

Every claim in the README should be reproducible with one of the commands below.

## Python

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -q --cov=protomind --cov-report=term-missing
uv run python -m protomind.evaluation
uv run python site/scripts/export_fixtures.py
```

The suite enforces 80% branch coverage. The current run is above that threshold;
the exact number is printed by the coverage command and recorded in CI.

## Site

```bash
cd site
npm ci
npm run lint
npm run typecheck
npm test -- --run
npm run build
```

The simulator is a TypeScript port of the Python segmenters. Its Vitest suite
compares every exported fixture against the Python result, so the browser lab cannot
silently drift from the backend.

## What is covered

| Area | Examples |
|---|---|
| Capture | TCP and UDP flows, directional streams, contiguous reassembly. |
| Segmentation | Delimited text, length prefixes, fixed size, opaque fallback, NUL ambiguity. |
| Clustering | Direction and first-token grouping, ASCII sanitization. |
| Fields | Constant columns, printable strings, confidence. |
| State machine | Prefix-tree transitions, merged outputs. |
| Export | JSON, Markdown and Mermaid artifacts. |
| Storage | Run lifecycle, experiments, connection closing. |
| Safety | Loopback-only guard, CIDRs, rate limit, DNS refusal. |
| Redaction | AUTH masking, stored experiment input and output. |
| API | Upload, run lookup, artifacts, active refusal and redacted rows. |
| Evaluation | Deterministic report, redaction check, fixture parity. |

## Generated artifacts

`protomind.evaluation` writes `docs/evaluation.json` and `docs/evaluation.md`.
`site/scripts/export_fixtures.py` writes the site result card and framing fixtures.
Both are deterministic; CI regenerates them and fails on a diff.

## CI

`.github/workflows/ci.yml` runs:

1. **python** — lint, format check, mypy, coverage-gated tests, evaluation,
   fixture export and a drift check.
2. **site** — npm ci, lint, typecheck, Vitest and a production build.
3. **docker** — `docker compose config -q` and `docker compose build`.

`.github/workflows/site.yml` publishes the site to GitHub Pages on `site/**` changes.
