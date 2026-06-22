// Bestemming.jsx — Editorial bestemmingspagina (Toscane meivakantie)
// Magazine-stijl met grote typografie, asymmetrie, en handgemaakte details

function PlaceholderBeeld({ ratio = '4/3', label = 'fotografie', kleur = '--papier-3', tilt = 0, group }) {
  return (
    <div style={{
      width: '100%', aspectRatio: ratio,
      background: `var(${kleur})`,
      backgroundImage: `repeating-linear-gradient(45deg, transparent 0 12px, rgba(0,0,0,0.05) 12px 13px)`,
      border: '1px dashed var(--inkt-3)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: 'var(--inkt-3)', fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: 1,
      transform: `rotate(${tilt}deg)`,
      position: 'relative',
    }}>
      <span>↳ {label}</span>
      {group && (
        <span style={{
          position: 'absolute', top: 10, left: 12, fontSize: 9, color: 'var(--inkt-3)',
        }}>● {group}</span>
      )}
    </div>
  );
}

function Bestemming() {
  return (
    <div className="sv-root" style={{ width: 1440, position: 'relative' }}>
      {/* breadcrumb */}
      <div style={{
        padding: '20px 56px', borderBottom: '1px solid var(--papier-line)',
        fontSize: 13, color: 'var(--inkt-3)', display: 'flex', justifyContent: 'space-between',
      }}>
        <div>
          schoolvakanties.nl / Bestemmingen / Italië / <span style={{ color: 'var(--inkt)' }}>Toscane</span>
        </div>
        <div style={{ display: 'flex', gap: 16 }} className="font-mono">
          <span>↧ bewaar</span>
          <span>↩ deel</span>
          <span>⎙ print pdf</span>
        </div>
      </div>

      {/* HERO — magazine cover stijl */}
      <section style={{
        padding: '80px 56px 40px', position: 'relative',
        background: 'linear-gradient(180deg, var(--papier) 0%, var(--papier-2) 100%)',
      }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 48, alignItems: 'end' }}>
          <div>
            <div className="eyebrow">
              § meivakantie · 25 april – 3 mei · 9 dagen
            </div>
            <h1 style={{
              fontFamily: 'var(--display)', fontWeight: 400,
              fontSize: 220, lineHeight: 0.82, letterSpacing: '-0.04em',
              marginTop: 16,
            }}>
              Tos<span style={{ fontStyle: 'italic' }}>ca</span><br />ne.
            </h1>
            <p style={{
              maxWidth: 540, fontSize: 18, lineHeight: 1.5, color: 'var(--inkt-2)',
              marginTop: 28,
            }}>
              Negen dagen, drie steden, twee glazen Chianti. De definitieve gezinsroute door Toscane in&nbsp;
              <span style={{ fontStyle: 'italic', fontFamily: 'var(--display)', fontSize: 20 }}>meivakantie 2026</span> — als de toeristen er nog niet zijn maar de zon al wel.
            </p>

            {/* Sticker-set */}
            <div style={{ display: 'flex', gap: 8, marginTop: 28, flexWrap: 'wrap' }}>
              <span className="sticker" style={{ color: 'var(--zomer-ink)' }}>23° gemiddeld</span>
              <span className="sticker" style={{ color: 'var(--diepblauw)' }}>2u20 vlucht</span>
              <span className="sticker" style={{ color: 'var(--lente-ink)' }}>€840 per persoon</span>
              <span className="sticker" style={{ color: 'var(--inkt-3)' }}>3.7/5 drukte</span>
            </div>
          </div>

          <div style={{ position: 'relative' }}>
            <PlaceholderBeeld ratio="3/4" label="Florence skyline · golden hour" kleur="--papier-3" tilt={1.5} group="HERO" />
            {/* Floating annotation */}
            <div style={{
              position: 'absolute', bottom: -20, left: -28, transform: 'rotate(-3deg)',
              background: 'var(--inkt)', color: 'var(--papier)',
              padding: '14px 22px', maxWidth: 220,
              fontFamily: 'var(--display)', fontStyle: 'italic', fontSize: 18, lineHeight: 1.25,
            }}>
              &ldquo;De best bewaarde meivakantie sinds 2011.&rdquo;
              <div style={{
                fontFamily: 'var(--mono)', fontStyle: 'normal', fontSize: 9,
                marginTop: 8, color: 'var(--zomer)',
              }}>— redactie schoolvakanties.nl</div>
            </div>
          </div>
        </div>
      </section>

      {/* Pull-quote / kerncijfers */}
      <section style={{
        padding: '40px 56px 64px', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
        gap: 32, borderTop: '1px solid var(--papier-line)', borderBottom: '1px solid var(--papier-line)',
      }}>
        {[
          { k: 'zonuren / dag', v: '9.2' },
          { k: 'gem. temp', v: '23°' },
          { k: 'kindvriendelijk', v: 'A+' },
          { k: 'drukte-prognose', v: 'gematigd' },
        ].map((s, i) => (
          <div key={s.k} style={{ borderRight: i < 3 ? '1px solid var(--papier-line)' : 'none', paddingRight: 20 }}>
            <div className="eyebrow">{s.k}</div>
            <div style={{ fontFamily: 'var(--display)', fontSize: 72, lineHeight: 0.95, marginTop: 8 }}>
              {s.v}
            </div>
          </div>
        ))}
      </section>

      {/* Verhaal-sectie — twee koloms editorial */}
      <section style={{ padding: '80px 56px', maxWidth: 1240, margin: '0 auto' }}>
        <div className="eyebrow" style={{ marginBottom: 18 }}>§ 01 · het verhaal</div>
        <h2 style={{ fontFamily: 'var(--display)', fontSize: 64, lineHeight: 0.95, maxWidth: 1000, letterSpacing: '-0.01em' }}>
          Met kinderen door <span style={{ fontStyle: 'italic', color: 'var(--zomer-ink)' }}>negen Toscaanse dagen</span> — een eerlijk reisplan, niet de versie die op Pinterest hangt.
        </h2>
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 56, marginTop: 48,
          fontSize: 16, lineHeight: 1.65, color: 'var(--inkt-2)',
        }}>
          <div>
            <p style={{ marginBottom: 18 }}>
              <span style={{
                fontFamily: 'var(--display)', fontSize: 60, lineHeight: 0.85, float: 'left',
                marginRight: 12, marginTop: 6, color: 'var(--inkt)',
              }}>T</span>
              oscane in meivakantie is een gok die je wint. De lavendel is nog niet paars, de zonnebloemen slapen nog onder het oppervlak, en het is precies daarom dat de Florentijnen je niet aankijken alsof je een onbeschofte zomerinval bent.
            </p>
            <p style={{ marginBottom: 18 }}>
              Wij gingen met twee kinderen (7 en 11) en een auto die we per ongeluk te groot hadden gehuurd. Wat we leerden: kies één hub, niet drie. We koersten op een agriturismo tussen Siena en Pienza — landweggetjes vol cipressen — en gebruikten dat als basis voor dagtochten.
            </p>
            <p>
              Wat overigens niet werkte: het Uffizi met een 7-jarige. Wat wél werkte: dezelfde middag een gelato eten op de Piazza della Signoria terwijl de straatartiesten ridders nadeden. Soms is dat het hele verhaal.
            </p>
          </div>
          <div>
            <p style={{ marginBottom: 18 }}>
              De praktische winst van meivakantie boven zomer: je rijdt niet om half twaalf 's nachts nog door een file bij Modena, je hoeft niet voor zonsopgang naar Pisa om die scheve toren te zien zonder vijftig poses van vreemden ervoor, en je krijgt op tweederde van de menukaart antwoord met &ldquo;sì certo&rdquo; in plaats van &ldquo;solo cena&rdquo;.
            </p>
            <div style={{
              padding: 24, background: 'var(--papier-2)', borderLeft: '3px solid var(--zomer)',
              fontFamily: 'var(--display)', fontStyle: 'italic', fontSize: 22, lineHeight: 1.35,
              color: 'var(--inkt)',
            }}>
              &ldquo;De winst is niet dat het mooier is in mei. De winst is dat het er nog gewoon ís — vóór 14 miljoen anderen dezelfde gedachte hebben.&rdquo;
            </div>
            <p style={{ marginTop: 18 }}>
              We hebben het hele plan hieronder per dag uitgesplitst — incl. de vergissingen, zodat jij die niet hoeft te maken.
            </p>
          </div>
        </div>
      </section>

      {/* Beeld-strip — asymmetrisch */}
      <section style={{
        padding: '0 56px 80px',
        display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: 14,
      }}>
        <div style={{ gridColumn: 'span 5' }}>
          <PlaceholderBeeld ratio="4/5" label="Piazza Siena, ochtend" kleur="--herfst" group="01" />
        </div>
        <div style={{ gridColumn: 'span 4', alignSelf: 'end' }}>
          <PlaceholderBeeld ratio="1/1" label="Pasta op Piazza del Campo" kleur="--zomer" group="02" />
        </div>
        <div style={{ gridColumn: 'span 3', alignSelf: 'center' }}>
          <PlaceholderBeeld ratio="3/4" label="Cipressen Val d'Orcia" kleur="--lente" group="03" />
        </div>
      </section>

      {/* Daagse routeplan */}
      <section style={{
        padding: '80px 56px', background: 'var(--inkt)', color: 'var(--papier)',
      }}>
        <div className="eyebrow" style={{ color: 'var(--zomer)' }}>§ 02 · dag-voor-dag</div>
        <h2 style={{ fontFamily: 'var(--display)', fontSize: 64, marginTop: 12, maxWidth: 800, lineHeight: 0.95 }}>
          Negen dagen, één lijn.
        </h2>
        <div style={{ marginTop: 56 }}>
          {[
            { d: 'dag 01', titel: 'Schiphol → Pisa → Lucca', txt: 'Vliegen om 06:25. Eind van de middag in Lucca, fietshuur 12€/dag.', km: '— · 78 km', icoon: '✈' },
            { d: 'dag 02', titel: 'Lucca op de fiets, dan Pistoia', txt: 'Hele dag de stadsmuren rond, om 16:00 doorrijden naar Pistoia.', km: '8 km · 51 km', icoon: '⊙' },
            { d: 'dag 03', titel: 'Florence — Uffizi tickets vooraf', txt: 'In 45 min in Florence. Ponte Vecchio bij zonsondergang.', km: '38 km', icoon: '☼' },
            { d: 'dag 04', titel: 'Pienza, agriturismo basis', txt: 'Lange rit zuidwaarts. Aankomst voor de lunch.', km: '128 km', icoon: '⌂' },
            { d: 'dag 05', titel: 'Siena & Piazza del Campo', txt: 'Dagje uit. Gelato verplicht.', km: '52 km', icoon: '✦' },
          ].map((r, i) => (
            <div key={i} style={{
              display: 'grid', gridTemplateColumns: '70px 80px 1fr 200px 60px',
              alignItems: 'baseline', gap: 24,
              padding: '24px 0', borderTop: i === 0 ? 'none' : '1px solid oklch(28% 0.04 250)',
            }}>
              <div className="font-mono" style={{ fontSize: 11, color: 'oklch(70% 0.04 80)' }}>{r.d}</div>
              <div style={{ fontFamily: 'var(--display)', fontSize: 36, color: 'var(--zomer)' }}>{r.icoon}</div>
              <div>
                <div style={{ fontFamily: 'var(--display)', fontSize: 32, lineHeight: 1.05 }}>{r.titel}</div>
                <div style={{ fontSize: 14, color: 'oklch(75% 0.02 80)', marginTop: 6, maxWidth: 440 }}>{r.txt}</div>
              </div>
              <div className="font-mono" style={{ fontSize: 11, color: 'oklch(70% 0.04 80)' }}>{r.km}</div>
              <div style={{ textAlign: 'right' }}>
                <a className="link-edit" style={{ color: 'var(--papier)', fontSize: 13 }}>open →</a>
              </div>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 32, textAlign: 'center', fontSize: 13, color: 'oklch(70% 0.04 80)' }}>
          ⌄ &nbsp; 4 dagen ingeklapt &nbsp; ⌄
        </div>
      </section>

      {/* Vergelijkbare bestemmingen */}
      <section style={{ padding: '80px 56px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: 36 }}>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 56, lineHeight: 0.95, maxWidth: 760 }}>
            Als je dít plant, kijk dan ook eens naar <span style={{ fontStyle: 'italic', color: 'var(--zomer-ink)' }}>deze vier.</span>
          </h2>
          <a className="link-edit" style={{ fontSize: 14 }}>Alle alternatieven →</a>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18 }}>
          {[
            { t: 'Umbrië', s: 'Italië', tag: 'rustiger broertje', k: '--lente' },
            { t: 'Provence', s: 'Frankrijk', tag: 'lavendel', k: '--herfst' },
            { t: 'Catalonië', s: 'Spanje', tag: 'kust + stad', k: '--zomer' },
            { t: 'Istrië', s: 'Kroatië', tag: 'onderschat', k: '--winter' },
          ].map((x, i) => (
            <a key={i} href="#" style={{
              display: 'block', textDecoration: 'none', color: 'inherit',
            }}>
              <PlaceholderBeeld ratio="4/5" label={`${x.t} stockmoment`} kleur={x.k} group={`0${i + 1}`} />
              <div style={{ marginTop: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <div>
                  <div style={{ fontFamily: 'var(--display)', fontSize: 28 }}>{x.t}</div>
                  <div style={{ fontSize: 12, color: 'var(--inkt-3)' }}>{x.s}</div>
                </div>
                <span className="sticker" style={{ color: `var(${x.k}-ink)`, fontSize: 11 }}>{x.tag}</span>
              </div>
            </a>
          ))}
        </div>
      </section>
    </div>
  );
}

window.Bestemming = Bestemming;
