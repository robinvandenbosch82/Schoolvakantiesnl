// PlannerV2.jsx — Vakantieplanner als scrapbook-werkblad

function PlannerV2() {
  return (
    <div className="v2-root" style={{ width: 1440, position: 'relative' }}>
      <header style={{
        padding: '20px 48px', borderBottom: '4px solid var(--inkt)',
        background: 'var(--inkt)', color: 'var(--papier)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <div className="eye-v2">
          schoolvakanties.nl / <span style={{ color: 'var(--geel)' }}>DE PLANNER</span>
        </div>
        <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
          <span className="eye-v2" style={{ color: 'oklch(70% 0.04 80)' }}>↻ AUTO-SAVE 14:48</span>
          <button className="knal-knop geel" style={{ padding: '8px 14px', fontSize: 12 }}>↧ EXPORT iCAL</button>
        </div>
      </header>

      {/* Header */}
      <section style={{ padding: '52px 48px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 24, marginBottom: 18 }}>
          <span className="eye-v2" style={{ color: 'var(--tomaat)' }}>§ STAP 2 VAN 4 · JOUW VAKANTIEJAAR</span>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--inkt-soft)' }}>
            ━━━━●━━━━━━ 50%
          </span>
        </div>
        <h1 style={{
          fontFamily: 'var(--display)', fontSize: 120, lineHeight: 0.88,
        }}>
          Welke vakantie ben je<br />
          aan het <span className="marker">plannen?</span>
        </h1>

        {/* Seizoen-pillen */}
        <div style={{ display: 'flex', gap: 12, marginTop: 32, flexWrap: 'wrap' }}>
          {[
            ['Meivakantie', 'var(--olijf)', 'var(--inkt)', false, '9d'],
            ['Zomervakantie', 'var(--tomaat)', 'var(--papier)', true, '42d'],
            ['Herfstvakantie', 'var(--geel)', 'var(--inkt)', false, '9d'],
            ['Kerstvakantie', 'var(--zee)', 'var(--papier)', false, '16d'],
          ].map(([t, c, ink, act, d], i) => (
            <button key={t} style={{
              background: c, color: ink,
              border: '2px solid var(--inkt)',
              boxShadow: act ? '5px 5px 0 var(--inkt)' : '3px 3px 0 var(--inkt)',
              padding: '12px 20px',
              fontFamily: 'var(--grotesk)', fontWeight: 700, fontSize: 15,
              transform: act ? 'translate(-2px, -2px)' : `rotate(${i % 2 ? -1 : 0.7}deg)`,
              display: 'flex', alignItems: 'center', gap: 10,
            }}>
              {t}
              <span style={{ fontFamily: 'var(--mono)', fontSize: 11, opacity: 0.7 }}>· {d}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Werkblad */}
      <section style={{ padding: '24px 48px 72px', display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 28 }}>
        {/* Linker werkblad — graph paper */}
        <div className="graph" style={{
          background: 'var(--papier)', backgroundColor: 'var(--papier)',
          border: '2px solid var(--inkt)', boxShadow: '8px 8px 0 var(--inkt)',
          padding: 32, position: 'relative', minHeight: 580,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <div className="eye-v2" style={{ color: 'var(--tomaat)' }}>JOUW BLOK · ZOMERVAKANTIE</div>
              <h2 style={{ fontFamily: 'var(--display)', fontSize: 80, lineHeight: 0.85, marginTop: 12 }}>
                4 juli<br />
                <span style={{ color: 'var(--tomaat)' }}>—</span> 16 aug
              </h2>
              <div style={{ marginTop: 12, fontFamily: 'var(--hand)', fontSize: 26, color: 'var(--zee)' }}>
                42 dagen · regio Noord
              </div>
            </div>
            <div className="stempel" style={{ color: 'var(--tomaat)', transform: 'rotate(8deg)' }}>
              <span className="stempel-text">JOUW</span>
              <span>ZOMER 2026</span>
            </div>
          </div>

          {/* Dagenstrip met events */}
          <div style={{ marginTop: 40 }}>
            <div className="eye-v2" style={{ color: 'var(--inkt-soft)', marginBottom: 14 }}>
              WEEK 27 · SLEEP-EN-DROP EVENTS
            </div>
            <div style={{
              display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 6,
            }}>
              {['MA 04', 'DI 05', 'WO 06', 'DO 07', 'VR 08', 'ZA 09', 'ZO 10'].map((d, i) => {
                const events = {
                  0: { l: 'vlucht', c: 'var(--tomaat)', ink: 'var(--papier)' },
                  1: { l: 'Lucca', c: 'var(--olijf)', ink: 'var(--inkt)' },
                  2: { l: 'Florence', c: 'var(--geel)', ink: 'var(--inkt)' },
                  4: { l: 'Pienza', c: 'var(--zee)', ink: 'var(--papier)' },
                  5: { l: 'Siena', c: 'var(--rose)', ink: 'var(--inkt)' },
                };
                const e = events[i];
                return (
                  <div key={d} style={{
                    minHeight: 140, background: e ? e.c : 'oklch(100% 0 0 / 0.4)',
                    color: e ? e.ink : 'var(--inkt-soft)',
                    border: '2px solid var(--inkt)',
                    padding: 10,
                    transform: e ? `rotate(${(i % 2 ? -0.8 : 0.5)}deg)` : 'none',
                    boxShadow: e ? '3px 3px 0 var(--inkt)' : 'none',
                    position: 'relative',
                  }}>
                    <div className="eye-v2" style={{ fontSize: 9 }}>{d}</div>
                    {e && (
                      <div style={{
                        fontFamily: 'var(--display)', fontSize: 20, lineHeight: 0.95, marginTop: 18,
                      }}>{e.l}</div>
                    )}
                    {!e && (
                      <div style={{
                        fontFamily: 'var(--hand)', fontSize: 22, position: 'absolute',
                        bottom: 10, left: 10,
                      }}>+</div>
                    )}
                  </div>
                );
              })}
            </div>
            <div style={{
              marginTop: 14, fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--inkt-soft)',
              display: 'flex', justifyContent: 'space-between',
            }}>
              <span>← WEEK 26</span>
              <span>+35 dagen scroll →</span>
            </div>
          </div>

          {/* Bestemming */}
          <div style={{
            marginTop: 32, display: 'flex', gap: 18, alignItems: 'center',
            padding: 18, background: 'var(--inkt)', color: 'var(--papier)',
            border: '2px solid var(--inkt)',
          }}>
            <div style={{
              width: 56, height: 56, background: 'var(--tomaat)',
              backgroundImage: `repeating-linear-gradient(45deg, transparent 0 6px, rgba(0,0,0,0.15) 6px 7px)`,
              border: '2px solid var(--papier)',
            }} />
            <div style={{ flex: 1 }}>
              <div className="eye-v2" style={{ color: 'var(--geel)' }}>BESTEMMING</div>
              <div style={{ fontFamily: 'var(--display)', fontSize: 30, lineHeight: 0.95 }}>
                Toscane · IT
              </div>
            </div>
            <button className="knal-knop geel" style={{ padding: '8px 12px', fontSize: 11 }}>VERANDER</button>
          </div>
        </div>

        {/* Rechter kolom — losse zine-blokken */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          <div style={{
            background: 'var(--tomaat)', color: 'var(--papier)',
            border: '2px solid var(--inkt)', boxShadow: '5px 5px 0 var(--inkt)',
            padding: 22, transform: 'rotate(-0.8deg)',
          }}>
            <div className="eye-v2" style={{ fontSize: 10, color: 'var(--geel)' }}>DRUKTE</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 64, lineHeight: 0.9, marginTop: 6 }}>
              9.4<span style={{ fontSize: 22, opacity: 0.7 }}>/10</span>
            </div>
            <div style={{ fontFamily: 'var(--hand)', fontSize: 22, marginTop: 4 }}>extreem — vermijd 9–12u</div>
          </div>

          <div style={{
            background: 'var(--zee)', color: 'var(--papier)',
            border: '2px solid var(--inkt)', boxShadow: '5px 5px 0 var(--inkt)',
            padding: 22, transform: 'rotate(0.6deg)',
          }}>
            <div className="eye-v2" style={{ fontSize: 10, color: 'var(--geel)' }}>VERWACHT WEER</div>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 16, marginTop: 6 }}>
              <span style={{ fontFamily: 'var(--display)', fontSize: 80, lineHeight: 0.85 }}>27°</span>
              <span style={{ paddingBottom: 16, fontSize: 13 }}>↑31 / ↓19 · 9u zon</span>
            </div>
          </div>

          <div style={{
            background: 'var(--geel)', border: '2px solid var(--inkt)',
            boxShadow: '5px 5px 0 var(--inkt)', padding: 22,
          }}>
            <div className="eye-v2" style={{ fontSize: 10, color: 'var(--tomaat)' }}>BUDGET (RAMING)</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 60, lineHeight: 0.9, marginTop: 6 }}>
              €<span style={{ color: 'var(--tomaat)' }}>3.420</span>
            </div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 10, marginTop: 8, fontWeight: 700, letterSpacing: 0.1 }}>
              VLUCHT 1280 · VERBLIJF 1560 · OVERIG 580
            </div>
          </div>

          <div style={{
            background: 'var(--papier)', border: '2px solid var(--inkt)',
            boxShadow: '5px 5px 0 var(--inkt)', padding: 22, transform: 'rotate(-0.4deg)',
          }}>
            <div className="eye-v2" style={{ fontSize: 10, color: 'var(--tomaat)' }}>CHECKLIST · 3 OPEN</div>
            <ul style={{ listStyle: 'none', padding: 0, margin: '12px 0 0', display: 'flex', flexDirection: 'column', gap: 6 }}>
              {[
                ['✓', 'Vlucht KL1607 geboekt', true],
                ['✓', 'Agriturismo bevestigd', true],
                ['☐', 'Huurauto vergelijken', false],
                ['☐', 'Tickets Uffizi (vooraf!)', false],
                ['☐', 'Reisverzekering check', false],
              ].map(([m, t, done], i) => (
                <li key={i} style={{
                  display: 'flex', gap: 10, fontSize: 14, alignItems: 'center',
                  textDecoration: done ? 'line-through' : 'none',
                  color: done ? 'var(--inkt-soft)' : 'var(--inkt)',
                }}>
                  <span style={{ fontFamily: 'var(--mono)', fontWeight: 700, color: done ? 'var(--olijf-deep)' : 'var(--tomaat)' }}>{m}</span>
                  {t}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}

window.PlannerV2 = PlannerV2;
