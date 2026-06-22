// BestemmingV2.jsx — Bestemmingspagina als zine-blad
// Tickets, stempels, ruled paper, postzegels

function BestemmingV2() {
  return (
    <div className="v2-root" style={{ width: 1440 }}>
      {/* Sub-header met breadcrumb als ticket-stub */}
      <div style={{
        padding: '20px 48px', borderBottom: '4px solid var(--inkt)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        background: 'var(--inkt)', color: 'var(--papier)',
      }}>
        <div className="eye-v2">
          schoolvakanties.nl / BESTEMMINGEN / ITALIË / <span style={{ color: 'var(--geel)' }}>TOSCANE</span>
        </div>
        <div style={{ display: 'flex', gap: 14 }} className="eye-v2">
          <span>↧ BEWAAR</span>
          <span>↩ DEEL</span>
          <span>⎙ PRINT</span>
        </div>
      </div>

      {/* HERO — ticket stub */}
      <section style={{
        padding: '56px 48px 72px', background: 'var(--papier)',
        position: 'relative', borderBottom: '4px solid var(--inkt)',
      }}>
        {/* Ticket-strook */}
        <div style={{
          position: 'absolute', top: 36, left: 48, right: 48,
          display: 'flex', alignItems: 'center', gap: 14,
          fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, letterSpacing: 0.1,
          color: 'var(--tomaat)',
        }}>
          <span>● BESTEMMING N° 124</span>
          <span style={{ flex: 1, borderTop: '2px dashed var(--inkt-soft)' }} />
          <span>MEI · 9 DAGEN · GEZIN A+</span>
        </div>

        <div style={{ marginTop: 32, display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 40, alignItems: 'flex-end' }}>
          <div>
            <h1 style={{
              fontFamily: 'var(--display)', fontSize: 280, lineHeight: 0.82,
              letterSpacing: '-0.04em', color: 'var(--inkt)',
            }}>
              Tos<span style={{ color: 'var(--tomaat)' }}>ca</span>ne.
            </h1>
            <div style={{
              fontFamily: 'var(--hand)', fontSize: 38, color: 'var(--zee)',
              transform: 'rotate(-1deg) translateX(20px)', marginTop: 8,
            }}>
              wel doen, niet wachten op augustus
            </div>
          </div>
          <div style={{ position: 'relative', minHeight: 360 }}>
            {/* Stempelbox: feiten */}
            <div style={{
              background: 'var(--geel)', border: '2px solid var(--inkt)',
              boxShadow: '8px 8px 0 var(--inkt)', padding: 24,
              transform: 'rotate(2deg)',
            }}>
              <div className="eye-v2" style={{ color: 'var(--tomaat)' }}>VAKANTIEKAART</div>
              <div style={{ marginTop: 14, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px 24px' }}>
                {[
                  ['ZON', '9.2u/dag'],
                  ['TEMP', '23°'],
                  ['DRUKTE', '3.7/5'],
                  ['VLUCHT', '2u20'],
                  ['BUDGET', '€840'],
                  ['KIND', 'A+'],
                ].map(([k, v]) => (
                  <div key={k}>
                    <div className="eye-v2" style={{ fontSize: 9, opacity: 0.6 }}>{k}</div>
                    <div style={{ fontFamily: 'var(--display)', fontSize: 30, lineHeight: 1 }}>{v}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Stempel */}
            <div className="stempel" style={{
              position: 'absolute', bottom: -28, left: -28, color: 'var(--tomaat)',
              transform: 'rotate(-14deg)', background: 'var(--papier)',
            }}>
              <span className="stempel-text">GOEDGEKEURD</span>
              <span>RED. 2026</span>
            </div>
          </div>
        </div>
      </section>

      {/* Twee koloms verhaal op gelijnd papier */}
      <section className="ruled" style={{
        padding: '80px 48px', borderBottom: '4px solid var(--inkt)',
      }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 56, maxWidth: 1140, margin: '0 auto' }}>
          <div>
            <div className="eye-v2" style={{ color: 'var(--tomaat)', marginBottom: 18 }}>§ 01 · HET VERHAAL</div>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 56, lineHeight: 0.95 }}>
              Met twee kinderen door <span className="marker">negen Toscaanse dagen</span>.
            </h2>
            <div style={{ marginTop: 28, fontSize: 17, lineHeight: 1.65, color: 'var(--inkt-soft)' }}>
              <p style={{ marginBottom: 16 }}>
                <span style={{ fontFamily: 'var(--display)', fontSize: 72, lineHeight: 0.85, float: 'left', marginRight: 14, marginTop: 4, color: 'var(--inkt)' }}>T</span>
                oscane in meivakantie is een gok die je wint. De lavendel is nog niet paars, de zonnebloemen slapen nog onder de grond, en de Florentijnen kijken je niet aan alsof je een onbeschofte zomerinval bent.
              </p>
              <p>
                We gingen met twee kinderen en een auto die te groot was. Wat we leerden: kies één hub, niet drie. Een agriturismo tussen Siena en Pienza — cipressen, landweggetjes — als basis voor dagtochten.
              </p>
            </div>
          </div>

          <div>
            {/* Pull quote als ticket */}
            <div style={{
              background: 'var(--tomaat)', color: 'var(--papier)', padding: 32,
              border: '2px solid var(--inkt)', boxShadow: '8px 8px 0 var(--inkt)',
              fontFamily: 'var(--display)', fontSize: 30, lineHeight: 1.15,
              position: 'relative', transform: 'rotate(-1deg)',
            }}>
              <div className="tape" style={{ top: -12, right: 30, background: 'oklch(89% 0.06 95 / 0.85)' }} />
              &ldquo;De winst is niet dat het mooier is in mei. De winst is dat het er <span style={{ background: 'var(--geel)', color: 'var(--inkt)', padding: '0 6px' }}>nog gewoon ís</span> — vóór 14 miljoen anderen dezelfde gedachte hebben.&rdquo;
              <div style={{ marginTop: 18, fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700, letterSpacing: 0.15, color: 'var(--geel)' }}>
                — REDACTIE · MEI 2026
              </div>
            </div>

            {/* Onderaan: stickers */}
            <div style={{
              marginTop: 36, display: 'flex', flexWrap: 'wrap', gap: 10,
            }}>
              {['agriturismo', 'kindvriendelijk', 'rijden ipv vliegen', 'geen Uffizi met 7-jarige', 'pasta', 'gelato'].map((s, i) => (
                <span key={s} style={{
                  padding: '6px 12px', background: i % 2 ? 'var(--zee)' : 'var(--olijf)',
                  color: i % 2 ? 'var(--papier)' : 'var(--inkt)',
                  border: '2px solid var(--inkt)', boxShadow: '3px 3px 0 var(--inkt)',
                  fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700,
                  transform: `rotate(${(i % 2 ? 1 : -1) * (1 + i * 0.4)}deg)`,
                }}>{s}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Dag-tijdlijn als bonnetjes-strook */}
      <section style={{
        padding: '80px 48px', background: 'var(--geel)', borderBottom: '4px solid var(--inkt)',
        position: 'relative', overflow: 'hidden',
      }}>
        <div className="eye-v2" style={{ color: 'var(--tomaat)' }}>§ 02 · NEGEN DAGEN · ÉÉN LIJN</div>
        <h2 style={{ fontFamily: 'var(--display)', fontSize: 88, lineHeight: 0.88, marginTop: 14, maxWidth: 1000 }}>
          De <span className="marker-tomaat">route</span> als bonnetjes-strook.
        </h2>

        <div style={{
          marginTop: 48, display: 'flex', gap: 14, overflowX: 'visible', flexWrap: 'wrap',
        }}>
          {[
            { d: 'DAG 01', t: 'Pisa → Lucca', sub: 'KL1607 06:25', km: '78 km', kleur: 'var(--papier)' },
            { d: 'DAG 02', t: 'Lucca op fiets', sub: 'stadsmuren', km: '8 km', kleur: 'var(--olijf)' },
            { d: 'DAG 03', t: 'Florence', sub: 'Uffizi vooraf', km: '38 km', kleur: 'var(--papier)' },
            { d: 'DAG 04', t: 'Pienza', sub: 'hub-aankomst', km: '128 km', kleur: 'var(--tomaat)', ink: 'var(--papier)' },
            { d: 'DAG 05', t: 'Siena', sub: 'Piazza del Campo', km: '52 km', kleur: 'var(--papier)' },
            { d: 'DAG 06', t: 'Val d\'Orcia', sub: 'cipresroad', km: '64 km', kleur: 'var(--zee)', ink: 'var(--papier)' },
            { d: 'DAG 07', t: 'Montepulciano', sub: 'wijnproeven', km: '38 km', kleur: 'var(--papier)' },
            { d: 'DAG 08', t: 'Rust', sub: 'agriturismo', km: '— km', kleur: 'var(--papier)' },
            { d: 'DAG 09', t: 'Terug naar Pisa', sub: 'KL1610 18:55', km: '154 km', kleur: 'var(--papier)' },
          ].map((r, i) => (
            <div key={i} style={{
              width: 160, minHeight: 200,
              background: r.kleur, color: r.ink || 'var(--inkt)',
              border: '2px solid var(--inkt)', boxShadow: '4px 4px 0 var(--inkt)',
              padding: '14px 14px 16px', transform: `rotate(${i % 2 ? -0.8 : 0.6}deg)`,
              position: 'relative',
            }}>
              <div className="eye-v2" style={{ fontSize: 10, opacity: 0.8 }}>{r.d}</div>
              <h3 style={{ fontFamily: 'var(--display)', fontSize: 24, lineHeight: 0.95, marginTop: 10 }}>
                {r.t}
              </h3>
              <div style={{ fontSize: 12, marginTop: 8, opacity: 0.8 }}>{r.sub}</div>
              <div style={{
                position: 'absolute', bottom: 12, left: 14,
                fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700,
              }}>{r.km}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Vergelijkbare bestemmingen — als kaart-collectie */}
      <section style={{ padding: '72px 48px 80px' }}>
        <div className="eye-v2" style={{ color: 'var(--tomaat)' }}>§ 03 · IN DE BUURT</div>
        <h2 style={{ fontFamily: 'var(--display)', fontSize: 64, marginTop: 14, lineHeight: 0.95, maxWidth: 900 }}>
          Niet helemaal&nbsp;<span style={{ color: 'var(--tomaat)' }}>overtuigd?</span> Kijk ook eens hier.
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginTop: 48 }}>
          {[
            { l: 'Umbrië', s: 'het rustige broertje', k: 'var(--olijf)', ink: 'var(--inkt)' },
            { l: 'Provence', s: 'lavendel-klassieker', k: 'var(--rose)', ink: 'var(--inkt)' },
            { l: 'Catalonië', s: 'kust + stad', k: 'var(--tomaat)', ink: 'var(--papier)' },
            { l: 'Istrië', s: 'onderschat', k: 'var(--zee)', ink: 'var(--papier)' },
          ].map((x, i) => (
            <div key={x.l} style={{
              background: x.k, color: x.ink,
              border: '2px solid var(--inkt)', boxShadow: '6px 6px 0 var(--inkt)',
              padding: 22, minHeight: 280, position: 'relative',
            }}>
              <div className="eye-v2" style={{ fontSize: 10, opacity: 0.8 }}>ALTERNATIEF · 0{i + 1}</div>
              <h3 style={{ fontFamily: 'var(--display)', fontSize: 44, lineHeight: 0.95, marginTop: 14 }}>{x.l}</h3>
              <div style={{ marginTop: 12, fontSize: 14 }}>{x.s}</div>
              <div style={{
                position: 'absolute', bottom: 18, left: 22,
                fontFamily: 'var(--hand)', fontSize: 24,
              }}>open →</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

window.BestemmingV2 = BestemmingV2;
