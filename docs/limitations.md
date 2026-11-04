# Limitations

ProtoMind is a portfolio-scale learning workbench. These limits are intentional and
should be stated whenever the project is described.

## Inference

- Framing is a score over three hand-written candidates. Ambiguous traffic can
  produce the wrong winner, and `whole_stream` is a fallback rather than a success.
- A NUL byte is only treated as a text delimiter in mostly printable streams. This
  avoids binary length-prefix confusion but is still a heuristic.
- Message types are grouped by the first token. Protocols with binary opcodes or
  shared prefixes will be grouped poorly.
- Field inference scans at most 64 bytes and stops at the first varying column.
  `string` and `unknown` are hypotheses, not schema truth.
- The Mealy model contains only observed transitions. It does not generalize to
  unseen inputs and is not a verified protocol state machine.
- TCP sequence gaps are marked with a newline sentinel, which is not observed
  traffic.
- TLS, compression and application-level encryption are not decoded.

## Evaluation

- The synthetic report uses five hand-written captures. A 100% pass rate means the
  implementation matches its fixtures, not that it understands real protocols.
- The report has no per-field accuracy metric because the fixtures do not carry
  field-boundary ground truth.
- UDP coverage is a single smoke case.

## Security and operations

- The API has no authentication or TLS. It is for loopback use only.
- Raw captures are retained on disk and are not redacted. Delete them manually.
- Redaction covers AUTH, LOGIN and PASS arguments only.
- The active endpoint returns the target's reply and is not a sandbox.
- Scapy parses untrusted captures in the API process.
- There is no automatic retention, purge or multi-user audit trail.

## Verification gaps

- Docker Desktop's Linux engine was not running during this pass, so image build and
  live container inspection were not executed locally. `docker compose config -q`
  and static checks passed. CI builds the image but does not start the stack. See
  [Final QA](qa.md#docker-verification-gap).
- The site is tested with Vitest and a production build, not browser automation.
- `npm audit` reports moderate findings in development-only lint tooling; the
  production dependency tree reports zero findings.
