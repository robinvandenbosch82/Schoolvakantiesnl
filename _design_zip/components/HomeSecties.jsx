// HomeSecties.jsx — SEO-content op de homepage: uitleg 3 regio's,
// landen vergelijken (NL vs. buurlanden), feestdagen 2026 en FAQ.
// Data uit landdata.js (window.LANDDATA) en data.js (window.SV).

const { useState: useStateHS } = React;

function RegioUitleg() {
  const nl = window.LANDDATA.nl;
  const tints = ["var(--lente, #11a07a)", "var(--accent)", "var(--herfst, #ff6a4d)"];
  return (
    <section className="page section">
      <div className="section-head">
        <div>
          <span className="eye">Hoe het werkt</span>
          <h2 style={{ marginTop: 8 }}>Zo werken de Nederlandse schoolvakanties</h2>
        </div>
        <p>Nederland verdeelt de zomervakantie over drie regio's, zodat niet heel het land tegelijk de weg op gaat.</p>
      </div>
      <p className="land-intro" style={{ marginBottom: 22 }}>{nl.intro}</p>
      <div className="regio-cols">
        {nl.regios.map(function (r, i) {
          return (
            <div key={r} className="regio-col" style={{ borderTop: "3px solid " + tints[i] }}>
              <span className="rc-tag" style={{ color: tints[i] }}>Regio {i + 1}</span>
              <h3>{r}-Nederland</h3>
              <p>{nl.regioUitleg[r]}</p>
            </div>
          );
        })}
      </div>
      <div className="reg-note">
        <strong>Verplicht vs. advies.</strong> De mei-, zomer- en kerstvakantie staan wettelijk vast voor het hele land.
        De voorjaars- en herfstvakantie zijn adviesdata — scholen mogen hiervan afwijken, dus check altijd de schoolgids.
      </div>
    </section>
  );
}

function LandenVergelijk({ goTo }) {
  const W = window.SV.weeks;
  const C = window.SV.countries;
  const focus = ["nl", "de", "be", "fr"].map(function (code) {
    return C.find(function (c) { return c.code === code; });
  }).filter(Boolean);

  // piekweek per land
  function piek(c) {
    let bi = 0;
    c.drukteByWeek.forEach(function (v, i) { if (v > c.drukteByWeek[bi]) bi = i; });
    return W[bi];
  }

  return (
    <section className="page section">
      <div className="section-head">
        <div>
          <span className="eye">Vergelijk</span>
          <h2 style={{ marginTop: 8 }}>Nederland vs. de buurlanden</h2>
        </div>
        <p>Reizen Duitsland, België en Frankrijk tegelijk met ons? Hoe meer overlap, hoe drukker en duurder.</p>
      </div>

      <div className="vergelijk card">
        <div className="vg-axis">
          <span className="vg-name-h"></span>
          <div className="vg-weeks">
            {W.map(function (w, i) {
              return <span key={w.wk} className={i % 3 === 0 ? "vw show" : "vw"}>{w.wk}</span>;
            })}
          </div>
        </div>
        {focus.map(function (c) {
          const pk = piek(c);
          return (
            <div key={c.code} className="vg-row">
              <span className="vg-name"><span className="fl">{c.flag}</span>{c.name}</span>
              <div className="vg-strip">
                {c.drukteByWeek.map(function (v, i) {
                  return <span key={i} className="vg-cell" title={"wk " + W[i].wk + " · drukte " + v}
                    style={{ background: window.drukteColor(v) }}></span>;
                })}
              </div>
              <span className="vg-peak">piek wk {pk.wk}<i>{pk.d1}</i></span>
            </div>
          );
        })}
        <div className="vg-legend">
          <span className="eye" style={{ margin: 0 }}>Drukte</span>
          <span className="vg-scale"><i style={{ background: window.drukteColor(20) }}></i><i style={{ background: window.drukteColor(50) }}></i><i style={{ background: window.drukteColor(75) }}></i><i style={{ background: window.drukteColor(95) }}></i></span>
          <span className="mono" style={{ fontSize: 11, color: "var(--ink-3)" }}>rustig → druk</span>
          <button className="btn-ghost vg-cta" onClick={function () { goTo("kaart"); }}>Open de Europese druktekaart →</button>
        </div>
      </div>
      <div className="reg-note">
        <strong>Het patroon.</strong> Eind juli en begin augustus pieken alle vier de landen samen — dat is de drukste en
        duurste periode. Begin juli en vanaf eind augustus lopen de vakanties uiteen: ideaal om de massa te ontwijken.
      </div>
    </section>
  );
}

function FeestdagenHome() {
  const nl = window.LANDDATA.nl;
  return (
    <section className="page section">
      <div className="section-head">
        <div>
          <span className="eye">Vrije dagen · 2026</span>
          <h2 style={{ marginTop: 8 }}>Officiële feestdagen 2026</h2>
        </div>
        <p>Plak een vrije dag aan het weekend en je hebt zonder verlof al een lang weekend weg.</p>
      </div>
      <div className="feest">
        {nl.feestdagen.map(function (f) {
          return (
            <div key={f.naam + f.datum} className="feest-row">
              <span className="feest-day">{f.dag}</span>
              <span className="feest-info"><span className="nm">{f.naam}</span><span className="dt">{f.datum}</span></span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function FaqHome() {
  const nl = window.LANDDATA.nl;
  return (
    <section className="page section">
      <div className="section-head">
        <div>
          <span className="eye">Veelgestelde vragen</span>
          <h2 style={{ marginTop: 8 }}>Vragen over de schoolvakanties</h2>
        </div>
      </div>
      <div className="faq">
        {nl.faq.map(function (q, i) {
          return (
            <details key={i} className="faq-item">
              <summary><span>{q.v}</span><span className="faq-ic" aria-hidden="true">+</span></summary>
              <p>{q.a}</p>
            </details>
          );
        })}
      </div>
    </section>
  );
}

function HomeSecties({ goTo }) {
  return (
    <React.Fragment>
      <RegioUitleg />
      <LandenVergelijk goTo={goTo} />
      <FeestdagenHome />
      <FaqHome />
    </React.Fragment>
  );
}

window.HomeSecties = HomeSecties;
