// Header.jsx — topbar met landen-mega-menu (echte links, SEO-vriendelijk)
// + full-screen mobiel menu. Vervangt de inline header in v3.html.

const { useState: useStateHdr, useEffect: useEffectHdr, useRef: useRefHdr } = React;

const HDR_NAV = [
  { id: "home", label: "Home" },
  { id: "land", label: "Landen", mega: true },
  { id: "planner", label: "Planner" },
  { id: "kaart", label: "Druktekaart" },
  { id: "blog", label: "Blog" },
  { id: "over", label: "Over ons" },
  { id: "mobiel", label: "Mobiel" },
];

const HDR_QUICK = [
  { id: "planner", label: "Vakantieplanner", desc: "Slimste reisweken per gezin", ic: "◎" },
  { id: "kaart", label: "Europese druktekaart", desc: "Heel Europa, week voor week", ic: "🗺" },
  { id: "blog", label: "Blog & reistips", desc: "Slim weg met de kinderen", ic: "✎" },
];

function landSlug(c) {
  return (c.name || "").toLowerCase()
    .replace(/ë/g, "e").replace(/ï/g, "i").replace(/[^a-z]+/g, "-").replace(/^-|-$/g, "");
}

function Logo() {
  return (
    <span className="mark">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 11l9-7 9 7"/><path d="M5 10v9a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-9"/><path d="M9 20v-5h6v5"/></svg>
    </span>
  );
}

function Flag({ c }) {
  return c.live
    ? <span className="ml-status live">live</span>
    : <span className="ml-status soon">binnenkort</span>;
}

function Header({ route, goTo }) {
  const [mega, setMega] = useStateHdr(false);
  const [mobile, setMobile] = useStateHdr(false);
  const [mobLanden, setMobLanden] = useStateHdr(true);
  const wrapRef = useRefHdr(null);
  const EUROPE = window.EUROPE || [];
  const popular = EUROPE.filter(function (c) { return c.pop; });
  const all = EUROPE.slice().sort(function (a, b) { return a.name.localeCompare(b.name, "nl"); });

  // sluit mega bij klik buiten / Esc
  useEffectHdr(function () {
    function onDoc(e) { if (wrapRef.current && !wrapRef.current.contains(e.target)) setMega(false); }
    function onKey(e) { if (e.key === "Escape") { setMega(false); setMobile(false); } }
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return function () { document.removeEventListener("mousedown", onDoc); document.removeEventListener("keydown", onKey); };
  }, []);

  // scroll-lock bij open mobiel menu
  useEffectHdr(function () {
    document.body.style.overflow = mobile ? "hidden" : "";
    return function () { document.body.style.overflow = ""; };
  }, [mobile]);

  function nav(id) { setMega(false); setMobile(false); goTo(id); }
  function pickLand(e, c) { if (e) e.preventDefault(); setMega(false); setMobile(false); goTo("land"); }

  function CountryLink({ c, big }) {
    return (
      <a className={"ml-country" + (big ? " big" : "")} href={"/landen/" + landSlug(c)}
        onClick={function (e) { pickLand(e, c); }}>
        <span className="ml-flag">{c.flag}</span>
        <span className="ml-name">{c.name}</span>
        <Flag c={c} />
      </a>
    );
  }

  return (
    <header className="topbar" ref={wrapRef}>
      <div className="topbar-in">
        <div className="brand" onClick={function () { nav("home"); }} style={{ cursor: "pointer" }}>
          <Logo />
          Schoolvakanties<span style={{ color: "var(--accent)" }}>.nl</span>
        </div>

        <nav className="nav">
          {HDR_NAV.map(function (n) {
            if (n.mega) {
              return (
                <button key={n.id}
                  className={(route === n.id ? "on " : "") + "has-mega" + (mega ? " open" : "")}
                  onClick={function () { setMega(!mega); }}
                  onMouseEnter={function () { setMega(true); }}>
                  {n.label}
                  <svg className="nav-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9l6 6 6-6"/></svg>
                </button>
              );
            }
            return <button key={n.id} className={route === n.id ? "on" : ""}
              onClick={function () { nav(n.id); }}>{n.label}</button>;
          })}
        </nav>

        <div className="right">
          <button className="btn-ghost hide-sm">Inloggen</button>
          <button className="hamb" aria-label="Menu" onClick={function () { setMobile(true); }}>
            <span></span><span></span><span></span>
          </button>
        </div>
      </div>

      {/* DESKTOP MEGA-MENU */}
      {mega && (
        <div className="mega" onMouseLeave={function () { setMega(false); }}>
          <div className="mega-in">
            <div className="mega-col feat">
              <div className="mega-eye">Populaire landen</div>
              <div className="mega-pop">
                {popular.map(function (c) { return <CountryLink key={c.code} c={c} big />; })}
              </div>
            </div>
            <div className="mega-col">
              <div className="mega-eye">Alle landen in Europa</div>
              <div className="mega-all">
                {all.map(function (c) { return <CountryLink key={c.code} c={c} />; })}
              </div>
            </div>
            <div className="mega-col side">
              <div className="mega-eye">Slim plannen</div>
              <div className="mega-quick">
                {HDR_QUICK.map(function (q) {
                  return (
                    <a key={q.id} className="mq" href={"/" + q.id}
                      onClick={function (e) { e.preventDefault(); nav(q.id); }}>
                      <span className="mq-ic">{q.ic}</span>
                      <span className="mq-tx"><b>{q.label}</b><i>{q.desc}</i></span>
                    </a>
                  );
                })}
              </div>
              <a className="mega-allbtn" href="/landen" onClick={function (e) { pickLand(e); }}>
                Alle landen bekijken
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
              </a>
            </div>
          </div>
        </div>
      )}

      {/* FULL-SCREEN MOBIEL MENU */}
      {mobile && (
        <div className="mobnav">
          <div className="mobnav-top">
            <div className="brand"><Logo />Schoolvakanties<span style={{ color: "var(--accent)" }}>.nl</span></div>
            <button className="mobnav-x" aria-label="Sluiten" onClick={function () { setMobile(false); }}>
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
            </button>
          </div>

          <div className="mobnav-body">
            <nav className="mobnav-main">
              {HDR_NAV.filter(function (n) { return !n.mega; }).map(function (n) {
                return <button key={n.id} className={route === n.id ? "on" : ""}
                  onClick={function () { nav(n.id); }}>{n.label}</button>;
              })}
            </nav>

            <div className="mobnav-sec">
              <button className={"mobnav-acc" + (mobLanden ? " open" : "")}
                onClick={function () { setMobLanden(!mobLanden); }}>
                Landen
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9l6 6 6-6"/></svg>
              </button>
              {mobLanden && (
                <div className="mobnav-landen">
                  {all.map(function (c) {
                    return (
                      <a key={c.code} className="mobnav-land" href={"/landen/" + landSlug(c)}
                        onClick={function (e) { pickLand(e, c); }}>
                        <span className="ml-flag">{c.flag}</span>
                        <span className="ml-name">{c.name}</span>
                        <Flag c={c} />
                      </a>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          <div className="mobnav-foot">
            <button className="btn lg" onClick={function () { nav("planner"); }}>Open de planner</button>
            <button className="btn-ghost" onClick={function () { setMobile(false); }}>Inloggen</button>
          </div>
        </div>
      )}
    </header>
  );
}

window.Header = Header;
