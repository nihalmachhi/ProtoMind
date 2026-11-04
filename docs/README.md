# ProtoMind documentation

ProtoMind is a local-first protocol discovery workbench. These documents describe
what it infers, what it stores, how the safety boundaries work and how to verify
the claims in the README.

| Document | Purpose |
|---|---|
| [Architecture](architecture.md) | Modules, data flow and trust boundaries |
| [Threat model](threat-model.md) | Assets, adversaries, mitigations and residual risk |
| [Privacy](privacy.md) | Exactly what is stored, redacted and retained |
| [API](api.md) | Upload, run, artifact and experiment endpoints |
| [Testing](testing.md) | Test, lint, type-check, coverage and CI commands |
| [Evaluation](evaluation.md) | Generated synthetic evaluation report |
| [Limitations](limitations.md) | Honest scope and known weaknesses |
| [Final QA](qa.md) | Point-in-time check results and gaps |

> **Synthetic data.** The evaluation report is generated from hand-written
> captures. It verifies the pipeline; it is not evidence of real-world protocol
> accuracy.
