/* Schoolvakanties.nl — homepage-interactie (vanilla JS, progressive enhancement).
   De pagina rendert volledig server-side; dit verrijkt alleen de radar, de
   mini-druktekaart en de menu's. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  function readJSON(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }

  // ── Header: mega-menu + mobiel menu ──────────────────────────────────────
  function header() {
    var megaBtn = $("#megaBtn"), mega = $("#mega"), topbar = $("#topbar");
    if (megaBtn && mega) {
      var open = function (v) { mega.hidden = !v; megaBtn.setAttribute("aria-expanded", v ? "true" : "false"); megaBtn.classList.toggle("open", v); };
      megaBtn.addEventListener("click", function () { open(mega.hidden); });
      megaBtn.addEventListener("mouseenter", function () { open(true); });
      if (topbar) topbar.addEventListener("mouseleave", function () { open(false); });
      document.addEventListener("click", function (e) { if (topbar && !topbar.contains(e.target)) open(false); });
    }
    var hamb = $("#hambBtn"), mob = $("#mobnav"), mobX = $("#mobnavX");
    var setMob = function (v) { if (!mob) return; mob.hidden = !v; document.body.style.overflow = v ? "hidden" : ""; };
    if (hamb) hamb.addEventListener("click", function () { setMob(true); });
    if (mobX) mobX.addEventListener("click", function () { setMob(false); });
    var acc = $("#mobLandenBtn"), accBox = $("#mobLanden");
    if (acc && accBox) acc.addEventListener("click", function () {
      acc.classList.toggle("open"); accBox.style.display = acc.classList.contains("open") ? "" : "none";
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { if (mega) { mega.hidden = true; } setMob(false); }
    });
  }

  // ── Kleur + band helpers (port van data.js / EuropeMap.jsx) ───────────────
  function drukteColor(v) {
    if (v < 38) return "var(--rustig)";
    if (v < 56) return "oklch(76% 0.135 120)";
    if (v < 70) return "var(--matig)";
    if (v < 84) return "oklch(72% 0.15 50)";
    return "var(--druk)";
  }
  function band(score) { return score >= 70 ? "rustig" : score >= 45 ? "matig" : "druk"; }
  var BAND_LABEL = { rustig: "Slim", matig: "Redelijk", druk: "Druk" };
  function factorCls(v, invert) { var g = invert ? 100 - v : v; return g >= 66 ? "is-rustig" : g >= 40 ? "is-matig" : "is-druk"; }

  // Controller waarmee de planner de radar live kan herrekenen (gezet door radar()).
  var radarAPI = null;

  // ── Realistische Europa-kaart bouwen uit /static/js/europe-geo.js ─────────
  var SVGNS = "http://www.w3.org/2000/svg";
  function buildEuropeMap(svg, countries, weekIdx, labelMode) {
    var geo = window.EUROPE_GEO;
    if (!geo || !svg || svg.getAttribute("data-built")) return;
    svg.setAttribute("viewBox", geo.viewBox);
    var byCode = {}; countries.forEach(function (c) { byCode[c.code] = c; });
    var ctx = document.createDocumentFragment(), data = document.createDocumentFragment();
    Object.keys(geo.paths).forEach(function (code) {
      var c = byCode[code], d = geo.paths[code];
      if (c) {
        var g = document.createElementNS(SVGNS, "g");
        g.setAttribute("data-code", code);
        if (labelMode === "big") g.setAttribute("style", "cursor:pointer");
        var p = document.createElementNS(SVGNS, "path");
        p.setAttribute("d", d); p.setAttribute("class", "country-shape");
        p.setAttribute("fill", drukteColor(c.drukte[weekIdx]));
        g.appendChild(p);
        var lab = geo.labels[code];
        if (lab) {
          var t = document.createElementNS(SVGNS, "text");
          t.setAttribute("x", lab[0]); t.setAttribute("y", lab[1]);
          t.setAttribute("text-anchor", "middle");
          t.setAttribute("font-size", labelMode === "big" ? "11" : "12");
          t.setAttribute("font-weight", "700");
          t.setAttribute("fill", "oklch(28% 0.02 285)");
          t.setAttribute("style", "pointer-events:none;font-family:var(--sans)");
          t.textContent = labelMode === "big" ? c.name : code.toUpperCase();
          g.appendChild(t);
        }
        data.appendChild(g);
      } else {
        var pc = document.createElementNS(SVGNS, "path");
        pc.setAttribute("d", d); pc.setAttribute("class", "country-ctx");
        pc.setAttribute("fill", "oklch(90% 0.008 95)");
        ctx.appendChild(pc);
      }
    });
    svg.appendChild(ctx);   // context-landen onder
    svg.appendChild(data);  // data-landen erbovenop
    svg.setAttribute("data-built", "1");
  }

  // ── Reisweek-radar ────────────────────────────────────────────────────────
  function radar() {
    var weeks = readJSON("weeks-data");
    var ring = $("#radarRing"), arc = $("#radarArc"), val = $("#radarVal"), lab = $("#radarLab");
    var chart = $("#radarChart");
    if (!weeks || !ring || !chart) return;
    var R = 56, CIRC = 2 * Math.PI * R;
    arc.style.strokeDasharray = CIRC;

    function setRing(score, bnd) {
      arc.style.transition = "stroke-dashoffset .5s cubic-bezier(.3,1,.4,1)";
      arc.style.strokeDashoffset = CIRC * (1 - score / 100);
      ring.className = "ring is-" + bnd;
      lab.textContent = BAND_LABEL[bnd];
      countUp(val, parseInt(val.textContent, 10) || 0, score);
    }
    function countUp(el, from, to) {
      var start = null, dur = 500;
      function step(t) {
        if (!start) start = t;
        var p = Math.min(1, (t - start) / dur), e = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(from + (to - from) * e);
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }
    function factorsHTML(w) {
      var specs = [["Drukte", w.drukte, true, "◌"], ["Prijs", w.prijs, true, "€"],
                   ["Weer", w.weer, false, "☀"], ["Overlap", w.overlap, true, "⇄"]];
      return specs.map(function (s) {
        return '<div class="factor ' + factorCls(s[1], s[2]) + '">' +
          '<span class="factor-ic">' + s[3] + '</span><span class="factor-lab">' + s[0] + '</span>' +
          '<span class="factor-bar"><i style="width:' + s[1] + '%"></i></span>' +
          '<span class="factor-val mono">' + s[1] + '</span></div>';
      }).join("");
    }
    var bestIdx = 0;
    function computeBest() {
      return weeks.reduce(function (b, w, i) { return w.score > weeks[b].score ? i : b; }, 0);
    }
    function renderBars() {
      bestIdx = computeBest();
      chart.innerHTML = weeks.map(function (w, i) {
        var bnd = w.band || band(w.score);
        return '<button class="wkbar is-' + bnd + (i === bestIdx ? " on" : "") +
          '" data-idx="' + i + '" title="Week ' + w.wk + " · " + w.score + '">' +
          (i === bestIdx ? '<span class="best-flag">★ slimste</span>' : "") +
          '<span class="wkbar-track"><span class="wkbar-fill" style="height:' + w.score + '%"></span></span>' +
          '<span class="wkbar-num mono">' + w.wk + "</span></button>";
      }).join("");
      $$(".wkbar", chart).forEach(function (b) {
        b.addEventListener("click", function () { select(parseInt(b.getAttribute("data-idx"), 10)); });
      });
    }
    function select(i) {
      var w = weeks[i]; if (!w) return;
      $$(".wkbar", chart).forEach(function (b, j) { b.classList.toggle("on", j === i); });
      setRing(w.score, w.band || band(w.score));
      $("#radarWk").textContent = "WEEK " + w.wk;
      $("#radarDate").textContent = w.d1;
      $("#radarFactors").innerHTML = factorsHTML(w);
      document.dispatchEvent(new CustomEvent("sv:week", { detail: { i: i, week: w } }));
    }

    renderBars();
    // init arc op de beste week
    var score0 = weeks[bestIdx] ? weeks[bestIdx].score : 0;
    arc.style.strokeDashoffset = CIRC * (1 - score0 / 100);

    // maand-segment -> selecteer bijbehorende week (homepage)
    var maandStart = { mei: 0, jun: 4, jul: 9, aug: 13, sep: 18 };
    $$("#maandSeg button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        $$("#maandSeg button").forEach(function (b) { b.classList.remove("on"); });
        btn.classList.add("on");
        var idx = Math.min(weeks.length - 1, maandStart[btn.getAttribute("data-maand")] || 0);
        select(idx);
      });
    });

    // De planner kan de dataset vervangen (andere bestemming/type) en de beste week tonen.
    radarAPI = {
      setData: function (newWeeks) { weeks = newWeeks; renderBars(); select(bestIdx); },
      selectBest: function () { select(bestIdx); }
    };
  }

  // ── Mini-druktekaart: slider herkleurt kaart + ranglijst ──────────────────
  function minimap() {
    var countries = readJSON("countries-data");
    var slider = $("#mapSlider"), wkLabel = $("#mapWkLabel"), weeks = readJSON("weeks-data");
    var map = $("#europeMap"), rank = $("#mapRank");
    if (!countries || !slider || !weeks) return;
    buildEuropeMap(map, countries, parseInt(slider.value, 10) || 0, "mini");

    function paint(idx) {
      if (map) $$("g[data-code]", map).forEach(function (g) {
        var c = countries.find(function (x) { return x.code === g.getAttribute("data-code"); });
        if (!c) return;
        var p = g.querySelector("path"); if (p) p.setAttribute("fill", drukteColor(c.drukte[idx]));
      });
      if (rank) {
        var ranked = countries.map(function (c) { return { c: c, v: c.drukte[idx] }; })
          .sort(function (a, b) { return a.v - b.v; }).slice(0, 10);
        rank.innerHTML = ranked.map(function (r) {
          return '<div class="map-rank-row" data-code="' + r.c.code + '">' +
            '<span class="flag">' + r.c.flag + '</span><span class="nm">' + r.c.name + '</span>' +
            '<span class="mini-bar"><i style="width:' + r.v + '%;background:' + drukteColor(r.v) + '"></i></span>' +
            '<span class="pct">' + r.v + '</span></div>';
        }).join("");
      }
      var w = weeks[idx]; if (w && wkLabel) wkLabel.textContent = "WK " + w.wk + " · " + w.d1;
    }
    slider.addEventListener("input", function () { paint(parseInt(slider.value, 10)); });
    paint(parseInt(slider.value, 10) || 0);
  }

  // ── Planner: steppers, type-segment en slim-vertrekadvies ─────────────────
  function planner() {
    if (!$(".planner")) return;            // alleen op de plannerpagina
    var base = readJSON("weeks-data");
    var destData = readJSON("dest-data") || {};
    var regioWindows = readJSON("regio-windows") || [];
    var destSummer = readJSON("dest-summer") || {};
    if (!base) return;

    // Wegingen per reistype (sommen tot 1). 'strand' laat het weer zwaarder wegen,
    // 'natuur' juist rust (drukte). drukte/prijs/overlap: hoog = slecht (geïnverteerd).
    var WEIGHTS = {
      strand: { drukte: 0.28, prijs: 0.24, weer: 0.34, overlap: 0.14 },
      stad:   { drukte: 0.34, prijs: 0.30, weer: 0.22, overlap: 0.14 },
      natuur: { drukte: 0.40, prijs: 0.26, weer: 0.20, overlap: 0.14 }
    };
    var state = { regio: null, code: null, type: "strand", adults: 2, kids: 2 };
    var current = [], curSel = 0;

    function scoreAt(gi, dd, W) {
      var drukte = dd && dd.drukte ? dd.drukte[gi] : base[gi].drukte;
      var weer = dd && dd.weer ? dd.weer[gi] : base[gi].weer;
      var prijs = dd && dd.prijs ? dd.prijs[gi] : base[gi].prijs;
      var s = Math.round((100 - drukte) * W.drukte + (100 - prijs) * W.prijs +
                         weer * W.weer + (100 - base[gi].overlap) * W.overlap);
      return { score: Math.max(0, Math.min(100, s)), drukte: drukte, weer: weer, prijs: prijs };
    }
    function windowFor() {
      var w = regioWindows.filter(function (x) { return x.code === state.regio; })[0]
        || regioWindows[0];
      if (w && w.weeks && w.weeks.length) return w;
      return { label: "", weeks: base.map(function (_, i) { return i; }) };
    }

    // ── invoer ────────────────────────────────────────────────────────────
    $$("[data-regio-seg] button").forEach(function (b) {
      b.addEventListener("click", function () {
        $$("[data-regio-seg] button").forEach(function (x) { x.classList.remove("on"); });
        b.classList.add("on"); state.regio = b.getAttribute("data-regio"); onChange();
      });
    });
    var r0 = $("[data-regio-seg] button.on") || $("[data-regio-seg] button");
    if (r0) state.regio = r0.getAttribute("data-regio");

    $$("[data-stepper]").forEach(function (s) {
      var disp = $("[data-value-display]", s);
      var min = +s.getAttribute("data-min"), max = +s.getAttribute("data-max");
      var val = +s.getAttribute("data-value"), key = s.getAttribute("data-stepper-key");
      if (key) state[key] = val;
      $$("button[data-step]", s).forEach(function (b) {
        b.addEventListener("click", function () {
          val = Math.min(max, Math.max(min, val + (+b.getAttribute("data-step"))));
          disp.textContent = val; if (key) state[key] = val; onChange();
        });
      });
    });
    var chips = $$(".dest-chip");
    chips.forEach(function (ch) {
      ch.addEventListener("click", function () {
        chips.forEach(function (x) { x.classList.remove("on"); });
        ch.classList.add("on"); state.code = ch.getAttribute("data-code"); onChange();
      });
    });
    var on0 = $(".dest-chip.on") || chips[0];
    if (on0) state.code = on0.getAttribute("data-code");
    $$("[data-seg] button").forEach(function (b) {
      b.addEventListener("click", function () {
        $$("[data-seg] button").forEach(function (x) { x.classList.remove("on"); });
        b.classList.add("on"); state.type = (b.textContent || "").trim().toLowerCase(); onChange();
      });
    });

    // ── WANNEER: bouw de weken binnen jouw zomervenster en voed de radar ────
    function recompute() {
      var win = windowFor(), dd = destData[state.code], W = WEIGHTS[state.type] || WEIGHTS.strand;
      current = win.weeks.map(function (gi) {
        var sf = scoreAt(gi, dd, W);
        return { wk: base[gi].wk, d1: base[gi].d1, drukte: sf.drukte, weer: sf.weer,
                 prijs: sf.prijs, overlap: base[gi].overlap, score: sf.score,
                 band: band(sf.score), _gi: gi };
      });
      var rw = $("#regioWindow");
      if (rw) rw.textContent = win.label ? "zomervakantie " + win.label : "";
      var wt = $("#whType"); if (wt) wt.textContent = state.type;
      if (radarAPI) radarAPI.setData(current);   // → select beste week → sv:week
    }

    // ── slim-vertrekadvies (binnen jouw venster) ────────────────────────────
    var line = $("#adviceLine"), actions = $("#adviceActions");
    function betterWeek(sel) {
      var cur = current[sel], alt = null;
      for (var d = 1; d <= 4; d++) {
        [sel - d, sel + d].forEach(function (j) {
          if (j >= 0 && j < current.length && current[j].score > cur.score + 5) {
            if (alt === null || current[j].score > current[alt].score) alt = j;
          }
        });
      }
      return alt;
    }
    function kidsTxt() {
      if (state.kids > 0) return "Met " + state.kids + " " + (state.kids === 1 ? "kind" : "kinderen") +
        " zit je vast aan de schoolvakanties — binnen jouw vakantie telt elke week. ";
      return "";
    }
    function updateAdvice(sel) {
      if (!line) return;
      var cur = current[sel]; if (!cur) return;
      var dest = destData[state.code], waar = dest ? dest.name : "je bestemming";
      var alt = betterWeek(sel);
      if (alt !== null) {
        var a = current[alt];
        var dD = Math.max(1, Math.round((cur.drukte - a.drukte) / Math.max(1, cur.drukte) * 100));
        var pD = Math.round((cur.prijs - a.prijs) / Math.max(1, cur.prijs) * 100);
        var laat = a._gi > cur._gi;
        line.innerHTML = kidsTxt() + (laat ? "De <strong>laatste weken</strong> van je vakantie zijn slimmer: " : "") +
          "voor <strong>" + waar + "</strong> is <strong>week " + a.wk + " (" + a.d1 +
          ")</strong> <strong class=\"good\">" + dD + "% rustiger</strong>" +
          (pD > 0 ? " en <strong class=\"good\">" + pD + "% goedkoper</strong>" : "") + " dan week " + cur.wk + ".";
        if (actions) {
          actions.innerHTML = '<button class="btn" data-goto-week="' + alt + '">Bekijk week ' + a.wk + '</button>' +
            '<a class="btn-ghost" style="padding:13px 20px;border-radius:14px" href="/druktekaart/">Vergelijk op de druktekaart →</a>';
          var gb = $("[data-goto-week]", actions);
          if (gb) gb.addEventListener("click", function () {
            var bar = document.querySelector('.wkbar[data-idx="' + alt + '"]'); if (bar) bar.click();
          });
        }
      } else {
        line.innerHTML = kidsTxt() + "<strong>Week " + cur.wk + "</strong> is voor <strong>" + waar +
          "</strong> de slimste keuze binnen jouw zomervakantie.";
        if (actions) actions.innerHTML =
          '<a class="btn-ghost" style="padding:13px 20px;border-radius:14px" href="/druktekaart/">Vergelijk op de druktekaart →</a>';
      }
    }

    // ── WAARHEEN: rangschik bestemmingen voor de gekozen week ───────────────
    function updateWaarheen(gi) {
      var list = $("#whList"); if (!list) return;
      var W = WEIGHTS[state.type] || WEIGHTS.strand;
      var rows = Object.keys(destData).map(function (code) {
        var sf = scoreAt(gi, destData[code], W), ds = destSummer[code];
        return { code: code, name: destData[code].name, flag: destData[code].flag,
                 score: sf.score, drukte: sf.drukte, weer: sf.weer, prijs: sf.prijs,
                 back: !!(ds && ds.back_idx != null && gi >= ds.back_idx) };
      }).sort(function (a, b) { return b.score - a.score; });
      var top = rows.slice(0, 6);
      if (!top.some(function (r) { return r.code === state.code; })) {
        var selRow = rows.filter(function (r) { return r.code === state.code; })[0];
        if (selRow) top.push(selRow);
      }
      function meter(lab, w, color) {
        return '<div class="wh-meter"><span class="wh-lab">' + lab + '</span>' +
          '<span class="mini-bar"><i style="width:' + Math.max(0, Math.min(100, w)) +
          '%;background:' + color + '"></i></span></div>';
      }
      list.innerHTML = top.map(function (r) {
        return '<button class="wh-card' + (r.code === state.code ? " on" : "") + '" data-code="' + r.code + '">' +
          '<div class="wh-card-top"><span class="wh-flag">' + r.flag + '</span>' +
            '<span class="wh-nm">' + r.name + '</span>' +
            '<span class="wh-score is-' + band(r.score) + '">' + r.score + '</span></div>' +
          '<div class="wh-meters">' +
            meter("rust", 100 - r.drukte, drukteColor(r.drukte)) +
            meter("weer", r.weer, drukteColor(100 - r.weer)) +
            meter("prijs", 100 - r.prijs, drukteColor(r.prijs)) +
          '</div>' +
          (r.back ? '<span class="wh-back">★ scholen daar al begonnen — extra rustig</span>' : "") +
          '</button>';
      }).join("");
    }
    var whList = $("#whList");
    if (whList) whList.addEventListener("click", function (e) {
      var b = e.target.closest("[data-code]"); if (!b) return;
      state.code = b.getAttribute("data-code");
      chips.forEach(function (x) { x.classList.toggle("on", x.getAttribute("data-code") === state.code); });
      onChange();
    });

    document.addEventListener("sv:week", function (e) {
      curSel = e.detail.i;
      updateAdvice(curSel);
      var cur = current[curSel];
      var whWeek = $("#whWeek");
      if (whWeek && cur) whWeek.textContent = "week " + cur.wk + " (" + cur.d1 + ")";
      if (cur) updateWaarheen(cur._gi);
    });

    function onChange() { recompute(); }   // → radar setData → sv:week → advies + waarheen
    onChange();
  }

  // ── Volledige druktekaart (/druktekaart/) ─────────────────────────────────
  function druktekaart() {
    var map = $("#bigMap"), slider = $("#ksSlider"), rank = $("#kpRank");
    var countries = readJSON("countries-data"), weeks = readJSON("weeks-data");
    if (!map || !slider || !countries || !weeks) return;
    var sel = "it";
    if (!countries.some(function (c) { return c.code === "it"; })) sel = countries[0].code;
    buildEuropeMap(map, countries, parseInt(slider.value, 10) || 0, "big");

    function bandOf(v) { return v < 45 ? "rustig" : v < 70 ? "matig" : "druk"; }
    function bandTxt(v) { return v < 45 ? "Rustig" : v < 70 ? "Matig druk" : "Erg druk"; }

    function updateDetail(idx) {
      var c = countries.find(function (x) { return x.code === sel; }); if (!c) return;
      var v = c.drukte[idx];
      var det = $("#kpDetail");
      det.className = "kp-detail is-" + bandOf(v);
      $("#kpFlag").textContent = c.flag;
      $("#kpName").textContent = c.name;
      $("#kpBand").textContent = bandTxt(v);
      $("#kpVal").textContent = v;
    }
    function paint(idx) {
      $$("g[data-code]", map).forEach(function (g) {
        var c = countries.find(function (x) { return x.code === g.getAttribute("data-code"); });
        if (!c) return;
        var p = g.querySelector("path");
        if (p) { p.setAttribute("fill", drukteColor(c.drukte[idx])); p.classList.toggle("sel", c.code === sel); }
      });
      var ranked = countries.map(function (c) { return { c: c, v: c.drukte[idx] }; })
        .sort(function (a, b) { return a.v - b.v; });
      if (rank) rank.innerHTML = ranked.map(function (r) {
        return '<button class="kp-row' + (r.c.code === sel ? " on" : "") + '" data-code="' + r.c.code + '">' +
          '<span class="flag">' + r.c.flag + '</span><span class="nm">' + r.c.name + '</span>' +
          '<span class="mini-bar"><i style="width:' + r.v + '%;background:' + drukteColor(r.v) + '"></i></span>' +
          '<span class="pct mono">' + r.v + '</span></button>';
      }).join("");
      var rust = ranked[0];
      var tip = $("#kpTip");
      if (rust && tip) tip.innerHTML = "Rustigste deze week: <strong>" + rust.c.flag + " " + rust.c.name +
        "</strong> (" + rust.v + "/100).";
      var w = weeks[idx], now = $("#ksNow");
      if (w && now) now.textContent = "WK " + w.wk + " · " + w.d1;
      updateDetail(idx);
    }
    function pick(code) { sel = code; paint(+slider.value); }

    slider.addEventListener("input", function () { paint(+slider.value); });
    map.addEventListener("click", function (e) {
      var g = e.target.closest("g[data-code]"); if (g) pick(g.getAttribute("data-code"));
    });
    if (rank) rank.addEventListener("click", function (e) {
      var b = e.target.closest("[data-code]"); if (b) pick(b.getAttribute("data-code"));
    });
    paint(parseInt(slider.value, 10) || 0);
  }

  // ── Blog: categoriefilter + nieuwsbrief ───────────────────────────────────
  function blog() {
    var filters = $("#blogFilters"), grid = $("#postGrid");
    if (filters && grid) {
      filters.addEventListener("click", function (e) {
        var b = e.target.closest("button[data-cat]"); if (!b) return;
        $$("button", filters).forEach(function (x) { x.classList.toggle("on", x === b); });
        var cat = b.getAttribute("data-cat");
        $$(".post-card", grid).forEach(function (card) {
          card.style.display = (cat === "Alle" || card.getAttribute("data-cat") === cat) ? "" : "none";
        });
      });
    }
    $$("[data-newsletter]").forEach(function (f) {
      f.addEventListener("submit", function () {
        f.innerHTML = '<div class="nb-done">✓ Je bent aangemeld!</div>';
      });
    });
  }

  // ── Feestdag info-icoon: tap-toggle (mobiel) naast hover (desktop) ────────
  function feestInfo() {
    var btns = $$(".feest-i");
    if (!btns.length) return;
    btns.forEach(function (b) {
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        var wasOpen = b.classList.contains("open");
        btns.forEach(function (x) { x.classList.remove("open"); });
        if (!wasOpen) b.classList.add("open");
      });
    });
    document.addEventListener("click", function () {
      btns.forEach(function (x) { x.classList.remove("open"); });
    });
  }

  function init() { header(); radar(); minimap(); planner(); druktekaart(); blog(); feestInfo(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
