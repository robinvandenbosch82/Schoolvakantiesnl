// HomepageV2.jsx — "Het Vakantie-zine"
// Brutalist editorial almanak: postzegels, plakband, split-flap, marker-highlights

function FlapCount({ n, label, size = 90 }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <div className="flap" style={{
        width: size, height: size * 1.1, fontSize: size * 0.62, lineHeight: 0.95,
      }}>
        <span className="flap-num">{n}</span>
      </div>
      <span className="eye-v2" style={{ color: 'var(--inkt-soft)' }}>{label}</span>
    </div>
  );
}

function Stempel({ kleur = 'var(--tomaat)', rot = -8, top, left, right, bottom, kop = 'DRUK!', sub = '4 JULI', children }) {
  return (
    <div style={{
      position: 'absolute',
      top, left, right, bottom,
      transform: `rotate(${rot}deg)`,
      color: kleur,
      pointerEvents: 'none',
      zIndex: 20,
    }}>
      <div className="stempel">
        <span className="stempel-text">{kop}</span>
        <span>{sub}</span>
        {children}
      </div>
    </div>
  );
}

function Postzegel({ kleur, ink, label, plaats, jaar, rot = 0, w = 180, h = 220 }) {
  return (
    <div style={{
      width: w, height: h, color: ink, transform: `rotate(${rot}deg)`,
      display: 'inline-block',
    }}>
      <div className="postzegel" style={{
        background:
          `radial-gradient(circle at 7px 0, transparent 5px, ${kleur} 5.5px) repeat-x,
           radial-gradient(circle at 7px 100%, transparent 5px, ${kleur} 5.5px) repeat-x,
           radial-gradient(circle at 0 7px, transparent 5px, ${kleur} 5.5px) repeat-y,
           radial-gradient(circle at 100% 7px, transparent 5px, ${kleur} 5.5px) repeat-y,
           ${kleur}`,
        backgroundSize: '14px 8px, 14px 8px, 8px 14px, 8px 14px, 100% 100%',
        backgroundPosition: '0 0, 0 100%, 0 0, 100% 0, 0 0',
        width: '100%', height: '100%',
        position: 'relative',
        boxShadow: '4px 4px 0 rgba(0,0,0,0.12)',
      }}>
        <div style={{
          width: '100%', height: '100%',
          border: `2px solid ${ink}`,
          padding: 14,
          display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700, letterSpacing: 1 }}>
            <span>NL · POST</span>
            <span>{jaar}</span>
          </div>
          <div style={{
            fontFamily: 'var(--display)', fontSize: w * 0.18, lineHeight: 0.95, textAlign: 'center',
          }}>{label}</div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 9, fontWeight: 700, letterSpacing: 1, textAlign: 'center' }}>
            {plaats}
          </div>
        </div>
      </div>
    </div>
  );
}

function MastheadV2() {
  return (
    <header style={{
      borderBottom: '4px solid var(--inkt)',
      padding: '28px 48px 16px',
      background: 'var(--papier)',
      position: 'relative',
    }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
        borderBottom: '1px solid var(--inkt)', paddingBottom: 12,
        fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: 0.15,
        textTransform: 'uppercase', fontWeight: 700,
      }}>
        <span>Vol. XVII — Editie 047</span>
        <span>★ Maandag · 25 mei 2026 · Week 22</span>
        <span>€ 0,00 — gratis, altijd</span>
      </div>
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end',
        marginTop: 14,
      }}>
        <h1 style={{
          fontFamily: 'var(--display)', fontSize: 110, lineHeight: 0.85, letterSpacing: '-0.025em',
        }}>
          School<span style={{ color: 'var(--tomaat)' }}>vakanties</span>
          <span style={{ fontFamily: 'var(--hand)', fontSize: 76, color: 'var(--zee)', display: 'inline-block', transform: 'rotate(-4deg) translateY(-8px)', marginLeft: 4 }}>
            .nl
          </span>
        </h1>
        <nav style={{ display: 'flex', gap: 24, paddingBottom: 18 }}>
          {['DE AGENDA', 'BESTEMMINGEN', 'DRUKTE', 'PLANNER', 'KENNIS'].map(x => (
            <a key={x} href="#" style={{
              fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700, letterSpacing: 0.12,
              color: 'var(--inkt)', textDecoration: 'none',
            }}>{x}</a>
          ))}
        </nav>
      </div>
    </header>
  );
}

function HeroV2() {
  return (
    <section style={{
      padding: '56px 48px 80px', position: 'relative',
      borderBottom: '4px solid var(--inkt)',
      background: 'var(--papier)',
    }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 40, position: 'relative' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 22 }}>
            <span style={{
              padding: '4px 12px', background: 'var(--tomaat)', color: 'var(--papier)',
              fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, letterSpacing: 0.15, textTransform: 'uppercase',
            }}>HOOFDARTIKEL</span>
            <span style={{
              fontFamily: 'var(--hand)', fontSize: 26, color: 'var(--zee)',
              transform: 'rotate(-2deg)',
            }}>door de redactie ✍</span>
          </div>

          <h2 style={{
            fontFamily: 'var(--display)', fontSize: 168, lineHeight: 0.82, letterSpacing: '-0.03em',
          }}>
            <span className="marker">Voorpret</span><br />
            is een <span className="streep">gevoel</span><br />
            <span style={{ color: 'var(--tomaat)' }}>plan.</span>
          </h2>

          <p style={{
            marginTop: 32, fontSize: 19, lineHeight: 1.45, maxWidth: 580,
            fontFamily: 'var(--grotesk)', color: 'var(--inkt-soft)',
          }}>
            Alle Nederlandse schoolvakanties — geen droge tabel, geen kaart met spelden, maar
            een levende almanak waar het hele jaar in past. Open een blad en je <span className="marker">ziet</span> de zomer al naderen.
          </p>

          <div style={{ display: 'flex', gap: 16, marginTop: 36, alignItems: 'center', flexWrap: 'wrap' }}>
            <button className="knal-knop tomaat">Bewaar mijn jaar →</button>
            <button className="knal-knop outline">Druktekalender</button>
            <span style={{ fontFamily: 'var(--hand)', fontSize: 22, color: 'var(--inkt-soft)', transform: 'rotate(-3deg)' }}>
              ⤴ begin hier
            </span>
          </div>
        </div>

        {/* Postzegel-collage */}
        <div style={{ position: 'relative', minHeight: 480 }}>
          <div style={{ position: 'absolute', top: 0, right: 60 }}>
            <Postzegel kleur="var(--geel)" ink="var(--inkt)" label="MEI" plaats="VOORJAAR" jaar="'26" rot={-7} />
          </div>
          <div style={{ position: 'absolute', top: 110, right: 0 }}>
            <Postzegel kleur="var(--tomaat)" ink="var(--papier)" label="JUL" plaats="ZOMER NL" jaar="'26" rot={5} w={170} h={210} />
          </div>
          <div style={{ position: 'absolute', top: 260, right: 80 }}>
            <Postzegel kleur="var(--zee)" ink="var(--papier)" label="DEC" plaats="KERST" jaar="'26" rot={-3} w={160} h={200} />
          </div>
          <div style={{ position: 'absolute', top: 320, right: 200 }}>
            <Postzegel kleur="var(--olijf)" ink="var(--inkt)" label="OKT" plaats="HERFST" jaar="'26" rot={9} w={140} h={170} />
          </div>
        </div>

        <Stempel kleur="var(--tomaat)" rot={-12} top={32} right={32} kop="LIVE" sub="VOORPRET" />
      </div>
    </section>
  );
}

function CountdownV2() {
  return (
    <section style={{
      padding: '64px 48px 72px',
      background: 'var(--inkt)', color: 'var(--papier)',
      borderBottom: '4px solid var(--inkt)',
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: 56, alignItems: 'center' }}>
        <div>
          <div style={{
            display: 'inline-block', padding: '4px 10px',
            background: 'var(--geel)', color: 'var(--inkt)',
            fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, letterSpacing: 0.15,
            transform: 'rotate(-2deg)', marginBottom: 22,
          }}>
            ● LIVE — TIKT NU
          </div>
          <h2 style={{
            fontFamily: 'var(--display)', fontSize: 88, lineHeight: 0.88, color: 'var(--papier)',
          }}>
            Nog <span style={{ color: 'var(--geel)' }}>40</span><br />
            dagen tot<br />
            <span className="marker-tomaat" style={{ display: 'inline-block', padding: '4px 16px' }}>zomer.</span>
          </h2>
          <p style={{
            marginTop: 24, color: 'oklch(75% 0.02 80)', fontSize: 15, lineHeight: 1.5, maxWidth: 380,
          }}>
            Tot regio Noord vrij krijgt. Daarna 6 weken vrijheid — start zaterdag 4 juli, eindigt 16 augustus.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 18, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
          <FlapCount n="40" label="DAGEN" size={140} />
          <FlapCount n="12" label="UUR" size={110} />
          <FlapCount n="31" label="MINUUT" size={110} />
          <FlapCount n="08" label="SECONDE" size={110} />
        </div>
      </div>
    </section>
  );
}

function AgendaV2() {
  const items = [
    { nr: '§ I', titel: 'Meivakantie', regio: 'heel NL', datum: '25.04 — 03.05.2026', dagen: 9, kleur: 'var(--olijf)', ink: 'var(--inkt)', status: 'AFGELOPEN', streep: true },
    { nr: '§ II', titel: 'Zomervakantie', regio: 'in 3 golven', datum: '04.07 — 30.08.2026', dagen: 42, kleur: 'var(--tomaat)', ink: 'var(--papier)', status: 'EERSTVOLGEND' },
    { nr: '§ III', titel: 'Herfstvakantie', regio: 'per regio', datum: '17.10 — 25.10.2026', dagen: 9, kleur: 'var(--geel)', ink: 'var(--inkt)' },
    { nr: '§ IV', titel: 'Kerstvakantie', regio: 'heel NL', datum: '19.12.26 — 03.01.27', dagen: 16, kleur: 'var(--zee)', ink: 'var(--papier)' },
    { nr: '§ V', titel: 'Voorjaarsvakantie', regio: 'in 3 golven', datum: '13.02 — 28.02.2027', dagen: 9, kleur: 'var(--rose)', ink: 'var(--inkt)' },
  ];
  return (
    <section style={{ padding: '72px 48px 80px', borderBottom: '4px solid var(--inkt)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 40 }}>
        <div>
          <div className="eye-v2" style={{ color: 'var(--tomaat)' }}>§ De agenda · vijf hoofdstukken</div>
          <h2 style={{
            fontFamily: 'var(--display)', fontSize: 88, lineHeight: 0.9, marginTop: 14,
          }}>
            Het jaar in <span className="marker">vijf bladen.</span>
          </h2>
        </div>
        <div style={{ fontFamily: 'var(--hand)', fontSize: 26, color: 'var(--zee)', transform: 'rotate(-3deg)', textAlign: 'right' }}>
          regio: <u>Midden</u><br />
          <span style={{ fontSize: 16, color: 'var(--inkt-soft)' }}>wijzig met een klik</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr 1fr', gap: 14 }}>
        {items.map((it, i) => (
          <div key={i} style={{
            background: it.kleur, color: it.ink,
            padding: '20px 18px 22px', position: 'relative',
            border: '2px solid var(--inkt)',
            boxShadow: i === 1 ? '8px 8px 0 var(--inkt)' : '4px 4px 0 var(--inkt)',
            transform: i === 1 ? 'translateY(-8px)' : 'none',
            minHeight: 300,
          }}>
            {/* Tape strip */}
            <div className="tape" style={{
              top: -10, left: '50%', marginLeft: -45,
              background: i === 1 ? 'oklch(89% 0.06 95 / 0.85)' : 'oklch(89% 0.06 95 / 0.75)',
            }} />
            <div className="eye-v2" style={{ opacity: 0.7, fontSize: 10 }}>{it.nr}</div>
            <h3 style={{
              fontFamily: 'var(--display)', fontSize: 30, lineHeight: 0.95, marginTop: 14,
            }} className={it.streep ? 'streep' : ''}>
              {it.titel}
            </h3>
            <div style={{ marginTop: 10, fontSize: 13 }}>{it.regio}</div>
            <div style={{
              fontFamily: 'var(--mono)', fontSize: 11, marginTop: 18, fontWeight: 700, letterSpacing: 0.05,
            }}>{it.datum}</div>
            <div style={{
              position: 'absolute', bottom: 18, left: 18, right: 18,
              display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end',
            }}>
              <div style={{ fontFamily: 'var(--display)', fontSize: 56, lineHeight: 0.85 }}>
                {it.dagen}<span style={{ fontSize: 18, fontFamily: 'var(--grotesk)', fontWeight: 700 }}>d</span>
              </div>
              {it.status && (
                <div style={{
                  border: `2px solid ${it.ink}`, padding: '3px 7px',
                  fontFamily: 'var(--mono)', fontSize: 9, fontWeight: 700, letterSpacing: 0.1,
                  transform: 'rotate(-3deg)',
                }}>{it.status}</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function MoodboardV2() {
  // A literal moodboard / scrapbook with mixed elements
  return (
    <section style={{
      padding: '80px 48px', background: 'var(--geel)',
      borderBottom: '4px solid var(--inkt)',
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48, alignItems: 'start' }}>
        <div>
          <div className="eye-v2" style={{ color: 'var(--tomaat)' }}>§ INSPIRATIE — TOP 4 DEZE MEI</div>
          <h2 style={{
            fontFamily: 'var(--display)', fontSize: 96, lineHeight: 0.88, marginTop: 14,
          }}>
            Het<br />
            <span className="streep">familieuitje</span><br />
            scrap<span style={{ color: 'var(--tomaat)' }}>boek</span>.
          </h2>
          <p style={{ marginTop: 26, fontSize: 17, lineHeight: 1.5, maxWidth: 440 }}>
            Vier bestemmingen die wij zelf ook willen onthouden — verzameld zoals een gezin doet:
            stickers, krantenknipsels, en een &ldquo;<span className="marker">moet ik nog boeken</span>&rdquo; op de keukentafel.
          </p>
          <div style={{ marginTop: 32, fontFamily: 'var(--hand)', fontSize: 28, color: 'var(--zee)', transform: 'rotate(-2deg)' }}>
            ↘ klik op een blok om te bewaren
          </div>
        </div>

        {/* Scrapbook */}
        <div style={{ position: 'relative', minHeight: 600 }}>
          {/* Card 1 — Toscane */}
          <div style={{
            position: 'absolute', top: 0, left: 0, width: 280, height: 320,
            background: 'var(--papier)', border: '2px solid var(--inkt)',
            boxShadow: '6px 6px 0 var(--inkt)', transform: 'rotate(-4deg)',
            padding: 0, overflow: 'hidden',
          }}>
            <div className="tape" style={{ top: -10, left: 60 }} />
            <div style={{
              height: 180, background: 'var(--tomaat)',
              backgroundImage: `repeating-linear-gradient(45deg, transparent 0 14px, rgba(0,0,0,0.07) 14px 16px)`,
              borderBottom: '2px solid var(--inkt)',
              display: 'flex', alignItems: 'flex-end', padding: 14,
              color: 'var(--papier)',
              fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700, letterSpacing: 0.1,
            }}>
              ↳ FOTO · TOSCANE · GOUDEN UUR
            </div>
            <div style={{ padding: '16px 18px' }}>
              <div className="eye-v2" style={{ fontSize: 10, color: 'var(--tomaat-deep)' }}>01 / IT</div>
              <h3 style={{ fontFamily: 'var(--display)', fontSize: 36, marginTop: 6 }}>Toscane</h3>
              <div style={{ marginTop: 8, fontFamily: 'var(--hand)', fontSize: 22, color: 'var(--zee)' }}>
                €840 pp · 23° ☀
              </div>
            </div>
          </div>

          {/* Card 2 — Texel */}
          <div style={{
            position: 'absolute', top: 40, left: 290, width: 240, height: 280,
            background: 'var(--zee)', color: 'var(--papier)',
            border: '2px solid var(--inkt)', boxShadow: '6px 6px 0 var(--inkt)',
            transform: 'rotate(3deg)', padding: 18, overflow: 'hidden',
          }}>
            <div className="eye-v2" style={{ fontSize: 10, color: 'var(--geel)' }}>02 / NL</div>
            <h3 style={{ fontFamily: 'var(--display)', fontSize: 50, marginTop: 8, lineHeight: 0.9 }}>
              Texel
            </h3>
            <div style={{ marginTop: 12, fontSize: 13 }}>laatste vrije huisjes</div>
            <div style={{ position: 'absolute', bottom: 18, left: 18, right: 18 }}>
              <div style={{
                fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700,
                background: 'var(--geel)', color: 'var(--inkt)', padding: '4px 8px',
                display: 'inline-block', transform: 'rotate(-3deg)',
              }}>2u15 ANWB</div>
            </div>
            <div className="stempel" style={{
              position: 'absolute', top: -20, right: -20, width: 70, height: 70,
              fontSize: 8, color: 'var(--geel)', transform: 'rotate(15deg)',
              background: 'var(--zee)',
            }}>
              <span className="stempel-text" style={{ fontSize: 11 }}>NIEUW</span>
            </div>
          </div>

          {/* Card 3 — Sankt Anton */}
          <div style={{
            position: 'absolute', top: 280, left: 80, width: 260, height: 200,
            background: 'var(--papier)', border: '2px solid var(--inkt)',
            boxShadow: '6px 6px 0 var(--inkt)', transform: 'rotate(2deg)',
            padding: 18,
          }}>
            <div className="eye-v2" style={{ fontSize: 10, color: 'var(--zee-deep)' }}>03 / AT</div>
            <h3 style={{ fontFamily: 'var(--display)', fontSize: 36, marginTop: 6 }}>St Anton</h3>
            <div style={{ marginTop: 8, fontSize: 13, color: 'var(--inkt-soft)' }}>
              wintersport · laatste sneeuw v/h seizoen
            </div>
            <div style={{ marginTop: 18, fontFamily: 'var(--hand)', fontSize: 26, color: 'var(--tomaat)' }}>
              ❄ −4° / +6°
            </div>
          </div>

          {/* Card 4 — Provence */}
          <div style={{
            position: 'absolute', top: 380, left: 320, width: 220, height: 260,
            background: 'var(--olijf)', color: 'var(--inkt)',
            border: '2px solid var(--inkt)', boxShadow: '6px 6px 0 var(--inkt)',
            transform: 'rotate(-5deg)', padding: 18,
          }}>
            <div className="tape" style={{ top: -10, left: 40, background: 'oklch(82% 0.05 130 / 0.85)' }} />
            <div className="eye-v2" style={{ fontSize: 10 }}>04 / FR</div>
            <h3 style={{ fontFamily: 'var(--display)', fontSize: 38, marginTop: 8, lineHeight: 0.9 }}>
              Pro<br />vence
            </h3>
            <div style={{
              position: 'absolute', bottom: 16, left: 18, fontSize: 13, fontWeight: 700,
            }}>
              lavendel<br />
              <span style={{ fontFamily: 'var(--hand)', fontSize: 22, color: 'var(--tomaat-deep)' }}>
                vanaf 1 juli
              </span>
            </div>
          </div>

          {/* Floating stempel */}
          <div className="stempel" style={{
            position: 'absolute', top: 200, right: -20, color: 'var(--tomaat)',
            transform: 'rotate(14deg)', background: 'var(--geel)',
          }}>
            <span className="stempel-text">BEWAARD</span>
            <span>3.412 KEER</span>
          </div>
        </div>
      </div>
    </section>
  );
}

function DrukteV2() {
  // A bold, blocky drukte-card series
  return (
    <section style={{ padding: '72px 48px 88px', borderBottom: '4px solid var(--inkt)' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.6fr', gap: 56, alignItems: 'start' }}>
        <div>
          <div className="eye-v2" style={{ color: 'var(--tomaat)' }}>§ DRUKTE-RAPPORT</div>
          <h2 style={{
            fontFamily: 'var(--display)', fontSize: 80, lineHeight: 0.88, marginTop: 14,
          }}>
            De&nbsp;<span style={{ color: 'var(--tomaat)' }}>files</span><br />
            van de week.
          </h2>
          <p style={{ marginTop: 20, fontSize: 16, lineHeight: 1.5, color: 'var(--inkt-soft)', maxWidth: 360 }}>
            Drie dagen waarop Nederland tegelijk de grens overgaat. Bewaar deze in je hoofd, of dump ze in de planner.
          </p>
          <button className="knal-knop" style={{ marginTop: 26 }}>Volledige druktekalender →</button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 18 }}>
          {[
            { dag: 'ZA', datum: '04.07', maand: 'JULI', idx: '9.4', label: 'EXTREEM', kleur: 'var(--tomaat)', ink: 'var(--papier)' },
            { dag: 'ZA', datum: '18.07', maand: 'JULI', idx: '8.7', label: 'ZEER DRUK', kleur: 'var(--geel)', ink: 'var(--inkt)' },
            { dag: 'ZA', datum: '01.08', maand: 'AUG', idx: '7.2', label: 'DRUK', kleur: 'var(--olijf)', ink: 'var(--inkt)' },
          ].map((d, i) => (
            <div key={i} style={{
              background: d.kleur, color: d.ink,
              border: '2px solid var(--inkt)', boxShadow: '6px 6px 0 var(--inkt)',
              padding: '20px 22px 24px', minHeight: 320, position: 'relative',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div className="eye-v2" style={{ fontSize: 10 }}>{d.dag} · {d.maand}</div>
                <div className="eye-v2" style={{ fontSize: 10, opacity: 0.7 }}>0{i + 1} / 03</div>
              </div>
              <div style={{
                fontFamily: 'var(--display)', fontSize: 140, lineHeight: 0.85, marginTop: 12,
              }}>
                {d.datum.split('.')[0]}
              </div>
              <div style={{
                fontFamily: 'var(--display)', fontSize: 64, marginTop: 12, lineHeight: 0.95,
              }}>
                {d.idx}<span style={{ fontSize: 22, opacity: 0.6 }}>/10</span>
              </div>
              <div style={{
                position: 'absolute', bottom: 22, left: 22, right: 22,
                display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end',
              }}>
                <div style={{
                  fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, letterSpacing: 0.12,
                  border: `2px solid ${d.ink}`, padding: '4px 8px',
                }}>{d.label}</div>
                <span style={{ fontFamily: 'var(--hand)', fontSize: 22, color: d.ink }}>vermijd 9–12u</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function ColumnFlowV2() {
  return (
    <section style={{
      padding: '80px 48px', background: 'var(--zee)', color: 'var(--papier)',
      borderBottom: '4px solid var(--inkt)', position: 'relative', overflow: 'hidden',
    }}>
      {/* zon */}
      <div style={{
        position: 'absolute', top: -120, right: -120, width: 380, height: 380,
        borderRadius: '50%', background: 'var(--geel)',
        boxShadow: '0 0 0 30px oklch(58% 0.16 240), 0 0 0 60px var(--geel)',
        opacity: 0.55,
      }} />
      <div style={{ position: 'relative', display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 48 }}>
        <div>
          <div className="eye-v2" style={{ color: 'var(--geel)' }}>§ DE ESSAYIST · 8 MIN</div>
          <h2 style={{
            fontFamily: 'var(--display)', fontSize: 96, lineHeight: 0.85, marginTop: 14,
          }}>
            Waarom we<br />
            <span style={{ color: 'var(--geel)', fontStyle: 'italic' }}>allemaal</span> tegelijk<br />
            de grens<br />
            overgaan.
          </h2>
          <p style={{
            marginTop: 26, fontSize: 17, lineHeight: 1.55, maxWidth: 460,
            color: 'oklch(92% 0.02 240)',
          }}>
            Drie regio's, één week, vier miljoen reizigers. Een data-essay over
            de drukste week van het Nederlandse vakantiejaar — en hoe je er
            eentje voorblijft.
          </p>
          <button className="knal-knop geel" style={{ marginTop: 32 }}>
            Lees het essay →
          </button>
        </div>

        {/* Eenvoudige bar-chart als magazine-graphic */}
        <div style={{
          background: 'var(--papier)', color: 'var(--inkt)',
          padding: 28, border: '2px solid var(--inkt)', boxShadow: '8px 8px 0 var(--inkt)',
          position: 'relative',
        }}>
          <div className="eye-v2" style={{ color: 'var(--tomaat)' }}>FIG. 1 · VERTREKDAG-INDEX MEI 2025</div>
          <div style={{ marginTop: 18, display: 'flex', alignItems: 'flex-end', gap: 12, height: 220 }}>
            {[
              { d: 'wo', v: 24 },
              { d: 'do', v: 36 },
              { d: 'vr', v: 62 },
              { d: 'za', v: 94, hot: true },
              { d: 'zo', v: 41 },
              { d: 'ma', v: 28 },
            ].map((b, i) => (
              <div key={i} style={{
                flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
              }}>
                <div style={{
                  width: '100%',
                  height: `${b.v}%`,
                  background: b.hot ? 'var(--tomaat)' : 'var(--inkt)',
                  border: '2px solid var(--inkt)',
                  position: 'relative',
                }}>
                  {b.hot && (
                    <div style={{
                      position: 'absolute', top: -28, left: '50%', transform: 'translateX(-50%)',
                      fontFamily: 'var(--hand)', fontSize: 22, color: 'var(--tomaat)',
                      whiteSpace: 'nowrap',
                    }}>de piek →</div>
                  )}
                </div>
                <span className="eye-v2" style={{ fontSize: 10 }}>{b.d}</span>
              </div>
            ))}
          </div>
          <div style={{
            marginTop: 14, fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--inkt-soft)',
            display: 'flex', justifyContent: 'space-between',
          }}>
            <span>BRON: ANWB / KNMI / NS</span>
            <span>n=4.2 mln</span>
          </div>
        </div>
      </div>
    </section>
  );
}

function FooterV2() {
  return (
    <footer style={{
      background: 'var(--inkt)', color: 'var(--papier)', padding: '56px 48px 40px',
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: 40 }}>
        <div>
          <h3 style={{ fontFamily: 'var(--display)', fontSize: 56, lineHeight: 0.85 }}>
            School<br /><span style={{ color: 'var(--tomaat)' }}>vakanties</span>
            <span style={{ fontFamily: 'var(--hand)', fontSize: 38, color: 'var(--geel)' }}>.nl</span>
          </h3>
          <p style={{ marginTop: 20, fontSize: 14, color: 'oklch(75% 0.02 80)', maxWidth: 320, lineHeight: 1.5 }}>
            Sinds 2009. Het centrale vakantieplatform van Nederland — voor 1 op 3 gezinnen.
          </p>
        </div>
        {[
          { kop: 'AGENDA', items: ['Mei', 'Zomer', 'Herfst', 'Kerst', 'Voorjaar'] },
          { kop: 'BESTEMMINGEN', items: ['Italië', 'Frankrijk', 'NL eilanden', 'Wintersport', '+380'] },
          { kop: 'KENNIS', items: ['Drukte A12', 'Roadtrips', 'Vakantiehuis', 'Weer', '+64'] },
        ].map(col => (
          <div key={col.kop}>
            <div className="eye-v2" style={{ color: 'var(--geel)', marginBottom: 12 }}>{col.kop}</div>
            {col.items.map(i => (
              <a key={i} href="#" style={{
                display: 'block', padding: '6px 0', color: 'var(--papier)',
                fontSize: 14, fontWeight: 500, textDecoration: 'none',
              }}>{i}</a>
            ))}
          </div>
        ))}
      </div>
      <div style={{
        marginTop: 48, paddingTop: 18, borderTop: '1px solid oklch(28% 0.04 250)',
        display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--mono)', fontSize: 11,
        color: 'oklch(70% 0.04 80)',
      }}>
        <span>VOL. XVII · ED. 047 · MEI 2026</span>
        <span>Gemaakt in Utrecht — gedrukt nergens</span>
      </div>
    </footer>
  );
}

function HomepageV2() {
  return (
    <div className="v2-root" style={{ width: 1440, position: 'relative' }}>
      <MastheadV2 />
      <HeroV2 />
      <CountdownV2 />
      <AgendaV2 />
      <MoodboardV2 />
      <DrukteV2 />
      <ColumnFlowV2 />
      <FooterV2 />
    </div>
  );
}

window.HomepageV2 = HomepageV2;
