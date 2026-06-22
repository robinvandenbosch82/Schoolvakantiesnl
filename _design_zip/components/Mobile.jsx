// Mobile.jsx — Mobile home + nav
// App-feel, swipebaar, social-first

function MobileFrame({ children, label }) {
  return (
    <div style={{
      width: 390, height: 844, borderRadius: 48, padding: 12,
      background: 'var(--inkt)', boxShadow: '0 30px 60px rgba(0,0,0,0.18)',
      position: 'relative',
    }}>
      <div style={{
        width: '100%', height: '100%', borderRadius: 38, overflow: 'hidden',
        background: 'var(--papier)', position: 'relative',
      }}>
        {/* notch */}
        <div style={{
          position: 'absolute', top: 14, left: '50%', transform: 'translateX(-50%)',
          width: 110, height: 32, borderRadius: 999, background: 'var(--inkt)', zIndex: 50,
        }} />
        {/* status bar */}
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, padding: '18px 30px 0',
          display: 'flex', justifyContent: 'space-between', fontSize: 14, fontWeight: 600,
          fontFamily: 'var(--grotesk)', zIndex: 60, color: 'var(--inkt)',
        }}>
          <span>9:41</span>
          <span style={{ display: 'flex', gap: 6 }}>
            <span>●●●</span>
            <span>▮</span>
          </span>
        </div>
        {children}
      </div>
    </div>
  );
}

function MobileHome() {
  return (
    <MobileFrame>
      <div style={{
        height: '100%', overflowY: 'auto', paddingTop: 64,
      }} className="sv-root">
        {/* Top header */}
        <div style={{ padding: '8px 22px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontFamily: 'var(--display)', fontSize: 22 }}>
            schoolvakanties<span style={{ color: 'var(--zomer)', fontStyle: 'italic' }}>.nl</span>
          </div>
          <div style={{
            width: 36, height: 36, borderRadius: '50%', background: 'var(--papier-2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 16,
          }}>☰</div>
        </div>

        {/* Hero: groot countdown */}
        <div style={{
          margin: '8px 16px 16px', padding: '28px 22px',
          background: 'var(--inkt)', color: 'var(--papier)', borderRadius: 24,
          position: 'relative', overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', right: -40, top: -40, width: 160, height: 160, borderRadius: '50%',
            background: 'radial-gradient(circle, var(--zomer), transparent 65%)', opacity: 0.5,
          }} />
          <div className="eyebrow" style={{ color: 'var(--zomer)' }}>tot zomervakantie</div>
          <div style={{ fontFamily: 'var(--display)', fontSize: 88, lineHeight: 0.85, marginTop: 8 }}>
            47<span style={{ color: 'var(--zomer)', fontStyle: 'italic', fontSize: 60 }}>d</span>
          </div>
          <div style={{ fontSize: 13, color: 'oklch(75% 0.02 80)', marginTop: 8 }}>
            12u 31m · regio Midden start 11 jul
          </div>
        </div>

        {/* Snelle sticker-keuze */}
        <div style={{
          padding: '0 22px 16px', display: 'flex', gap: 8, overflowX: 'auto',
          flexWrap: 'wrap',
        }}>
          {[
            ['mei', 'var(--lente)', 'var(--lente-ink)'],
            ['zomer', 'var(--zomer)', 'var(--zomer-ink)'],
            ['herfst', 'var(--herfst)', 'var(--herfst-ink)'],
            ['kerst', 'var(--winter)', 'var(--winter-ink)'],
            ['feestdagen', 'var(--papier-2)', 'var(--inkt)'],
          ].map(([t, c, ink], i) => (
            <span key={i} style={{
              padding: '8px 14px', borderRadius: 999,
              background: c, color: ink, fontSize: 13, fontWeight: 500,
              whiteSpace: 'nowrap',
            }}>{t}</span>
          ))}
        </div>

        {/* Bento — varied tiles */}
        <div style={{
          padding: '0 16px 16px',
          display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10,
        }}>
          {/* Big tile */}
          <div style={{
            gridColumn: 'span 2',
            padding: '24px 22px', background: 'var(--zomer)', color: 'var(--zomer-ink)',
            borderRadius: 20, position: 'relative', minHeight: 200, overflow: 'hidden',
          }}>
            <div className="eyebrow">trending · 4.6k bewaard</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 44, lineHeight: 0.95, marginTop: 8 }}>
              Toscane <span style={{ fontStyle: 'italic' }}>in mei</span>
            </div>
            <div style={{ fontSize: 12, marginTop: 6, opacity: 0.85 }}>
              negen dagen · €840 pp · 23° gemiddeld
            </div>
            <div style={{
              position: 'absolute', bottom: -10, right: -10, width: 130, height: 130,
              border: '12px solid rgba(255,255,255,0.25)', borderRadius: '50%',
            }} />
          </div>

          <div style={{
            padding: 18, background: 'var(--papier-2)', borderRadius: 20,
            minHeight: 130,
          }}>
            <div className="eyebrow">drukte vrij 4 jul</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 44, lineHeight: 0.95, color: 'var(--zomer-ink)' }}>9.4</div>
            <div style={{ fontSize: 11, color: 'var(--inkt-3)' }}>vermijd 09–12u</div>
            <div style={{ height: 4, background: 'var(--papier-3)', borderRadius: 2, marginTop: 12 }}>
              <div style={{ width: '94%', height: '100%', background: 'var(--zomer)', borderRadius: 2 }} />
            </div>
          </div>

          <div style={{
            padding: 18, background: 'var(--lente)', color: 'var(--lente-ink)', borderRadius: 20,
          }}>
            <div className="eyebrow">over 2 dagen</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 30, lineHeight: 1.05, marginTop: 6 }}>
              Mei-<br />vakantie
            </div>
            <div style={{ fontSize: 11, marginTop: 8 }}>klaar?</div>
          </div>

          <div style={{
            gridColumn: 'span 2',
            padding: 18, background: 'var(--diepblauw)', color: 'var(--papier)', borderRadius: 20,
            display: 'flex', alignItems: 'center', gap: 14,
          }}>
            <div style={{
              width: 50, height: 50, borderRadius: '50%', background: 'var(--zomer)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'var(--display)', fontSize: 28, color: 'var(--zomer-ink)',
            }}>☼</div>
            <div style={{ flex: 1 }}>
              <div className="eyebrow" style={{ color: 'var(--zomer)' }}>weekendweer</div>
              <div style={{ fontFamily: 'var(--display)', fontSize: 22, marginTop: 2 }}>
                25° zaterdag in Texel
              </div>
            </div>
            <span style={{ fontSize: 18 }}>→</span>
          </div>
        </div>

        {/* Editorial story tile */}
        <div style={{
          margin: '0 16px 16px', padding: 22, background: 'var(--papier-2)', borderRadius: 20,
        }}>
          <div className="eyebrow">redactioneel</div>
          <div style={{ fontFamily: 'var(--display)', fontSize: 28, lineHeight: 1.05, marginTop: 8 }}>
            7 kleine reisfouten die <span style={{ fontStyle: 'italic', color: 'var(--zomer-ink)' }}>iedereen maakt</span> in mei
          </div>
          <div style={{ fontSize: 12, color: 'var(--inkt-3)', marginTop: 8 }}>
            5 min lezen · door redactie
          </div>
        </div>

        {/* Footer spacer */}
        <div style={{ height: 100 }} />

        {/* Tab bar */}
        <div style={{
          position: 'absolute', bottom: 18, left: 16, right: 16, padding: '12px 8px',
          background: 'var(--inkt)', color: 'var(--papier)', borderRadius: 999,
          display: 'flex', justifyContent: 'space-around',
        }}>
          {[
            ['◐', 'jaar', true],
            ['⌖', 'plan', false],
            ['☼', 'inspiratie', false],
            ['◔', 'drukte', false],
          ].map(([i, l, a], idx) => (
            <button key={idx} style={{
              background: a ? 'var(--zomer)' : 'transparent',
              color: a ? 'var(--zomer-ink)' : 'var(--papier)',
              border: 'none', padding: '8px 16px', borderRadius: 999,
              display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 600,
            }}>
              <span style={{ fontSize: 14 }}>{i}</span>
              {a && l}
            </button>
          ))}
        </div>
      </div>
    </MobileFrame>
  );
}

function MobileNav() {
  return (
    <MobileFrame>
      <div style={{
        height: '100%', paddingTop: 64,
        background: 'var(--inkt)', color: 'var(--papier)',
        position: 'relative', overflow: 'hidden',
      }} className="sv-root">
        {/* Decoratieve halve cirkel */}
        <div style={{
          position: 'absolute', right: -120, top: 0, width: 320, height: 320, borderRadius: '50%',
          background: 'radial-gradient(circle, var(--zomer), transparent 60%)', opacity: 0.45,
        }} />
        <div style={{
          position: 'absolute', left: -80, bottom: -80, width: 280, height: 280, borderRadius: '50%',
          background: 'radial-gradient(circle, var(--diepblauw), transparent 65%)', opacity: 0.55,
        }} />

        <div style={{ padding: '8px 22px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'relative', zIndex: 10 }}>
          <div style={{ fontFamily: 'var(--display)', fontSize: 22, color: 'var(--papier)' }}>
            menu
          </div>
          <div style={{
            width: 36, height: 36, borderRadius: '50%', background: 'oklch(28% 0.04 250)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 16, color: 'var(--papier)',
          }}>×</div>
        </div>

        <div style={{ padding: '24px 22px 0', position: 'relative', zIndex: 10 }}>
          <div className="eyebrow" style={{ color: 'var(--zomer)' }}>navigatie</div>
          {[
            ['vakantieoverzicht', '5 hoofdstukken'],
            ['bestemmingen', '380+ regio\'s'],
            ['druktekalender', 'A1 · A2 · A12'],
            ['planner', 'mijn vakantiejaar'],
            ['kennisbank', '64 onderwerpen'],
          ].map(([t, sub], i) => (
            <a key={i} href="#" style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
              padding: '20px 0', borderBottom: '1px solid oklch(28% 0.04 250)',
              color: 'var(--papier)', textDecoration: 'none',
            }}>
              <div>
                <div style={{ fontFamily: 'var(--display)', fontSize: 34, lineHeight: 1 }}>
                  {t}
                </div>
                <div style={{ fontSize: 11, color: 'oklch(70% 0.04 80)', marginTop: 4 }}>{sub}</div>
              </div>
              <span style={{ color: 'var(--zomer)' }}>→</span>
            </a>
          ))}
        </div>

        {/* Seizoenswitcher onderaan */}
        <div style={{
          position: 'absolute', bottom: 32, left: 22, right: 22, zIndex: 10,
        }}>
          <div className="eyebrow" style={{ color: 'var(--zomer)', marginBottom: 12 }}>thema · volg het seizoen</div>
          <div style={{ display: 'flex', gap: 6 }}>
            {[
              ['lente', '--lente'],
              ['zomer', '--zomer'],
              ['herfst', '--herfst'],
              ['winter', '--winter'],
            ].map(([t, c], i) => (
              <div key={t} style={{
                flex: 1, padding: '10px', background: i === 1 ? `var(${c})` : 'oklch(28% 0.04 250)',
                color: i === 1 ? 'var(--inkt)' : 'oklch(75% 0.02 80)',
                borderRadius: 12, textAlign: 'center', fontSize: 11, fontWeight: 600,
              }}>{t}</div>
            ))}
          </div>
        </div>
      </div>
    </MobileFrame>
  );
}

window.MobileHome = MobileHome;
window.MobileNav = MobileNav;
