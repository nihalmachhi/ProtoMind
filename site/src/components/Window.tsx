import { useEffect, useState } from "react";
import { content } from "../data/content";
import { useTour } from "../features/tour/useTour";

export function Window() {
  const tabs = content.tour.tabs;
  const { index, setIndex, paused, setPaused } = useTour(tabs.length, 7000);
  const [hover, setHover] = useState(false);
  useEffect(() => {
    setPaused(hover);
  }, [hover, setPaused]);
  const held = hover || paused;
  const tab = tabs[index];
  return (
    <div
      className="win"
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onFocus={() => setHover(true)}
      onBlur={() => setHover(false)}
    >
      <aside className="side">
        <div className="dots">
          <i />
          <i />
          <i />
        </div>
        {tabs.map((item, itemIndex) => (
          <button
            key={item.name}
            className={`it${itemIndex === index ? " on" : ""}`}
            role="tab"
            aria-selected={itemIndex === index}
            onClick={() => setIndex(itemIndex)}
            onKeyDown={(event) => {
              if (event.key === "ArrowRight") setIndex((index + 1) % tabs.length);
              if (event.key === "ArrowLeft") setIndex((index - 1 + tabs.length) % tabs.length);
            }}
          >
            {item.name}
            {itemIndex === index && !held && <span className="bar" />}
          </button>
        ))}
        <h4>{content.tour.sideTitle}</h4>
        <div className="it">
          <span>{content.tour.promptLabel}</span>
          <span>{content.tour.promptValue}</span>
        </div>
      </aside>
      <div className="main">
        <div className="col">
          <div className="cv" style={{ opacity: held ? 0.9 : 1 }}>
            <h3>{tab.name}</h3>
            <p className="sub">Auto-playing tour</p>
            <p className="tx">{tab.copy}</p>
            <div className="term">{tab.code}</div>
          </div>
        </div>
        <div className="col">
          <h4>Observed</h4>
          <div className="rw">
            <span>{tab.label}</span>
            <span>{tab.value}</span>
          </div>
          <p className="sub">{tab.detail}</p>
          <ul className="lst">
            {tab.stats.map(([key, value]) => (
              <li key={key}>
                {key}
                <b style={{ float: "right" }}>{value}</b>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <button
        className="ctrl"
        onClick={() => setPaused(!paused)}
        aria-label={paused ? content.tour.resume : content.tour.pause}
      >
        {paused ? ">" : "||"}
      </button>
    </div>
  );
}
