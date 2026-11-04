import { content } from "../data/content";

export function Pipeline() {
  return (
    <section className="sec" id="how">
      <div className="wrap">
        <h2>{content.pipeline.heading}</h2>
        <p className="lead2">{content.pipeline.intro}</p>
        <div className="steps">
          {content.pipeline.steps.map((step) => (
            <div className="step" key={step.title}>
              <div className="ib" style={{ "--c": step.color } as React.CSSProperties}>
                <svg viewBox="0 0 24 24">
                  <path d="M5 7h14M5 12h14M5 17h14" />
                </svg>
              </div>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
              <div className="mini">
                <b>{step.mini}</b>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
