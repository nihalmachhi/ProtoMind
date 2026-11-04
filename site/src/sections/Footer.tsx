import { content, DOCS, GITHUB } from "../data/content";

const LINKS: Record<string, string> = {
  Overview: "#top",
  Pipeline: "#how",
  Simulator: "#try",
  Results: "#results",
  Features: "#features",
  "Quick start": "#start",
  FAQ: "#faq",
  Limitations: `${DOCS}/limitations.md`,
  GitHub: GITHUB,
  Docs: DOCS,
  Issues: `${GITHUB}/issues`,
  "MIT License": `${GITHUB}/blob/main/LICENSE`,
};

export function Footer() {
  return (
    <footer className="wrap">
      <div className="foot">
        <div className="fcols">
          <div>
            <a className="brand" href="#top">
              ProtoMind
            </a>
            <p className="tg">{content.footer.blurb}</p>
          </div>
          {content.footer.columns.map((column, index) => (
            <div key={index}>
              <h5>{["Product", "Run it", "Source"][index]}</h5>
              <ul>
                {column.map((label) => (
                  <li key={label}>
                    <a href={LINKS[label] ?? "#top"}>{label}</a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="fbot">
          <span>{content.footer.note}</span>
          <span>Python / SQLite / JSON / MIT License</span>
        </div>
        <div className="mark" aria-hidden="true">
          ProtoMind
        </div>
      </div>
    </footer>
  );
}
