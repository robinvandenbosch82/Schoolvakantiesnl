"""
Europa-data voor de navigatie en de druktekaart.

- EUROPE: de volledige landenlijst voor het mega-menu / de landenkiezer (port
  van het v3-prototype, components/CountryPicker.jsx). `live` wordt at-runtime
  bepaald: een land is 'live' zodra er een actief Land in de DB staat.
- Het drukteprofiel per land (gauss rond een piekweek) en de kalme kleurschaal
  zijn een 1-op-1 port van data.js / EuropeMap.jsx, zodat de mini-druktekaart en
  de vergelijk-strip server-side renderen met exact dezelfde cijfers.
"""
from __future__ import annotations

import math
import re
from functools import lru_cache

# (code, naam, vlag, populair)
_EUROPE = [
    ("nl", "Nederland", "🇳🇱", True), ("de", "Duitsland", "🇩🇪", True),
    ("be", "België", "🇧🇪", True), ("fr", "Frankrijk", "🇫🇷", True),
    ("es", "Spanje", "🇪🇸", True), ("it", "Italië", "🇮🇹", True),
    ("at", "Oostenrijk", "🇦🇹", True), ("pt", "Portugal", "🇵🇹", True),
    ("ch", "Zwitserland", "🇨🇭", False), ("gb", "Verenigd Koninkrijk", "🇬🇧", False),
    ("ie", "Ierland", "🇮🇪", False), ("dk", "Denemarken", "🇩🇰", False),
    ("se", "Zweden", "🇸🇪", False), ("no", "Noorwegen", "🇳🇴", False),
    ("fi", "Finland", "🇫🇮", False), ("pl", "Polen", "🇵🇱", False),
    ("cz", "Tsjechië", "🇨🇿", False), ("sk", "Slowakije", "🇸🇰", False),
    ("hu", "Hongarije", "🇭🇺", False), ("si", "Slovenië", "🇸🇮", False),
    ("hr", "Kroatië", "🇭🇷", False), ("gr", "Griekenland", "🇬🇷", False),
    ("lu", "Luxemburg", "🇱🇺", False), ("li", "Liechtenstein", "🇱🇮", False),
    ("mt", "Malta", "🇲🇹", False), ("ee", "Estland", "🇪🇪", False),
    ("lv", "Letland", "🇱🇻", False), ("lt", "Litouwen", "🇱🇹", False),
    ("bg", "Bulgarije", "🇧🇬", False), ("ro", "Roemenië", "🇷🇴", False),
]


def _slug(naam):
    s = naam.lower().replace("ë", "e").replace("ï", "i")
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z]+", "-", s))


def europe_list(live_codes=()):
    """Landenlijst met slug + live-status (live_codes = set ISO-codes lowercase)."""
    live = {c.lower() for c in live_codes}
    return [
        {"code": code, "name": naam, "flag": vlag, "pop": pop,
         "slug": _slug(naam), "live": code in live}
        for code, naam, vlag, pop in _EUROPE
    ]


# ── Drukteprofiel per land (gauss rond een piekweek) ────────────────────────
# code -> (piek-week-index 0..19 [wk19..wk38], spreiding, basisdrukte).
# Indicatief model: zuidelijke bestemmingen pieken later/hoger (augustus),
# noordelijke vroeger. Bepaalt de kleur op de druktekaart per week.
_PROFILES = {
    # West/Centraal-Europa
    "nl": (12, 2.4, 24), "be": (12, 2.6, 24), "de": (14, 3.2, 26), "fr": (13, 2.0, 22),
    "at": (11, 2.4, 22), "ch": (11, 2.4, 22), "lu": (12, 2.4, 24), "gb": (14, 2.8, 24),
    "ie": (14, 2.8, 24),
    # Zuid-Europa (druk & laat)
    "es": (13, 2.6, 30), "it": (13, 2.2, 28), "pt": (14, 2.4, 28), "hr": (14, 2.2, 30),
    "gr": (14, 2.4, 30),
    # Centraal/Oost-Europa
    "pl": (12, 2.8, 24), "cz": (12, 2.6, 23), "sk": (12, 2.6, 23), "hu": (13, 2.6, 25),
    "si": (12, 2.4, 24), "ro": (13, 2.8, 24), "bg": (13, 2.6, 25),
    # Noord/Baltisch (vroeg). NB: Zweden/Noorwegen vallen buiten de kaart-bbox
    # (te noordelijk), dus geen profiel, anders staan ze wel in de lijst maar
    # niet op de kaart.
    "dk": (10, 2.6, 22), "ee": (10, 2.6, 21), "lv": (10, 2.6, 21), "lt": (10, 2.6, 21),
}


# Structureel prijsniveau per land (NL-toeristenperspectief, 0-100; 50 ≈ gemiddeld).
# Indicatief: Alpen/Scandinavië duur, Zuid- en Oost-Europa goedkoper. Samen met de
# lokale drukte (vraag op de bestemming) en de NL-vakantie-overlap (vluchtprijzen
# vanuit NL) bepaalt dit de prijs-as per week (zie views.planner).
PRIJS_NIVEAU = {
    "ch": 82, "li": 80, "dk": 74, "lu": 70, "se": 70, "ie": 70, "gb": 68,
    "fr": 66, "at": 66, "nl": 64, "be": 62, "de": 62, "it": 58, "mt": 54,
    "es": 52, "pt": 50, "si": 50, "ee": 50, "gr": 50, "hr": 50,
    "lv": 46, "lt": 46, "hu": 44, "cz": 44, "pl": 42, "sk": 42,
    "bg": 36, "ro": 36,
}


def prijs_curve(drukte, overlap, niveau):
    """Indicatieve prijs-as (0-100) per week: blend van lokale drukte op de
    bestemming, de NL-vakantie-overlap (origin-premie) en het structurele niveau."""
    return [max(5, min(100, round(0.45 * d + 0.30 * o + 0.25 * niveau)))
            for d, o in zip(drukte, overlap)]


@lru_cache(maxsize=None)
def drukte_profile(peak, spread, base, n):
    """Gauss-drukteprofiel rond de piekweek (0–100 per week). Gememoized: de invoer
    komt uit de constante _PROFILES, dus elk uniek profiel wordt één keer berekend
    i.p.v. per request (country_drukte roept dit 25× aan). Geeft een tuple terug,     immutable, dus veilig om tussen requests te delen."""
    return tuple(
        round(base + (100 - base) * math.exp(-((i - peak) ** 2) / (2 * spread * spread)))
        for i in range(n)
    )


def country_drukte(weeks):
    """[(code, naam, vlag, [drukte per week])] voor de mini-kaart + vergelijking."""
    n = len(weeks)
    by_code = {c["code"]: c for c in europe_list()}
    rows = []
    for code, (peak, spread, base) in _PROFILES.items():
        meta = by_code.get(code, {"name": code.upper(), "flag": ""})
        rows.append({"code": code, "name": meta["name"], "flag": meta["flag"],
                     "drukte": drukte_profile(peak, spread, base, n)})
    return rows


# Realistische Europa-landpaden (gegenereerd uit GeoJSON, zie _gen_geo.py).
from .europe_geo import COUNTRY_PATHS, LABEL_POS, NAMES, VIEWBOX  # noqa: E402

CONTEXT_KLEUR = "oklch(90% 0.008 95)"  # zacht grijs voor landen zonder drukte-data


def map_shapes(countries, week_idx):
    """Alle Europese landvormen voor de SVG-kaart: landen mét drukte-data worden
    gekleurd + zijn interactief (`data`=True), de rest is grijze context."""
    by_code = {c["code"]: c for c in countries}
    out = []
    for code, path in COUNTRY_PATHS.items():
        lx, ly = LABEL_POS.get(code, (0, 0))
        c = by_code.get(code)
        if c and c.get("drukte"):
            v = c["drukte"][week_idx]
            out.append({"code": code, "name": c["name"], "path": path, "lx": lx, "ly": ly,
                        "v": v, "color": drukte_color(v), "data": True})
        else:
            out.append({"code": code, "name": NAMES.get(code, code.upper()), "path": path,
                        "lx": lx, "ly": ly, "v": None, "color": CONTEXT_KLEUR, "data": False})
    # Context eerst tekenen, data-landen erbovenop.
    out.sort(key=lambda s: s["data"])
    return out


def drukte_color(v):
    """0–100 -> kalme groen→amber→rood-schaal (port van EuropeMap.drukteColor)."""
    if v < 38:
        return "var(--rustig)"
    if v < 56:
        return "oklch(76% 0.135 120)"
    if v < 70:
        return "var(--matig)"
    if v < 84:
        return "oklch(72% 0.15 50)"
    return "var(--druk)"


def band(score):
    if score >= 70:
        return "rustig"
    if score >= 45:
        return "matig"
    return "druk"
