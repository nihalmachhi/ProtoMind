import { content, GITHUB } from "../data/content";

export function Cta() {
  const stages = content.cta.stages;
  const boxWidth = 112;
  const gap = 30;
  return (
    <section className="cta2" aria-label="Get started">
      <div className="wrap">
        <div style={{ overflowX: "auto", padding: "6px 4px 10px", marginBottom: 24 }}>
          <svg
            className="flow arch"
            viewBox="0 0 964 90"
            role="img"
            aria-label="ProtoMind pipeline"
            style={{ width: "100%", minWidth: 820, maxWidth: 964, height: "auto", overflow: "visible" }}
          >
            {stages.map((_, index) => {
              if (index === stages.length - 1) return null;
              const x1 = index * (boxWidth + gap) + boxWidth;
              const x2 = x1 + gap;
              return (
                <path
                  key={index}
                  className="fl"
                  d={`M${x1} 45H${x2}`}
                  style={{
                    fill: "none",
                    stroke: "#5a5a64",
                    strokeWidth: 1.2,
                    strokeDasharray: "4 4",
                    animation: "dash 1.2s linear infinite",
                  }}
                />
              );
            })}
            {stages.map((stage, index) => {
              const x = index * (boxWidth + gap);
              const last = index === stages.length - 1;
              return (
                <g
                  key={stage}
                  className={`gn st ${last ? "last" : ""}`}
                  style={{ animation: `${last ? "stlb" : "stl"} 6.3s ease-in-out infinite`, animationDelay: `${index * 0.9}s` }}
                >
                  <rect x={x} y={12} width={boxWidth} height={66} rx={9} style={{ fill: "#19191c", stroke: "#242428" }} />
                  <text textAnchor="middle" style={{ font: "500 10px var(--fm)", fill: "#ececee" }}>
                    <tspan x={x + boxWidth / 2} y={42}>
                      {stage}
                    </tspan>
                  </text>
                </g>
              );
            })}
            <circle r={3.2} fill="#f4f4f5">
              <animateMotion dur="6.3s" repeatCount="indefinite" path="M0 45H964" />
            </circle>
          </svg>
        </div>
        <h2>{content.cta.heading}</h2>
        <p className="lead2" style={{ margin: "12px auto 0" }}>
          {content.cta.copy}
        </p>
        <div className="btns">
          <a className="pill w" href={GITHUB}>
            {content.cta.primary}
          </a>
          <a className="pill" href="#try">
            {content.cta.secondary}
          </a>
        </div>
      </div>
    </section>
  );
}
