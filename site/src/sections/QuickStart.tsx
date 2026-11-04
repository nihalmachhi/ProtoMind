import { content } from "../data/content";

export function QuickStart() {
  return (
    <section className="sec" id="start">
      <div className="wrap">
        <h2>{content.quickstart.heading}</h2>
        <p className="lead2">{content.quickstart.intro}</p>
        <div className="steps qs">
          {content.quickstart.cards.map((card) => (
            <div className="step" key={card.title}>
              <h3>{card.title}</h3>
              <p>{card.body}</p>
              <div className="code">
                {card.code.split("\n").map((line) => (
                  <div key={line} className={line.startsWith("#") ? "c" : undefined}>
                    {line}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        <p className="note">{content.quickstart.notice}</p>
      </div>
    </section>
  );
}
