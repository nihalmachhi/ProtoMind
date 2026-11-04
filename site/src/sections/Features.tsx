import { content } from "../data/content";

export function Features() {
  return (
    <section className="sec" id="features">
      <div className="wrap">
        <h2>{content.features.heading}</h2>
        <p className="lead2">{content.features.intro}</p>
        <div className="bento">
          {content.features.cards.map((card) => (
            <div className={card.span} key={card.title}>
              <div className="ib" style={{ "--c": card.color } as React.CSSProperties}>
                <svg viewBox="0 0 24 24">
                  <path d={card.icon} />
                </svg>
              </div>
              <h3>{card.title}</h3>
              <p>{card.body}</p>
              <div className="tags">
                {card.tags.map((tag) => (
                  <span key={tag}>{tag}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
