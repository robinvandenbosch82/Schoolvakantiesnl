// OverOns.jsx — E-E-A-T over-ons-pagina: missie, redactie/experts, werkwijze, bronnen

function OverOns({ goTo }) {
  const T = window.TEAM;
  const Avatar = window.EEAT.Avatar;

  const werkwijze = [
    { n: "01", t: "Officiële bron eerst", d: "Vakantie- en feestdagdata halen we rechtstreeks uit Rijksoverheid.nl, de OpenHolidays-API en de Duitse KMK — nooit uit overgenomen lijstjes." },
    { n: "02", t: "Handmatig geverifieerd", d: "Elke datum wordt door de redactie tegen de officiële kalender gelegd voordat hij live gaat. Adviesweken markeren we duidelijk als advies." },
    { n: "03", t: "Drukte berekend, niet gegokt", d: "De Slim-score combineert vakantie-overlap, verkeers- en boekingspatronen tot één getal — transparant en jaarlijks herijkt." },
    { n: "04", t: "Continu bijgewerkt", d: "Zodra een overheid data wijzigt, passen we het aan. Onderaan elke pagina zie je wie controleerde en wanneer." },
  ];

  return (
    <div className="page overons rise">
      {/* HERO */}
      <header className="oo-hero">
        <span className="eye">Over ons</span>
        <h1>De mensen achter Schoolvakanties.nl</h1>
        <p className="lead">Sinds 2009 helpen we Nederlandse gezinnen om slim weg te gaan. Geen overgenomen lijstjes, maar officiële data, een vaste redactie en een drukte-model dat we zelf bouwden en onderhouden.</p>
        <div className="oo-trust">
          <div className="oo-trust-it"><strong>Sinds 2009</strong><span>actief &amp; onafhankelijk</span></div>
          <div className="oo-trust-it"><strong>1 op 3</strong><span>NL gezinnen gebruikt ons</span></div>
          <div className="oo-trust-it"><strong>Officiële bronnen</strong><span>Rijksoverheid · OpenHolidays · KMK</span></div>
          <div className="oo-trust-it"><strong>Handmatig</strong><span>gecontroleerd door de redactie</span></div>
        </div>
      </header>

      {/* MISSIE */}
      <section className="land-block oo-missie">
        <div className="section-head"><div><span className="eye">Onze missie</span><h2 style={{ marginTop: 8 }}>Vakantieplannen zonder gedoe — en zonder verrassingen</h2></div></div>
        <p className="oo-body">Schoolvakanties verschillen per regio, per land en per jaar. Dat maakt plannen lastig en drukte onvoorspelbaar. Wij brengen alle officiële data samen op één plek en vertalen die naar concreet advies: wanneer is het rustig, waar is het betaalbaar, en welke week past bij jouw gezin. Onafhankelijk, transparant en altijd herleidbaar naar de bron.</p>
      </section>

      {/* REDACTIE / EXPERTS */}
      <section className="land-block">
        <div className="section-head"><div><span className="eye">Onze redactie</span><h2 style={{ marginTop: 8 }}>Wie schrijft en controleert</h2></div><p>Een vast team met aantoonbare ervaring in reizen, data en onderwijs.</p></div>
        <div className="oo-team">
          {T.experts.map(function (e) {
            return (
              <article key={e.id} className="oo-expert">
                <div className="oo-expert-head">
                  <Avatar p={e} size={60} />
                  <div>
                    <h3>{e.naam}</h3>
                    <span className="oo-expert-rol">{e.rol}</span>
                  </div>
                </div>
                <p className="oo-expert-bio">{e.bio}</p>
                <ul className="eeat-cred">
                  {e.cred.map(function (c, i) { return <li key={i}>{c}</li>; })}
                </ul>
              </article>
            );
          })}
        </div>
      </section>

      {/* WERKWIJZE */}
      <section className="land-block">
        <div className="section-head"><div><span className="eye">Werkwijze</span><h2 style={{ marginTop: 8 }}>Hoe we onze data controleren</h2></div></div>
        <div className="oo-werk">
          {werkwijze.map(function (w) {
            return (
              <div key={w.n} className="oo-werk-step">
                <span className="oo-werk-n mono">{w.n}</span>
                <h4>{w.t}</h4>
                <p>{w.d}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* BRONNEN + CONTACT */}
      <section className="land-block oo-onder">
        <div className="oo-bronnen">
          <span className="eye">Onze bronnen</span>
          <ul>
            {T.bronnen.map(function (b, i) {
              return <li key={i}><strong>{b.naam}</strong><span>{b.wat}</span></li>;
            })}
          </ul>
        </div>
        <div className="oo-contact">
          <span className="eye">Contact &amp; correcties</span>
          <p>Klopt er iets niet of mist er een datum? We horen het graag — correcties verwerken we doorgaans binnen een werkdag.</p>
          <a className="btn" href="mailto:redactie@schoolvakanties.nl">redactie@schoolvakanties.nl</a>
        </div>
      </section>
    </div>
  );
}

window.OverOns = OverOns;
