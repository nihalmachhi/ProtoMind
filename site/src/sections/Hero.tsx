import { content, DOCS, GITHUB } from "../data/content";
import { Window } from "../components/Window";

export function Hero() {
  return (
    <header className="hero" id="top">
      <h1>{content.hero.headline}</h1>
      <p>{content.hero.subcopy}</p>
      <div className="cta">
        <a className="pill w" href="#start">
          {content.hero.primary}
        </a>
        <a className="pill" href={DOCS}>
          {content.hero.secondary}
        </a>
      </div>
      <div className="wrap">
        <Window />
      </div>
      <p className="note">
        Source: <a href={GITHUB}>github.com/nihalmachhi/ProtoMind</a>
      </p>
    </header>
  );
}
