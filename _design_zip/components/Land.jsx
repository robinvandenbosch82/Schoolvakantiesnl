// Land.jsx — landenpagina (NL + DE): LIVE schoolvakantie- & feestdagdata via
// OpenHolidays API, met jaar-switcher (2026–2030). Statische editorial (intro,
// regio's, studiedagen, officieuze dagen, FAQ) komt uit landdata.js.

const { useState: useStateLand, useEffect: useEffectLand, useRef: useRefLand } = React;

// EUROPE + CountryPicker komen uit het gedeelde components/CountryPicker.jsx
const EUROPE = window.EUROPE;
const CountryPicker = window.CountryPicker;

function VakBlok({ vak, regios, deelLabel }) {
  const verplicht = /verplicht/i.test(vak.status);
  const showWk = !!vak.weken;
  return (
    <div className="vakblok">
      <div className="vakblok-head">
        <div>
          <h3>{vak.naam}</h3>
          {vak.alias && <span className="alias">{vak.alias}</span>}
        </div>
        <span className={"status" + (verplicht ? " verplicht" : "")}>{vak.status}</span>
      </div>
      <table className="ftable">
        <thead><tr><th>{deelLabel}</th><th>Periode</th>{showWk && <th>Weken</th>}</tr></thead>
        <tbody>
          {regios.map(function (r) {
            const per = vak.perRegio[r];
            if (!per) return null;
            return (
              <tr key={r}>
                <td>{r}</td>
                <td>{per}</td>
                {showWk && <td><span className="wk">{vak.weken[r] || ""}</span></td>}
              </tr>
            );
          })}
        </tbody>
      </table>
      {vak.note && <p className="note">{vak.note}</p>}
    </div>
  );
}

function Land({ goTo }) {
  const [land, setLand] = useStateLand("de");
  const [year, setYear] = useStateLand(2026);
  const [live, setLive] = useStateLand(null);
  const [overlap, setOverlap] = useStateLand(null);
  const [status, setStatus] = useStateLand("loading"); // loading | live | error
  const [selG, setSelG] = useStateLand(null);

  const picked = EUROPE.find(function (c) { return c.code === land; }) || EUROPE[0];
  const isLive = !!window.LANDDATA[land];
  const D = isLive ? window.LANDDATA[land] : { flag: picked.flag, name: picked.name };
  const deelLabel = land === "de" ? "Deelstaat" : "Regio";
  const regioLabels = isLive ? window.Holidays.COUNTRIES[land].regions.map(function (r) { return r.label; }) : [];

  useEffectLand(function () {
    let alive = true;
    setStatus("loading"); setLive(null); setOverlap(null); setSelG(null);
    if (!isLive) { setStatus("soon"); return function () { alive = false; }; }
    Promise.all([window.Holidays.getYearData(land, year), window.Holidays.getOverlap(land, year)])
      .then(function (res) { if (!alive) return; setLive(res[0]); setOverlap(res[1]); setStatus("live"); })
      .catch(function () { if (!alive) return; setStatus("error"); });
    return function () { alive = false; };
  }, [land, year]);

  // eerstvolgende vakantie vanaf vandaag (leuke vooruitblik)
  function vooruitblik() {
    if (!live || !live.vakanties.length) return null;
    const vandaag = new Date(); vandaag.setHours(0, 0, 0, 0);
    let next = null;
    live.vakanties.forEach(function (v) {
      const d = window.Holidays.helpers.parse(v.minStart);
      if (d >= vandaag && (!next || d < next.d)) next = { d: d, v: v };
    });
    if (!next) return null;
    const dagen = Math.round((next.d - vandaag) / 86400000);
    return { naam: next.v.naam, dagen: dagen };
  }
  const vb = vooruitblik();

  const zomer = live && live.vakanties.find(function (v) { return /zomer|sommer/i.test(v.naam); });
  const overige = live ? live.vakanties.filter(function (v) { return v !== zomer; }) : [];
  const ganttRows = live ? live.gantt : [];
  const weekNums = live ? live.weekWindow.map(function (w) { return w.wk; }) : [];

  return (
    <div className="page land rise">
      {/* SWITCHERS */}
      <div className="land-controls">
        <CountryPicker land={land} onPick={setLand} />
        <div className="year-switch">
          <span className="ys-lab">Plan vooruit</span>
          {window.Holidays.years.map(function (y) {
            return <button key={y} className={year === y ? "on" : ""} onClick={function () { setYear(y); }}>{y}</button>;
          })}
        </div>
        <span className={"live-badge " + status}>
          <i></i>{status === "live" ? "Live via OpenHolidays" : status === "loading" ? "Laden…" : status === "soon" ? "Binnenkort live" : "Offline"}
        </span>
      </div>

      {/* HERO */}
      <div className="land-hero">
        <div className="land-hero-main">
          <span className="land-flag">{D.flag}</span>
          <div>
            <span className="eye">Schoolvakanties &amp; vrije dagen · {year}</span>
            <h1>{D.name}</h1>
            <p className="land-sub">{land === "de"
              ? "16 deelstaten, elk met eigen schoolvakanties. Daardoor is het hele land nooit tegelijk vrij."
              : land === "nl"
              ? "Vijf schoolvakanties, gespreid over drie regio's om de drukte te verdelen."
              : "Bekijk straks alle schoolvakanties, feestdagen en vrije dagen van " + D.name + "."}</p>
            {vb && <p className="vooruitblik">📅 Eerstvolgende vakantie in {D.name}: <strong>{vb.naam}</strong> — nog <strong>{vb.dagen} dagen</strong>.</p>}
          </div>
        </div>
        {isLive && (
        <div className="overlap-card">
          <span className="ov-lab">Overlap met {land === "de" ? "🇳🇱 Nederland" : "🇩🇪 Duitsland"}</span>
          <div className="ov-ring">
            {overlap
              ? <window.ScoreRing score={overlap.peak} band={overlap.peak >= 70 ? "druk" : overlap.peak >= 45 ? "matig" : "rustig"} size={104} />
              : <div className="ring-skel" />}
          </div>
          <p className="ov-note">{overlap
            ? <span>Piek-overlap in <strong>week {overlap.peakWk}</strong>. Hoge overlap = drukker &amp; duurder. <span style={{ color: "var(--ink-3)" }}>Lager is beter.</span></span>
            : "Berekenen…"}</p>
        </div>
        )}
      </div>

      {status === "soon" && (
        <div className="land-soon">
          <div className="land-soon-flag">{D.flag}</div>
          <h2>Schoolvakanties {D.name} — binnenkort live</h2>
          <p>We rollen heel Europa stap voor stap uit via de OpenHolidays API. <strong>Nederland</strong> en <strong>Duitsland</strong> zijn nu al volledig beschikbaar; {D.name} volgt binnenkort met dezelfde live vakantie- en feestdagdata.</p>
          <div className="land-soon-live">
            <button className="btn" onClick={function () { setLand("nl"); }}>🇳🇱 Bekijk Nederland</button>
            <button className="btn-ghost" onClick={function () { setLand("de"); }}>🇩🇪 Bekijk Duitsland</button>
          </div>
        </div>
      )}

      {isLive && status === "error" && (
        <div className="land-error">Kon de live data even niet laden. Controleer de verbinding en probeer een ander jaar — of <button className="linklike" onClick={function () { setYear(year); }}>opnieuw</button>.</div>
      )}

      {status === "loading" && <div className="land-loading"><div className="spinner" /><span>Schoolvakanties {year} ophalen…</span></div>}

      {live && (
        <React.Fragment>
          {/* GANTT */}
          <section className="land-block">
            <div className="section-head">
              <div>
                <span className="eye">Zomervakantie {year} — spreiding</span>
                <h2 style={{ marginTop: 8 }}>{land === "de" ? "Wanneer is welke deelstaat vrij?" : "Wanneer is welke regio vrij?"}</h2>
              </div>
              <p>Klik een {land === "de" ? "deelstaat" : "regio"} om de drukte-tijdlijn eronder te filteren.</p>
            </div>
            <div className="gantt">
              <div className="gantt-axis">
                <span></span>
                <div className="gantt-weeks">
                  {weekNums.map(function (n, i) { return <span key={n} className={i % 2 === 0 ? "wkn show" : "wkn"}>{n}</span>; })}
                </div>
              </div>
              {ganttRows.map(function (bl) {
                const on = selG === bl.name;
                const startPct = ((weekNums.indexOf(bl.start)) / weekNums.length) * 100;
                const widthPct = ((bl.eind - bl.start + 1) / weekNums.length) * 100;
                return (
                  <div key={bl.name} className={"gantt-row" + (on ? " on" : "")} onClick={function () { setSelG(on ? null : bl.name); }}>
                    <span className="gantt-name">{bl.name}</span>
                    <div className="gantt-track">
                      <div className="gantt-bar" style={{ left: Math.max(0, startPct) + "%", width: widthPct + "%" }}>
                        <span className="mono">wk {bl.start}–{bl.eind}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          {/* DRUKTE TIJDLIJN (live afgeleid uit vakantie-dekking) */}
          <section className="land-block">
            <div className="section-head">
              <div>
                <span className="eye">Vakantiedrukte · {year}</span>
                <h2 style={{ marginTop: 8 }}>{selG ? "Drukte tijdens zomervakantie " + selG : "Hoeveel " + (land === "de" ? "deelstaten" : "regio's") + " zijn er vrij?"}</h2>
              </div>
              <p>Afgeleid uit de schoolvakanties: meer regio's vrij = drukker &amp; duurder.</p>
            </div>
            <div className="timeline card">
              {live.drukteWeeks.map(function (w) {
                const v = w.drukte;
                const row = selG && ganttRows.find(function (b) { return b.name === selG; });
                const dimmed = row && !(w.wk >= row.start && w.wk <= row.eind);
                return (
                  <div key={w.wk} className={"tl-col" + (dimmed ? " dim" : "")}>
                    <div className="tl-bar" style={{ height: Math.max(6, v) + "%", background: window.drukteColor(v) }}></div>
                    <span className="tl-wk mono">{w.wk}</span>
                  </div>
                );
              })}
            </div>
          </section>

          {/* ALLE SCHOOLVAKANTIES PER PERIODE */}
          <section className="land-block">
            <div className="section-head">
              <div>
                <span className="eye">Alle schoolvakanties {year}</span>
                <h2 style={{ marginTop: 8 }}>Schoolvakanties {D.name} {year}</h2>
              </div>
            </div>
            <p className="land-intro" style={{ marginBottom: 22 }}>{D.intro}</p>
            <div className="vakgrid">
              {zomer && <div className="vakblok wide"><div className="vakblok-head"><div><h3>{zomer.naam} {D.name} {year}</h3>{zomer.alias && <span className="alias">{zomer.alias}</span>}</div><span className="status">{zomer.status}</span></div>
                <table className="ftable"><thead><tr><th>{deelLabel}</th><th>Periode</th><th>Weken</th></tr></thead>
                  <tbody>{regioLabels.map(function (r) { const per = zomer.perRegio[r]; if (!per) return null; return (<tr key={r}><td>{r}</td><td>{per}</td><td><span className="wk">{zomer.weken[r] || ""}</span></td></tr>); })}</tbody>
                </table>
              </div>}
              {overige.map(function (v) { return <VakBlok key={v.naam + "-" + v.minStart} vak={v} regios={regioLabels} deelLabel={deelLabel} />; })}
            </div>
          </section>

          {/* OFFICIËLE FEESTDAGEN */}
          <section className="land-block">
            <div className="section-head">
              <div>
                <span className="eye">Vrije dagen</span>
                <h2 style={{ marginTop: 8 }}>Officiële feestdagen {D.name} {year}</h2>
              </div>
              <p>Landelijke vrije dagen — handig voor een lang weekend of midweek.</p>
            </div>
            <div className="feest">
              {live.feestdagen.map(function (f) {
                return (
                  <div key={f.naam + f.datum} className="feest-row">
                    <span className="feest-day">{f.dag}</span>
                    <span className="feest-info"><span className="nm">{f.naam}</span><span className="dt">{f.datum}</span></span>
                  </div>
                );
              })}
            </div>
            {(D.feestdagenNote || live.regionaalAantal > 0) && (
              <p className="feest-note">
                {live.regionaalAantal > 0 && <span><strong>+ {live.regionaalAantal} regionale feestdagen</strong> die alleen in bepaalde {land === "de" ? "deelstaten" : "regio's"} gelden. </span>}
                {D.feestdagenNote}
              </p>
            )}
          </section>
        </React.Fragment>
      )}

      {/* ===== BESTE REISWEKEN + WEER PER MAAND ===== */}
      {isLive && <window.LandExtra land={land} landNaam={D.name} goTo={goTo} />}

      {/* ===== VIATOR AFFILIATE: dingen om te doen (na de data) ===== */}
      {isLive && live && (
        <window.ActivitiesSection countryCode={land} countryName={D.name}
          defaultTheme={vb ? window.VIATOR.themeForVacation(vb.naam) : "familie"} />
      )}

      {/* ===== STATISCHE EDITORIAL (niet in de API) ===== */}
      {isLive && (
      <React.Fragment>
      <section className="land-block">
        <div className="section-head"><div><span className="eye">Roostervrij</span><h2 style={{ marginTop: 8 }}>Officiële vrije schooldagen</h2></div></div>
        <div className="studie">
          <p className="studie-txt">{D.studiedagen.uitleg}</p>
          <div className="studie-list">{D.studiedagen.voorbeelden.map(function (v) { return <div key={v} className="it">{v}</div>; })}</div>
        </div>
      </section>

      <section className="land-block">
        <div className="section-head"><div><span className="eye">Goed om te weten</span><h2 style={{ marginTop: 8 }}>Officieuze feestdagen</h2></div><p>Geen vrije dag, wél druk: vaak een uitje of dagje weg.</p></div>
        <div className="officieus">
          {D.officieus.map(function (o) { return (<div key={o.naam} className="off-chip"><span className="oc-txt"><span className="oc-nm">{o.naam}</span><span className="oc-dt">{o.datum}</span></span></div>); })}
        </div>
      </section>

      <section className="land-block">
        <div className="section-head"><div><span className="eye">Regio-indeling</span><h2 style={{ marginTop: 8 }}>{land === "de" ? "Hoe is Duitsland ingedeeld?" : "Welke regio is mijn provincie?"}</h2></div></div>
        {land === "nl" ? (
          <div className="regio-cols">
            {D.regios.map(function (r) { return (<div key={r} className="regio-col"><h3>{r}-Nederland</h3><p>{D.regioUitleg[r]}</p></div>); })}
          </div>
        ) : <p className="land-intro">{D.regioInfo}</p>}
      </section>

      <section className="land-block">
        <div className="section-head"><div><span className="eye">Veelgestelde vragen</span><h2 style={{ marginTop: 8 }}>Vragen over schoolvakanties in {D.name}</h2></div></div>
        <div className="faq">
          {D.faq.map(function (q, i) {
            return (
              <details key={i} className="faq-item">
                <summary><span>{q.v}</span><span className="faq-ic" aria-hidden="true">+</span></summary>
                <p>{q.a}</p>
              </details>
            );
          })}
        </div>
      </section>

      <p className="bronregel">
        {D.bron} <span className="bron-upd">Live opgehaald via de OpenHolidays API · {D.bijgewerkt}.</span>
      </p>
      </React.Fragment>
      )}

      <div style={{ textAlign: "center", margin: "20px 0 10px" }}>
        <button className="btn" onClick={function () { goTo("planner"); }}>Plan jullie slimste reisweek</button>
      </div>
    </div>
  );
}

window.Land = Land;
