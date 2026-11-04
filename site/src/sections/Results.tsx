import results from "../data/results.generated.json";
import { content } from "../data/content";

interface Detail {
  scenario: string;
  description: string;
  predicted_framing: string;
  expected_framing: string;
  predicted_messages: number;
  expected_messages: number;
  predicted_sessions: number;
  expected_sessions: number;
  predicted_transitions: number;
  expected_transitions: number;
  passed: boolean;
}

interface Report {
  kind: string;
  scenarios: number;
  metrics: Record<string, number>;
  redaction: { checked: boolean; passed: boolean };
  details: Detail[];
  boundary_case: { scenario: string; note: string };
}

const report = results as Report;

function percent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function Results() {
  return (
    <section className="sec" id="results">
      <div className="wrap">
        <h2>{content.results.heading}</h2>
        <p className="lead2">{content.results.intro}</p>
        <div className="rg">
          {content.results.cards.map((card, index) => (
            <div className="rc" key={card.title}>
              <h3>{card.title}</h3>
              <p>{card.copy}</p>
              <div className="tb">
                <div className="mr">
                  <span>{card.title.split(" ")[0]}</span>
                  <div className="track">
                    <div
                      className="grow"
                      style={
                        {
                          "--w": percent(report.metrics[card.valueKey] ?? 0),
                          "--c": card.color,
                          "--i": index,
                        } as React.CSSProperties
                      }
                    />
                  </div>
                  <b>{percent(report.metrics[card.valueKey] ?? 0)}</b>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="evp">
          <b>{content.results.tableTitle}</b>
          <table style={{ marginTop: 8 }}>
            <thead>
              <tr>
                <th>Scenario</th>
                <th>Framing</th>
                <th>Messages</th>
                <th>Sessions</th>
                <th>Transitions</th>
                <th>Pass</th>
              </tr>
            </thead>
            <tbody>
              {report.details.map((item) => (
                <tr key={item.scenario}>
                  <td>{item.scenario}</td>
                  <td>
                    {item.predicted_framing}
                    {item.predicted_framing !== item.expected_framing && ` (expected ${item.expected_framing})`}
                  </td>
                  <td>
                    {item.predicted_messages}/{item.expected_messages}
                  </td>
                  <td>
                    {item.predicted_sessions}/{item.expected_sessions}
                  </td>
                  <td>
                    {item.predicted_transitions}/{item.expected_transitions}
                  </td>
                  <td className={item.passed ? "ok" : "no"}>{item.passed ? "yes" : "no"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p style={{ marginTop: 12 }}>
            {content.results.redactionLabel}:{" "}
            <b className={report.redaction.passed ? "ok" : "no"}>
              {report.redaction.passed ? "pass" : "fail"}
            </b>
          </p>
        </div>
        <div className="evp">
          <b>{content.results.boundaryTitle}</b>
          <p style={{ color: "var(--mu)", marginTop: 6 }}>{content.results.boundaryCopy}</p>
          <dl>
            <dt>scenario</dt>
            <dd>{report.boundary_case.scenario}</dd>
            <dt>note</dt>
            <dd>{report.boundary_case.note}</dd>
          </dl>
        </div>
        <p className="note">{content.results.note}</p>
      </div>
    </section>
  );
}
