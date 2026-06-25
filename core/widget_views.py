"""Embeddable widget voor externe partnersites.

Drie endpoints (geregistreerd vóór de root-slugroute in core/urls.py):
- /widget/       self-service generator (geen login): land + domein → snippet.
- /widget.js     het embed-script (gecached, CORS-vrij als <script>).
- /widget/data   JSON-data voor het script (CORS open; Origin bepaalt full/teaser).

Hefboom: wíj serveren de data. Staat onze (statische) backlink op de pagina, dan
toont de widget de volledige vakantietabel; is die weg, dan degradeert hij naar
een prikkelende halve teaser met een CTA naar de landpagina. `check_backlinks`
verifieert de backlink periodiek (simpele HTML-fetch) en zet de modus.
"""
import re
import secrets
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_protect

from .models import Land, Widget, WidgetPagina
from .views import _client_ip, _periode_str, _vakantie_nl

MAX_PAGINAS_PER_WIDGET = 50  # rem tegen ongebreidelde auto-registratie


# ── gedeelde datalaag ────────────────────────────────────────────────────────
def _widget_vakanties(land, jaar):
    """Compacte vakantielijst voor een land in een jaar: één regel per
    periodenaam met de overspannende datum (vroegste start – laatste eind)."""
    periods = {}
    for v in (land.schoolvakanties.filter(start_datum__year=jaar)
              .order_by("start_datum")):
        if v.eind_datum and (v.eind_datum - v.start_datum).days < 2:
            continue  # losse vrije/zweefdagen horen niet in de vakantietabel
        periods.setdefault(v.naam, []).append(v)

    rows = []
    for naam, entries in sorted(periods.items(), key=lambda kv: kv[1][0].start_datum):
        starts = [v.start_datum for v in entries]
        ends = [v.eind_datum or v.start_datum for v in entries]
        ranges = {(v.start_datum, v.eind_datum) for v in entries}
        nl_naam = _vakantie_nl(naam) if land.iso_code != "NL" else ""
        if nl_naam and nl_naam == naam.lower():
            nl_naam = ""
        rows.append({
            "naam": (nl_naam or naam).strip().capitalize() if nl_naam else naam,
            "periode": _periode_str(min(starts), max(ends)),
            "gespreid": len(ranges) > 1,
        })
    return rows


def _volgende_vakantie(land):
    """Eerstvolgende vakantie vanaf vandaag (voor de teaser-prikkel)."""
    today = timezone.localdate()
    nxt = (land.schoolvakanties.filter(start_datum__gte=today)
           .order_by("start_datum").first())
    if not nxt:
        return None
    nl_naam = _vakantie_nl(nxt.naam) if land.iso_code != "NL" else ""
    return {
        "naam": (nl_naam.capitalize() if nl_naam and nl_naam != nxt.naam.lower() else nxt.naam),
        "periode": _periode_str(nxt.start_datum, nxt.eind_datum),
        "dagen": (nxt.start_datum - today).days,
    }


def _land_jaar(land):
    """Het jaar waarvoor we data tonen: het lopende jaar als dat data heeft,
    anders het eerstvolgende jaar met vakanties."""
    jaar = timezone.localdate().year
    if land.schoolvakanties.filter(start_datum__year=jaar).exists():
        return jaar
    nxt = land.schoolvakanties.order_by("start_datum").first()
    return nxt.start_datum.year if nxt else jaar


# ── helpers ──────────────────────────────────────────────────────────────────
def _norm_domein(raw):
    """example.com uit https://www.Example.com/pad → example.com (zonder www)."""
    raw = (raw or "").strip().lower()
    if "//" not in raw:
        raw = "//" + raw
    host = urlsplit(raw).netloc or ""
    host = host.split("@")[-1].split(":")[0]
    return host[4:] if host.startswith("www.") else host


def _origin_host(request):
    """Host uit de Origin- of (anders) Referer-header van de cross-origin call."""
    src = request.headers.get("Origin") or request.headers.get("Referer") or ""
    if not src:
        return ""
    host = (urlsplit(src).netloc or "").split(":")[0].lower()
    return host[4:] if host.startswith("www.") else host


def _host_matcht(origin_host, domein):
    return bool(origin_host) and (origin_host == domein or origin_host.endswith("." + domein))


def _url_op_domein(url, domein):
    """Staat deze URL op (een subdomein van) het opgegeven domein?"""
    host = (urlsplit(url).netloc or "").split(":")[0].lower()
    host = host[4:] if host.startswith("www.") else host
    return _host_matcht(host, domein)


def _norm_url(raw):
    """URL normaliseren voor opslag/matching: schema+host+pad, zonder fragment."""
    raw = (raw or "").strip()
    if not raw:
        return ""
    if "//" not in raw:
        raw = "https://" + raw
    p = urlsplit(raw)
    if not p.netloc:
        return ""
    pad = p.path or "/"
    return f"{p.scheme}://{p.netloc.lower()}{pad}" + (f"?{p.query}" if p.query else "")


def _bron(land):
    return {
        "url": f"{settings.SITE_ORIGIN}/{land.slug}/",
        "tekst": f"Schoolvakanties {land.naam} {_land_jaar(land)}",
        "merk": "Schoolvakanties.nl",
    }


# ── data-endpoint ──────────────────────────────────────────────────────────────
def widget_data(request):
    """JSON voor het embed-script. Open CORS (publieke data); de Origin bepaalt of
    er volledige data óf een teaser teruggaat. Niet cachen (per-Origin/per-pagina)."""
    land = Land.objects.filter(slug=request.GET.get("land", ""), actief=True).first()
    if not land:
        resp = JsonResponse({"error": "onbekend land"}, status=404)
        resp["Access-Control-Allow-Origin"] = "*"
        return resp

    jaar = _land_jaar(land)
    volledig = False
    widget = Widget.objects.filter(site_key=request.GET.get("site", ""), actief=True).first()
    if widget and widget.land_id == land.id:
        if _host_matcht(_origin_host(request), widget.domein):
            volledig = _resolveer_pagina(widget, request.GET.get("u", ""))

    if volledig:
        payload = {
            "mode": "full", "land": land.naam, "jaar": jaar,
            "bron": _bron(land), "vakanties": _widget_vakanties(land, jaar),
        }
    else:
        alle = _widget_vakanties(land, jaar)
        payload = {
            "mode": "teaser", "land": land.naam, "jaar": jaar, "bron": _bron(land),
            "volgende": _volgende_vakantie(land),
            "preview": alle[:1],                       # prikkel: één periode zichtbaar
            "verborgen": max(0, len(alle) - 1),        # de rest 'achter het slot'
        }
    resp = JsonResponse(payload)
    resp["Access-Control-Allow-Origin"] = "*"
    resp["Cache-Control"] = "no-store"
    return resp


def _resolveer_pagina(widget, raw_url):
    """Vind/maak de WidgetPagina voor de huidige paginalaadbeurt en geef terug of
    er volledige data getoond mag worden (status != teaser)."""
    url = _norm_url(raw_url)
    if not url or not _url_op_domein(url, widget.domein):
        return False
    pagina = WidgetPagina.objects.filter(widget=widget, url=url).first()
    if pagina:
        return pagina.toont_volledig
    # Nieuwe pagina op het geverifieerde domein: auto-registreren (binnen limiet)
    # en provisorisch (pending) volledig tonen tot de eerste backlink-check.
    if widget.paginas.count() < MAX_PAGINAS_PER_WIDGET:
        WidgetPagina.objects.create(widget=widget, url=url)
    return True


# ── embed-script ───────────────────────────────────────────────────────────────
@cache_control(public=True, max_age=3600)
def widget_js(request):
    resp = render(request, "widget/embed.js", content_type="application/javascript")
    resp["Access-Control-Allow-Origin"] = "*"
    return resp


# ── self-service generator (geen login) ──────────────────────────────────────────
@csrf_protect
def widget_generator(request):
    landen = list(Land.objects.filter(actief=True).order_by("naam"))
    ctx = {"landen": landen, "site_origin": settings.SITE_ORIGIN}
    if request.method == "POST":
        if request.POST.get("website", "").strip():   # honeypot
            ctx["fout"] = "Er ging iets mis."
            return render(request, "widget/generator.html", ctx)

        from django.core.cache import cache
        ip = _client_ip(request) or "?"
        key = f"widget-gen:{ip}"
        pogingen = cache.get(key, 0)

        land = Land.objects.filter(slug=request.POST.get("land", ""), actief=True).first()
        domein = _norm_domein(request.POST.get("domein", ""))
        url = _norm_url(request.POST.get("url", ""))
        email = request.POST.get("email", "").strip()[:254]
        email_ok = True
        if email:
            try:
                validate_email(email)
            except ValidationError:
                email_ok = False

        if pogingen >= 10:
            ctx["fout"] = "Je hebt zojuist al widgets aangemaakt; probeer het over een uur opnieuw."
        elif not land:
            ctx["fout"] = "Kies een geldig land."
        elif not _geldig_domein(domein):
            ctx["fout"] = "Vul een geldig domein in, bijvoorbeeld example.com."
        elif not email_ok:
            ctx["fout"] = "Vul een geldig e-mailadres in (of laat het leeg)."
        elif url and not _url_op_domein(url, domein):
            ctx["fout"] = "De pagina-URL moet op het opgegeven domein staan."
        else:
            widget = Widget.objects.create(
                site_key=_nieuwe_key(), domein=domein, land=land, email=email)
            if url:
                WidgetPagina.objects.create(widget=widget, url=url)
            cache.set(key, pogingen + 1, 3600)
            ctx.update(widget=widget, snippet=_snippet(widget), gelukt=True)
    return render(request, "widget/generator.html", ctx)


def _geldig_domein(domein):
    return bool(re.fullmatch(r"(?=.{4,190}$)([a-z0-9](-?[a-z0-9])*\.)+[a-z]{2,}", domein or ""))


def _nieuwe_key():
    for _ in range(10):
        key = "sv_" + secrets.token_urlsafe(8)[:12]
        if not Widget.objects.filter(site_key=key).exists():
            return key
    return "sv_" + secrets.token_urlsafe(16)[:16]


def _snippet(widget):
    """Het embed-snippet: statische backlink (de te verifiëren link) + container +
    script. Natuurlijke, merkgerichte anchortekst (geen keyword-stuffing)."""
    o = settings.SITE_ORIGIN
    land = widget.land
    jaar = _land_jaar(land)
    return (
        f'<a href="{o}/{land.slug}/" rel="noopener">'
        f'Schoolvakanties {land.naam} {jaar} – bron: Schoolvakanties.nl</a>\n'
        f'<div data-sv-widget data-land="{land.slug}" data-site="{widget.site_key}"></div>\n'
        f'<script src="{o}/widget.js" defer></script>'
    )
