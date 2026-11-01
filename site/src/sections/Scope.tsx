export function Scope() {
  return (
    <section className="sec" id="scope">
      <div className="wrap">
        <h2>Built to <i className="ico" style={{ "--c": "#f97316" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M9 18h6M10 21h4M12 3a6 6 0 00-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0012 3z"/></svg></i> <span className="m">teach.</span></h2>
        <p className="lead2">ProtoMind is for learning how protocol discovery works. It is not a production tool.</p>
        <div className="sc">
          <div className="scc">
            <div className="ib" style={{ "--c": "#22c55e" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div>
            <h3>In scope</h3>
            <ul><li>Passive protocol discovery</li><li>Framing inference</li><li>Field detection</li><li>State machine learning</li><li>Exports</li><li>Guarded lab mode</li></ul>
          </div>
          <div className="scc">
            <div className="ib" style={{ "--c": "#ef4444" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></div>
            <h3>Out of scope</h3>
            <ul><li>Decoding encrypted traffic</li><li>Scanning non-lab targets</li><li>Exploit generation</li><li>Unguarded active learning</li></ul>
          </div>
        </div>
      </div>
    </section>
  );
}