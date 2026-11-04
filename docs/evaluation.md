# Synthetic evaluation

> **Synthetic data.** This report is generated from hand-written captures. It
> verifies the pipeline; it is not evidence of real-world protocol accuracy.

- Scenarios: **5**
- Framing accuracy: **100.00%**
- Message-count accuracy: **100.00%**
- Session accuracy: **100.00%**
- Transition accuracy: **100.00%**
- Full pipeline pass rate: **100.00%**
- Credential redaction: **pass**

## Per-scenario results

| Scenario | Framing | Messages | Sessions | Transitions | Pass |
|---|---|---:|---:|---:|:---:|
| `tinykv_delimiter` | `delimiter` | 10/10 | 1/1 | 5/5 | yes |
| `tinykv_two_sessions` | `delimiter` | 20/20 | 2/2 | 5/5 | yes |
| `length_prefix` | `length_prefix` | 6/6 | 1/1 | 3/3 | yes |
| `fixed_size` | `fixed_size` | 2/2 | 1/1 | 1/1 | yes |
| `opaque_binary` | `whole_stream` | 2/2 | 1/1 | 1/1 | yes |

## UDP smoke check

- Sessions: 1
- Messages: 2
- Framing: `whole_stream`

## Known boundary

- `opaque_binary`: No delimiter, length prefix or fixed size was found; the stream stays opaque.
