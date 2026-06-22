// Home.jsx — homepage van v3. Hero-kiezer + Reisweek-radar (held) + mini-druktekaart
// + bestemmings-cards + beste periodes + kennisbank-fundament.

const { useState: useStateHome } = React;

const REGIOS = ["Heel NL", "Noord", "Midden", "Zuid"];

function MiniMapBlock({ goTo }) {
  const C = window.SV.countries;
  const W = window.SV.weeks;
  const [wk, setWk] = useStateHome(11); // start rond piek om contrast te tonen
  const [sel, setSel] = useStateHome("nl");
  // ranglijst rustigste landen deze week
  const ranked = C.map(function (c) { return { c: c, v: c.drukteByWeek[wk] }; })
    .sort(function (a, b) { return a.v - b.v; });

  return (
    <div className="minimap">
      <div className="map-wrap">
        <window.EuropeMap countries={C} weekIdx={wk} selected={sel} onSelect={setSel} />
        <div className="wkslider">
          <span className="wknow">WK {W[wk].wk} · {W[wk].d1}</span>
          <input type="range" min="0" max={W.length - 1} value={wk}
            onChange={function (e) { setWk(+e.target.value); }} />
        </div>
      </div>
      <div className="map-side">
        <div className="section-head" style={{ marginBottom: 4 }}>
          <div>
            <span className="eye">Druktekaart</span>
            <h2 style={{ fontSize: 24, marginTop: 8 }}>Waar is het rustig?</h2>
          </div>
        </div>
        <p style={{ color: "var(--ink-3)", fontSize: 14, margin: "0 0 6px" }}>
          Schuif door de weken en zie meteen welke landen rustig blijven.
        </p>
        <div className="map-rank">
          {ranked.map(function (r) {
            return (
              <div key={r.c.code} className={"map-rank-row" + (sel === r.c.code ? " sel" : "")}
                onClick={function () { setSel(r.c.code); }}>
                <span className="flag">{r.c.flag}</span>
                <span className="nm">{r.c.name}</span>
                <span className="mini-bar"><i style={{ width: r.v + "%", background: window.drukteColor(r.v) }}></i></span>
                <span className="pct">{r.v}</span>
              </div>
            );
          })}
        </div>
        <button className="btn-ghost" style={{ marginTop: 6, alignSelf: "flex-start" }}
          onClick={function () { goTo("kaart"); }}>Open volledige kaart →</button>
      </div>
    </div>
  );
}

function Home({ goTo }) {
  const W = window.SV.weeks;
  const D = window.SV.destinations;
  const [regio, setRegio] = useStateHome(0);
  const [dest, setDest] = useStateHome("it");
  const EU = window.EUROPE || [];
  const heroLanden = ["nl", "de", "be", "fr", "it", "es"].map(function (code) {
    return EU.find(function (c) { return c.code === code; });
  }).filter(Boolean);
  const [maand, setMaand] = useStateHome("sep");
  // selecteer week op basis van maand-keuze
  const maandStart = { mei: 0, jun: 4, jul: 9, aug: 13, sep: 18 };
  // open op de slimste week zodat de waarde meteen leesbaar is
  const bestIdx = W.reduce(function (b, w, i) { return w.score > W[b].score ? i : b; }, 0);
  const [selWeek, setSelWeek] = useStateHome(bestIdx);

  function pickMaand(m) {
    setMaand(m);
    setSelWeek(maandStart[m]);
  }

  return (
    <div>
      {/* HERO */}
      <section className="page hero">
        <div className="hero-grid">
          <div className="rise">
            <span className="eye">Slimme reisplanner voor gezinnen</span>
            <h1 style={{ marginTop: 14 }}>
              Ga weg wanneer het <span className="accent-word">rustig, betaalbaar en fijn</span> is.
            </h1>
            <p className="lead">
              Kies je bestemming en maand — wij tonen meteen de slimste weken om met de kinderen
              op pad te gaan. Drukte, prijs, weer en schoolvakanties, in één score.
            </p>
            <div className="picker">
              <span className="picker-lab">Bestemming</span>
              <div className="dest-chips">
                {heroLanden.map(function (c) {
                  return (
                    <a key={c.code} className={"dest-chip" + (dest === c.code ? " on" : "")}
                      href={"/landen/" + c.name.toLowerCase().replace(/ë/g, "e").replace(/[^a-z]+/g, "-")}
                      onClick={function (e) { e.preventDefault(); setDest(c.code); }}>
                      <span className="fl">{c.flag}</span>{c.name}
                    </a>
                  );
                })}
                <a className="dest-more" href="/landen"
                  onClick={function (e) { e.preventDefault(); goTo("land"); }}>Alle landen →</a>
              </div>
            </div>
            <div className="picker" style={{ marginTop: 14 }}>
              <span className="picker-lab">Maand</span>
              <div className="seg">
                {["mei", "jun", "jul", "aug", "sep"].map(function (m) {
                  return <button key={m} className={maand === m ? "on" : ""}
                    onClick={function () { pickMaand(m); }}>{m}</button>;
                })}
              </div>
            </div>
          </div>

          {/* HELD: Reisweek-radar */}
          <window.Radar weeks={W} selected={selWeek} onSelect={setSelWeek} />

          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <button className="btn lg" onClick={function () { goTo("planner"); }}>
              Open de planner
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
            </button>
            <button className="btn-ghost" style={{ padding: "16px 24px", fontSize: 16, borderRadius: 16 }}
              onClick={function () { goTo("kaart"); }}>Bekijk druktekaart</button>
          </div>
        </div>
      </section>

      {/* MINI DRUKTEKAART */}
      <section className="page section">
        <MiniMapBlock goTo={goTo} />
      </section>

      {/* BESTEMMINGEN */}
      <section className="page section">
        <div className="section-head">
          <div>
            <span className="eye">Bestemmingen</span>
            <h2 style={{ marginTop: 8 }}>Slim &amp; gezinsvriendelijk</h2>
          </div>
          <p>Gescoord op rust, reistijd, weer en hoe fijn het is met kinderen.</p>
        </div>
        <div className="dest-grid">
          {D.map(function (d) {
            const cls = d.slim >= 70 ? "is-rustig" : d.slim >= 45 ? "is-matig" : "is-druk";
            return (
              <article key={d.name} className="dest" onClick={function () { goTo("land"); }}>
                <div className="dest-img">
                  <img src={d.img} alt={d.name} loading="lazy" />
                  <div className={"dest-badge " + cls}>
                    <span className="bdot" style={{ background: "var(--c)" }}>{d.slim}</span>
                    <span className="blab">Slim-score</span>
                  </div>
                  <span className="dest-tag">{d.tag}</span>
                </div>
                <div className="dest-body">
                  <div className="nm">{d.name}</div>
                  <div className="ld">{d.land}</div>
                  <div className="row">
                    <span className="heart">♥</span> Gezinsscore {d.gezin}/100
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      {/* BESTE PERIODES — tips */}
      <section className="page section">
        <div className="section-head">
          <div>
            <span className="eye">Voor gezinnen</span>
            <h2 style={{ marginTop: 8 }}>Slim plannen, minder gedoe</h2>
          </div>
        </div>
        <div className="tipbar">
          <div className="tip"><span className="ic">🗓</span><div><h4>Reis net buiten de piek</h4><p>Een week voor of na de drukste week is vaak 30% rustiger én goedkoper.</p></div></div>
          <div className="tip"><span className="ic">⇄</span><div><h4>Check de overlap</h4><p>Als NL én Duitsland tegelijk vrij zijn, stijgen prijzen en drukte snel.</p></div></div>
          <div className="tip"><span className="ic">☀</span><div><h4>Weeg het weer mee</h4><p>September geeft vaak nog zomers weer met half zoveel toeristen.</p></div></div>
        </div>
      </section>

      {/* SEO-CONTENT: uitleg regio's, vergelijk, feestdagen, FAQ */}
      <window.HomeSecties goTo={goTo} />
    </div>
  );
}

window.Home = Home;
