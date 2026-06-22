"""
Page views for Schoolvakanties.nl.

De homepage (scherm 1 uit het v3-design) is server-side gerenderd uit de DB:
de Reisweek-radar, mini-druktekaart, bestemmingen en de SEO-secties (regio's,
landenvergelijking, feestdagen, FAQ). Lichte vanilla-JS (static/js/site.js)
verzorgt de interactie. Overige schermen (landenpagina, planner, druktekaart,
blog, over-ons) volgen in latere fasen.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from django.conf import settings
from django.http import Http404
from django.shortcuts import render

from . import europe
from .models import (Bestemming, BlogArtikel, Faq, Feestdag, Land, Regio,
                     Reisweek, Schoolvakantie)

BLOG_CATS = ["Slim plannen", "Bestemmingen", "Met kinderen", "Drukte & prijzen"]


# ── SEO: JSON-LD helpers ────────────────────────────────────────────────────
def _page_url(request):
    return settings.SITE_ORIGIN + request.path


def _jsonld(nodes):
    nodes = [n for n in nodes if n]
    if not nodes:
        return ""
    return json.dumps({"@context": "https://schema.org", "@graph": nodes}, ensure_ascii=False)


def _faqpage_node(faqs, url):
    qs = [{"@type": "Question", "name": f.question,
           "acceptedAnswer": {"@type": "Answer", "text": f.answer}} for f in faqs]
    return {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": qs} if qs else None


def _breadcrumb_node(items):
    """items = [(naam, pad)]; pad relatief vanaf origin."""
    origin = settings.SITE_ORIGIN
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": naam, "item": origin + pad}
        for i, (naam, pad) in enumerate(items)]}


def _article_node(post, url):
    origin = settings.SITE_ORIGIN
    node = {
        "@type": "Article", "@id": url + "#article", "headline": post.titel,
        "description": post.excerpt, "inLanguage": "nl-NL",
        "image": f"{origin}/static/img/blog/{post.slug}.jpg",
        "mainEntityOfPage": {"@id": url},
        "isPartOf": {"@id": f"{origin}/#website"},
        "publisher": {"@id": f"{origin}/#organization"},
    }
    if post.author:
        node["author"] = {"@type": "Person", "name": post.author.name}
        if post.author.role:
            node["author"]["jobTitle"] = post.author.role
    else:
        node["author"] = {"@id": f"{origin}/#organization"}
    return node


@dataclass(frozen=True)
class PageSpec:
    """Eén route in het register: pad, URL-naam en SEO-defaults (voor sitemap +
    de admin-bewerkbare Page-rij via sync_pages)."""
    path: str
    name: str
    title: str = ""
    description: str = ""
    sitemap_priority: float = 0.6
    sitemap_changefreq: str = "monthly"
    context: dict = field(default_factory=dict)


PAGES: list[PageSpec] = [
    PageSpec(
        path="", name="home",
        title="Schoolvakanties & feestdagen 2026 — slim weg met het gezin | Schoolvakanties.nl",
        description="Vergelijk schoolvakanties, feestdagen en de drukste reisweken van heel Europa. "
                    "Eén Slim-score per week: ga weg wanneer het rustig, betaalbaar en fijn is.",
        sitemap_priority=1.0, sitemap_changefreq="weekly"),
]

_MAANDEN = ["", "januari", "februari", "maart", "april", "mei", "juni", "juli",
            "augustus", "september", "oktober", "november", "december"]
_MND = ["", "jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
_DAGEN = ["ma", "di", "wo", "do", "vr", "za", "zo"]
# NL-vakanties die landelijk gelijk zijn (OpenHolidays levert ze onder één regio).
_NL_LANDELIJK = {"Kerstvakantie", "Meivakantie"}
# Het kalenderjaar dat de landenpagina toont. De import bevat ~13 maanden (om
# vooruit te kunnen plannen), dus zónder dit filter verschijnen twee kerst-
# vakanties (schooljaar 2025-26 én 2026-27) als schijnduplicaten.
TOON_JAAR = 2026

# viewBox-string van de realistische Europa-kaart (uit de gegenereerde geo-data).
_MAP_VB = "0 0 %d %d" % (round(europe.VIEWBOX[2]), round(europe.VIEWBOX[3]))

# Regio-codes die we per land verbergen: Franse overzeese gebieden (DOM-TOM) —
# eigen, afwijkende schoolkalenders, niet relevant voor een NL-reispubliek en
# bron van schijnduplicaten. Exact-match (FR-NA = Nouvelle-Aquitaine is métropole!).
VERBERG_REGIO_CODES = {
    "FR": {"FR-GP", "FR-MQ", "FR-GF", "FR-GY", "FR-RE", "FR-RU", "FR-YT",
           "FR-BL", "FR-MF", "FR-PM", "FR-WF", "FR-PF", "FR-NC", "FR-TF", "FR-CP"},
}


# Nederlandse vertaling van buitenlandse vakantienamen (keyword-match, eerste hit;
# meertalig voor alle ondersteunde landen). Specifiek vóór generiek.
_VAK_NL = [
    # ski / sport / februariweek
    (("ski", "schi", "sport", "weiße woche", "semana blanca", "settimana bianca",
      "februarwoche", "februar"), "ski-/sportvakantie"),
    # carnaval / krokus
    (("fasching", "fastnacht", "karneval", "carnaval", "krokus", "détente", "detente",
      "rosenmontag", "fašank"), "carnavalsvakantie"),
    # kerst
    (("kerst", "noël", "noel", "weihnacht", "navidad", "natal", "natale", "christmas",
      "vánoc", "vianoč", "vianoc", "crăciun", "craciun", "boże narodzenie", "kalėd",
      "ziemassvētk", "jõulu", "karácsony", "božič", "jul"), "kerstvakantie"),
    # pasen
    (("paas", "oster", "pâque", "paque", "páscoa", "pascoa", "pascua", "pasqua", "easter",
      "velikonoc", "velikonočne", "veľkonoč", "wielkanoc", "lieldienas", "húsvét",
      "semana santa", "semaine sainte", "velykų"), "paasvakantie"),
    # pinksteren
    (("pinkster", "pfingst", "pentecôte", "pentecote", "pentecost", "binkošti"), "pinkstervakantie"),
    # hemelvaart / brugdag rond hemelvaart
    (("himmelfahrt", "ascension", "auffahrt"), "hemelvaart(brug)dag"),
    # halfjaar / semester
    (("halbjahr", "halfjaar", "semestr", "mid-year", "mid-term", "midterm",
      "poolaasta", "pusaasta", "polletni"), "halfjaarvakantie"),
    # zomer
    (("zomer", "sommer", "été", "ete", "summer", "verano", "verão", "estate", "estiv",
      "vasaras", "vasaros", "letnie", "letné", "letní", "nyári", "ljetni", "vară",
      "vara", "poletne", "kesä", "letné"), "zomervakantie"),
    # herfst
    (("herfst", "herbst", "toussaint", "autumn", "automne", "otoño", "outono", "autunno",
      "rudens", "podzim", "jesien", "jeseni", "jesenne", "őszi", "syksy", "rudenį"), "herfstvakantie"),
    # voorjaar / lente
    (("voorjaar", "frühjahr", "fruhjahr", "frühling", "printemps", "primavera", "primăvar",
      "spring", "proljetni", "pavasar", "wiosenne", "wiosenna", "jarní", "jarné", "jarne",
      "kevad", "tavasz", "spomladanske"), "voorjaarsvakantie"),
    # winter
    (("winter", "hiver", "invierno", "inverno", "žiemos", "žiema", "ziemas", "zima",
      "zimowe", "zimní", "zimné", "talvi", "téli", "zimske"), "wintervakantie"),
    # begin/einde schooljaar / terug naar school
    (("fin des cours", "fin de les", "fin de lecciones", "fine delle lezioni", "fine lezioni",
      "schuljahr", "schulbeginn", "schulanfang", "atgal", "mokykl", "back to school",
      "rentrée", "início", "inizio"), "begin/einde schooljaar"),
    # losse (regionale) vrije dagen die als 'schoolvakantie' binnenkomen
    (("buß", "buss", "bettag"), "boete- en bededag"),
    (("reformation",), "hervormingsdag"),
    (("fronleichnam", "corpus christi", "boží tělo", "fête-dieu"), "sacramentsdag"),
    (("allerseelen", "défunts", "all souls", "dušiček"), "allerzielen"),
    (("allerheiligen", "all saints", "ognissanti", "wszystkich"), "allerheiligen"),
    (("schulfrei", "unterrichtsfrei", "no lectivo", "no lectivos", "libre disposición",
      "libre disposicion", "día no", "dia no", "day off", "no school", "compensation",
      "beweglich", "variabler", "zusätzlicher", "ferientag", "galleggiante", "floating",
      "schulfreier"), "roostervrije dag"),
    # generieke terugval: bevat een 'vakantie'-woord maar geen type matchte
    (("ferien", "vacances", "vacaciones", "vacanze", "vacanza", "vacanţ", "vacant",
      "vakantie", "holiday", "wakacje", "prázdniny", "prazdniny", "prázdnin", "férias",
      "ferias", "ferie", "loma", "počitnice", "počitn", "odmor", "atostogos", "przerwa",
      "školske", "počitnice"), "vakantie"),
]


def _vakantie_nl(naam):
    n = (naam or "").lower()
    for keys, nl in _VAK_NL:
        if any(k in n for k in keys):
            return nl
    return ""


# Korte Nederlandse uitleg per officieuze/themadag.
_OFFICIEUS_UITLEG = [
    (("valentijn", "valentin", "valentine"), "Valentijnsdag (14 feb) — dag van de geliefden."),
    (("carnaval", "rosenmontag", "fasching", "fastnacht", "karneval"),
     "Carnaval — uitbundig volksfeest vóór de vastentijd; in het zuiden groot gevierd."),
    (("moederdag", "muttertag", "mother"), "Moederdag — eerbetoon aan moeders (2e zondag van mei)."),
    (("vaderdag", "vatertag", "father"), "Vaderdag — eerbetoon aan vaders."),
    (("dierendag",), "Dierendag (4 okt) — extra aandacht voor (huis)dieren."),
    (("halloween",), "Halloween (31 okt) — griezelfeest met verkleden en snoep, vooral voor kinderen."),
    (("sint-maarten", "sint maarten", "martin"), "Sint-Maarten (11 nov) — kinderen lopen met lampionnen langs de deuren."),
    (("sinterklaas", "nikolaus"), "Sinterklaas (5–6 dec) — kinderfeest met cadeaus en pepernoten."),
    (("oudjaar", "silvester", "oudejaars", "saint-sylvestre"), "Oudejaarsavond (31 dec) — de jaarwisseling met vuurwerk."),
    (("oktoberfest",), "Oktoberfest — groot bierfestival in München (eind sep–begin okt)."),
    (("koningsdag",), "Koningsdag (27 apr) — de verjaardag van de koning."),
]


def _officieus_uitleg(naam):
    n = (naam or "").lower()
    for keys, tekst in _OFFICIEUS_UITLEG:
        if any(k in n for k in keys):
            return tekst
    return "Onofficiële themadag — geen vrije dag, maar vaak wel extra druk."


# Provincies per NL-schoolvakantieregio (officieel; Gelderland is gesplitst).
NL_REGIO_PROVINCIES = {
    "Noord": ["Groningen", "Friesland", "Drenthe", "Overijssel", "Flevoland", "Noord-Holland"],
    "Midden": ["Utrecht", "Zuid-Holland", "Gelderland (deels)"],
    "Zuid": ["Zeeland", "Noord-Brabant", "Limburg", "Gelderland (deels)"],
}


# Korte Nederlandse uitleg per feestdag (keyword-match, specifiek vóór generiek).
_FEEST_UITLEG = [
    (("driekoning", "heilige drei", "epiphan", "épiphanie", "reyes", "befana"),
     "Driekoningen (6 jan) — het bezoek van de drie wijzen aan het kind Jezus."),
    (("nieuwjaar", "jour de l", "neujahr", "new year", "año nuevo", "ano nuevo",
      "capodanno", "anul nou", "nový rok", "nowy rok", "uusaasta", "naujieji"),
     "Nieuwjaarsdag — de eerste dag van het jaar."),
    (("goede vrijdag", "vendredi saint", "karfreitag", "good friday", "viernes santo",
      "venerdì santo", "velký pátek"), "Goede Vrijdag — herdenking van de kruisiging, de vrijdag vóór Pasen."),
    (("tweede paas", "lundi de pâques", "ostermontag", "easter monday", "lunes de pascua",
      "lunedì dell'angelo", "velikonoční pondělí"), "Tweede Paasdag — de maandag na Pasen."),
    (("eerste paas", "ostersonntag", "easter sunday", "pâques", "paasdag", "pascua", "pasqua"),
     "Pasen — christelijk feest van de opstanding van Christus."),
    (("koningsdag",), "Koningsdag — de verjaardag van de koning, nationale feestdag."),
    (("bevrijding", "victoire 1945", "victory in europe", "8 mai", "liberación", "liberation"),
     "Bevrijdingsdag / Dag van de Overwinning — einde van WO II in Europa (8 mei 1945)."),
    (("arbeid", "travail", "tag der arbeit", "labour", "labor", "trabajo", "lavoro",
      "premier mai", "święto pracy"), "Dag van de Arbeid (1 mei) — internationale dag van de werkende mens."),
    (("hemelvaart", "ascension", "himmelfahrt", "ascensione", "ascensión"),
     "Hemelvaartsdag — 40 dagen na Pasen; valt altijd op een donderdag."),
    (("pinkster", "pentecôte", "pfingst", "pentecost", "pentecoste", "pentecostés"),
     "Pinksteren — 50 dagen na Pasen, met vaak een vrije Tweede Pinksterdag."),
    (("sacrament", "fronleichnam", "corpus christi", "fête-dieu", "boží tělo"),
     "Sacramentsdag — katholiek feest, 60 dagen na Pasen."),
    (("duitse eenheid", "deutschen einheit"),
     "Dag van de Duitse Eenheid (3 okt) — viert de hereniging van Duitsland in 1990."),
    (("nationale feestdag", "fête nationale", "quatorze juillet", "bastille", "nationalfeiertag",
      "fiesta nacional", "festa della repubblica", "national day", "státní svátek"),
     "Nationale feestdag van het land."),
    (("maria", "assomption", "assumption", "assunzione", "asunción", "himmelfahrt mariä"),
     "Maria-Hemelvaart (15 aug) — katholiek hoogfeest."),
    (("allerheiligen", "toussaint", "all saints", "ognissanti", "todos los santos"),
     "Allerheiligen (1 nov) — herdenking van alle heiligen."),
    (("allerziel", "défunts", "all souls", "dušiček"),
     "Allerzielen (2 nov) — herdenking van alle overledenen."),
    (("wapenstilstand", "armistice", "11 novembre"),
     "Wapenstilstandsdag (11 nov 1918) — einde van de Eerste Wereldoorlog."),
    (("hervorming", "reformationstag", "reformation"),
     "Hervormingsdag (31 okt) — protestantse gedenkdag van de Reformatie."),
    (("buß", "buss- und bet", "bettag"), "Boete- en bededag — protestantse gedenkdag."),
    (("tweede kerst", "2ème jour de noël", "zweiter weihnacht", "2. weihnacht", "stephen",
      "stefano", "stefanitag", "boxing day", "santo estêvão", "druhý svátek vánoční"),
     "Tweede Kerstdag (26 dec)."),
    (("kerst", "noël", "weihnacht", "navidad", "natale", "christmas", "crăciun",
      "boże narodzenie", "vánoce", "1. svátek vánoční"), "Eerste Kerstdag (25 dec) — de geboorte van Christus."),
    (("oudejaar", "silvester", "saint-sylvestre", "new year's eve", "nochevieja"),
     "Oudejaarsdag (31 dec) — de laatste dag van het jaar."),
    (("afschaffing", "abolition", "esclavage", "slavernij"),
     "Afschaffing van de slavernij — herdenkingsdag."),
    (("vrouwendag", "frauentag", "women's day"), "Internationale Vrouwendag (8 maart)."),
]


def _feestdag_uitleg(naam):
    n = (naam or "").lower()
    for keys, tekst in _FEEST_UITLEG:
        if any(k in n for k in keys):
            return tekst
    return "Een officiële, landelijke vrije dag."


def _periode_str(start, eind):
    if not start or not eind:
        return ""
    return f"{start.day} {_MND[start.month]} – {eind.day} {_MND[eind.month]}"


def _weken_str(start, eind):
    if not start or not eind:
        return ""
    w1, w2 = start.isocalendar()[1], eind.isocalendar()[1]
    return f"wk {w1}" if w1 == w2 else f"wk {w1}–{w2}"
_BAND_LABEL = {"rustig": "Slim", "matig": "Redelijk", "druk": "Druk"}


def _factor_cls(value, invert):
    good = (100 - value) if invert else value
    return "is-rustig" if good >= 66 else "is-matig" if good >= 40 else "is-druk"


def _factors(w: dict) -> list:
    spec = [("Drukte", w["drukte"], True, "◌"), ("Prijs", w["prijs"], True, "€"),
            ("Weer", w["weer"], False, "☀"), ("Overlap", w["overlap"], True, "⇄")]
    return [{"label": lab, "value": v, "icon": ic, "cls": _factor_cls(v, inv)}
            for lab, v, inv, ic in spec]


def _week_dict(w: Reisweek) -> dict:
    return {"wk": w.weeknr, "d1": w.start_label, "score": w.slim_score, "band": w.band,
            "drukte": w.drukte, "prijs": w.prijs, "weer": w.weer, "overlap": w.overlap}


def home(request):
    from .models import Page
    page = Page.objects.filter(key="home").first()

    weeks = list(Reisweek.objects.filter(jaar=2026).order_by("weeknr"))
    wk = [_week_dict(w) for w in weeks]
    best_idx = max(range(len(wk)), key=lambda i: wk[i]["score"]) if wk else 0

    # Drukteprofiel per land + standaard-week voor de mini-kaart (rond de piek).
    countries = europe.country_drukte(weeks)
    default_idx = max(range(len(weeks)), key=lambda i: countries[0]["drukte"][i]) if weeks and countries else 0
    for c in countries:
        v = c["drukte"][default_idx] if c["drukte"] else 0
        c["v0"] = v
        c["color0"] = europe.drukte_color(v)
    ranked0 = sorted(countries, key=lambda c: c["v0"])

    # Vergelijk-strip: NL vs. buurlanden, elke cel met kleur + piekweek.
    by_code = {c["code"]: c for c in countries}
    vergelijk = []
    for code in ("nl", "de", "be", "fr"):
        c = by_code.get(code)
        if not c:
            continue
        cells = [{"v": v, "color": europe.drukte_color(v)} for v in c["drukte"]]
        peak_i = max(range(len(c["drukte"])), key=lambda i: c["drukte"][i]) if c["drukte"] else 0
        vergelijk.append({"name": c["name"], "flag": c["flag"], "cells": cells,
                          "peak": wk[peak_i] if wk else None})

    nl = Land.objects.filter(iso_code="NL").first()
    nl_regios = list(nl.regios.all()) if nl else []
    nl_feestdagen, _seen = [], set()
    if nl:
        for f in nl.feestdagen.filter(categorie="officieel", start_datum__year=TOON_JAAR).order_by("start_datum"):
            d = f.start_datum
            if (f.naam, d) in _seen:
                continue
            _seen.add((f.naam, d))
            nl_feestdagen.append({"naam": f.naam, "dag": _DAGEN[d.weekday()],
                                  "datum": f"{d.day} {_MAANDEN[d.month]}"})

    ctx = {
        "page": page,
        "seo_title": (page.seo_title if page else "") or PAGES[0].title,
        "seo_description": (page.seo_description if page else "") or PAGES[0].description,
        "weeks": wk,
        "best_idx": best_idx,
        "sel": wk[best_idx] if wk else None,
        "sel_factors": _factors(wk[best_idx]) if wk else [],
        "sel_band_label": _BAND_LABEL.get(wk[best_idx]["band"], "") if wk else "",
        "bestemmingen": Bestemming.objects.filter(actief=True),
        "ranked0": ranked0[:10],
        "default_idx": default_idx,
        "default_week": wk[default_idx] if wk else None,
        "map_vb": _MAP_VB,
        "vergelijk": vergelijk,
        "nl": nl,
        "nl_regios": nl_regios,
        "nl_feestdagen": nl_feestdagen,
        "faq": Faq.objects.filter(page_key="home", active=True),
        "latest_blog": BlogArtikel.objects.filter(active=True).order_by("order", "-id")[:3],
        "weeks_json": json.dumps(wk),
        "countries_json": json.dumps([{"code": c["code"], "name": c["name"],
                                       "flag": c["flag"], "drukte": c["drukte"]} for c in countries]),
    }
    ctx["jsonld"] = _jsonld([_faqpage_node(ctx["faq"], _page_url(request))])
    return render(request, "pages/home.html", ctx)


# ── Over ons ────────────────────────────────────────────────────────────────
def over_ons(request):
    from .models import Expert
    return render(request, "pages/over_ons.html", {
        "experts": Expert.objects.filter(active=True).order_by("order"),
        "bronnen": [
            ("Rijksoverheid.nl", "officiële schoolvakanties NL"),
            ("OpenHolidays API", "live vakantie- & feestdagdata EU"),
            ("KMK (Duitsland)", "spreiding van de deelstaten"),
        ],
        "seo_title": "Over ons — de mensen achter Schoolvakanties.nl",
        "seo_description": "Onafhankelijke vakantieplanner sinds 2009. Officiële data, een vaste "
                           "redactie en een zelfgebouwd drukte-model. Lees hoe we werken.",
    })


# ── Samenwerken (B2B / partnerships) ─────────────────────────────────────────
SAMENWERKING_TYPES = [
    "Reisbureau / touroperator", "Contentcreator / influencer",
    "Linkbuilding / advertorial", "Hotel / accommodatie", "Data / API", "Anders",
]


def _client_ip(request):
    """Beste-gok client-IP, achter de proxy van Render (X-Forwarded-For)."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _mail_samenwerking(naam, bedrijf, email, soort, bericht):
    """Best-effort doormailen van een lead. Faalt dit (geen/verkeerde mailserver),
    dan loggen we het — de lead staat al in de DB, dus gaat nooit verloren."""
    import logging
    from django.core.mail import send_mail
    body = (f"Naam: {naam}\nBedrijf: {bedrijf}\nE-mail: {email}\n"
            f"Type samenwerking: {soort}\n\n{bericht}")
    try:
        send_mail(f"Samenwerkingsaanvraag — {naam}", body,
                  settings.DEFAULT_FROM_EMAIL, [settings.PARTNER_INBOX],
                  fail_silently=False)
    except Exception:  # noqa: BLE001
        logging.getLogger("core").warning(
            "Samenwerking-mail mislukt (lead is wél opgeslagen).", exc_info=True)


def samenwerken(request):
    verzonden = False
    fout = ""
    if request.method == "POST":
        # Honeypot: bots vullen dit verborgen veld. Doe alsof het lukte en stop
        # (geen lead opslaan, geen mail) — zo merkt de bot niets.
        if request.POST.get("website", "").strip():
            verzonden = True
        else:
            from django.core.cache import cache
            from django.core.exceptions import ValidationError
            from django.core.validators import validate_email
            from core.models import Samenwerkingsaanvraag

            ip = _client_ip(request) or "?"
            key = f"sw-lead:{ip}"
            pogingen = cache.get(key, 0)
            naam = request.POST.get("naam", "").strip()[:120]
            bedrijf = request.POST.get("bedrijf", "").strip()[:160]
            email = request.POST.get("email", "").strip()[:254]
            soort = request.POST.get("soort", "").strip()
            bericht = request.POST.get("bericht", "").strip()[:4000]
            if soort not in SAMENWERKING_TYPES:
                soort = ""
            try:
                validate_email(email)
                email_ok = True
            except ValidationError:
                email_ok = False

            if pogingen >= 5:
                fout = ("Je hebt zojuist al een aanvraag verstuurd — probeer het over "
                        "een uurtje opnieuw of mail ons direct.")
            elif not (naam and bericht and email_ok):
                fout = "Vul je naam, een geldig e-mailadres en een kort bericht in."
            else:
                Samenwerkingsaanvraag.objects.create(
                    naam=naam, bedrijf=bedrijf, email=email, soort=soort,
                    bericht=bericht, ip=_client_ip(request))
                cache.set(key, pogingen + 1, 3600)
                _mail_samenwerking(naam, bedrijf, email, soort, bericht)
                verzonden = True
    return render(request, "pages/samenwerken.html", {
        "types": SAMENWERKING_TYPES,
        "verzonden": verzonden,
        "fout": fout,
        "seo_title": "Samenwerken met Schoolvakanties.nl — partnerships & adverteren",
        "seo_description": "Bereik Nederlandse gezinnen op het moment dat ze hun vakantie plannen. "
                           "Reisbureau, hotel, creator of merk — ontdek de mogelijkheden om samen te werken.",
    })


# ── Blog ────────────────────────────────────────────────────────────────────
def _blog_sidebar():
    """Gedeelde sidebar-data: slimste reisweek + eerstvolgende NL-vakanties."""
    from django.utils import timezone
    weeks = list(Reisweek.objects.filter(jaar=2026).order_by("weeknr"))
    best = max(weeks, key=lambda w: w.slim_score) if weeks else None
    today = timezone.localdate()
    nl = Land.objects.filter(iso_code="NL").first()
    komend = []
    if nl:
        seen = set()
        for v in nl.schoolvakanties.filter(start_datum__gte=today).order_by("start_datum"):
            if v.naam in seen:
                continue
            seen.add(v.naam)
            komend.append({"naam": v.naam, "dagen": (v.start_datum - today).days})
            if len(komend) >= 3:
                break
    return {"best_week": best, "komend": komend}


def blog_overzicht(request):
    posts = list(BlogArtikel.objects.filter(active=True).order_by("order", "-id"))
    featured = next((p for p in posts if p.featured), posts[0] if posts else None)
    rest = [p for p in posts if p != featured]
    ctx = {"featured": featured, "posts": rest, "cats": BLOG_CATS,
           "seo_title": "Blog — slim weg met het gezin | Schoolvakanties.nl",
           "seo_description": "Praktische tips, rustige bestemmingen en slim plannen rond de "
                              "schoolvakanties. Lees de blog van Schoolvakanties.nl."}
    ctx.update(_blog_sidebar())
    return render(request, "pages/blog.html", ctx)


def blog_detail(request, slug):
    post = BlogArtikel.objects.filter(slug=slug, active=True).first()
    if not post:
        raise Http404("Artikel niet gevonden")
    same = list(BlogArtikel.objects.filter(active=True, categorie=post.categorie).exclude(pk=post.pk))
    others = list(BlogArtikel.objects.filter(active=True).exclude(categorie=post.categorie).exclude(pk=post.pk))
    related = (same + others)[:3]
    url = _page_url(request)
    ctx = {"post": post, "related": related,
           "seo_title": f"{post.titel} | Schoolvakanties.nl",
           "seo_description": post.excerpt,
           "og_image": f"{settings.SITE_ORIGIN}/static/img/blog/{post.slug}.jpg",
           "crumbs": [{"naam": "Home", "url": "/"}, {"naam": "Blog", "url": "/blog/"},
                      {"naam": post.titel, "url": f"/blog/{post.slug}/"}],
           "jsonld": _jsonld([
               _breadcrumb_node([("Home", "/"), ("Blog", "/blog/"),
                                 (post.titel, f"/blog/{post.slug}/")]),
               _article_node(post, url),
           ])}
    ctx.update(_blog_sidebar())
    return render(request, "pages/blog_detail.html", ctx)


# ── Planner ─────────────────────────────────────────────────────────────────
def planner(request):
    import datetime as _dt
    weeks = list(Reisweek.objects.filter(jaar=2026).order_by("weeknr"))
    wk = [_week_dict(w) for w in weeks]
    best_idx = max(range(len(wk)), key=lambda i: wk[i]["score"]) if wk else 0

    # Per-bestemming data zodat de planner client-side kan herrekenen:
    #  - drukte: het echte drukteprofiel per land (europe.country_drukte)
    #  - weer: maand-temperatuur (WeerMaand) → 0-100 'zomers'-score, per week-maand
    # Landen zonder WeerMaand vallen terug op de generieke weer-curve.
    countries = europe.country_drukte(weeks)
    week_month = []
    for w in weeks:
        try:
            week_month.append(_dt.date.fromisocalendar(w.jaar, w.weeknr, 1).month)
        except Exception:
            week_month.append(7)
    weer_map = {}
    for land in Land.objects.filter(actief=True).prefetch_related("weermaanden"):
        mm = {m.maand: max(5, min(100, round(float(m.temp) / 28 * 100)))
              for m in land.weermaanden.all()}
        if mm:
            weer_map[land.iso_code.lower()] = mm
    overlap_curve = [d["overlap"] for d in wk]
    dest_data = {}
    for c in countries:
        wbm = weer_map.get(c["code"])
        weer = ([wbm.get(m, wk[i]["weer"]) for i, m in enumerate(week_month)] if wbm
                else [d["weer"] for d in wk])
        prijs = europe.prijs_curve(c["drukte"], overlap_curve,
                                   europe.PRIJS_NIVEAU.get(c["code"], 50))
        dest_data[c["code"]] = {"name": c["name"], "flag": c["flag"],
                                "drukte": c["drukte"], "weer": weer, "prijs": prijs}

    # Maandag/zondag per week (voor het koppelen van vakantievensters aan weken).
    week_span = []
    for w in weeks:
        try:
            mon = _dt.date.fromisocalendar(w.jaar, w.weeknr, 1)
            week_span.append((mon, mon + _dt.timedelta(days=6)))
        except Exception:
            week_span.append((None, None))

    # WANNEER — de échte NL-regio zomervensters (Noord/Midden/Zuid) als week-indexen.
    nl = Land.objects.filter(iso_code="NL").first()
    regio_windows = []
    if nl:
        for r in nl.regios.order_by("order"):
            zomer = (nl.schoolvakanties.filter(regios=r, naam__icontains="zomer",
                     start_datum__year=TOON_JAAR).order_by("start_datum").first())
            if not zomer or not zomer.eind_datum:
                continue
            s, e = zomer.start_datum, zomer.eind_datum
            # Weken die ín de vakantie starten (maandag binnen het venster) — zo
            # tonen we alleen volle reisweken, niet een halve week ervoor.
            idxs = [i for i, (mon, sun) in enumerate(week_span) if mon and s <= mon <= e]
            regio_windows.append({
                "code": r.code, "naam": r.naam,
                "label": f"{s.day} {_MND[s.month]} – {e.day} {_MND[e.month]}",
                "weeks": idxs})

    # WAARHEEN — wanneer is de (lange) zomervakantie op de bestemming afgelopen?
    # Dan zijn de scholen daar weer begonnen → meteen rustiger en goedkoper.
    def _summer_end(land):
        best = None
        for v in land.schoolvakanties.all():
            if (not v.eind_datum or v.start_datum.year != TOON_JAAR
                    or v.start_datum.month not in (6, 7)
                    or (v.eind_datum - v.start_datum).days < 20):
                continue
            if best is None or v.eind_datum > best:
                best = v.eind_datum
        return best
    dest_summer = {}
    for land in Land.objects.filter(actief=True).prefetch_related("schoolvakanties"):
        e = _summer_end(land)
        if not e:
            continue
        back = next((i for i, (mon, sun) in enumerate(week_span) if mon and mon > e), None)
        dest_summer[land.iso_code.lower()] = {
            "end": f"{e.day} {_MND[e.month]}", "back_idx": back}

    return render(request, "pages/planner.html", {
        "weeks": wk, "best_idx": best_idx,
        "sel": wk[best_idx] if wk else None,
        "sel_factors": _factors(wk[best_idx]) if wk else [],
        "sel_band_label": _BAND_LABEL.get(wk[best_idx]["band"], "") if wk else "",
        "weeks_json": json.dumps(wk),
        "dest_data_json": json.dumps(dest_data),
        "regio_windows": regio_windows,
        "regio_windows_json": json.dumps(regio_windows),
        "dest_summer_json": json.dumps(dest_summer),
        "seo_title": "Vakantieplanner — vind jullie slimste reisweek | Schoolvakanties.nl",
        "seo_description": "Plan de slimste week om met de kinderen weg te gaan. We scoren elke "
                           "week op drukte, prijs, weer en schoolvakantie-overlap.",
    })


# ── Druktekaart ─────────────────────────────────────────────────────────────
def _drukte_band(v):
    return "rustig" if v < 45 else "matig" if v < 70 else "druk"


def druktekaart(request):
    weeks = list(Reisweek.objects.filter(jaar=2026).order_by("weeknr"))
    wk = [_week_dict(w) for w in weeks]
    countries = europe.country_drukte(weeks)
    default_idx = min(11, len(weeks) - 1) if weeks else 0
    for c in countries:
        c["v0"] = c["drukte"][default_idx] if c["drukte"] else 0
        c["color0"] = europe.drukte_color(c["v0"])
    ranked0 = sorted(countries, key=lambda c: c["v0"])
    live = set(Land.objects.filter(actief=True).values_list("iso_code", flat=True))
    sel = next((c for c in countries if c["code"] == "it"), countries[0] if countries else None)
    sel_band = _drukte_band(sel["v0"]) if sel else "rustig"
    return render(request, "pages/druktekaart.html", {
        "ranked0": ranked0, "default_idx": default_idx,
        "map_vb": _MAP_VB,
        "default_week": wk[default_idx] if wk else None,
        "sel": sel, "sel_band": sel_band,
        "week_max": max(0, len(weeks) - 1),
        "live_codes": json.dumps(sorted(live)),
        "weeks_json": json.dumps(wk),
        "countries_json": json.dumps([{"code": c["code"], "name": c["name"],
                                       "flag": c["flag"], "drukte": c["drukte"]} for c in countries]),
        "seo_title": "Europese druktekaart — waar is het rustig per week | Schoolvakanties.nl",
        "seo_description": "Schuif door de weken en zie in één oogopslag waar het in Europa rustig is. "
                           "Groen→rood drukte per land, week voor week.",
    })


# ── Landen ──────────────────────────────────────────────────────────────────
def landen_overzicht(request):
    """Overzicht van alle Europese landen (live = al in de DB)."""
    return render(request, "pages/landen.html", {
        "europe": context_europe(),
        "seo_title": "Schoolvakanties per land in Europa | Schoolvakanties.nl",
        "seo_description": "Bekijk de schoolvakanties en feestdagen per Europees land. "
                           "Nederland en Duitsland zijn live; meer landen volgen.",
    })


def context_europe():
    live = list(Land.objects.filter(actief=True).values_list("iso_code", flat=True))
    return europe.europe_list(live)


def land_detail(request, slug):
    land = Land.objects.filter(slug=slug, actief=True).first()
    if not land:
        # Bekend land uit de navigatielijst maar (nog) zonder data — bv. Noorwegen,
        # Finland, Verenigd Koninkrijk, Denemarken, Griekenland: die worden niet door
        # OpenHolidays gedekt en hebben geen eigen bron. Toon een nette 'binnenkort'-
        # pagina (200, noindex) i.p.v. een harde 404. Onbekende slug -> echte 404.
        kandidaat = next((c for c in europe.europe_list() if c["slug"] == slug), None)
        if not kandidaat:
            raise Http404("Land niet gevonden")
        return render(request, "pages/land_soon.html", {
            "naam": kandidaat["name"], "vlag": kandidaat["flag"], "noindex": True,
            "crumbs": [{"naam": "Home", "url": "/"}, {"naam": "Landen", "url": "/landen/"},
                       {"naam": kandidaat["name"], "url": f"/landen/{slug}/"}],
            "seo_title": f"Schoolvakanties {kandidaat['name']} — binnenkort | Schoolvakanties.nl",
            "seo_description": f"De schoolvakanties en feestdagen van {kandidaat['name']} "
                               "voegen we binnenkort toe aan Schoolvakanties.nl.",
        })

    verberg = VERBERG_REGIO_CODES.get(land.iso_code, set())
    regios = [r for r in land.regios.order_by("order", "naam") if r.code not in verberg]
    regio_order = {r.id: i for i, r in enumerate(regios)}
    nationwide_names = _NL_LANDELIJK if land.iso_code == "NL" else set()

    # Jaar-switcher: welke jaren hebben (genoeg) data voor dit land? De import
    # bevat staarten van aangrenzende schooljaren — die filteren we eruit (>=3).
    from django.db.models import Count
    from django.db.models.functions import ExtractYear
    jaar_counts = (land.schoolvakanties.annotate(j=ExtractYear("start_datum"))
                   .values("j").annotate(n=Count("id")).order_by("j"))
    beschikbare_jaren = [r["j"] for r in jaar_counts if r["n"] >= 3 and r["j"] >= TOON_JAAR]
    if not beschikbare_jaren:
        beschikbare_jaren = [TOON_JAAR]
    try:
        jaar = int(request.GET.get("jaar", TOON_JAAR))
    except (TypeError, ValueError):
        jaar = TOON_JAAR
    if jaar not in beschikbare_jaren:
        jaar = beschikbare_jaren[0]

    # Schoolvakanties groeperen per periodenaam (op eerste startdatum). Alleen
    # vakanties die in het gekozen jaar starten (anders verschijnt de kerst-
    # vakantie van twee schooljaren als schijnduplicaat).
    periods = {}
    for v in (land.schoolvakanties.filter(start_datum__year=jaar)
              .prefetch_related("regios").order_by("start_datum")):
        # Alleen echte vakantieperiodes (≥3 dagen). Losse vrije/zweef-/brugdagen
        # (1–2 dagen: 'Día de libre disposición', 'Auffahrtsbrücke', studiedagen)
        # horen niet in de vakantietabel en veroorzaken schijnduplicaten.
        if v.eind_datum and (v.eind_datum - v.start_datum).days < 2:
            continue
        periods.setdefault(v.naam, []).append(v)

    period_list = []
    for naam, entries in sorted(periods.items(), key=lambda kv: kv[1][0].start_datum):
        first = entries[0]
        rows = []
        if naam in nationwide_names:
            rows.append({"regio": "Heel Nederland",
                         "periode": _periode_str(first.start_datum, first.eind_datum),
                         "weken": _weken_str(first.start_datum, first.eind_datum)})
        else:
            for v in entries:
                vr = [r for r in v.regios.all() if r.code not in verberg]
                # Entry die alleen verborgen (overzeese) regio's betreft: overslaan.
                if not vr and v.regios.exists():
                    continue
                base = {"periode": _periode_str(v.start_datum, v.eind_datum),
                        "weken": _weken_str(v.start_datum, v.eind_datum),
                        "_dur": (v.eind_datum - v.start_datum).days if v.eind_datum else 0,
                        "_start": v.start_datum}
                if not vr:
                    rows.append({**base, "regio": "Landelijk", "_o": -1})
                for r in vr:
                    rows.append({**base, "regio": r.naam, "_o": regio_order.get(r.id, 99)})
            # Eén rij per regio binnen een periode: heeft een regio meerdere
            # datums (sub-regio's/districten/schooltypes die verschillen, bv. CH-
            # kantons of CZ-gespreide voorjaarsvakantie), dan tonen we de langste
            # (hoofd)periode — anders verschijnt dezelfde regio verwarrend 2-3×.
            best = {}
            for r in rows:
                cur = best.get(r["regio"])
                if (cur is None or r["_dur"] > cur["_dur"]
                        or (r["_dur"] == cur["_dur"] and r["_start"] < cur["_start"])):
                    best[r["regio"]] = r
            rows = sorted(best.values(), key=lambda x: x.get("_o", 99))
        if not rows:  # periode bevatte alleen verborgen regio's
            continue
        nl_vert = _vakantie_nl(naam) if land.iso_code != "NL" else ""
        if nl_vert and nl_vert == naam.lower():
            nl_vert = ""
        period_list.append({
            "naam": naam, "nl_naam": nl_vert, "alias": first.alias, "status": first.status,
            "note": first.note, "rows": rows,
            "verplicht": "verplicht" in (first.status or "").lower(),
        })

    # Feestdagen (officieel) met NL-weergave. Alléén LANDELIJKE feestdagen — de
    # vrije dagen die in het hele land gelden. Regionale/lokale dagen (bv. de
    # Portugese 'Feriado Municipal' per gemeente, of de autonome-gemeenschapsdagen
    # in Spanje) zijn voor een landelijk reisoverzicht ruis en blazen de lijst op.
    feestdagen, _fseen = [], set()
    landelijke = list(land.feestdagen.filter(
        categorie="officieel", start_datum__year=jaar, landelijk=True)
        .prefetch_related("regios").order_by("start_datum"))
    regio_feest_aantal = (land.feestdagen.filter(
        categorie="officieel", start_datum__year=jaar, landelijk=False).count())
    for f in landelijke:
        d = f.start_datum
        key = (f.naam, d)
        if key in _fseen:
            continue
        _fseen.add(key)
        feestdagen.append({"naam": f.naam, "dag": _DAGEN[d.weekday()],
                           "datum": f"{d.day} {_MAANDEN[d.month]}",
                           "uitleg": _feestdag_uitleg(f.naam)})
    officieus = [{"naam": f.naam, "datum": _periode_str(f.start_datum, f.eind_datum)
                  if f.eind_datum else f"{f.start_datum.day} {_MND[f.start_datum.month]}",
                  "emoji": f.emoji, "uitleg": _officieus_uitleg(f.naam)}
                 for f in land.feestdagen.filter(categorie="officieus").order_by("start_datum")]

    # Weer-band (temperatuur): hoogte + kalme kleur per maand.
    weer_rows = []
    for w in land.weermaanden.order_by("maand"):
        t = float(w.temp)
        weer_rows.append({"m": _MND[w.maand], "temp": t,
                          "h": max(8, round(t / 28 * 100)),
                          "color": europe.drukte_color(100 - min(100, t / 28 * 100)),
                          "zomer": w.maand in (6, 7, 8)})

    # Beste reisweken (Slim-score) uit de radar-data.
    brw = [{"wk": w.weeknr, "d1": w.start_label, "score": w.slim_score, "band": w.band}
           for w in Reisweek.objects.filter(jaar=2026).order_by("weeknr")]
    brw_max = max((w["score"] for w in brw), default=1) or 1
    brw_top = sorted(sorted(brw, key=lambda w: -w["score"])[:4], key=lambda w: w["wk"])

    # Vooruitblik: eerstvolgende vakantie vanaf vandaag.
    from django.utils import timezone
    today = timezone.localdate()
    nxt = land.schoolvakanties.filter(start_datum__gte=today).order_by("start_datum").first()
    vooruitblik = None
    if nxt:
        vooruitblik = {"naam": nxt.naam, "dagen": (nxt.start_datum - today).days}

    deel_label = {"DE": "Deelstaat", "BE": "Gemeenschap"}.get(land.iso_code, "Regio")
    bron_kort = {"NL": "Rijksoverheid.nl", "FR": "Éducation nationale",
                 "DE": "OpenHolidays (KMK)",
                 "NO": "Nager.Date", "DK": "Nager.Date", "FI": "Nager.Date",
                 "GB": "Nager.Date", "GR": "Nager.Date"}.get(land.iso_code, "OpenHolidays")
    return render(request, "pages/land.html", {
        "land": land, "regios": regios, "deel_label": deel_label, "bron_kort": bron_kort,
        "regio_feest_aantal": regio_feest_aantal,
        "jaar": jaar, "beschikbare_jaren": beschikbare_jaren,
        "nl_regio_overzicht": ([{"naam": r.naam, "uitleg": r.uitleg,
                                 "provincies": NL_REGIO_PROVINCIES.get(r.naam, [])} for r in regios]
                               if land.iso_code == "NL" else None),
        "periods": period_list, "feestdagen": feestdagen, "officieus": officieus,
        "weer_rows": weer_rows, "brw": brw, "brw_max": brw_max, "brw_top": brw_top,
        "faq": Faq.objects.filter(page_key=f"land-{land.iso_code.lower()}", active=True),
        "land_blog": BlogArtikel.objects.filter(active=True, landen=land).order_by("order", "-id")[:3],
        "vooruitblik": vooruitblik,
        "crumbs": [{"naam": "Home", "url": "/"}, {"naam": "Landen", "url": "/landen/"},
                   {"naam": land.naam, "url": f"/landen/{land.slug}/"}],
        "jsonld": _jsonld([
            _breadcrumb_node([("Home", "/"), ("Landen", "/landen/"),
                              (land.naam, f"/landen/{land.slug}/")]),
            _faqpage_node(Faq.objects.filter(page_key=f"land-{land.iso_code.lower()}", active=True),
                          _page_url(request)),
        ]),
        "seo_title": f"Schoolvakanties {land.naam} {jaar} — data per {deel_label.lower()} | Schoolvakanties.nl",
        "seo_description": f"Alle schoolvakanties en feestdagen van {land.naam} in {jaar}, "
                           f"overzichtelijk per {deel_label.lower()}. {land.intro[:90]}",
    })
