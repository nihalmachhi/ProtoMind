import { content, GITHUB } from "../data/content";

export function Nav() {
  return (
    <nav className="top" aria-label="Main">
      <div className="wrap" style={{ display: "flex", alignItems: "center", gap: 26, width: "100%" }}>
        <a className="brand" href="#top">
          <img src={`${import.meta.env.BASE_URL}readme-icon.png`} alt="ProtoMind" width={22} height={22} />
          {content.name}
        </a>
        <div className="links">
          {content.nav.links.map((link) => (
            <a key={link.href} href={link.href}>
              {link.label}
            </a>
          ))}
        </div>
        <div className="sp">
          <a className="pill" href={GITHUB}>
            {content.nav.githubLabel}
          </a>
          <a className="pill w" href="#start">
            {content.nav.runLabel}
          </a>
        </div>
      </div>
    </nav>
  );
}
