// Druktekalender.jsx — Interactieve heatmap voor vertrekdagen
// Editorial datavisualization, niet als typische dashboard

function Druktekalender() {
  // Genereer een heatmap: weken × dagen, met intensity
  // Hoogtepunten rond schoolvakanties
  const weken = 14; // 14 weken van mei tot half augustus
  const dagen = ['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo'];

  // intensities per cel — gestyleerd om realistische vertrekpatroon te tonen
  function getIntensity(w, d) {
    // Zomerstart pieken: week 6 (start zomer Noord), 8 (Midden), 10 (Zuid)
    let base = 0.1 + Math.random() * 0.15;
    if (d === 4) base += 0.25; // vrijdag
    if (d === 5) base += 0.4;  // zaterdag
    if (w === 6 && d === 5) base = 0.98;
    if (w === 8 && d === 5) base = 0.92;
    if (w === 10 && d === 5) base = 0.88;
    if (w === 7 && d === 5) base = 0.7;
    if (w === 6 && d === 4) base = 0.65;
    if (w === 0 && d === 5) base = 0.78; // meivakantie zaterdag
    if (w === 1 && d === 5) base = 0.4;
    return Math.min(1, base);
  }

  function intensityColor(v) {
    if (v < 0.2) return 'var(--papier-2)';
    if (v < 0.4) return 'oklch(86% 0.07 70)';
    if (v < 0.6) return 'oklch(80% 0.12 60)';
    if (v < 0.8) return 'oklch(72% 0.16 50)';
    return 'var(--zomer)';
  }

  const weekLabels = [
    '25 apr', '02 mei', '09 mei', '16 mei', '23 mei', '30 mei',
    '06 jun', '13 jun', '20 jun', '27 jun', '04 jul', '11 jul',
    '18 jul', '25 jul',
  ];

  // Side annotations
  const annotaties = [
    { weekIdx: 0, tekst: 'Meivakantie start', kleur: 'var(--lente)' },
    { weekIdx: 6, tekst: 'Zomer Noord — heaviest 24h v/d zomer', kleur: 'var(--zomer)' },
    { weekIdx: 8, tekst: 'Zomer Midden volgt', kleur: 'var(--zomer)' },
    { weekIdx: 10, tekst: 'Zomer Zuid — Frankrijk start', kleur: 'var(--herfst)' },
  ];

  return (
    <div className="sv-root" style={{ width: 1440, minHeight: 900, padding: 0 }}>
      {/* Header sub-nav */}
      <div style={{
        padding: '20px 56px', borderBottom: '1px solid var(--papier-line)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        fontSize: 13,
      }}>
        <div style={{ display: 'flex', gap: 4, alignItems: 'center', color: 'var(--inkt-3)' }}>
          <span>schoolvakanties.nl</span>
          <span> / </span>
          <span style={{ color: 'var(--inkt)' }}>Druktekalender</span>
          <span> / </span>
          <span style={{ color: 'var(--inkt)' }}>Zomer 2026</span>
        </div>
        <div className="font-mono" style={{ color: 'var(--inkt-3)' }}>updated · 14:32 NL</div>
      </div>

      {/* Page header — editorial */}
      <section style={{ padding: '64px 56px 48px', borderBottom: '1px solid var(--papier-line)', position: 'relative' }}>
        <div className="eyebrow" style={{ marginBottom: 18 }}>
          § Drukte-index · KNMI · ANWB · NS · zelflerend
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 60, alignItems: 'end' }}>
          <h1 style={{
            fontFamily: 'var(--display)', fontSize: 128, lineHeight: 0.85, letterSpacing: '-0.02em',
            fontWeight: 400,
          }}>
            Wanneer is<br />
            <span style={{ fontStyle: 'italic', color: 'var(--zomer-ink)' }}>iedereen</span> óók<br />
            onderweg?
          </h1>
          <div>
            <p style={{ fontSize: 16, color: 'var(--inkt-2)', lineHeight: 1.5, maxWidth: 380 }}>
              Een levende kaart van Nederlandse vertrekgolven — bouwen voort op 17 jaar data van ANWB, files, OV-spits en boekingsdata.
            </p>
            <div style={{ marginTop: 22, display: 'flex', gap: 10 }}>
              <span className="sticker" style={{ color: 'var(--diepblauw)' }}>
                heel NL
              </span>
              <span className="sticker" style={{ color: 'var(--inkt-3)' }}>
                A1 · A2 · A12 · A50
              </span>
              <span className="sticker" style={{ color: 'var(--zomer-ink)' }}>
                weken 18 – 30
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* HEATMAP */}
      <section style={{ padding: '56px 56px 32px', position: 'relative', background: 'var(--papier)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 56 }}>
          {/* Grid */}
          <div>
            <div style={{
              display: 'grid',
              gridTemplateColumns: `52px repeat(${weken}, 1fr)`,
              gap: 4,
              fontFamily: 'var(--mono)', fontSize: 10,
            }}>
              {/* Top labels: week-start dates */}
              <div />
              {weekLabels.map((w, i) => (
                <div key={i} style={{
                  textAlign: 'center', color: 'var(--inkt-3)', fontSize: 9,
                  padding: '0 0 6px', transform: 'rotate(-45deg)', transformOrigin: 'center', height: 30,
                }}>{w}</div>
              ))}
              {/* Rows */}
              {dagen.map((d, di) => (
                <React.Fragment key={d}>
                  <div style={{
                    color: 'var(--inkt-3)', fontSize: 11,
                    display: 'flex', alignItems: 'center',
                    fontWeight: [4, 5].includes(di) ? 700 : 400,
                  }}>{d}</div>
                  {Array.from({ length: weken }).map((_, wi) => {
                    const v = getIntensity(wi, di);
                    return (
                      <div key={wi} style={{
                        aspectRatio: '1', background: intensityColor(v), borderRadius: 2,
                        position: 'relative',
                      }}>
                        {v > 0.85 && (
                          <div style={{
                            position: 'absolute', inset: 2, border: '1.5px solid var(--inkt)', borderRadius: 2,
                            pointerEvents: 'none',
                          }} />
                        )}
                      </div>
                    );
                  })}
                </React.Fragment>
              ))}
            </div>

            {/* Legend */}
            <div style={{ marginTop: 28, display: 'flex', alignItems: 'center', gap: 14 }}>
              <span className="eyebrow">druk</span>
              <div style={{ display: 'flex', gap: 3 }}>
                {[0.1, 0.3, 0.5, 0.7, 0.95].map((v, i) => (
                  <div key={i} style={{
                    width: 26, height: 14, background: intensityColor(v), borderRadius: 2,
                  }} />
                ))}
              </div>
              <span className="font-mono" style={{ fontSize: 11, color: 'var(--inkt-3)' }}>
                rustig → extreem
              </span>
              <div style={{ marginLeft: 'auto', display: 'flex', gap: 14, fontSize: 12, color: 'var(--inkt-2)' }}>
                <span>● iconen markeren top-3 dagen</span>
              </div>
            </div>
          </div>

          {/* Side panel — gefocuste cel */}
          <aside style={{ padding: 28, background: 'var(--inkt)', color: 'var(--papier)', borderRadius: 4, alignSelf: 'start' }}>
            <div className="eyebrow" style={{ color: 'var(--zomer)' }}>geselecteerd</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 56, lineHeight: 0.9, marginTop: 10 }}>
              zaterdag<br />
              <span style={{ fontStyle: 'italic' }}>4 juli</span>
            </div>
            <div className="font-mono" style={{ fontSize: 11, color: 'oklch(75% 0.02 80)', marginTop: 12 }}>
              week 27 · zomer-noord start
            </div>

            {/* Index meter */}
            <div style={{ marginTop: 28 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <span style={{ fontSize: 12, color: 'oklch(75% 0.02 80)' }}>drukte-index</span>
                <span style={{ fontFamily: 'var(--display)', fontSize: 48, color: 'var(--zomer)' }}>9.4<span style={{ fontSize: 18, color: 'oklch(75% 0.02 80)' }}>/10</span></span>
              </div>
              <div style={{ height: 6, background: 'oklch(30% 0.04 250)', borderRadius: 3, marginTop: 8, overflow: 'hidden' }}>
                <div style={{ width: '94%', height: '100%', background: 'var(--zomer)' }} />
              </div>
            </div>

            {/* Detail-lijst */}
            <div style={{ marginTop: 28, borderTop: '1px solid oklch(28% 0.04 250)', paddingTop: 18 }}>
              {[
                ['Snelste vertrek', '04:30 – 06:00'],
                ['Slechtste vertrek', '09:30 – 12:00'],
                ['Hot spots', 'A12 · A2 · A50'],
                ['Verwachte file', '+ 213 km'],
                ['Alternatief', 'Vrijdag 3 juli, na 21:00'],
              ].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid oklch(28% 0.04 250)' }}>
                  <span style={{ fontSize: 12, color: 'oklch(75% 0.02 80)' }}>{k}</span>
                  <span style={{ fontSize: 13, fontWeight: 500 }}>{v}</span>
                </div>
              ))}
            </div>

            <button style={{
              width: '100%', marginTop: 22, padding: '12px', background: 'var(--zomer)',
              color: 'var(--zomer-ink)', border: 'none', borderRadius: 999,
              fontWeight: 600, fontSize: 13, cursor: 'pointer',
            }}>Voeg toe aan mijn jaar →</button>
          </aside>
        </div>
      </section>

      {/* Annotaties onderlangs heatmap — editorial */}
      <section style={{ padding: '32px 56px 80px', borderBottom: '1px solid var(--papier-line)' }}>
        <div className="eyebrow" style={{ marginBottom: 20 }}>§ leesgids bij bovenstaande</div>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 28,
        }}>
          {annotaties.map((a, i) => (
            <div key={i} style={{
              borderTop: `3px solid ${a.kleur}`, paddingTop: 14,
            }}>
              <div className="font-mono" style={{ fontSize: 10, color: 'var(--inkt-3)' }}>
                annotatie · 0{i + 1}
              </div>
              <div style={{ fontFamily: 'var(--display)', fontSize: 24, marginTop: 8, lineHeight: 1.1 }}>
                {a.tekst}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Snelste alternatieven — secundaire viz */}
      <section style={{ padding: '72px 56px', background: 'var(--papier-2)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 36 }}>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 56, lineHeight: 0.95, maxWidth: 700 }}>
            Wil je tóch op zaterdag? <span style={{ fontStyle: 'italic', color: 'var(--diepblauw)' }}>Dit zijn je vluchtroutes.</span>
          </h2>
          <a className="link-edit" style={{ fontSize: 14 }}>Volledige route-data →</a>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
          {[
            { route: 'A12 · oost', via: 'via Veenendaal', tijd: '+ 18 min', winst: '−2u file' },
            { route: 'A2 · zuid', via: 'via Den Bosch ringweg', tijd: '+ 24 min', winst: '−2u30 file' },
            { route: 'A50 · noord', via: 'Apeldoorn afslag 23', tijd: '+ 12 min', winst: '−1u15 file' },
          ].map((r, i) => (
            <div key={i} style={{
              padding: 28, background: 'var(--papier)', border: '1px solid var(--papier-line)',
              position: 'relative',
            }}>
              <div className="font-mono" style={{ fontSize: 10, color: 'var(--inkt-3)' }}>
                alternatief 0{i + 1}
              </div>
              <div style={{ fontFamily: 'var(--display)', fontSize: 44, marginTop: 8 }}>
                {r.route}
              </div>
              <div style={{ fontSize: 14, color: 'var(--inkt-2)', marginTop: 4 }}>{r.via}</div>
              <div style={{ display: 'flex', gap: 18, marginTop: 22 }}>
                <div>
                  <div className="eyebrow">extra rijtijd</div>
                  <div style={{ fontFamily: 'var(--display)', fontSize: 28 }}>{r.tijd}</div>
                </div>
                <div>
                  <div className="eyebrow">winst</div>
                  <div style={{ fontFamily: 'var(--display)', fontSize: 28, color: 'var(--diepblauw)' }}>{r.winst}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

window.Druktekalender = Druktekalender;
