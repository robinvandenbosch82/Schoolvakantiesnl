// Planner.jsx — vakantieplanner: invoer + grote Reisweek-radar + slim-vertrekadvies.

const { useState: useStatePl } = React;

function Stepper({ label, value, set, min, max }) {
  return (
    <div className="stepper">
      <span className="stepper-lab">{label}</span>
      <div className="stepper-ctl">
        <button onClick={function () { set(Math.max(min, value - 1)); }} disabled={value <= min}>−</button>
        <span className="mono">{value}</span>
        <button onClick={function () { set(Math.min(max, value + 1)); }} disabled={value >= max}>+</button>
      </div>
    </div>
  );
}

function Planner({ goTo }) {
  const W = window.SV.weeks;
  const [volw, setVolw] = useStatePl(2);
  const [kind, setKind] = useStatePl(2);
  const [dest, setDest] = useStatePl("it");
  const [type, setType] = useStatePl("strand");
  const bestIdx = W.reduce(function (b, w, i) { return w.score > W[b].score ? i : b; }, 0);
  const [sel, setSel] = useStatePl(bestIdx);

  const cur = W[sel];
  // zoek een betere week binnen 3 weken afstand
  let alt = null;
  for (let d = 1; d <= 3; d++) {
    [sel - d, sel + d].forEach(function (j) {
      if (j >= 0 && j < W.length && W[j].score > cur.score + 6) {
        if (!alt || W[j].score > W[alt].score) alt = j;
      }
    });
  }
  const altW = alt != null ? W[alt] : null;
  const drukteDelta = altW ? Math.round(((cur.drukte - altW.drukte) / cur.drukte) * 100) : 0;
  const prijsDelta = altW ? Math.round(((cur.prijs - altW.prijs) / cur.prijs) * 100) : 0;

  const REGIOS = ["Heel NL", "Noord", "Midden", "Zuid"];
  const TYPES = ["strand", "stad", "natuur"];

  return (
    <div className="page planner rise">
      <div className="planner-head">
        <span className="eye">Vakantieplanner</span>
        <h1>Vind jullie slimste reisweek.</h1>
        <p className="lead">Vertel ons kort wie er meegaat en wat je zoekt — wij scoren elke week op drukte, prijs, weer en schoolvakantie-overlap.</p>
      </div>

      {/* INVOER */}
      <div className="planner-inputs card">
        <Stepper label="Volwassenen" value={volw} set={setVolw} min={1} max={6} />
        <Stepper label="Kinderen" value={kind} set={setKind} min={0} max={6} />
        <div className="inp-block">
          <span className="stepper-lab">Bestemming</span>
          <window.CountryPicker compact showStatus land={dest} onPick={setDest} />
        </div>
        <div className="inp-block">
          <span className="stepper-lab">Type vakantie</span>
          <div className="seg">
            {TYPES.map(function (tp) {
              return <button key={tp} className={type === tp ? "on" : ""} onClick={function () { setType(tp); }}>{tp}</button>;
            })}
          </div>
        </div>
      </div>

      {/* GROTE RADAR */}
      <div style={{ marginTop: 22 }}>
        <window.Radar weeks={W} selected={sel} onSelect={setSel} />
      </div>

      {/* SLIM-VERTREKADVIES */}
      <div className="advice card">
        <div className="advice-ic">⚑</div>
        <div className="advice-txt">
          <span className="eye">Slim-vertrekadvies</span>
          {altW ? (
            <p className="advice-line">
              Week {cur.wk} is prima, maar <strong>week {altW.wk} ({altW.d1})</strong> is
              <strong className="good"> {Math.max(1, drukteDelta)}% rustiger</strong> en
              <strong className="good"> {Math.max(1, prijsDelta)}% goedkoper</strong>.
              Een kleine verschuiving, een groot verschil voor het gezin.
            </p>
          ) : (
            <p className="advice-line">
              Goede keuze — <strong>week {cur.wk}</strong> hoort al bij de slimste weken.
              Rustiger dan dit wordt het in deze periode niet.
            </p>
          )}
          <div className="advice-actions">
            {altW && <button className="btn" onClick={function () { setSel(alt); }}>Bekijk week {altW.wk}</button>}
            <button className="btn-ghost" style={{ padding: "13px 20px", borderRadius: 14 }}
              onClick={function () { goTo("kaart"); }}>Waar is het dan rustig? →</button>
          </div>
        </div>
      </div>
    </div>
  );
}

window.Planner = Planner;
