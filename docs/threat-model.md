# Threat model

## Assets

- Authorized capture files, which may contain credentials or personal data.
- Derived protocol hypotheses, run metadata and exported artifacts.
- The local host and any loopback lab target reachable from the API.
- The integrity of the evaluation and documentation claims.

## Adversaries and failure modes

| Threat | Example | Mitigation |
|---|---|---|
| Malicious capture | A crafted PCAP exploits the parser or causes unbounded work. | Extension and size limits, offline parsing, bounded field scan, no execution of payload bytes. |
| Accidental exposure | The API is published on all interfaces or put behind a public proxy. | Compose binds `127.0.0.1`; docs say loopback only; no TLS or auth is provided. |
| Active probing abuse | A caller points `/experiments/query` at an external host. | Literal-IP validation, loopback default, DNS refusal, 30/min rate limit, 2s timeout. |
| Credential leakage | AUTH arguments appear in examples or experiment rows. | `redact_message` masks AUTH/LOGIN/PASS arguments before examples and rows are stored. |
| Capture leakage | The raw capture is kept on disk longer than intended. | Local storage only; documented manual deletion; no automatic retention policy. |
| False confidence | A heuristic is presented as protocol truth. | Confidence and evidence are exported; docs and site label results synthetic. |
| Supply-chain drift | Site fixtures or reports diverge from the Python code. | CI regenerates evaluation and fixtures and fails on a diff. |

## Non-goals

ProtoMind does not defend a production network, terminate TLS, authenticate users,
sandbox the parser in a separate process, or promise that a capture is safe to
process. Do not upload captures you are not authorized to inspect.

## Residual risk

- Scapy parsing happens in the API process. A parser vulnerability could affect the
  service.
- The API has no authentication. Anyone who can reach loopback can upload captures,
  read runs and call the active endpoint.
- Raw captures are retained indefinitely unless an operator deletes them.
- The active endpoint returns the target's reply to the caller. It is not a
  sandboxed interaction service.
- Container runtime behavior was not verified locally in this pass; see
  [Final QA](qa.md#docker-verification-gap).
