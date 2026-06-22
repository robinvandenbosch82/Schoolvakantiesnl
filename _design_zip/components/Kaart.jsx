// Kaart.jsx — Europese druktekaart op volledig scherm met week-slider en land-paneel.

const { useState: useStateK } = React;

function Kaart({ goTo }) {
  const C = window.SV.countries;
  const W = window.SV.weeks;
  const [wk, setWk] = useStateK(11);
  const [sel, setSel] = useStateK("it");

  const selC = C.find(function (c) { return c.code === sel; });
  const selV = selC.drukteByWeek[wk];
  const ranked = C.map(function (c) { return { c: c, v: c.drukteByWeek[wk] }; })
    .sort(function (a, b) { return a.v - b.v; });
  const rustigste = ranked[0];

  function bandOf(v) { return v < 45 ? "rustig" : v < 70 ? "matig" : "druk"; }

  return (
    <div className="kaart rise">
      <div className="kaart-stage">
        <window.EuropeMap countries={C} weekIdx={wk} selected={sel} onSelect={setSel} big />
      </div>

      <aside className="kaart-panel">
        <div className="kp-head">
          <span className="eye">Druktekaart Europa</span>
          <h2>Waar is het rustig?</h2>
        </div>

        {/* geselecteerd land detail */}
        <div className={"kp-detail is-" + bandOf(selV)}>
          <span className="kp-flag">{selC.flag}</span>
          <div className="kp-detail-info">
            <strong>{selC.name}</strong>
            <span className="kp-detail-band">{selV < 45 ? "Rustig" : selV < 70 ? "Matig druk" : "Erg druk"}</span>
          </div>
          <span className="kp-detail-val mono" style={{ color: "var(--c-ink)" }}>{selV}</span>
        </div>

        {/* ranglijst */}
        <div className="kp-rank">
          {ranked.map(function (r) {
            return (
              <button key={r.c.code} className={"kp-row" + (sel === r.c.code ? " on" : "")}
                onClick={function () { setSel(r.c.code); }}>
                <span className="flag">{r.c.flag}</span>
                <span className="nm">{r.c.name}</span>
                <span className="mini-bar"><i style={{ width: r.v + "%", background: window.drukteColor(r.v) }}></i></span>
                <span className="pct mono">{r.v}</span>
              </button>
            );
          })}
        </div>

        <div className="kp-tip">
          <span className="kp-tip-ic">✓</span>
          <p>Rustigste deze week: <strong>{rustigste.c.flag} {rustigste.c.name}</strong> ({rustigste.v}/100).</p>
        </div>

        <div className="kp-legend">
          <span><i style={{ background: "var(--rustig)" }}></i> Rustig</span>
          <span><i style={{ background: "var(--matig)" }}></i> Matig</span>
          <span><i style={{ background: "var(--druk)" }}></i> Druk</span>
        </div>
      </aside>

      {/* week slider sticky */}
      <div className="kaart-slider">
        <span className="ks-now mono">WK {W[wk].wk} · {W[wk].d1}</span>
        <input type="range" min="0" max={W.length - 1} value={wk}
          onChange={function (e) { setWk(+e.target.value); }} />
        <div className="ks-marks">
          {["mei", "jun", "jul", "aug", "sep"].map(function (m) { return <span key={m}>{m}</span>; })}
        </div>
      </div>
    </div>
  );
}

window.Kaart = Kaart;
