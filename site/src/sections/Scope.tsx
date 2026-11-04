import { content } from "../data/content";

export function Scope() {
  return (
    <section className="sec" id="scope">
      <div className="wrap">
        <h2>{content.scope.heading}</h2>
        <p className="lead2">{content.scope.intro}</p>
        <div className="sc">
          <div className="scc">
            <div className="ib" style={{ "--c": "#22c55e" } as React.CSSProperties}>
              <svg viewBox="0 0 24 24">
                <path d="M5 12.5l4.5 4.5L19 7.5" />
              </svg>
            </div>
            <h3>{content.scope.inTitle}</h3>
            <ul>
              {content.scope.inItems.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="scc">
            <div className="ib" style={{ "--c": "#ef4444" } as React.CSSProperties}>
              <svg viewBox="0 0 24 24">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </div>
            <h3>{content.scope.outTitle}</h3>
            <ul>
              {content.scope.outItems.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
