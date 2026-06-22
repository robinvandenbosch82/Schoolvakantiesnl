// MobileV2.jsx — Mobile als zine-app

function MobileFrameV2({ children }) {
  return (
    <div style={{
      width: 390, height: 844, borderRadius: 48, padding: 12,
      background: 'var(--inkt)', boxShadow: '0 30px 60px rgba(0,0,0,0.22)',
      position: 'relative',
    }}>
      <div style={{
        width: '100%', height: '100%', borderRadius: 38, overflow: 'hidden',
        background: 'var(--papier)', position: 'relative',
      }}>
        <div style={{
          position: 'absolute', top: 14, left: '50%', transform: 'translateX(-50%)',
          width: 110, height: 32, borderRadius: 999, background: 'var(--inkt)', zIndex: 50,
        }} />
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, padding: '18px 30px 0',
          display: 'flex', justifyContent: 'space-between', fontSize: 14, fontWeight: 700,
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

function MobileHomeV2() {
  return (
    <MobileFrameV2>
      <div className="v2-root" style={{
        height: '100%', overflowY: 'auto', paddingTop: 60,
        background: 'var(--papier)',
      }}>
        {/* Masthead */}
        <div style={{
          padding: '14px 20px 14px', borderBottom: '3px solid var(--inkt)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end',
        }}>
          <div>
            <div className="eye-v2" style={{ fontSize: 9, color: 'var(--tomaat)' }}>VOL. XVII · 25 MEI</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 28, lineHeight: 0.9, marginTop: 2 }}>
              School<span style={{ color: 'var(--tomaat)' }}>vakanties</span>
              <span style={{ fontFamily: 'var(--hand)', fontSize: 22, color: 'var(--zee)' }}>.nl</span>
            </div>
          </div>
          <div style={{
            width: 36, height: 36, background: 'var(--inkt)', color: 'var(--papier)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: '2px solid var(--inkt)', boxShadow: '3px 3px 0 var(--tomaat)',
            fontSize: 18, fontWeight: 700,
          }}>≡</div>
        </div>

        {/* HERO — countdown ticket */}
        <div style={{ padding: '18px 16px 18px' }}>
          <div style={{
            background: 'var(--inkt)', color: 'var(--papier)',
            border: '2px solid var(--inkt)', boxShadow: '5px 5px 0 var(--tomaat)',
            padding: 20, position: 'relative', overflow: 'hidden',
          }}>
            <div className="eye-v2" style={{ color: 'var(--geel)', fontSize: 10 }}>● LIVE · TIKT NU</div>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, marginTop: 10 }}>
              <div style={{ fontFamily: 'var(--display)', fontSize: 96, lineHeight: 0.85, color: 'var(--geel)' }}>
                40
              </div>
              <div style={{ paddingBottom: 14 }}>
                <div style={{ fontFamily: 'var(--display)', fontSize: 28, lineHeight: 0.9 }}>dagen</div>
                <div className="eye-v2" style={{ fontSize: 10, color: 'oklch(75% 0.02 80)' }}>tot zomer NL</div>
              </div>
            </div>
            <div style={{
              marginTop: 12, fontFamily: 'var(--hand)', fontSize: 22, color: 'var(--geel)',
              transform: 'rotate(-1deg)',
            }}>
              ☼ za 4 jul · regio Noord
            </div>
          </div>
        </div>

        {/* Sticker-rij */}
        <div style={{ padding: '0 16px 16px', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {[
            ['mei', 'var(--olijf)', 'var(--inkt)'],
            ['zomer', 'var(--tomaat)', 'var(--papier)'],
            ['herfst', 'var(--geel)', 'var(--inkt)'],
            ['kerst', 'var(--zee)', 'var(--papier)'],
            ['+12', 'var(--papier-2)', 'var(--inkt)'],
          ].map(([t, c, ink], i) => (
            <span key={t} style={{
              padding: '6px 12px', background: c, color: ink,
              border: '2px solid var(--inkt)', boxShadow: '2px 2px 0 var(--inkt)',
              fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, letterSpacing: 0.05,
              transform: `rotate(${i % 2 ? -1.2 : 1}deg)`,
              textTransform: 'lowercase',
            }}>{t}</span>
          ))}
        </div>

        {/* Postzegel + scrap collage */}
        <div style={{ padding: '0 16px 16px', position: 'relative', minHeight: 280 }}>
          <div className="eye-v2" style={{ color: 'var(--tomaat)', marginBottom: 8 }}>§ TRENDING DEZE WEEK</div>
          <div style={{
            background: 'var(--tomaat)', color: 'var(--papier)',
            border: '2px solid var(--inkt)', boxShadow: '5px 5px 0 var(--inkt)',
            padding: 18, position: 'relative', transform: 'rotate(-1deg)',
          }}>
            <div style={{
              position: 'absolute', top: -10, left: 30, width: 80, height: 18,
              background: 'oklch(89% 0.06 95 / 0.85)',
              borderLeft: '1px dashed oklch(75% 0.07 90)',
              borderRight: '1px dashed oklch(75% 0.07 90)',
            }} />
            <div className="eye-v2" style={{ fontSize: 10, color: 'var(--geel)' }}>01 / ITALIË</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 56, lineHeight: 0.88, marginTop: 8 }}>
              Toscane
            </div>
            <div style={{ marginTop: 8, fontFamily: 'var(--hand)', fontSize: 24, color: 'var(--geel)' }}>
              €840 pp · 23° ☀
            </div>
            <div className="stempel" style={{
              position: 'absolute', top: -22, right: -10, color: 'var(--geel)',
              transform: 'rotate(14deg)', background: 'var(--inkt)',
              width: 76, height: 76, fontSize: 7,
            }}>
              <span className="stempel-text" style={{ fontSize: 12 }}>4.6K</span>
              <span>BEWAARD</span>
            </div>
          </div>
        </div>

        {/* Bento — varied */}
        <div style={{ padding: '0 16px 16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <div style={{
            background: 'var(--geel)', border: '2px solid var(--inkt)',
            boxShadow: '4px 4px 0 var(--inkt)', padding: 16, minHeight: 130,
            transform: 'rotate(-0.7deg)',
          }}>
            <div className="eye-v2" style={{ fontSize: 9 }}>DRUKTE · ZA 4 JUL</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 56, lineHeight: 0.85, marginTop: 6 }}>9.4</div>
            <div style={{ fontSize: 10, marginTop: 4, color: 'var(--inkt-soft)' }}>extreem · 09–12u</div>
          </div>
          <div style={{
            background: 'var(--zee)', color: 'var(--papier)',
            border: '2px solid var(--inkt)', boxShadow: '4px 4px 0 var(--inkt)',
            padding: 16, minHeight: 130, transform: 'rotate(0.5deg)',
          }}>
            <div className="eye-v2" style={{ fontSize: 9, color: 'var(--geel)' }}>WEEKENDWEER</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 56, lineHeight: 0.85, marginTop: 6 }}>25°</div>
            <div style={{ fontFamily: 'var(--hand)', fontSize: 18, marginTop: 4 }}>Texel · zon</div>
          </div>
        </div>

        {/* Redactioneel */}
        <div style={{ padding: '0 16px 16px' }}>
          <div style={{
            background: 'var(--papier)', border: '2px solid var(--inkt)',
            boxShadow: '4px 4px 0 var(--inkt)', padding: 18,
          }}>
            <div className="eye-v2" style={{ fontSize: 10, color: 'var(--tomaat)' }}>§ ESSAY · 5 MIN</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 24, lineHeight: 1.0, marginTop: 8 }}>
              Zeven kleine reisfouten die <span className="marker">iedereen maakt</span> in mei.
            </div>
          </div>
        </div>

        <div style={{ height: 100 }} />

        {/* Tab bar */}
        <div style={{
          position: 'absolute', bottom: 18, left: 14, right: 14, padding: '10px 6px',
          background: 'var(--inkt)', color: 'var(--papier)',
          border: '2px solid var(--inkt)', boxShadow: '4px 4px 0 var(--tomaat)',
          display: 'flex', justifyContent: 'space-around',
        }}>
          {[
            ['◐', 'JAAR', true],
            ['⌖', 'PLAN', false],
            ['☼', 'INSPI', false],
            ['◔', 'DRUKTE', false],
          ].map(([i, l, a], idx) => (
            <button key={idx} style={{
              background: a ? 'var(--geel)' : 'transparent',
              color: a ? 'var(--inkt)' : 'var(--papier)',
              border: a ? '2px solid var(--inkt)' : 'none',
              padding: '6px 12px',
              display: 'flex', alignItems: 'center', gap: 6,
              fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700, letterSpacing: 0.1,
            }}>
              <span style={{ fontSize: 14 }}>{i}</span>
              {a && l}
            </button>
          ))}
        </div>
      </div>
    </MobileFrameV2>
  );
}

function MobileNavV2() {
  return (
    <MobileFrameV2>
      <div className="v2-root" style={{
        height: '100%', overflowY: 'auto', paddingTop: 60,
        background: 'var(--inkt)', color: 'var(--papier)',
        position: 'relative', overflow: 'hidden',
      }}>
        {/* Geel zon-blok */}
        <div style={{
          position: 'absolute', top: 60, right: -100, width: 280, height: 280,
          background: 'var(--geel)', borderRadius: '50%', opacity: 0.6,
        }} />

        <div style={{
          padding: '12px 20px 12px', display: 'flex', justifyContent: 'space-between',
          borderBottom: '2px solid oklch(28% 0.04 250)', alignItems: 'flex-end',
          position: 'relative', zIndex: 5,
        }}>
          <div className="eye-v2" style={{ color: 'var(--geel)', fontSize: 11 }}>menu · sluiten ↘</div>
          <div style={{
            width: 36, height: 36, background: 'var(--geel)', color: 'var(--inkt)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: '2px solid var(--papier)', boxShadow: '3px 3px 0 var(--papier)',
            fontSize: 18, fontWeight: 700,
          }}>×</div>
        </div>

        <div style={{ padding: '32px 20px 0', position: 'relative', zIndex: 5 }}>
          {[
            { t: 'De agenda', sub: '5 hoofdstukken', kleur: 'var(--geel)' },
            { t: 'Bestemmingen', sub: '380 regio\'s', kleur: 'var(--tomaat)' },
            { t: 'Druktekalender', sub: 'A1 · A2 · A12', kleur: 'var(--olijf)' },
            { t: 'Planner', sub: 'mijn vakantiejaar', kleur: 'var(--zee)' },
            { t: 'Kennisbank', sub: '64 onderwerpen', kleur: 'var(--rose)' },
          ].map((x, i) => (
            <a key={i} href="#" style={{
              display: 'block', textDecoration: 'none', color: 'var(--papier)',
              padding: '14px 0', borderBottom: '1px solid oklch(28% 0.04 250)',
            }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 12 }}>
                <span style={{
                  width: 12, height: 12, background: x.kleur, display: 'inline-block',
                  border: '1.5px solid var(--papier)',
                }} />
                <span style={{ fontFamily: 'var(--display)', fontSize: 36, lineHeight: 0.95 }}>
                  {x.t}
                </span>
              </div>
              <div style={{ fontFamily: 'var(--hand)', fontSize: 18, color: x.kleur, marginLeft: 24, marginTop: 2 }}>
                {x.sub} →
              </div>
            </a>
          ))}
        </div>

        {/* Stempel onderaan */}
        <div className="stempel" style={{
          position: 'absolute', bottom: 60, left: 24, color: 'var(--geel)',
          transform: 'rotate(-10deg)', zIndex: 5, background: 'var(--inkt)',
        }}>
          <span className="stempel-text">VOL. XVII</span>
          <span>26.05.26</span>
        </div>

        <div style={{
          position: 'absolute', bottom: 24, right: 24,
          fontFamily: 'var(--hand)', fontSize: 22, color: 'var(--geel)',
          zIndex: 5,
        }}>
          ↖ kies maar
        </div>
      </div>
    </MobileFrameV2>
  );
}

window.MobileHomeV2 = MobileHomeV2;
window.MobileNavV2 = MobileNavV2;
