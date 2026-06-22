// Mobiel.jsx — volwaardige mobiele suite: 5 interactieve telefoonschermen
// (Home, Planner, Landen, Druktekaart, Blog) in realistische device-frames.

const { useState: useStateM, useEffect: useEffectM } = React;

/* ---------- device frame met statusbalk + bottom tab ---------- */
function StatusBar({ dark }) {
  return (
    <div className={"sb" + (dark ? " dark" : "")}>
      <span className="sb-time mono">9:41</span>
      <span className="sb-icons">
        <svg width="17" height="11" viewBox="0 0 17 11" fill="currentColor"><rect x="0" y="7" width="3" height="4" rx="1"/><rect x="4.5" y="5" width="3" height="6" rx="1"/><rect x="9" y="2.5" width="3" height="8.5" rx="1"/><rect x="13.5" y="0" width="3" height="11" rx="1"/></svg>
        <svg width="16" height="11" viewBox="0 0 16 11" fill="currentColor"><path d="M8 2.2c2 0 3.8.8 5.1 2.1l1.2-1.2C13.6 1.4 11 0.4 8 0.4S2.4 1.4.7 3.1l1.2 1.2C3.2 3 5 2.2 8 2.2Z"/><path d="M8 5c1.1 0 2.1.45 2.8 1.18l1.2-1.2C10.9 3.9 9.5 3.3 8 3.3s-2.9.6-4 1.68l1.2 1.2C5.9 5.45 6.9 5 8 5Z"/><circle cx="8" cy="8.6" r="1.7"/></svg>
        <span className="sb-bat"><i></i></span>
      </span>
    </div>
  );
}

function TabBar({ active, onTab }) {
  const tabs = [
    { id: "home", label: "Home", icon: "M3 11l9-7 9 7M5 10v9a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-9" },
    { id: "land", label: "Vakanties", icon: "M8 2v3M16 2v3M3 9h18M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z" },
    { id: "kaart", label: "Kaart", icon: "M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2ZM9 4v14M15 6v14" },
    { id: "blog", label: "Blog", icon: "M4 5h16M4 12h16M4 19h10" },
  ];
  return (
    <div className="tabbar">
      {tabs.map(function (t) {
        return (
          <button key={t.id} className={"tab" + (active === t.id ? " on" : "")} onClick={function () { onTab && onTab(t.id); }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d={t.icon}/></svg>
            <span>{t.label}</span>
          </button>
        );
      })}
    </div>
  );
}

function Phone({ label, active, onTab, children, noTab }) {
  return (
    <div className="phone-wrap">
      <div className="phone">
        <div className="phone-island"></div>
        <div className="phone-screen">
          <StatusBar />
          <div className="m-scroll">{children}</div>
          {!noTab && <TabBar active={active} onTab={onTab} />}
        </div>
      </div>
      <span className="phone-label">{label}</span>
    </div>
  );
}

/* ---------- mini score-ring ---------- */
function MiniRing({ score, band, size }) {
  const s = size || 76;
  const cls = band === "rustig" ? "is-rustig" : band === "matig" ? "is-matig" : "is-druk";
  const r = (s - 16) / 2, circ = 2 * Math.PI * r, off = circ * (1 - score / 100);
  return (
    <div className={"mring " + cls} style={{ width: s, height: s }}>
      <svg width={s} height={s} viewBox={"0 0 " + s + " " + s}>
        <circle cx={s/2} cy={s/2} r={r} fill="none" stroke="var(--line)" strokeWidth="7" />
        <circle cx={s/2} cy={s/2} r={r} fill="none" stroke="var(--c)" strokeWidth="7" strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={off} transform={"rotate(-90 " + s/2 + " " + s/2 + ")"} />
      </svg>
      <span className="mring-val mono" style={{ fontSize: s * 0.29 }}>{score}</span>
    </div>
  );
}

function bandLabel(b) { return b === "rustig" ? "Slimme week" : b === "matig" ? "Redelijk" : "Druk"; }
function bandCls(b) { return b === "rustig" ? "is-rustig" : b === "matig" ? "is-matig" : "is-druk"; }

function WeekBars({ weeks, sel, onSel }) {
  return (
    <div className="m-chart">
      {weeks.map(function (w, i) {
        return (
          <button key={w.wk} className={"m-bar " + bandCls(w.band) + (i === sel ? " on" : "")} onClick={function () { onSel(i); }}>
            <span className="m-bar-fill" style={{ height: Math.max(8, w.score) + "%" }}></span>
          </button>
        );
      })}
    </div>
  );
}

/* ===================== SCHERMEN ===================== */

function ScreenHome({ onTab }) {
  const W = window.SV.weeks;
  const best = W.reduce(function (b, w, i) { return w.score > W[b].score ? i : b; }, 0);
  const [sel, setSel] = useStateM(best);
  const cur = W[sel];
  const D = window.SV.destinations.slice(0, 3);
  return (
    <React.Fragment>
      <div className="m-app">
        <div className="m-appbar">
          <span className="m-brand">Schoolvakanties<b>.nl</b></span>
          <span className="m-avatar">👨‍👩‍👧</span>
        </div>
        <div className="m-pad">
          <h3 className="m-h">Ga weg wanneer het <span className="acc">rustig</span> is.</h3>
          <div className="m-seg">
            {["mei", "jun", "jul", "aug", "sep"].map(function (m, i) {
              return <button key={m} className={i === 4 ? "on" : ""}>{m}</button>;
            })}
          </div>

          <div className="m-radar">
            <span className="m-radar-eye mono">REISWEEK-RADAR</span>
            <div className="m-radar-top">
              <MiniRing score={cur.score} band={cur.band} />
              <div className="m-radar-info">
                <span className="mono m-wk">WEEK {cur.wk}</span>
                <strong>{cur.d1}</strong>
                <span className={"m-pill " + bandCls(cur.band)}>{bandLabel(cur.band)}</span>
              </div>
            </div>
            <WeekBars weeks={W} sel={sel} onSel={setSel} />
            <div className="m-factors">
              <span><i className="is-druk"></i>Drukte {cur.drukte}</span>
              <span><i className="is-matig"></i>Prijs {cur.prijs}</span>
              <span><i className="is-rustig"></i>Weer {cur.weer}</span>
            </div>
          </div>

          <div className="m-sec-head"><h4>Slim &amp; gezinsvriendelijk</h4><span onClick={function(){ onTab("kaart"); }}>Meer</span></div>
          <div className="m-destrow">
            {D.map(function (d) {
              return (
                <div key={d.name} className="m-destcard">
                  <div className="m-destimg"><img src={d.img} alt={d.name} /><span className={"m-destscore " + bandCls(d.slim>=70?'rustig':d.slim>=45?'matig':'druk')}>{d.slim}</span></div>
                  <div className="m-destname">{d.name}</div>
                  <div className="m-destland">{d.land}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      <div className="m-fab"><button className="btn" onClick={function(){ onTab("planner"); }}>Open de planner →</button></div>
    </React.Fragment>
  );
}

function ScreenPlanner({ onTab }) {
  const W = window.SV.weeks;
  const best = W.reduce(function (b, w, i) { return w.score > W[b].score ? i : b; }, 0);
  const [sel, setSel] = useStateM(best);
  const [kids, setKids] = useStateM(2);
  const cur = W[sel];
  // alternatief advies
  const alt = W.map(function (w, i) { return { w: w, i: i }; }).filter(function (x) { return x.i !== sel; }).sort(function (a, b) { return b.w.score - a.w.score; })[0];
  return (
    <React.Fragment>
      <div className="m-app">
        <div className="m-appbar">
          <button className="m-back" onClick={function(){ onTab("home"); }}>←</button>
          <span className="m-brand">Planner</span>
          <span></span>
        </div>
        <div className="m-pad">
          <div className="m-inputs">
            <div className="m-inp"><span>Volwassenen</span><div className="m-step"><button>–</button><b className="mono">2</b><button>+</button></div></div>
            <div className="m-inp"><span>Kinderen</span><div className="m-step"><button onClick={function(){ setKids(Math.max(0,kids-1)); }}>–</button><b className="mono">{kids}</b><button onClick={function(){ setKids(kids+1); }}>+</button></div></div>
          </div>
          <div className="m-seg">
            {["NL", "Noord", "Midden", "Zuid"].map(function (r, i) {
              return <button key={r} className={i === 0 ? "on" : ""}>{r}</button>;
            })}
          </div>

          <div className="m-radar">
            <div className="m-radar-top">
              <MiniRing score={cur.score} band={cur.band} size={84} />
              <div className="m-radar-info">
                <span className="mono m-wk">WEEK {cur.wk} · {cur.d1}</span>
                <strong>Slim-score {cur.score}</strong>
                <span className={"m-pill " + bandCls(cur.band)}>{bandLabel(cur.band)}</span>
              </div>
            </div>
            <WeekBars weeks={W} sel={sel} onSel={setSel} />
          </div>

          <div className={"m-advice " + bandCls(cur.band)}>
            <span className="m-advice-ic">⚑</span>
            <p>Week {cur.wk} is {cur.band === "rustig" ? "een slimme week — rustig én betaalbaar." : "drukker. Probeer week " + alt.w.wk + " (" + alt.w.d1 + "): score " + alt.w.score + "."}</p>
          </div>

          <div className="m-detailgrid">
            <div className="m-detail"><span>Drukte</span><b className="mono">{cur.drukte}</b></div>
            <div className="m-detail"><span>Prijs</span><b className="mono">{cur.prijs}</b></div>
            <div className="m-detail"><span>Weer</span><b className="mono">{cur.weer}</b></div>
            <div className="m-detail"><span>Overlap</span><b className="mono">{cur.overlap}</b></div>
          </div>
        </div>
      </div>
      <div className="m-fab"><button className="btn" onClick={function(){ onTab("kaart"); }}>Bekijk bestemmingen</button></div>
    </React.Fragment>
  );
}

function ScreenLand({ onTab }) {
  const [data, setData] = useStateM(null);
  const [cd, setCd] = useStateM(null);
  useEffectM(function () {
    let alive = true;
    window.Holidays.getYearData("nl", 2026).then(function (d) {
      if (!alive) return;
      setData(d);
      const vandaag = new Date(); vandaag.setHours(0,0,0,0);
      const items = d.vakanties.map(function (v) {
        const start = window.Holidays.helpers.parse(v.minStart);
        return { naam: v.naam, dagen: Math.round((start - vandaag)/86400000) };
      }).filter(function (x){ return x.dagen>=0; }).sort(function(a,b){return a.dagen-b.dagen;}).slice(0,4);
      setCd(items);
    }).catch(function(){});
    return function(){ alive = false; };
  }, []);
  return (
    <React.Fragment>
      <div className="m-app">
        <div className="m-appbar"><span className="m-brand">Schoolvakanties</span><span className="m-livedot"></span></div>
        <div className="m-pad">
          <div className="m-landswitch">
            <button className="on">🇳🇱 NL</button><button>🇩🇪 DE</button>
          </div>
          <div className="m-yearrow">
            {[2026,2027,2028,2029].map(function(y,i){ return <button key={y} className={i===0?"on":""}>{y}</button>; })}
          </div>
          <div className="m-vooruit">📅 Eerstvolgende: <b>{cd ? cd[0].naam : "…"}</b>{cd && <span> · nog {cd[0].dagen} dagen</span>}</div>

          <div className="m-sec-head"><h4>Aankomende vakanties</h4><span className="m-livetag">live</span></div>
          <div className="m-cdlist">
            {cd ? cd.map(function(it){
              return <div key={it.naam} className="m-cdrow"><span>{it.naam}</span><b className="mono">{it.dagen} d</b></div>;
            }) : <div className="m-skel">Laden…</div>}
          </div>

          <div className="m-sec-head"><h4>Zomervakantie 2026</h4></div>
          <div className="m-vaktable">
            {data && data.vakanties.filter(function(v){return /zomer/i.test(v.naam);}).map(function(v){
              return ["Noord","Midden","Zuid"].map(function(r){
                return <div key={r} className="m-vakrow"><span className="m-vakreg">{r}</span><span className="m-vakper">{v.perRegio[r]}</span></div>;
              });
            })}
          </div>
        </div>
      </div>
      <div className="m-fab"><button className="btn" onClick={function(){ onTab("planner"); }}>Plan slimste week</button></div>
    </React.Fragment>
  );
}

function ScreenKaart({ onTab }) {
  const C = window.SV.countries;
  const W = window.SV.weeks;
  const [wk, setWk] = useStateM(11);
  const [sel, setSel] = useStateM("it");
  const ranked = C.map(function(c){ return { c:c, v:c.drukteByWeek[wk] }; }).sort(function(a,b){return a.v-b.v;});
  return (
    <React.Fragment>
      <div className="m-app">
        <div className="m-appbar"><span className="m-brand">Druktekaart</span><span className="m-livedot"></span></div>
        <div className="m-pad">
          <div className="m-mapbox">
            <window.EuropeMap countries={C} weekIdx={wk} selected={sel} onSelect={setSel} />
          </div>
          <div className="m-wkslider">
            <span className="mono">WK {W[wk].wk}</span>
            <input type="range" min="0" max={W.length-1} value={wk} onChange={function(e){ setWk(+e.target.value); }} />
          </div>
          <div className="m-sec-head"><h4>Rustigste landen · wk {W[wk].wk}</h4></div>
          <div className="m-ranklist">
            {ranked.slice(0,6).map(function(r){
              return (
                <div key={r.c.code} className={"m-rankrow" + (sel===r.c.code?" on":"")} onClick={function(){ setSel(r.c.code); }}>
                  <span className="m-flag">{r.c.flag}</span>
                  <span className="m-rankname">{r.c.name}</span>
                  <span className="m-rankbar"><i style={{ width:r.v+"%", background:window.drukteColor(r.v) }}></i></span>
                  <span className="mono m-rankval">{r.v}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </React.Fragment>
  );
}

function ScreenBlog({ onTab }) {
  const posts = window.BLOG.posts;
  const feat = posts.find(function(p){return p.featured;}) || posts[0];
  const rest = posts.filter(function(p){return p!==feat;}).slice(0,3);
  return (
    <React.Fragment>
      <div className="m-app">
        <div className="m-appbar"><span className="m-brand">Blog</span><span className="m-search">🔍</span></div>
        <div className="m-pad">
          <div className="m-chips">
            {["Alle","Slim plannen","Bestemmingen","Met kinderen"].map(function(c,i){
              return <button key={c} className={i===0?"on":""}>{c}</button>;
            })}
          </div>
          <div className="m-featpost">
            <div className="m-featimg"><img src={feat.img} alt={feat.titel} /><span className="m-featbadge">Uitgelicht</span></div>
            <div className="m-featbody">
              <span className="m-cat">{feat.cat}</span>
              <h4>{feat.titel}</h4>
              <span className="m-postmeta">{feat.datum} · {feat.leestijd} min</span>
            </div>
          </div>
          {rest.map(function(p){
            return (
              <div key={p.id} className="m-postrow">
                <div className="m-postthumb"><img src={p.img} alt={p.titel} /></div>
                <div className="m-postinfo">
                  <span className="m-cat">{p.cat}</span>
                  <h5>{p.titel}</h5>
                  <span className="m-postmeta">{p.leestijd} min</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </React.Fragment>
  );
}

/* ===================== SUITE ===================== */
function Mobiel() {
  // elk toestel heeft eigen actieve tab zodat ze los te bedienen zijn
  const SCREENS = {
    home: ScreenHome, planner: ScreenPlanner, land: ScreenLand, kaart: ScreenKaart, blog: ScreenBlog,
  };
  function Device({ initial, label }) {
    const [tab, setTab] = useStateM(initial);
    const Screen = SCREENS[tab] || SCREENS.home;
    const tabActive = tab === "planner" ? "home" : tab; // planner valt onder home-tab
    return (
      <Phone label={label} active={tabActive} onTab={setTab}>
        <Screen onTab={setTab} />
      </Phone>
    );
  }

  return (
    <div className="page mobiel rise">
      <div className="mobiel-head">
        <span className="eye">Mobiel · 70% van het verkeer</span>
        <h1>Ontworpen voor de duim.</h1>
        <p className="lead">Het antwoord boven de vouw, een vaste tabbalk onderaan en swipebare weken. Tik op de schermen — ze werken echt. Dezelfde tools, verkleind tot de essentie.</p>
      </div>

      <div className="phones">
        <Device initial="home" label="Home" />
        <Device initial="planner" label="Planner" />
        <Device initial="land" label="Vakanties (live)" />
        <Device initial="kaart" label="Druktekaart" />
        <Device initial="blog" label="Blog" />
      </div>
    </div>
  );
}

window.Mobiel = Mobiel;
