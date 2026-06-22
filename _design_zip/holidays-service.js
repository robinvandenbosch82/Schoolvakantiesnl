// holidays-service.js — live datalaag bovenop de OpenHolidays API.
// Haalt schoolvakanties + feestdagen op per land/jaar, transformeert naar onze
// structuur, cachet in localStorage en valt terug op de gebakken LANDDATA (2026).
// Doc: https://www.openholidaysapi.org/en/

window.Holidays = (function () {
  const BASE = "https://openholidaysapi.org";

  // landconfig: ISO-code, taal, hoe de regio's in de API heten
  const COUNTRIES = {
    nl: {
      iso: "NL", lang: "NL", regionField: "groups",
      regions: [
        { key: "NL-NO", label: "Noord" },
        { key: "NL-MI", label: "Midden" },
        { key: "NL-ZU", label: "Zuid" },
      ],
    },
    de: {
      iso: "DE", lang: "DE", regionField: "subdivisions",
      regions: [
        { key: "DE-BW", label: "Baden-Württemberg" }, { key: "DE-BY", label: "Bayern" },
        { key: "DE-BE", label: "Berlin" }, { key: "DE-BB", label: "Brandenburg" },
        { key: "DE-HB", label: "Bremen" }, { key: "DE-HH", label: "Hamburg" },
        { key: "DE-HE", label: "Hessen" }, { key: "DE-MV", label: "Meckl.-Vorp." },
        { key: "DE-NI", label: "Niedersachsen" }, { key: "DE-NW", label: "NRW" },
        { key: "DE-RP", label: "Rheinland-Pfalz" }, { key: "DE-SL", label: "Saarland" },
        { key: "DE-SN", label: "Sachsen" }, { key: "DE-ST", label: "Sachsen-Anhalt" },
        { key: "DE-SH", label: "Schleswig-Holstein" }, { key: "DE-TH", label: "Thüringen" },
      ],
    },
  };

  // status-badge per vakantienaam (niet in de API)
  const STATUS = {
    nl: { Meivakantie: "Wettelijk verplicht", Zomervakantie: "Wettelijk verplicht", Kerstvakantie: "Wettelijk verplicht", Voorjaarsvakantie: "Adviesdata", Herfstvakantie: "Adviesdata" },
    de: { Sommerferien: "Gespreid (KMK)" },
  };
  const ALIAS = {
    nl: { Voorjaarsvakantie: "Krokus- / carnavalsvakantie" },
    de: { Sommerferien: "Zomer", Osterferien: "Pasen", Pfingstferien: "Pinksteren", Herbstferien: "Herfst", Weihnachtsferien: "Kerst", Winterferien: "Februari", Frühjahrsferien: "Voorjaar" },
  };

  const MND_KORT = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"];
  const MND_LANG = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"];
  const DAG = ["zo", "ma", "di", "wo", "do", "vr", "za"];

  function parse(iso) { const p = iso.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function fmtKort(iso) { const d = parse(iso); return d.getDate() + " " + MND_KORT[d.getMonth()]; }
  function fmtLang(iso) { const d = parse(iso); return d.getDate() + " " + MND_LANG[d.getMonth()]; }
  function range(a, b) { return fmtKort(a) + " – " + fmtKort(b); }

  // ISO-weeknummer
  function isoWeek(d) {
    const t = new Date(d.getTime());
    t.setHours(0, 0, 0, 0);
    t.setDate(t.getDate() + 3 - ((t.getDay() + 6) % 7));
    const week1 = new Date(t.getFullYear(), 0, 4);
    return 1 + Math.round(((t - week1) / 86400000 - 3 + ((week1.getDay() + 6) % 7)) / 7);
  }
  function weeksBetween(a, b) {
    const out = [];
    const d = parse(a), end = parse(b);
    while (d <= end) { const w = isoWeek(d); if (out.indexOf(w) < 0) out.push(w); d.setDate(d.getDate() + 7); }
    const wEnd = isoWeek(end); if (out.indexOf(wEnd) < 0) out.push(wEnd);
    return out;
  }
  function wkRange(a, b) {
    // start- en eindweek in volgorde (correct rond de jaarwisseling, bv. wk 51–1)
    const wa = isoWeek(parse(a)), wb = isoWeek(parse(b));
    return wa === wb ? "wk " + wa : "wk " + wa + "–" + wb;
  }

  function pickName(arr, lang) {
    const m = arr.find(function (x) { return x.language === lang; }) || arr.find(function (x) { return x.language === "EN"; }) || arr[0];
    return m ? m.text : "";
  }

  async function fetchJSON(url) {
    const ctrl = new AbortController();
    const to = setTimeout(function () { ctrl.abort(); }, 9000);
    try {
      const r = await fetch(url, { signal: ctrl.signal, headers: { accept: "application/json" } });
      clearTimeout(to);
      if (!r.ok) throw new Error("HTTP " + r.status);
      return await r.json();
    } finally { clearTimeout(to); }
  }

  // travel-seizoen window (mei–sep) voor Gantt + drukte
  const WK_VAN = 19, WK_TOT = 38;
  function weekWindow(year) {
    const out = [];
    // vind maandag van elke ISO-week in het venster
    const jan4 = new Date(year, 0, 4);
    const week1Mon = new Date(jan4); week1Mon.setDate(jan4.getDate() - ((jan4.getDay() + 6) % 7));
    for (let w = WK_VAN; w <= WK_TOT; w++) {
      const mon = new Date(week1Mon); mon.setDate(week1Mon.getDate() + (w - 1) * 7);
      out.push({ wk: w, label: mon.getDate() + " " + MND_KORT[mon.getMonth()] });
    }
    return out;
  }

  // alleen de echte schoolvakanties tonen (geen losse beweegbare vrije dagen)
  const HOOFDVAKANTIES = {
    nl: ["voorjaarsvakantie", "meivakantie", "zomervakantie", "herfstvakantie", "kerstvakantie"],
    de: ["winterferien", "frühjahrsferien", "osterferien", "pfingstferien", "sommerferien", "herbstferien", "weihnachtsferien"],
  };

  // transformeer ruwe schoolvakantie-data -> onze structuur
  function transformSchool(country, raw) {
    const cfg = COUNTRIES[country];
    const witlijst = HOOFDVAKANTIES[country];
    const covWeeks = {}; // wk -> Set(regiolabel)

    // 1) verzamel geaccepteerde records (hoofdvakanties met geraakte regio's)
    const records = [];
    raw.forEach(function (h) {
      const naam = pickName(h.name, cfg.lang);
      if (witlijst.indexOf(naam.toLowerCase()) < 0) return;
      const entries = h[cfg.regionField] || [];
      const hit = cfg.regions.filter(function (r) { return entries.some(function (e) { return e.code === r.key; }); });
      if (!hit.length) return;
      records.push({ naam: naam, start: h.startDate, end: h.endDate, hit: hit });
      weeksBetween(h.startDate, h.endDate).forEach(function (w) {
        if (!covWeeks[w]) covWeeks[w] = new Set();
        hit.forEach(function (r) { covWeeks[w].add(r.label); });
      });
    });

    // 2) groepeer per naam, en cluster op datum-afstand (>120 dgn = aparte vakantie,
    //    bv. kerstvakantie begin vs. eind van het kalenderjaar)
    const perNaam = {};
    records.forEach(function (rec) { (perNaam[rec.naam] = perNaam[rec.naam] || []).push(rec); });
    const blokken = [];
    Object.keys(perNaam).forEach(function (naam) {
      const recs = perNaam[naam].sort(function (a, b) { return a.start < b.start ? -1 : 1; });
      let cluster = null;
      recs.forEach(function (rec) {
        const gap = cluster ? (parse(rec.start) - parse(cluster.minStart)) / 86400000 : 0;
        if (!cluster || gap > 120) {
          cluster = { naam: naam, perRegio: {}, weken: {}, minStart: rec.start };
          blokken.push(cluster);
        }
        rec.hit.forEach(function (r) {
          cluster.perRegio[r.label] = range(rec.start, rec.end);
          cluster.weken[r.label] = wkRange(rec.start, rec.end);
        });
        if (rec.start < cluster.minStart) cluster.minStart = rec.start;
      });
    });

    const vakanties = blokken.map(function (v) {
      const n = v.naam;
      v.status = (STATUS[country] && STATUS[country][n]) || (country === "de" ? "Per deelstaat" : "Schoolvakantie");
      v.alias = (ALIAS[country] && ALIAS[country][n]) || "";
      v.maand = MND_LANG[parse(v.minStart).getMonth()];
      return v;
    }).sort(function (a, b) { return a.minStart < b.minStart ? -1 : 1; });

    // drukte per week wordt in getYearData berekend uit covWeeks
    const total = cfg.regions.length;
    return { vakanties: vakanties, covWeeks: covWeeks, total: total };
  }

  function publicHolidays(country, raw) {
    const cfg = COUNTRIES[country];
    const nat = raw.filter(function (h) { return h.nationwide; })
      .sort(function (a, b) { return a.startDate < b.startDate ? -1 : 1; });
    const reg = raw.filter(function (h) { return !h.nationwide; });
    const feestdagen = nat.map(function (h) {
      const d = parse(h.startDate);
      return { naam: pickName(h.name, cfg.lang), datum: fmtLang(h.startDate), dag: DAG[d.getDay()] };
    });
    return { feestdagen: feestdagen, regionaalAantal: reg.length };
  }

  // hoofd-API: alle data voor een land+jaar
  async function getYearData(country, year) {
    const cfg = COUNTRIES[country];
    const cacheKey = "ohv5:" + country + ":" + year;
    let cached = null;
    try { cached = JSON.parse(localStorage.getItem(cacheKey)); } catch (e) {}
    if (cached) return cached;

    const from = year + "-01-01", to = year + "-12-31";
    const [school, pub] = await Promise.all([
      fetchJSON(BASE + "/SchoolHolidays?countryIsoCode=" + cfg.iso + "&languageIsoCode=" + cfg.lang + "&validFrom=" + from + "&validTo=" + to),
      fetchJSON(BASE + "/PublicHolidays?countryIsoCode=" + cfg.iso + "&languageIsoCode=" + cfg.lang + "&validFrom=" + from + "&validTo=" + to),
    ]);
    const t = transformSchool(country, school);
    const p = publicHolidays(country, pub);

    // drukte + gantt uit dekking
    const win = weekWindow(year);
    const drukteWeeks = win.map(function (w) {
      const set = t.covWeeks[w.wk];
      const frac = set ? set.size / t.total : 0;
      return { wk: w.wk, label: w.label, drukte: Math.round(frac * 100) };
    });
    // gantt: zomervakantie-venster per regio
    const zomer = t.vakanties.find(function (v) { return /zomer|sommer/i.test(v.naam); });
    const gantt = [];
    if (zomer) {
      cfg.regions.forEach(function (r) {
        const wkStr = zomer.weken[r.label];
        if (wkStr) {
          const nums = wkStr.replace("wk ", "").split("–").map(Number);
          gantt.push({ name: r.label, start: nums[0], eind: nums[1] || nums[0] });
        }
      });
    }

    const result = {
      country: country, year: year, live: true,
      vakanties: t.vakanties, feestdagen: p.feestdagen, regionaalAantal: p.regionaalAantal,
      drukteWeeks: drukteWeeks, gantt: gantt, weekWindow: win,
      eersteVakantie: t.vakanties.length ? t.vakanties[0].minStart : null,
    };
    try { localStorage.setItem(cacheKey, JSON.stringify(result)); } catch (e) {}
    return result;
  }

  // overlap-piek met buurland (min van beide drukte-curves)
  async function getOverlap(country, year) {
    const other = country === "de" ? "nl" : "de";
    const [a, b] = await Promise.all([getYearData(country, year), getYearData(other, year)]);
    let peak = 0, peakWk = a.weekWindow[0].wk;
    a.drukteWeeks.forEach(function (w, i) {
      const m = Math.min(w.drukte, b.drukteWeeks[i].drukte);
      if (m > peak) { peak = m; peakWk = w.wk; }
    });
    return { peak: peak, peakWk: peakWk, other: other };
  }

  return {
    getYearData: getYearData,
    getOverlap: getOverlap,
    COUNTRIES: COUNTRIES,
    years: [2026, 2027, 2028, 2029, 2030],
    helpers: { isoWeek: isoWeek, fmtKort: fmtKort, parse: parse },
  };
})();
