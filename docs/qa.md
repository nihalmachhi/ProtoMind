# Final QA

This is a point-in-time record, not a permanent guarantee. Re-run the commands
below on the commit you intend to show.

## Scope

- Date: 2026-11-05
- Branch: `main`
- Commit tested: `ea98f0b` (`fix: quote compose tmpfs options so the container starts`)
- Local environment: Windows, Python 3.13.7, Node.js 22.19.0, npm 10.9.3
- Fresh-clone environment: `uv` resolved CPython 3.12.12, Node.js 22.19.0,
  npm 10.9.3

## Local checks

| Check | Command | Result |
|---|---|---|
| Python lint | `uv run ruff check .` | pass |
| Python format | `uv run ruff format --check .` | pass, 45 files |
| Python types | `uv run mypy src` | pass, 23 files |
| Python tests | `uv run pytest -q --cov=protomind --cov-report=term-missing` | 17 passed |
| Coverage gate | same as above | 88.11% branch coverage (gate 80%) |
| Evaluation | `uv run python -m protomind.evaluation` | pass, 5 scenarios, 100% framing/message/session/transition |
| Fixture export | `uv run python site/scripts/export_fixtures.py` | pass, no content diff |
| Site lint | `npm run lint` | pass |
| Site types | `npm run typecheck` | pass |
| Site tests | `npm test` | 10 passed |
| Site build | `npm run build` | pass |
| Production audit | `npm audit --omit=dev` | 0 findings |
| Dev audit | `npm audit` | 7 moderate findings in lint tooling, no fix available |
| Compose config | `docker compose config -q` | pass |
| Container build | `docker compose build` | pass |
| Container health | `docker compose up -d`, healthcheck | healthy |
| End-to-end upload | demo capture through `/captures` | complete, 10 messages, delimiter framing |
| Runtime controls | `docker inspect` | uid 10001, read-only root, all caps dropped, 256M / 64 pids |

Re-running the evaluation and fixture exporter produced no content diff in
`docs/evaluation.json`, `docs/evaluation.md`, `site/src/data/results.generated.json`
or `site/src/features/simulator/__fixtures__/`. The generated numbers on the site
therefore match the committed report.

> **Synthetic data.** The evaluation is generated from five hand-written captures.
> A 100% pass rate means the implementation matches its fixtures; it is not evidence
> of real-world protocol accuracy.

## Fresh-clone check

A clean clone of `origin/main` at `ea98f0b` was created outside the working tree
and verified without reusing local build artifacts:

```bash
git clone --depth 1 https://github.com/nihalmachhi/ProtoMind.git protomind-fresh
cd protomind-fresh
uv sync --frozen --extra dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -q --cov=protomind --cov-fail-under=80
uv run python -m protomind.evaluation
uv run python site/scripts/export_fixtures.py
git diff --exit-code -- \
  docs/evaluation.json \
  docs/evaluation.md \
  site/src/data/results.generated.json \
  site/src/features/simulator/__fixtures__
cd site
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```

All steps passed (17 tests). The clone was clean after the generated-report check,
so the committed artifacts reproduce from the committed source.
`npm audit --omit=dev` reported zero production vulnerabilities.

## Docker runtime verification

Docker Desktop's Linux engine was available on 2026-11-05, so the image was built,
started and exercised:

```bash
docker compose config -q
docker compose build
docker compose up -d
curl -s http://127.0.0.1:8000/health
curl -s -X POST -F "file=@data/captures/tinykv-demo.pcap" http://127.0.0.1:8000/captures
docker inspect --format '{{.Config.User}}' protomind-api-1
```

Results:

- The healthcheck reached `healthy` and `/health` returned `{"status":"ok"}`.
- Uploading the generated demo capture completed the pipeline: delimiter framing,
  10 messages, one session and five observed transitions. AUTH examples were
  stored redacted.
- Run lookup and Markdown/Mermaid artifact downloads returned the expected data.
- `docker inspect` confirmed uid/gid `10001:10001`, a read-only root filesystem,
  `CapDrop=["ALL"]`, a 256 MiB memory limit and a 64-process limit.
- The container publishes only `127.0.0.1:8000`.

The first live run exposed a real bug: the unquoted YAML flow sequence
`tmpfs: [/tmp:rw,noexec,nosuid,size=16m]` split the options on commas, so Docker
treated `size=16m` as a mount path and refused to start the container. Quoting the
value fixed it, and `tests/unit/test_packaging.py` now guards the compose file.

CI still runs only `docker compose config -q` and `docker compose build`; it does
not start the stack. The runtime results above are a local point-in-time record.

## Known non-blocking findings

- The dev-only `npm audit` findings are transitive lint dependencies. The
  production dependency tree reports zero findings.
- The site has Vitest and a production build, not browser automation.
- The synthetic evaluation is a pipeline check, not a real-world accuracy score.
- The API has no authentication or TLS and is intended for loopback use only.
- Raw captures are retained unredacted; only AUTH, LOGIN and PASS arguments in
  derived examples and experiment rows are masked.
