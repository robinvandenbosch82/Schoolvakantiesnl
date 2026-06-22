// EuropeMap.jsx — gestileerde, zachte Europa-kaart gekleurd naar drukte per week.
// Gedeeld door homepage (mini) en de fullscreen druktekaart.

const { useState: useStateMap } = React;

// Vereenvoudigde, organische land-paden (viewBox 0 0 460 500).
// Niet geografisch exact — bewust zacht & vriendelijk gestileerd.
const COUNTRY_PATHS = {
  uk: "M96 70 q22 -10 34 6 q10 16 2 34 q8 14 -4 26 q-16 14 -34 6 q4 -18 -6 -28 q-14 -8 -8 -24 q10 -16 20 -26 z",
  nl: "M250 156 q26 -6 34 10 q4 16 -8 24 q-18 10 -32 2 q-8 -14 -2 -26 q2 -8 8 -10 z",
  be: "M236 196 q26 -4 34 10 q2 14 -12 20 q-18 6 -28 -6 q-4 -16 6 -24 z",
  de: "M286 142 q44 -10 64 8 q14 30 6 64 q-2 30 -22 44 q-30 8 -52 -6 q-14 -22 -10 -50 q-2 -34 14 -60 z",
  fr: "M196 226 q44 -14 70 6 q16 22 8 52 q-4 36 -30 56 q-30 12 -54 -6 q-18 -28 -12 -60 q2 -34 18 -54 z",
  at: "M324 256 q40 -8 60 8 q8 16 -8 26 q-32 12 -60 4 q-12 -14 -4 -28 q4 -8 12 -10 z",
  it: "M318 290 q26 -6 34 12 q6 28 -4 56 q14 30 -2 58 q-16 22 -30 6 q-2 -28 -8 -54 q-16 -22 -6 -50 q4 -22 16 -28 z",
  es: "M150 352 q56 -16 92 6 q12 26 -8 48 q-44 22 -94 8 q-18 -22 -8 -44 q6 -16 26 -26 z",
};
const LABEL_POS = {
  uk: [105, 110], nl: [266, 176], be: [252, 216], de: [322, 210],
  fr: [232, 290], at: [354, 280], it: [332, 360], es: [200, 392],
};

function drukteColor(v) {
  // 0..100 -> groen→amber→rood, kalm
  if (v < 38) return "var(--rustig)";
  if (v < 56) return "oklch(76% 0.135 120)";
  if (v < 70) return "var(--matig)";
  if (v < 84) return "oklch(72% 0.15 50)";
  return "var(--druk)";
}
window.drukteColor = drukteColor;

function EuropeMap({ countries, weekIdx, selected, onSelect, big }) {
  return (
    <svg viewBox="0 0 460 500" className={big ? "europe big" : "europe"} role="img" aria-label="Druktekaart Europa">
      {/* zachte zee-achtergrond */}
      <defs>
        <radialGradient id="sea" cx="45%" cy="40%" r="75%">
          <stop offset="0%" stopColor="oklch(97% 0.02 230)" />
          <stop offset="100%" stopColor="oklch(94% 0.022 235)" />
        </radialGradient>
      </defs>
      <rect x="0" y="0" width="460" height="500" rx="24" fill="url(#sea)" />
      {countries.map(function (c) {
        const v = c.drukteByWeek[weekIdx];
        const isSel = selected === c.code;
        return (
          <g key={c.code} onClick={function () { onSelect && onSelect(c.code); }}
             style={{ cursor: "pointer" }}>
            <path d={COUNTRY_PATHS[c.code]} fill={drukteColor(v)}
              className={"country-shape" + (isSel ? " sel" : "")}
              style={{ transform: isSel ? "scale(1.03)" : "none" }} />
            <text x={LABEL_POS[c.code][0]} y={LABEL_POS[c.code][1]}
              textAnchor="middle" fontSize={big ? 13 : 11} fontWeight="700"
              fill="oklch(28% 0.02 285)" style={{ pointerEvents: "none", fontFamily: "var(--sans)" }}>
              {big ? c.name : c.code.toUpperCase()}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

window.EuropeMap = EuropeMap;
