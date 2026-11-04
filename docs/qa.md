# Final QA

This is a point-in-time record, not a permanent guarantee. Re-run the commands
below on the commit you intend to show.

## Scope

- Date: 2026-11-04
- Branch: `main`
- Commit tested: `22237a4` (`feat: rebuild ProtoMind around verified synthetic evaluation`)
- Local environment: Windows, Python 3.13.7, Node.js 22.19.0, npm 10.9.3
- Fresh-clone environment: `uv` resolved CPython 3.12.12, Node.js 22.19.0,
  npm 10.9.3

## Local checks

| Check | Command | Result |
|---|---|---|
| Python lint | `uv run ruff check .` | pass |
| Python format | `uv run ruff format --check .` | pass, 45 files |
| Python types | `uv run mypy src` | pass, 23 files |
| Python tests | `uv run pytest -q --cov=protomind --cov-report=term-missing` | 16 passed |
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

Re-running the evaluation and fixture exporter produced no content diff in
`docs/evaluation.json`, `docs/evaluation.md`, `site/src/data/results.generated.json`
or `site/src/features/simulator/__fixtures__/`. The generated numbers on the site
therefore match the committed report.

> **Synthetic data.** The evaluation is generated from five hand-written captures.
> A 100% pass rate means the implementation matches its fixtures; it is not evidence
> of real-world protocol accuracy.

## Fresh-clone check

A clean clone of `origin/main` at `22237a4` was created outside the working tree
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

All steps passed. The clone was clean after the generated-report check, so the
committed artifacts reproduce from the committed source. `npm audit --omit=dev`
reported zero production vulnerabilities.

## Docker verification gap

Static configuration passed:

```bash
docker compose config -q
```

Image build and live container inspection could not run on this machine:

```text
error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping":
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

Consequences:

- `docker compose build` and container startup are unverified locally.
- The Compose hardening (non-root user, read-only root, dropped capabilities,
  tmpfs, resource limits, loopback-only port) is declared in `docker-compose.yml`
  but not confirmed by inspecting a live container.
- CI runs `docker compose config -q` and `docker compose build`, but it does not
  start the stack or inspect live containers.
- Do not claim a live end-to-end container run until this is executed and recorded.

## Known non-blocking findings

- The dev-only `npm audit` findings are transitive lint dependencies. The
  production dependency tree reports zero findings.
- The site has Vitest and a production build, not browser automation.
- The synthetic evaluation is a pipeline check, not a real-world accuracy score.
- The API has no authentication or TLS and is intended for loopback use only.
- Raw captures are retained unredacted; only AUTH, LOGIN and PASS arguments in
  derived examples and experiment rows are masked.
