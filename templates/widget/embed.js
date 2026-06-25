/* Schoolvakanties.nl — embeddable widget.
   Plaats op een externe site via:
     <a href="https://schoolvakanties.nl/<land>/">…bron: Schoolvakanties.nl</a>
     <div data-sv-widget data-land="<land>" data-site="<site-key>"></div>
     <script src="https://schoolvakanties.nl/widget.js" defer></script>

   Het script haalt de data bij ons op. Staat onze backlink op de pagina, dan
   toont het de volledige vakantietabel; is die weg, dan een prikkelende halve
   teaser met een doorklik naar de landpagina. Vanilla JS, geen dependencies. */
(function () {
  "use strict";

  // Basis-origin afleiden uit de eigen <script src> (werkt op elk domein).
  var self = document.currentScript ||
    (function () { var s = document.getElementsByTagName("script"); return s[s.length - 1]; })();
  var BASE = (function () { try { return new URL(self.src).origin; } catch (e) { return ""; } })();

  var STYLE_ID = "sv-widget-style";
  var CSS =
    ".svw{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;" +
    "max-width:560px;border:1px solid #e6e6ef;border-radius:14px;padding:18px 20px;" +
    "background:#fff;color:#1c1c28;line-height:1.5;box-sizing:border-box}" +
    ".svw *{box-sizing:border-box}" +
    ".svw-h{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin:0 0 12px}" +
    ".svw-h b{font-size:16px}.svw-h span{font-size:12px;color:#6b6b80}" +
    ".svw-t{width:100%;border-collapse:collapse;font-size:14px}" +
    ".svw-t td{padding:7px 0;border-top:1px solid #f0f0f5;vertical-align:top}" +
    ".svw-t td:last-child{text-align:right;color:#3a3a4d;white-space:nowrap;padding-left:12px}" +
    ".svw-t tr:first-child td{border-top:0}" +
    ".svw-sp{display:inline-block;margin-left:6px;font-size:11px;color:#7a5cff;border:1px solid #e0d8ff;" +
    "border-radius:999px;padding:0 7px;vertical-align:middle}" +
    ".svw-next{background:#f4f1ff;border:1px solid #e6dfff;border-radius:10px;padding:10px 13px;" +
    "margin:0 0 12px;font-size:14px}.svw-next b{color:#5a3df0}" +
    ".svw-lock{position:relative;margin-top:6px}" +
    ".svw-blur{filter:blur(5px);opacity:.55;pointer-events:none;user-select:none}" +
    ".svw-blur td{padding:8px 0;border-top:1px solid #f0f0f5}" +
    ".svw-ov{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;" +
    "justify-content:center;text-align:center;gap:8px;padding:8px}" +
    ".svw-cta{display:inline-block;background:#5a3df0;color:#fff;text-decoration:none;font-weight:700;" +
    "font-size:14px;padding:10px 16px;border-radius:10px}" +
    ".svw-cta:hover{background:#4a2fd6}" +
    ".svw-ov small{color:#52526b;font-size:12.5px;max-width:320px}" +
    ".svw-f{margin:13px 0 0;font-size:12px;color:#8a8a9c}" +
    ".svw-f a{color:#5a3df0;text-decoration:none}.svw-f a:hover{text-decoration:underline}";

  function injectStyle() {
    if (document.getElementById(STYLE_ID)) return;
    var s = document.createElement("style");
    s.id = STYLE_ID; s.textContent = CSS;
    document.head.appendChild(s);
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function rij(v) {
    var sp = v.gespreid ? '<span class="svw-sp">per regio</span>' : "";
    return "<tr><td>" + esc(v.naam) + sp + "</td><td>" + esc(v.periode) + "</td></tr>";
  }

  function header(d) {
    return '<div class="svw-h"><b>Schoolvakanties ' + esc(d.land) + " " + esc(d.jaar) +
      "</b><span>bron: Schoolvakanties.nl</span></div>";
  }

  function footer(d) {
    return '<div class="svw-f">Bron: <a href="' + esc(d.bron.url) +
      '" target="_blank" rel="noopener">' + esc(d.bron.tekst) + "</a></div>";
  }

  function renderFull(el, d) {
    el.innerHTML = header(d) +
      '<table class="svw-t"><tbody>' + (d.vakanties || []).map(rij).join("") + "</tbody></table>" +
      footer(d);
  }

  function renderTeaser(el, d) {
    var next = d.volgende
      ? '<div class="svw-next">Eerstvolgende vakantie: <b>' + esc(d.volgende.naam) + "</b> — " +
        esc(d.volgende.periode) + (d.volgende.dagen >= 0
          ? " (over " + d.volgende.dagen + " dag" + (d.volgende.dagen === 1 ? "" : "en") + ")" : "") +
        "</div>"
      : "";
    var preview = (d.preview || []).map(rij).join("");
    // Nep-balken achter de blur, zodat er 'meer' lijkt te zitten.
    var ghost = "";
    var n = Math.max(3, d.verborgen || 3);
    for (var i = 0; i < Math.min(n, 5); i++) {
      ghost += '<tr><td>&nbsp;</td><td>&nbsp;</td></tr>';
    }
    var meer = d.verborgen
      ? "Nog " + d.verborgen + " vakantieperiode" + (d.verborgen === 1 ? "" : "s") +
        " — bekijk de volledige kalender:"
      : "Bekijk de volledige vakantiekalender:";
    el.innerHTML = header(d) + next +
      '<table class="svw-t"><tbody>' + preview + "</tbody></table>" +
      '<div class="svw-lock"><table class="svw-t svw-blur"><tbody>' + ghost + "</tbody></table>" +
      '<div class="svw-ov"><small>' + esc(meer) + "</small>" +
      '<a class="svw-cta" href="' + esc(d.bron.url) + '" target="_blank" rel="noopener">' +
      "Alle schoolvakanties " + esc(d.land) + " " + esc(d.jaar) + " →</a></div></div>" +
      footer(d);
  }

  function load(el) {
    var land = el.getAttribute("data-land");
    var site = el.getAttribute("data-site") || "";
    if (!land || !BASE) return;
    var url = BASE + "/widget/data?land=" + encodeURIComponent(land) +
      "&site=" + encodeURIComponent(site) +
      "&u=" + encodeURIComponent(location.href);
    fetch(url, { credentials: "omit" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d || d.error) return;
        el.classList.add("svw");
        if (d.mode === "full") renderFull(el, d); else renderTeaser(el, d);
      })
      .catch(function () { /* stil falen: laat de statische backlink staan */ });
  }

  function init() {
    injectStyle();
    var nodes = document.querySelectorAll("[data-sv-widget]");
    for (var i = 0; i < nodes.length; i++) load(nodes[i]);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
