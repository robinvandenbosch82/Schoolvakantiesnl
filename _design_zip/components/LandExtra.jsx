// LandExtra.jsx — extra landpagina-content: beste reisweken (slim-score per week)
// en weer per maand. Data uit data.js (window.SV) en landdata.js (window.LANDDATA).

const { useState: useStateLX } = React;

function BesteReisweken({ landNaam, goTo }) {
  const W = window.SV.weeks;
  // top 4 slimste weken
  const top = W.map(function (w, i) { return { w: w, i: i }; })
    .sort(function (a, b) { return b.w.score - a.w.score; })
    .slice(0, 4)
    .sort(function (a, b) { return a.i - b.i; });
  const maxScore = Math.max.apply(null, W.map(function (w) { return w.score; }));

  return (
    <section className="land-block">
      <div className="section-head">
        <div>
          <span className="eye">Slim plannen</span>
          <h2 style={{ marginTop: 8 }}>Beste weken voor een reis naar {landNaam}</h2>
        </div>
        <p>Slim-score per week: drukte, prijs, weer en overlap gewogen tot één cijfer. Hoger = slimmer.</p>
      </div>

      <div className="brw card">
        <div className="brw-bars">
          {W.map(function (w) {
            const cls = w.band === "rustig" ? "go" : w.band === "matig" ? "mid" : "no";
            return (
              <div key={w.wk} className={"brw-col " + cls}>
                <span className="brw-score">{w.score}</span>
                <div className="brw-bar" style={{ height: Math.round((w.score / maxScore) * 100) + "%" }}></div>
                <span className="brw-wk mono">{w.wk}</span>
              </div>
            );
          })}
        </div>
        <div className="brw-foot">
          <span className="brw-key"><i className="go"></i>Slim (rustig &amp; voordelig)</span>
          <span className="brw-key"><i className="mid"></i>Matig</span>
          <span className="brw-key"><i className="no"></i>Druk &amp; duur</span>
        </div>
      </div>

      <div className="brw-top">
        {top.map(function (t) {
          return (
            <div key={t.w.wk} className="brw-pick">
              <span className="bp-score">{t.w.score}</span>
              <div className="bp-info">
                <span className="bp-wk">Week {t.w.wk}</span>
                <span className="bp-dt">vanaf {t.w.d1}</span>
              </div>
            </div>
          );
        })}
        <button className="btn brw-cta" onClick={function () { goTo("planner"); }}>
          Plan met de vakantieplanner
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </button>
      </div>
    </section>
  );
}

function WeerPerMaand({ land, landNaam }) {
  const data = window.LANDDATA[land] && window.LANDDATA[land].weer;
  const [metric, setMetric] = useStateLX("temp");
  if (!data) return null;
  const M = data.maanden;

  const cfg = {
    temp: { lab: "Temperatuur", unit: "°C", max: 28, get: function (x) { return x.temp; }, fmt: function (v) { return v + "°"; } },
    zon:  { lab: "Zon",         unit: "u/dag", max: 9, get: function (x) { return x.zon; },  fmt: function (v) { return v + "u"; } },
    regen:{ lab: "Regendagen",  unit: "/maand", max: 16, get: function (x) { return x.regen; }, fmt: function (v) { return v; } },
  };
  const c = cfg[metric];

  function color(x) {
    if (metric === "temp") return window.drukteColor(100 - Math.min(100, c.get(x) / c.max * 100));
    if (metric === "zon") return "var(--accent)";
    return "oklch(70% 0.09 235)";
  }

  return (
    <section className="land-block">
      <div className="section-head">
        <div>
          <span className="eye">Klimaat</span>
          <h2 style={{ marginTop: 8 }}>Weer per maand in {landNaam}</h2>
        </div>
        <div className="seg wm-seg">
          {Object.keys(cfg).map(function (k) {
            return <button key={k} className={metric === k ? "on" : ""} onClick={function () { setMetric(k); }}>{cfg[k].lab}</button>;
          })}
        </div>
      </div>

      <div className="weer card">
        <div className="weer-grid">
          {M.map(function (x) {
            const v = c.get(x);
            const h = Math.max(8, Math.round(v / c.max * 100));
            const isZomer = ["jun", "jul", "aug"].indexOf(x.m) >= 0;
            return (
              <div key={x.m} className={"weer-col" + (isZomer ? " zomer" : "")}>
                <span className="weer-val">{c.fmt(v)}</span>
                <div className="weer-track">
                  <div className="weer-bar" style={{ height: h + "%", background: color(x) }}></div>
                </div>
                <span className="weer-m mono">{x.m}</span>
              </div>
            );
          })}
        </div>
        <div className="weer-meta">
          <span className="weer-unit mono">{c.lab} · {c.unit}</span>
          <span className="weer-bron mono">{data.bron}</span>
        </div>
      </div>
      <div className="reg-note"><strong>Beste reismaanden.</strong> {data.beste}</div>
    </section>
  );
}

function LandExtra({ land, landNaam, goTo }) {
  return (
    <React.Fragment>
      <BesteReisweken landNaam={landNaam} goTo={goTo} />
      <WeerPerMaand land={land} landNaam={landNaam} />
    </React.Fragment>
  );
}

window.LandExtra = LandExtra;
