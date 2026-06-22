// Activities.jsx — Viator affiliate activiteiten: kaart + sectie (land) + blog-strip.

const { useState: useStateAct } = React;

function Stars({ rating }) {
  return (
    <span className="act-stars" title={rating + " / 5"}>
      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3 6.5 7 .8-5.2 4.8 1.5 6.9L12 17.8 5.7 21l1.5-6.9L2 9.3l7-.8z"/></svg>
      {rating.toFixed(1)}
    </span>
  );
}

function ActivityCard({ a }) {
  return (
    <a className="act-card" href={a.affiliateUrl} target="_blank" rel="nofollow sponsored noopener">
      <div className="act-img"><img src={a.img} alt={a.title} loading="lazy" />
        {a.themes.indexOf("familie") >= 0 && <span className="act-fam">👨‍👩‍👧 Gezin</span>}
      </div>
      <div className="act-body">
        <div className="act-meta"><Stars rating={a.rating} /><span className="act-rev">{a.reviews.toLocaleString("nl-NL")}</span></div>
        <h4>{a.title}</h4>
        <div className="act-foot">
          <span className="act-dur">⏱ {a.duration}</span>
          <span className="act-price">vanaf <strong>€{a.priceFrom}</strong></span>
        </div>
      </div>
    </a>
  );
}

// volledige sectie voor de landenpagina (thema-chips + grid)
window.ActivitiesSection = function ActivitiesSection({ countryCode, countryName, defaultTheme }) {
  const V = window.VIATOR;
  const [theme, setTheme] = useStateAct(defaultTheme || "familie");
  const items = V.getForCountry(countryCode, theme, 6);
  return (
    <section className="land-block">
      <div className="section-head">
        <div>
          <span className="eye">Dingen om te doen · powered by Viator</span>
          <h2 style={{ marginTop: 8 }}>Maak er een uitje van in {countryName}</h2>
        </div>
        <p>Gezinsvriendelijke activiteiten, afgestemd op je vakantieperiode.</p>
      </div>
      <div className="act-themes">
        {V.THEMES.map(function (t) {
          return (
            <button key={t.key} className={"act-chip" + (theme === t.key ? " on" : "")} onClick={function () { setTheme(t.key); }}>
              <span>{t.emoji}</span>{t.label}
            </button>
          );
        })}
      </div>
      <div className="act-grid">
        {items.map(function (a) { return <ActivityCard key={a.code} a={a} />; })}
      </div>
      <p className="act-disclosure">
        <span className="act-disc-ic">ⓘ</span> Deze sectie bevat affiliate-links naar Viator. Boek je via een link, dan ontvangen wij een kleine commissie — zonder extra kosten voor jou. Het helpt Schoolvakanties.nl gratis te houden.
      </p>
    </section>
  );
};

// compacte strip voor in een blogartikel
window.ActivitiesStrip = function ActivitiesStrip({ theme, title, countryCode }) {
  const items = countryCode
    ? window.VIATOR.getForCountry(countryCode, theme, 3)
    : window.VIATOR.getByTheme(theme || "familie", 3);
  return (
    <div className="act-strip">
      <div className="act-strip-head">
        <span className="eye">Dit kun je daar doen · Viator</span>
        <h3>{title || "Maak er een uitje van"}</h3>
      </div>
      <div className="act-grid three">
        {items.map(function (a) { return <ActivityCard key={a.code} a={a} />; })}
      </div>
      <p className="act-disclosure compact"><span className="act-disc-ic">ⓘ</span> Bevat affiliate-links — wij ontvangen een kleine commissie bij een boeking.</p>
    </div>
  );
};
