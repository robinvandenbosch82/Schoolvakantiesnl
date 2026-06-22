// CountryPicker.jsx — gedeelde, schaalbare landenkiezer (heel Europa).
// Gebruikt op de landenpagina, homepage-hero en planner voor consistente landselectie.

const { useState: useStateCP, useEffect: useEffectCP, useRef: useRefCP } = React;

// Heel Europa in het menu. live:true = data nu al via OpenHolidays.
window.EUROPE = [
  { code: "nl", name: "Nederland", flag: "🇳🇱", live: true, pop: true },
  { code: "de", name: "Duitsland", flag: "🇩🇪", live: true, pop: true },
  { code: "be", name: "België", flag: "🇧🇪", pop: true },
  { code: "fr", name: "Frankrijk", flag: "🇫🇷", pop: true },
  { code: "es", name: "Spanje", flag: "🇪🇸", pop: true },
  { code: "it", name: "Italië", flag: "🇮🇹", pop: true },
  { code: "at", name: "Oostenrijk", flag: "🇦🇹", pop: true },
  { code: "pt", name: "Portugal", flag: "🇵🇹", pop: true },
  { code: "ch", name: "Zwitserland", flag: "🇨🇭" },
  { code: "gb", name: "Verenigd Koninkrijk", flag: "🇬🇧" },
  { code: "ie", name: "Ierland", flag: "🇮🇪" },
  { code: "dk", name: "Denemarken", flag: "🇩🇰" },
  { code: "se", name: "Zweden", flag: "🇸🇪" },
  { code: "no", name: "Noorwegen", flag: "🇳🇴" },
  { code: "fi", name: "Finland", flag: "🇫🇮" },
  { code: "pl", name: "Polen", flag: "🇵🇱" },
  { code: "cz", name: "Tsjechië", flag: "🇨🇿" },
  { code: "sk", name: "Slowakije", flag: "🇸🇰" },
  { code: "hu", name: "Hongarije", flag: "🇭🇺" },
  { code: "si", name: "Slovenië", flag: "🇸🇮" },
  { code: "hr", name: "Kroatië", flag: "🇭🇷" },
  { code: "gr", name: "Griekenland", flag: "🇬🇷" },
  { code: "lu", name: "Luxemburg", flag: "🇱🇺" },
  { code: "li", name: "Liechtenstein", flag: "🇱🇮" },
  { code: "mt", name: "Malta", flag: "🇲🇹" },
  { code: "ee", name: "Estland", flag: "🇪🇪" },
  { code: "lv", name: "Letland", flag: "🇱🇻" },
  { code: "lt", name: "Litouwen", flag: "🇱🇹" },
  { code: "bg", name: "Bulgarije", flag: "🇧🇬" },
  { code: "ro", name: "Roemenië", flag: "🇷🇴" },
];

// props: land (code), onPick(code), compact (bool), showStatus (bool)
window.CountryPicker = function CountryPicker({ land, onPick, compact, showStatus }) {
  const [open, setOpen] = useStateCP(false);
  const [q, setQ] = useStateCP("");
  const ref = useRefCP(null);
  const EUROPE = window.EUROPE;
  const cur = EUROPE.find(function (c) { return c.code === land; }) || EUROPE[0];

  useEffectCP(function () {
    function onDoc(e) { if (ref.current && !ref.current.contains(e.target)) { setOpen(false); setQ(""); } }
    document.addEventListener("mousedown", onDoc);
    return function () { document.removeEventListener("mousedown", onDoc); };
  }, []);

  const term = q.trim().toLowerCase();
  const matches = EUROPE.filter(function (c) { return c.name.toLowerCase().indexOf(term) >= 0; });
  const popular = matches.filter(function (c) { return c.pop; });

  function pick(c) { onPick(c.code); setOpen(false); setQ(""); }

  function Row({ c }) {
    return (
      <button className={"cp-row" + (c.code === land ? " on" : "")} onClick={function () { pick(c); }}>
        <span className="cp-flag">{c.flag}</span>
        <span className="cp-name">{c.name}</span>
        {c.live ? <span className="cp-live">live</span> : <span className="cp-soon">binnenkort</span>}
      </button>
    );
  }

  return (
    <div className={"country-picker" + (compact ? " compact" : "")} ref={ref}>
      <button className="cp-trigger" onClick={function () { setOpen(!open); }} aria-expanded={open}>
        <span className="cp-flag">{cur.flag}</span>
        <span className="cp-trigger-name">{cur.name}</span>
        {showStatus && (cur.live ? <span className="cp-live">live</span> : <span className="cp-soon">binnenkort</span>)}
        <svg className={"cp-chev" + (open ? " up" : "")} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9l6 6 6-6"/></svg>
      </button>
      {open && (
        <div className="cp-panel">
          <div className="cp-search">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
            <input autoFocus value={q} onChange={function (e) { setQ(e.target.value); }} placeholder="Zoek een land…" />
          </div>
          <div className="cp-list">
            {term === "" && (
              <React.Fragment>
                <div className="cp-group">Populair</div>
                {popular.map(function (c) { return <Row key={c.code} c={c} />; })}
                <div className="cp-group">Alle landen</div>
              </React.Fragment>
            )}
            {matches.map(function (c) {
              if (term === "" && c.pop) return null;
              return <Row key={c.code} c={c} />;
            })}
            {matches.length === 0 && <div className="cp-empty">Geen land gevonden voor “{q}”.</div>}
          </div>
          <div className="cp-foot"><span className="cp-livedot"></span>Live landen tonen direct alle schoolvakanties &amp; feestdagen.</div>
        </div>
      )}
    </div>
  );
};
