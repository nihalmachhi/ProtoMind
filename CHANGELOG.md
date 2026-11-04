# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-11-04

### Added

- Deterministic synthetic evaluation covering delimiter, length-prefix, fixed-size,
  multi-session and opaque-binary captures, plus credential redaction.
- Generated `docs/evaluation.json` and `docs/evaluation.md` reports.
- Generated site fixtures from the Python segmenters, with a Vitest parity suite.
- Full documentation set: architecture, threat model, privacy, API, testing,
  limitations and final QA.
- CI drift check for generated evaluation and site fixtures.
- Site framing lab with presets and custom hex streams.

### Changed

- Rebuilt the site around ProtoMind content, links and evidence.
- Hardened the Docker image and Compose service: non-root user, read-only root,
  dropped capabilities, tmpfs, healthcheck, resource limits and loopback-only port.
- Expanded the Makefile with coverage, evaluation, fixture, site and verify targets.
- Bumped the package version to 0.2.0.

### Fixed

- Contiguous TCP segments were treated as gaps, injecting a newline sentinel into
  reassembled streams and corrupting framing inference.
- A NUL byte in a binary length prefix could be mistaken for a text delimiter.
- SQLite connections were not closed after each operation.
- Experiment output was stored without redaction.

## [0.1.0] - 2026-10-20

### Added

- Initial passive pipeline: PCAP parsing, TCP/UDP reassembly, framing candidates,
  message grouping, field hypotheses, prefix-tree Mealy model and artifact export.
- FastAPI upload, run lookup, artifact download and guarded loopback experiment
  endpoint.
- SQLite run store, loopback target guard and AUTH/LOGIN/PASS redaction.
- TinyKV demo target and synthetic capture generator.
- React site, tests, CI and MIT license.
