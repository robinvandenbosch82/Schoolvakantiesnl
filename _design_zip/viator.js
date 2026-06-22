// viator.js — affiliate-datalaag in Viator Partner API-vorm.
// Activiteiten voor de live landen (NL + DE), getagd op thema/seizoen zodat ze
// meebewegen met het vakantietype (Kerst → kerstmarkt, Zomer → city tour, enz.).
// In productie: server-side ophalen via de Viator Partner API en deze structuur
// 1-op-1 vullen. De affiliateUrl draagt de partner-ID (mcid/pid) voor commissie.

window.VIATOR = (function () {
  const PARTNER = "P00146821"; // voorbeeld partner-ID (mcid)
  function aff(city, slug, dest, prod) {
    return "https://www.viator.com/tours/" + city + "/" + slug + "/d" + dest + "-" + prod +
      "?pid=" + PARTNER + "&mcid=42383&medium=link";
  }

  // thema's met label + bijbehorende vakantieperiodes
  const THEMES = [
    { key: "kerst", label: "Kerst & winter", emoji: "🎄" },
    { key: "zomer", label: "Zomer & stad", emoji: "☀️" },
    { key: "herfst", label: "Herfst & cultuur", emoji: "🍂" },
    { key: "lente", label: "Lente & natuur", emoji: "🌷" },
    { key: "familie", label: "Met kinderen", emoji: "👨‍👩‍👧" },
  ];

  // koppel vakantienaam → thema-key (voor automatische selectie)
  function themeForVacation(naam) {
    const n = (naam || "").toLowerCase();
    if (/weihnacht|kerst|winter/.test(n)) return "kerst";
    if (/sommer|zomer/.test(n)) return "zomer";
    if (/herbst|herfst/.test(n)) return "herfst";
    if (/oster|pfingst|voorjaar|mei|frühjahr|fasching/.test(n)) return "lente";
    return "familie";
  }

  const activities = {
    nl: [
      { code: "5010AMS", title: "Amsterdam lichtjes-grachtcruise", city: "amsterdam", dest: "525", img: "img/act-boottocht.jpg",
        rating: 4.8, reviews: 18420, duration: "1,5 uur", priceFrom: 24, themes: ["zomer", "stad", "familie"], plek: "Amsterdam" },
      { code: "5011AMS", title: "Wintermarkt & oliebollen-wandeling", city: "amsterdam", dest: "525", img: "img/act-kerstmarkt.jpg",
        rating: 4.6, reviews: 2140, duration: "2 uur", priceFrom: 29, themes: ["kerst", "winter", "food"], plek: "Amsterdam" },
      { code: "5021KIN", title: "Kinderdijk molens & boottocht", city: "kinderdijk", dest: "60106", img: "img/act-fietstour.jpg",
        rating: 4.7, reviews: 5310, duration: "3 uur", priceFrom: 39, themes: ["lente", "natuur", "familie"], plek: "Kinderdijk" },
      { code: "5030ZEE", title: "Zeeland strand & duinen dagtrip", city: "zeeland", dest: "60112", img: "img/act-strand.jpg",
        rating: 4.5, reviews: 980, duration: "Hele dag", priceFrom: 45, themes: ["zomer", "natuur", "familie"], plek: "Domburg" },
      { code: "5040UTR", title: "Rijksmuseum skip-the-line + gids", city: "amsterdam", dest: "525", img: "img/act-museum.jpg",
        rating: 4.9, reviews: 9870, duration: "2,5 uur", priceFrom: 59, themes: ["herfst", "cultuur", "familie"], plek: "Amsterdam" },
      { code: "5050EFT", title: "Sprookjespark dagje uit", city: "kaatsheuvel", dest: "60120", img: "img/act-pretpark.jpg",
        rating: 4.8, reviews: 12300, duration: "Hele dag", priceFrom: 41, themes: ["familie", "zomer", "herfst"], plek: "Kaatsheuvel" },
      { code: "5060KEU", title: "Keukenhof tulpentuinen + entree", city: "lisse", dest: "60130", img: "img/act-fietstour.jpg",
        rating: 4.7, reviews: 7640, duration: "4 uur", priceFrom: 35, themes: ["lente", "natuur", "familie"], plek: "Lisse" },
      { code: "5070DEN", title: "Den Haag & Scheveningen kustfietstour", city: "den-haag", dest: "60140", img: "img/act-citytour.jpg",
        rating: 4.6, reviews: 1450, duration: "3 uur", priceFrom: 32, themes: ["zomer", "stad", "natuur"], plek: "Den Haag" },
    ],
    de: [
      { code: "6010BER", title: "Berlijnse kerstmarkten-avondtour", city: "berlijn", dest: "488", img: "img/act-kerstmarkt.jpg",
        rating: 4.8, reviews: 6210, duration: "2,5 uur", priceFrom: 34, themes: ["kerst", "winter", "food"], plek: "Berlijn" },
      { code: "6011MUN", title: "München stad & Marienplatz hoogtepunten", city: "munchen", dest: "489", img: "img/act-citytour.jpg",
        rating: 4.7, reviews: 8930, duration: "3 uur", priceFrom: 29, themes: ["zomer", "stad", "familie"], plek: "München" },
      { code: "6020NEU", title: "Slot Neuschwanstein dagtrip vanuit München", city: "fussen", dest: "60210", img: "img/act-kasteel.jpg",
        rating: 4.6, reviews: 14200, duration: "Hele dag", priceFrom: 65, themes: ["herfst", "cultuur", "familie"], plek: "Füssen" },
      { code: "6030RHE", title: "Rijnvallei & kasteel boottocht", city: "rudesheim", dest: "60220", img: "img/act-boottocht.jpg",
        rating: 4.7, reviews: 3120, duration: "4 uur", priceFrom: 49, themes: ["zomer", "natuur", "familie"], plek: "Rüdesheim" },
      { code: "6040HAM", title: "Hamburg haven & Miniatur Wunderland", city: "hamburg", dest: "60230", img: "img/act-museum.jpg",
        rating: 4.9, reviews: 11050, duration: "Halve dag", priceFrom: 38, themes: ["familie", "herfst", "stad"], plek: "Hamburg" },
      { code: "6050EUR", title: "Europa-Park dagje uit", city: "rust", dest: "60240", img: "img/act-pretpark.jpg",
        rating: 4.8, reviews: 9600, duration: "Hele dag", priceFrom: 56, themes: ["familie", "zomer", "herfst"], plek: "Rust" },
      { code: "6060SCH", title: "Zwarte Woud & watervallen wandeltour", city: "triberg", dest: "60250", img: "img/act-fietstour.jpg",
        rating: 4.6, reviews: 2240, duration: "5 uur", priceFrom: 44, themes: ["lente", "natuur", "herfst"], plek: "Triberg" },
      { code: "6070DRE", title: "Dresden Striezelmarkt & oude stad", city: "dresden", dest: "60260", img: "img/act-kerstmarkt.jpg",
        rating: 4.7, reviews: 1890, duration: "2 uur", priceFrom: 27, themes: ["kerst", "winter", "cultuur"], plek: "Dresden" },
    ],
  };

  // haal activiteiten voor een land, optioneel gefilterd op thema, gesorteerd op relevantie
  function getForCountry(code, theme, limit) {
    const list = (activities[code] || []).slice();
    let out = list;
    if (theme) {
      out = list.filter(function (a) { return a.themes.indexOf(theme) >= 0; });
      // vul aan met overige (op rating) als er te weinig matchen
      if (out.length < (limit || 6)) {
        const rest = list.filter(function (a) { return a.themes.indexOf(theme) < 0; })
          .sort(function (a, b) { return b.rating - a.rating; });
        out = out.concat(rest);
      }
    }
    out = out.map(function (a) {
      return Object.assign({}, a, { affiliateUrl: aff(a.city, a.code.toLowerCase(), a.dest, a.code) });
    });
    return out.slice(0, limit || 6);
  }

  // voor blogs: trek uit de NL+DE pool op thema
  function getByTheme(theme, limit) {
    const all = activities.nl.concat(activities.de);
    const matched = all.filter(function (a) { return a.themes.indexOf(theme) >= 0; })
      .sort(function (a, b) { return b.reviews - a.reviews; });
    const out = (matched.length ? matched : all).slice(0, limit || 3);
    return out.map(function (a) {
      return Object.assign({}, a, { affiliateUrl: aff(a.city, a.code.toLowerCase(), a.dest, a.code) });
    });
  }

  return {
    THEMES: THEMES,
    themeForVacation: themeForVacation,
    getForCountry: getForCountry,
    getByTheme: getByTheme,
    isLiveCountry: function (code) { return !!activities[code]; },
  };
})();
