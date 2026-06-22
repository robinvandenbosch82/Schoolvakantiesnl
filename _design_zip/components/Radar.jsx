// Radar.jsx — de Reisweek-radar: held-component van v3.
// Toont per week een Slim-score (0-100) als balken, met geselecteerde week-detail.

const { useState, useRef, useEffect } = React;

// kleur op basis van band
function bandVars(band) {
  if (band === "rustig") return "is-rustig";
  if (band === "matig") return "is-matig";
  return "is-druk";
}
function bandLabel(band) {
  return band === "rustig" ? "Slim" : band === "matig" ? "Redelijk" : "Druk";
}

// kleine count-up hook
function useCountUp(target, dur) {
  const [v, setV] = useState(0);
  const ref = useRef(0);
  useEffect(function () {
    let raf, start;
    function step(t) {
      if (!start) start = t;
      const p = Math.min(1, (t - start) / (dur || 700));
      const eased = 1 - Math.pow(1 - p, 3);
      setV(Math.round(target * eased));
      if (p < 1) raf = requestAnimationFrame(step);
    }
    raf = requestAnimationFrame(step);
    return function () { cancelAnimationFrame(raf); };
  }, [target]);
  return v;
}

// Score-ring (SVG) — schaalt mee met `size`
function ScoreRing({ score, band, size }) {
  const s = size || 132;
  const stroke = Math.max(6, Math.round(s * 0.068));
  const r = (s - stroke * 2 - 2) / 2;
  const circ = 2 * Math.PI * r;
  const val = useCountUp(score, 800);
  const off = circ * (1 - val / 100);
  const cls = bandVars(band);
  const valFont = Math.round(s * 0.3);
  const labFont = Math.max(8, Math.round(s * 0.092));
  return (
    <div className={"ring " + cls} style={{ width: s, height: s }}>
      <svg width={s} height={s} viewBox={"0 0 " + s + " " + s}>
        <circle cx={s/2} cy={s/2} r={r} fill="none" stroke="var(--line)" strokeWidth={stroke} />
        <circle cx={s/2} cy={s/2} r={r} fill="none" stroke="var(--c)" strokeWidth={stroke}
          strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={off}
          transform={"rotate(-90 " + s/2 + " " + s/2 + ")"}
          style={{ transition: "stroke-dashoffset .2s linear" }} />
      </svg>
      <div className="ring-mid">
        <span className="ring-val mono" style={{ fontSize: valFont }}>{val}</span>
        <span className="ring-lab" style={{ fontSize: labFont }}>{bandLabel(band)}</span>
      </div>
    </div>
  );
}

// factor-meter rijtje in detail
function Factor({ label, value, invert, icon }) {
  // value 0-100; invert=true betekent laag is goed (drukte/prijs)
  const good = invert ? 100 - value : value;
  const cls = good >= 66 ? "is-rustig" : good >= 40 ? "is-matig" : "is-druk";
  return (
    <div className={"factor " + cls}>
      <span className="factor-ic">{icon}</span>
      <span className="factor-lab">{label}</span>
      <span className="factor-bar"><i style={{ width: value + "%" }}></i></span>
      <span className="factor-val mono">{value}</span>
    </div>
  );
}

function Radar({ weeks, selected, onSelect, accent }) {
  const sel = weeks[selected];
  const max = 100;
  // beste week markeren
  const bestIdx = weeks.reduce(function (b, w, i) { return w.score > weeks[b].score ? i : b; }, 0);

  return (
    <div className="radar card rise">
      <div className="radar-top">
        <div>
          <span className="eye">Reisweek-radar</span>
          <h3 className="radar-title">Wanneer is het slim weg?</h3>
          <p className="radar-sub">Eén score per week — drukte, prijs, weer en overlap samen.</p>
        </div>
        <div className="radar-detail">
          <ScoreRing score={sel.score} band={sel.band} />
          <div className="radar-detail-txt">
            <span className="mono dt-wk">WEEK {sel.wk}</span>
            <span className="dt-date">{sel.d1}</span>
            <div className="factors">
              <Factor label="Drukte" value={sel.drukte} invert icon="◌" />
              <Factor label="Prijs" value={sel.prijs} invert icon="€" />
              <Factor label="Weer" value={sel.weer} icon="☀" />
              <Factor label="Overlap" value={sel.overlap} invert icon="⇄" />
            </div>
          </div>
        </div>
      </div>

      <div className="radar-chart">
        {weeks.map(function (w, i) {
          const h = Math.max(8, (w.score / max) * 100);
          const on = i === selected;
          const best = i === bestIdx;
          return (
            <button key={w.wk} className={"wkbar " + bandVars(w.band) + (on ? " on" : "")}
              onClick={function () { onSelect(i); }} title={"Week " + w.wk + " · " + w.score}>
              {best && <span className="best-flag">★ slimste</span>}
              <span className="wkbar-track">
                <span className="wkbar-fill" style={{ height: h + "%" }}></span>
              </span>
              <span className="wkbar-num mono">{w.wk}</span>
            </button>
          );
        })}
      </div>
      <div className="radar-legend">
        <span><i className="dot is-rustig"></i> Slim (70+)</span>
        <span><i className="dot is-matig"></i> Redelijk</span>
        <span><i className="dot is-druk"></i> Druk &amp; duur</span>
        <span className="radar-hint">Tik op een week voor details</span>
      </div>
    </div>
  );
}

window.Radar = Radar;
window.ScoreRing = ScoreRing;
window.radarBandVars = bandVars;
