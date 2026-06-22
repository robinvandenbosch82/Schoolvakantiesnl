// data.js — gedeelde datalaag voor het v3-prototype
// Slim-score 0-100 combineert: drukte (laag=goed), prijs (laag=goed),
// weer (hoog=goed), overlap met andere landen (laag=goed).

window.SV = (function () {
  // helper: classificeer een score naar band
  function band(score) {
    if (score >= 70) return "rustig";
    if (score >= 45) return "matig";
    return "druk";
  }

  // 18 weken: mei t/m september 2026 (de relevante reisperiode)
  // elke week: weeknr, label, drukte 0-100 (hoog=druk), prijsindex 0-100 (hoog=duur),
  // weer 0-100 (hoog=mooi), overlap 0-100 (hoog=veel landen tegelijk vrij)
  const rawWeeks = [
    { wk: 19, d1: "4 mei",  drukte: 28, prijs: 34, weer: 52, overlap: 18 },
    { wk: 20, d1: "11 mei", drukte: 30, prijs: 36, weer: 58, overlap: 22 },
    { wk: 21, d1: "18 mei", drukte: 46, prijs: 52, weer: 62, overlap: 40 }, // hemelvaart
    { wk: 22, d1: "25 mei", drukte: 38, prijs: 44, weer: 66, overlap: 30 },
    { wk: 23, d1: "1 jun",  drukte: 34, prijs: 40, weer: 70, overlap: 26 },
    { wk: 24, d1: "8 jun",  drukte: 36, prijs: 42, weer: 74, overlap: 28 },
    { wk: 25, d1: "15 jun", drukte: 40, prijs: 46, weer: 78, overlap: 34 },
    { wk: 26, d1: "22 jun", drukte: 48, prijs: 54, weer: 80, overlap: 44 },
    { wk: 27, d1: "29 jun", drukte: 62, prijs: 66, weer: 82, overlap: 60 },
    { wk: 28, d1: "6 jul",  drukte: 74, prijs: 78, weer: 84, overlap: 72 },
    { wk: 29, d1: "13 jul", drukte: 86, prijs: 88, weer: 85, overlap: 84 },
    { wk: 30, d1: "20 jul", drukte: 92, prijs: 94, weer: 86, overlap: 92 }, // piek NL
    { wk: 31, d1: "27 jul", drukte: 96, prijs: 97, weer: 85, overlap: 96 }, // piek
    { wk: 32, d1: "3 aug",  drukte: 90, prijs: 92, weer: 84, overlap: 90 },
    { wk: 33, d1: "10 aug", drukte: 80, prijs: 84, weer: 82, overlap: 78 },
    { wk: 34, d1: "17 aug", drukte: 64, prijs: 70, weer: 78, overlap: 58 },
    { wk: 35, d1: "24 aug", drukte: 44, prijs: 50, weer: 72, overlap: 36 },
    { wk: 36, d1: "31 aug", drukte: 30, prijs: 38, weer: 66, overlap: 22 },
    { wk: 37, d1: "7 sep",  drukte: 22, prijs: 30, weer: 60, overlap: 14 },
    { wk: 38, d1: "14 sep", drukte: 24, prijs: 32, weer: 56, overlap: 16 },
  ];

  // Slim-score: gewogen, hoog = slim om te gaan
  const weeks = rawWeeks.map(function (w) {
    const score = Math.round(
      (100 - w.drukte) * 0.34 +
      (100 - w.prijs) * 0.30 +
      w.weer * 0.22 +
      (100 - w.overlap) * 0.14
    );
    return Object.assign({}, w, { score: score, band: band(score) });
  });

  // landen voor druktekaart + overlap (drukte per week index 0..19)
  // we genereren een drukteprofiel per land met eigen piekverschuiving
  function profile(peakIdx, spread, base) {
    return weeks.map(function (_, i) {
      const dist = Math.abs(i - peakIdx);
      const v = base + (100 - base) * Math.exp(-(dist * dist) / (2 * spread * spread));
      return Math.round(v);
    });
  }

  const countries = [
    { code: "nl", name: "Nederland",  flag: "🇳🇱", peak: 12, spread: 2.4, base: 24 },
    { code: "de", name: "Duitsland",  flag: "🇩🇪", peak: 14, spread: 3.2, base: 26 },
    { code: "fr", name: "Frankrijk",  flag: "🇫🇷", peak: 13, spread: 2.0, base: 22 },
    { code: "be", name: "België",     flag: "🇧🇪", peak: 12, spread: 2.6, base: 24 },
    { code: "it", name: "Italië",     flag: "🇮🇹", peak: 13, spread: 2.2, base: 28 },
    { code: "es", name: "Spanje",     flag: "🇪🇸", peak: 13, spread: 2.6, base: 30 },
    { code: "at", name: "Oostenrijk", flag: "🇦🇹", peak: 11, spread: 2.4, base: 22 },
    { code: "uk", name: "VK",         flag: "🇬🇧", peak: 14, spread: 2.8, base: 24 },
  ].map(function (c) {
    return Object.assign({}, c, { drukteByWeek: profile(c.peak, c.spread, c.base) });
  });

  // bestemmingen (warme cards, foto-eerst)
  const destinations = [
    { name: "Toscane",        land: "Italië",    img: "img/toscane.jpg",   slim: 84, gezin: 88, tag: "Rustig in september" },
    { name: "Algarve",        land: "Portugal",  img: "img/algarve.jpg",   slim: 79, gezin: 91, tag: "Strand & zon" },
    { name: "Beierse Alpen",  land: "Duitsland", img: "img/beieren.jpg",   slim: 76, gezin: 85, tag: "Korte reis" },
    { name: "Ardennen",       land: "België",    img: "img/ardennen.jpg",  slim: 81, gezin: 87, tag: "Natuur dichtbij" },
    { name: "Costa Brava",    land: "Spanje",    img: "img/costabrava.jpg",slim: 72, gezin: 84, tag: "Familiestranden" },
    { name: "Zeeland",        land: "Nederland", img: "img/zeeland.jpg",   slim: 86, gezin: 90, tag: "Geen reistijd" },
  ];

  // Duitse deelstaten met eigen vakantievenster (start..eind week)
  const bundeslander = [
    { name: "Beieren",              start: 30, eind: 36 },
    { name: "Baden-Württemberg",    start: 30, eind: 36 },
    { name: "Nordrhein-Westfalen",  start: 27, eind: 33 },
    { name: "Niedersachsen",        start: 26, eind: 32 },
    { name: "Hessen",               start: 27, eind: 33 },
    { name: "Berlin",               start: 25, eind: 31 },
    { name: "Sachsen",              start: 26, eind: 32 },
    { name: "Hamburg",              start: 25, eind: 31 },
  ];

  return {
    weeks: weeks,
    countries: countries,
    destinations: destinations,
    bundeslander: bundeslander,
    band: band,
  };
})();
