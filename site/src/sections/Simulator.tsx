import { useMemo, useState } from "react";
import { content } from "../data/content";
import {
  bytesToDisplay,
  bytesToHex,
  inferFramingHex,
  type Segmentation,
} from "../features/simulator/engine";
import framingData from "../features/simulator/__fixtures__/framing.generated.json";

interface FramingCase {
  name: string;
  streams_hex: string[];
  expected: {
    kind: string;
    score: number;
    params: Record<string, string | number>;
    messages_hex: string[];
  };
}

const CASES = framingData as FramingCase[];

const LABELS: Record<string, string> = {
  tinykv_delimiter: "CRLF text",
  length_prefix: "Length prefix",
  fixed_size: "Fixed size",
  opaque_binary: "Opaque binary",
};

function infer(input: string): { result?: Segmentation; error?: string } {
  const streams = input
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  if (!streams.length) return { error: content.simulator.result.invalid };
  try {
    return { result: inferFramingHex(streams) };
  } catch {
    return { error: content.simulator.result.invalid };
  }
}

export function Simulator() {
  const [input, setInput] = useState(CASES[0].streams_hex.join("\n"));
  const [selected, setSelected] = useState(CASES[0].name);
  const { result, error } = useMemo(() => infer(input), [input]);

  return (
    <section className="sec" id="try">
      <div className="wrap">
        <h2>{content.simulator.heading}</h2>
        <p className="lead2">{content.simulator.intro}</p>
        <div className="sim">
          <div className="shead">
            <span>{content.simulator.presets}</span>
            <div className="ctl">
              {CASES.map((item) => (
                <button
                  key={item.name}
                  className={`pill${selected === item.name ? " w" : ""}`}
                  aria-pressed={selected === item.name}
                  onClick={() => {
                    setSelected(item.name);
                    setInput(item.streams_hex.join("\n"));
                  }}
                >
                  {LABELS[item.name] ?? item.name}
                </button>
              ))}
            </div>
          </div>
          <div className="scols">
            <div>
              <label htmlFor="framing-input">
                <h3>{content.simulator.customLabel}</h3>
              </label>
              <textarea
                id="framing-input"
                value={input}
                onChange={(event) => {
                  setSelected("custom");
                  setInput(event.target.value);
                }}
                spellCheck={false}
                rows={10}
                style={{
                  width: "100%",
                  marginTop: 8,
                  background: "#0a0a0b",
                  border: "1px solid var(--ln)",
                  borderRadius: 12,
                  color: "var(--fg)",
                  padding: 14,
                  font: "400 0.78rem/1.6 var(--fm)",
                  resize: "vertical",
                }}
              />
              <p className="note" style={{ textAlign: "left", margin: "10px 0 0" }}>
                {content.simulator.note}
              </p>
            </div>
            <div>
              {error && <p className="no">{error}</p>}
              {result && (
                <>
                  <div className="stats">
                    <div className="stat">
                      <b>{result.kind}</b>
                      <span>{content.simulator.result.kind}</span>
                    </div>
                    <div className="stat">
                      <b>{result.score.toFixed(2)}</b>
                      <span>{content.simulator.result.score}</span>
                    </div>
                    <div className="stat">
                      <b>{result.messages.length}</b>
                      <span>{content.simulator.result.messages}</span>
                    </div>
                  </div>
                  <p className="sub">
                    {content.simulator.result.params}: <code>{JSON.stringify(result.params)}</code>
                  </p>
                  <ul className="lst" style={{ marginTop: 10 }}>
                    {result.messages.length === 0 && <li>{content.simulator.result.noMessages}</li>}
                    {result.messages.map((message, index) => (
                      <li key={`${index}-${bytesToHex(message)}`}>
                        <b>#{index + 1}</b> {bytesToDisplay(message)}
                        <div className="sub">{bytesToHex(message)}</div>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
