// Homepage.jsx — De grote interactieve jaarkalender als hero
// Editorial layout met seizoensdynamiek, countdown, en kaartmodule

const SEIZOENEN = [
  { id: 'lente', label: 'Lente', maand: ['mrt', 'apr', 'mei'], var: '--lente', ink: '--lente-ink', icon: '✿' },
  { id: 'zomer', label: 'Zomer', maand: ['jun', 'jul', 'aug'], var: '--zomer', ink: '--zomer-ink', icon: '☼' },
  { id: 'herfst', label: 'Herfst', maand: ['sep', 'okt', 'nov'], var: '--herfst', ink: '--herfst-ink', icon: '✦' },
  { id: 'winter', label: 'Winter', maand: ['dec', 'jan', 'feb'], var: '--winter', ink: '--winter-ink', icon: '❋' },
];

const VAKANTIES_2026 = [
  { naam: 'Voorjaarsvakantie', start: 'wk 8', regios: 'Noord · Midden · Zuid', kleur: '--lente', dagen: 9, status: 'binnenkort' },
  { naam: 'Meivakantie', start: '25 apr', regios: 'Heel Nederland', kleur: '--lente', dagen: 9, status: 'gepland' },
  { naam: 'Zomervakantie', start: '4 jul', regios: 'Noord eerst', kleur: '--zomer', dagen: 42, status: 'hoogtepunt' },
  { naam: 'Herfstvakantie', start: '17 okt', regios: 'Per regio verschillend', kleur: '--herfst', dagen: 9, status: 'gepland' },
  { naam: 'Kerstvakantie', start: '19 dec', regios: 'Heel Nederland', kleur: '--winter', dagen: 16, status: 'gepland' },
];

function CountdownBlok() {
  // Statische "live" countdown — toont 47 dagen tot zomervakantie
  const dagen = 47, uren = 12, min = 31;
  return (
    <div style={{
      background: 'var(--inkt)', color: 'var(--papier)',
      padding: '36px 40px', borderRadius: 4,
      position: 'relative', overflow: 'hidden',
    }}>
      <div className="eyebrow" style={{ color: 'var(--zomer)', marginBottom: 18 }}>
        Live · Aftellen naar zomer
      </div>
      <div style={{
        display: 'flex', alignItems: 'baseline', gap: 14,
        fontFamily: 'var(--display)', fontSize: 96, lineHeight: 0.9,
      }}>
        <span>{dagen}</span>
        <span style={{ fontSize: 22, fontFamily: 'var(--mono)', color: 'var(--inkt-mute)', letterSpacing: '-0.02em' }}>
          dagen {uren}u {min}m
        </span>
      </div>
      <div style={{ marginTop: 22, fontSize: 14, color: 'oklch(75% 0.02 80)', maxWidth: 360, lineHeight: 1.45 }}>
        Tot de zomervakantie begint in regio Noord. 
        Tijd om de koffers uit zolder te halen.
      </div>
      {/* Subtiele zon-illustratie rechts */}
      <div style={{
        position: 'absolute', right: -60, top: -60, width: 220, height: 220,
        borderRadius: '50%', background: 'radial-gradient(circle at 30% 30%, var(--zomer), transparent 65%)',
        opacity: 0.55,
      }} />
    </div>
  );
}

function JaarRing() {
  // Een ringvormige jaarkalender — 12 segmenten met vakantieperiodes
  const r = 165, cx = 200, cy = 200;
  const maanden = ['JAN', 'FEB', 'MRT', 'APR', 'MEI', 'JUN', 'JUL', 'AUG', 'SEP', 'OKT', 'NOV', 'DEC'];
  // Vakantieperiodes als segmenten (startMaand, eindMaand fractie, kleur)
  const periodes = [
    { start: 1.5, end: 2.2, kleur: 'var(--lente)' },    // voorjaar
    { start: 4.0, end: 4.4, kleur: 'var(--lente)' },    // mei
    { start: 6.2, end: 7.5, kleur: 'var(--zomer)' },    // zomer
    { start: 9.7, end: 10.0, kleur: 'var(--herfst)' },  // herfst
    { start: 11.7, end: 12.5, kleur: 'var(--winter)' },// kerst
  ];
  const arc = (a0, a1, rad) => {
    const x0 = cx + rad * Math.cos((a0 - 90) * Math.PI / 180);
    const y0 = cy + rad * Math.sin((a0 - 90) * Math.PI / 180);
    const x1 = cx + rad * Math.cos((a1 - 90) * Math.PI / 180);
    const y1 = cy + rad * Math.sin((a1 - 90) * Math.PI / 180);
    const large = a1 - a0 > 180 ? 1 : 0;
    return `M ${x0} ${y0} A ${rad} ${rad} 0 ${large} 1 ${x1} ${y1}`;
  };

  return (
    <svg viewBox="0 0 400 400" style={{ width: '100%', height: 'auto', display: 'block' }}>
      {/* Vakantieperiode-arcs */}
      {periodes.map((p, i) => {
        const a0 = (p.start / 12) * 360;
        const a1 = (p.end / 12) * 360;
        return (
          <path key={i} d={arc(a0, a1, r)} stroke={p.kleur} strokeWidth="22" fill="none" strokeLinecap="butt" />
        );
      })}
      {/* Maand-tick labels */}
      {maanden.map((m, i) => {
        const a = ((i + 0.5) / 12) * 360 - 90;
        const x = cx + (r + 28) * Math.cos(a * Math.PI / 180);
        const y = cy + (r + 28) * Math.sin(a * Math.PI / 180);
        const a2 = ((i + 0.5) / 12) * 360 - 90;
        const xt = cx + (r - 26) * Math.cos(a2 * Math.PI / 180);
        const yt = cy + (r - 26) * Math.sin(a2 * Math.PI / 180);
        return (
          <g key={m}>
            <text x={x} y={y} fontSize="10" fontFamily="var(--mono)" fill="var(--inkt-3)"
              textAnchor="middle" dominantBaseline="middle" letterSpacing="1">{m}</text>
            <line
              x1={cx + (r - 11) * Math.cos(a * Math.PI / 180)}
              y1={cy + (r - 11) * Math.sin(a * Math.PI / 180)}
              x2={cx + (r + 11) * Math.cos(a * Math.PI / 180)}
              y2={cy + (r + 11) * Math.sin(a * Math.PI / 180)}
              stroke="var(--papier-line)" strokeWidth="1"
            />
          </g>
        );
      })}
      {/* "Vandaag" marker - 23 mei = ~5.7/12 */}
      {(() => {
        const a = ((5.7) / 12) * 360 - 90;
        const x = cx + r * Math.cos(a * Math.PI / 180);
        const y = cy + r * Math.sin(a * Math.PI / 180);
        return (
          <g>
            <line x1={cx} y1={cy} x2={x} y2={y} stroke="var(--inkt)" strokeWidth="1" strokeDasharray="3 3" />
            <circle cx={x} cy={y} r="7" fill="var(--inkt)" />
            <circle cx={x} cy={y} r="3" fill="var(--papier)" />
          </g>
        );
      })()}
      {/* Centrum */}
      <text x={cx} y={cy - 20} fontSize="11" fontFamily="var(--mono)" fill="var(--inkt-3)"
        textAnchor="middle" letterSpacing="2">SCHOOLJAAR</text>
      <text x={cx} y={cy + 22} fontSize="72" fontFamily="var(--display)" fill="var(--inkt)"
        textAnchor="middle" dominantBaseline="middle">2026</text>
      <text x={cx} y={cy + 56} fontSize="10" fontFamily="var(--mono)" fill="var(--inkt-3)"
        textAnchor="middle" letterSpacing="2">→ vandaag · 23 mei</text>
    </svg>
  );
}

function VakantieRij({ v, i }) {
  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '32px 1fr auto auto auto', alignItems: 'center',
      gap: 18, padding: '20px 4px', borderTop: '1px solid var(--papier-line)',
      fontFamily: 'var(--grotesk)',
    }}>
      <div className="font-mono" style={{ fontSize: 11, color: 'var(--inkt-3)' }}>
        0{i + 1}
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 14 }}>
        <span style={{
          width: 10, height: 10, borderRadius: '50%', background: `var(${v.kleur})`,
          display: 'inline-block',
        }} />
        <span style={{ fontFamily: 'var(--display)', fontSize: 30 }}>{v.naam}</span>
        <span className="font-mono" style={{ fontSize: 11, color: 'var(--inkt-3)' }}>
          {v.dagen} dagen
        </span>
      </div>
      <span style={{ fontSize: 13, color: 'var(--inkt-2)' }}>{v.regios}</span>
      <span className="font-mono" style={{ fontSize: 12, color: 'var(--inkt-2)' }}>{v.start}</span>
      <a href="#" className="link-edit" style={{ color: 'var(--inkt)', fontSize: 13, fontWeight: 500 }}>
        bekijk →
      </a>
    </div>
  );
}

function Inspiratiekaart({ kleur, ink, label, titel, plaats, sticker, rot = 0 }) {
  return (
    <div style={{
      background: `var(${kleur})`,
      color: `var(${ink})`,
      borderRadius: 4,
      padding: 22,
      minHeight: 280,
      position: 'relative',
      display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
      transform: `rotate(${rot}deg)`,
      overflow: 'hidden',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
        <span className="font-mono" style={{ fontSize: 10, letterSpacing: 1.5, opacity: 0.7 }}>
          {label}
        </span>
        {sticker && (
          <span className="sticker" style={{ background: 'rgba(255,255,255,0.4)' }}>
            {sticker}
          </span>
        )}
      </div>
      {/* Placeholder image area */}
      <div style={{
        position: 'absolute', inset: '50px 22px 90px',
        background: `repeating-linear-gradient(45deg, transparent 0 8px, rgba(0,0,0,0.06) 8px 9px)`,
        border: `1px dashed currentColor`, opacity: 0.5, borderRadius: 2,
      }} />
      <div>
        <div style={{ fontFamily: 'var(--display)', fontSize: 36, lineHeight: 0.95, fontStyle: 'italic' }}>
          {titel}
        </div>
        <div className="font-mono" style={{ fontSize: 11, marginTop: 6, opacity: 0.8 }}>
          {plaats}
        </div>
      </div>
    </div>
  );
}

function Nav() {
  const items = ['Vakanties', 'Bestemmingen', 'Drukte', 'Planner', 'Kennisbank'];
  return (
    <header style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '24px 56px', borderBottom: '1px solid var(--papier-line)',
      position: 'relative', zIndex: 2,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {/* Logo: tekst + handgemaakte glyph */}
        <svg width="36" height="36" viewBox="0 0 40 40">
          <circle cx="20" cy="20" r="18" fill="var(--inkt)" />
          <path d="M 13 22 Q 20 12 27 22" stroke="var(--zomer)" strokeWidth="2.5" fill="none" strokeLinecap="round" />
          <circle cx="28" cy="13" r="3" fill="var(--zomer)" />
        </svg>
        <div>
          <div style={{ fontFamily: 'var(--display)', fontSize: 22, lineHeight: 1, letterSpacing: '-0.01em' }}>
            schoolvakanties<span style={{ color: 'var(--zomer)', fontStyle: 'italic' }}>.nl</span>
          </div>
        </div>
      </div>
      <nav style={{ display: 'flex', gap: 32 }}>
        {items.map(x => (
          <a key={x} href="#" style={{
            fontSize: 14, color: 'var(--inkt-2)', textDecoration: 'none', fontWeight: 500,
          }}>{x}</a>
        ))}
      </nav>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <button style={{
          background: 'transparent', border: 'none', fontSize: 13, color: 'var(--inkt-3)', cursor: 'pointer',
        }}>regio: <b style={{ color: 'var(--inkt)' }}>Midden</b> ⌄</button>
        <button style={{
          background: 'var(--inkt)', color: 'var(--papier)', border: 'none',
          padding: '10px 18px', borderRadius: 999, fontSize: 13, fontWeight: 600, cursor: 'pointer',
        }}>Bewaar mijn jaar</button>
      </div>
    </header>
  );
}

function Homepage() {
  return (
    <div className="sv-root" style={{ width: 1440, position: 'relative' }}>
      <Nav />

      {/* HERO — editorial layout, asymmetric */}
      <section style={{
        display: 'grid', gridTemplateColumns: '1.15fr 1fr', gap: 0,
        borderBottom: '1px solid var(--papier-line)',
        position: 'relative',
      }}>
        <div style={{ padding: '72px 56px 64px', position: 'relative' }}>
          <div className="eyebrow" style={{ marginBottom: 28 }}>
            Editie · Voorjaar 2026 · No. 047
          </div>
          <h1 style={{
            fontFamily: 'var(--display)', fontSize: 144, lineHeight: 0.88,
            letterSpacing: '-0.02em', fontWeight: 400, color: 'var(--inkt)',
            maxWidth: 720,
          }}>
            Een heel <span style={{ fontStyle: 'italic', color: 'var(--zomer-ink)' }}>jaar</span><br />
            aan vrije <br />
            dagen, <span style={{ fontStyle: 'italic' }}>uitgestald.</span>
          </h1>
          <p style={{
            marginTop: 32, fontSize: 18, lineHeight: 1.5, maxWidth: 480, color: 'var(--inkt-2)',
          }}>
            Schoolvakanties.nl is een levende almanak — geen tabel. Plan, anticipeer, en bewaar je gezinsjaar in één plek waar je daadwerkelijk graag terugkomt.
          </p>
          <div style={{ marginTop: 36, display: 'flex', gap: 12, alignItems: 'center' }}>
            <button style={{
              background: 'var(--zomer)', color: 'var(--zomer-ink)', border: 'none',
              padding: '14px 22px', borderRadius: 999, fontWeight: 600, fontSize: 14, cursor: 'pointer',
            }}>Open mijn jaar →</button>
            <button style={{
              background: 'transparent', border: '1px solid var(--papier-line)',
              padding: '14px 22px', borderRadius: 999, fontWeight: 500, fontSize: 14, color: 'var(--inkt)', cursor: 'pointer',
            }}>Druktekalender</button>
          </div>

          {/* Decoratieve handgeschreven note */}
          <div style={{
            position: 'absolute', bottom: 60, left: 56, display: 'flex', gap: 10, alignItems: 'center',
          }}>
            <svg width="40" height="20" viewBox="0 0 40 20">
              <path d="M2 10 Q 15 -5 38 12" stroke="var(--inkt-3)" strokeWidth="1.2" fill="none" />
              <polyline points="32,8 38,12 33,18" stroke="var(--inkt-3)" strokeWidth="1.2" fill="none" />
            </svg>
            <span style={{ fontFamily: 'var(--display)', fontStyle: 'italic', color: 'var(--inkt-3)', fontSize: 16 }}>
              start hier
            </span>
          </div>
        </div>

        {/* Jaar-ring */}
        <div style={{
          background: 'var(--papier-2)', padding: '56px 48px', borderLeft: '1px solid var(--papier-line)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          position: 'relative',
        }}>
          <JaarRing />
          {/* Floating label-stickers rond de ring */}
          <div className="sticker" style={{
            position: 'absolute', top: 80, right: 60, background: 'var(--papier)',
            color: 'var(--zomer-ink)', transform: 'rotate(8deg)',
          }}>
            <span style={{ fontSize: 14 }}>☼</span> nog 47 dagen
          </div>
          <div className="sticker" style={{
            position: 'absolute', bottom: 110, left: 30, background: 'var(--papier)',
            color: 'var(--lente-ink)', transform: 'rotate(-6deg)',
          }}>
            ✿ meivakantie · over 2 dagen
          </div>
        </div>
      </section>

      {/* Vakantie-tabel — editorial lijst, geen cards */}
      <section style={{ padding: '80px 56px 60px', borderBottom: '1px solid var(--papier-line)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 32 }}>
          <div>
            <div className="eyebrow">§ 01 — De agenda</div>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 64, marginTop: 12 }}>
              Vijf hoofdstukken<span style={{ fontStyle: 'italic', color: 'var(--zomer-ink)' }}> van vrij.</span>
            </h2>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            {['Alle', 'Mijn regio', 'Nationaal'].map((x, i) => (
              <button key={x} style={{
                padding: '8px 16px', borderRadius: 999, border: '1px solid var(--papier-line)',
                background: i === 0 ? 'var(--inkt)' : 'transparent',
                color: i === 0 ? 'var(--papier)' : 'var(--inkt-2)',
                fontSize: 13, cursor: 'pointer',
              }}>{x}</button>
            ))}
          </div>
        </div>
        <div>
          {VAKANTIES_2026.map((v, i) => <VakantieRij key={v.naam} v={v} i={i} />)}
          <div style={{ borderTop: '1px solid var(--papier-line)' }} />
        </div>
      </section>

      {/* Drie-koloms: countdown + drukte + weer */}
      <section style={{
        padding: '64px 56px', display: 'grid', gridTemplateColumns: '1.2fr 1fr 1fr', gap: 24,
        borderBottom: '1px solid var(--papier-line)', background: 'var(--papier-2)',
      }}>
        <CountdownBlok />
        <div style={{ padding: 28, background: 'var(--papier)', borderRadius: 4 }}>
          <div className="eyebrow" style={{ marginBottom: 16 }}>§ Drukte-index · A12</div>
          <div style={{ fontFamily: 'var(--display)', fontSize: 64, lineHeight: 1 }}>
            extreem<span style={{ fontStyle: 'italic', color: 'var(--zomer-ink)' }}>.</span>
          </div>
          {/* Mini drukte-graph */}
          <svg viewBox="0 0 200 60" style={{ width: '100%', marginTop: 18 }}>
            {[14, 22, 35, 48, 62, 84, 95, 78, 56, 38, 24, 18].map((h, i) => (
              <rect key={i} x={i * 17} y={60 - h * 0.55} width="11" height={h * 0.55}
                fill={i === 6 ? 'var(--zomer)' : 'var(--papier-3)'} />
            ))}
          </svg>
          <p style={{ fontSize: 13, color: 'var(--inkt-2)', marginTop: 14, lineHeight: 1.4 }}>
            Vrijdag 4 juli — eerste zaterdag zomer Noord. Vertrek vóór 06:00 of na 14:00.
          </p>
        </div>
        <div style={{ padding: 28, background: 'var(--papier)', borderRadius: 4 }}>
          <div className="eyebrow" style={{ marginBottom: 16 }}>§ Vooruitzicht · meivakantie</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
            <span style={{ fontFamily: 'var(--display)', fontSize: 84, lineHeight: 0.9 }}>22°</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--inkt-3)' }}>↑ 24 / ↓ 11</span>
          </div>
          <div style={{ display: 'flex', gap: 6, marginTop: 18 }}>
            {['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo'].map((d, i) => (
              <div key={d} style={{ flex: 1, textAlign: 'center' }}>
                <div style={{ fontSize: 10, color: 'var(--inkt-3)', fontFamily: 'var(--mono)' }}>{d}</div>
                <div style={{
                  width: 22, height: 22, borderRadius: '50%', margin: '6px auto 0',
                  background: [0, 1, 5].includes(i) ? 'var(--zomer)' : 'var(--papier-3)',
                }} />
                <div style={{ fontSize: 11, marginTop: 4 }}>{[22, 24, 19, 18, 20, 25, 23][i]}°</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Inspiratie — moodboard, gerouleerd */}
      <section style={{ padding: '96px 56px 80px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: 48 }}>
          <div>
            <div className="eyebrow">§ 02 — Inspiratie</div>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 72, marginTop: 12, letterSpacing: '-0.02em', maxWidth: 720 }}>
              Waar gaan<br /> Nederlanders <span style={{ fontStyle: 'italic', color: 'var(--diepblauw)' }}>deze meivakantie</span>?
            </h2>
          </div>
          <a href="#" className="link-edit" style={{ color: 'var(--inkt)', fontSize: 14 }}>
            Alle bestemmingen →
          </a>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18 }}>
          <Inspiratiekaart kleur="--zomer" ink="--zomer-ink" label="01 / IT" titel="Toscane" plaats="Florence → Siena" sticker="trending" rot={-1} />
          <Inspiratiekaart kleur="--winter" ink="--winter-ink" label="02 / AT" titel="Sankt Anton" plaats="laatste sneeuw" rot={1} />
          <Inspiratiekaart kleur="--lente" ink="--lente-ink" label="03 / NL" titel="Waddeneilanden" plaats="Texel · Vlieland" sticker="dichtbij" rot={-0.6} />
          <Inspiratiekaart kleur="--herfst" ink="--herfst-ink" label="04 / FR" titel="Provence" plaats="Avignon → Arles" rot={0.8} />
        </div>
      </section>

      {/* Toolbalk — SEO ingangen */}
      <section style={{
        padding: '60px 56px', background: 'var(--inkt)', color: 'var(--papier)',
        position: 'relative', overflow: 'hidden',
      }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 64, alignItems: 'start' }}>
          <div>
            <div className="eyebrow" style={{ color: 'oklch(70% 0.04 80)' }}>§ 03 — Vind alles</div>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 56, marginTop: 12, lineHeight: 0.95 }}>
              Een ingang voor <span style={{ fontStyle: 'italic', color: 'var(--zomer)' }}>elke</span> vraag.
            </h2>
            <p style={{ fontSize: 14, color: 'oklch(75% 0.02 80)', marginTop: 22, maxWidth: 320, lineHeight: 1.5 }}>
              Per vakantie, per regio, per land, per type. We koppelen 12.400 pagina&apos;s zonder ooit een filter dropdown te gebruiken.
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px 56px' }}>
            {[
              { kop: 'Per vakantie', items: ['Meivakantie 2026', 'Zomervakantie Noord', 'Herfstvakantie Zuid', 'Kerstvakantie', '+ 21 meer'] },
              { kop: 'Per bestemming', items: ['Camping Frankrijk', 'Wintersport Oostenrijk', 'Citytrip Berlijn', 'Waddeneilanden', '+ 380 meer'] },
              { kop: 'Per onderwerp', items: ['Druktekalender A2/A12', 'Roadtrip-routes', 'Vakantiehuizen', 'Weer & zonuren', '+ 64 onderwerpen'] },
            ].map(col => (
              <div key={col.kop}>
                <div className="eyebrow" style={{ color: 'var(--zomer)', marginBottom: 14 }}>{col.kop}</div>
                {col.items.map(it => (
                  <a key={it} href="#" style={{
                    display: 'block', color: 'var(--papier)', textDecoration: 'none',
                    padding: '8px 0', borderBottom: '1px solid oklch(28% 0.04 250)',
                    fontSize: 14, fontWeight: 500,
                  }}>{it}</a>
                ))}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ padding: '48px 56px', background: 'var(--inkt)', color: 'oklch(70% 0.02 80)', fontSize: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid oklch(28% 0.04 250)', paddingTop: 30 }}>
          <span>Schoolvakanties.nl — sinds 2009, voor 1 op 3 Nederlandse gezinnen</span>
          <span className="font-mono">v.026.05.23 · made in Utrecht</span>
        </div>
      </footer>
    </div>
  );
}

window.Homepage = Homepage;
