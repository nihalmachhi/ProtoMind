export const faq = [
  {
    q: "Does ProtoMind upload my capture anywhere?",
    a: "No. Parsing is offline and local. The API writes the capture to the configured local directory and stores a SHA-256, run status and result JSON in SQLite. Nothing is sent to a third party.",
  },
  {
    q: "Can it decode TLS or compressed payloads?",
    a: "No. It works on plaintext payloads. Encrypted or compressed application data stays opaque and should not be described as inferred.",
  },
  {
    q: "How sure is a guessed field?",
    a: "Each field carries a confidence and a kind. Constant columns are the strongest signal; the first varying region is only labelled as a string or unknown hypothesis. Treat every boundary as something to check against the trace.",
  },
  {
    q: "What is the state machine learned from?",
    a: "Observed request/reply sequences only. It builds a prefix-tree Mealy hypothesis: states and transitions that appear in the capture. It does not claim to cover unseen behavior.",
  },
  {
    q: "What does active mode do?",
    a: "POST /experiments/query sends one symbol to a literal loopback IP and port, with a two-second timeout and a 30-query-per-minute limit. DNS names, private ranges and external addresses are refused by default.",
  },
  {
    q: "Are the evaluation numbers real?",
    a: "They are real outputs from deterministic synthetic captures, but they are not a benchmark against real protocols. The report is labelled synthetic and includes the opaque-binary boundary where framing is not found.",
  },
  {
    q: "Why can framing be wrong?",
    a: "Ambiguous bytes can look like more than one format. A NUL byte can be a length prefix or a text delimiter, so it is only treated as text in mostly printable streams. The scoring is a heuristic, not proof.",
  },
  {
    q: "How do I add a protocol?",
    a: "Add an authorized capture or a deterministic fixture, run the pipeline, and inspect the framing score, message groups, fields and transitions. Extend the segmenters only when a fixture demonstrates the gap.",
  },
  {
    q: "Is it production ready?",
    a: "No. It is a local learning build. There is no TLS termination, authentication layer, multi-user identity model or production deployment configuration.",
  },
];
