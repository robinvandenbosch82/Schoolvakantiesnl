"""
Genereer een SVG-kaart van de Franse schoolvakantie-zones (A/B/C + Corse) uit
de officiële régions-GeoJSON, plus een legenda. Schrijft een Django-partial:

    templates/partials/france_zones.html

Eenmalig draaien (de output is statisch en wordt gecachet):

    python deploy/tools/gen_france_zones.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")

GEO = ("https://raw.githubusercontent.com/gregoiredavid/france-geojson/"
       "master/regions-version-simplifiee.geojson")
OUT = Path(__file__).resolve().parents[2] / "templates" / "partials" / "france_zones.html"

# Régio -> schoolzone. De zones zijn officieel per académie bepaald; de 13
# métropole-régions vallen er schoon in (geverifieerd 2023–2026).
ZONE = {
    "Auvergne-Rhône-Alpes": "A", "Bourgogne-Franche-Comté": "A", "Nouvelle-Aquitaine": "A",
    "Bretagne": "B", "Centre-Val de Loire": "B", "Grand Est": "B", "Hauts-de-France": "B",
    "Normandie": "B", "Pays de la Loire": "B", "Provence-Alpes-Côte d'Azur": "B",
    "Île-de-France": "C", "Occitanie": "C",
    "Corse": "COR",
}
KLEUR = {
    "A":   "oklch(72% 0.115 250)",   # blauw
    "B":   "oklch(73% 0.125 150)",   # groen
    "C":   "oklch(78% 0.135 70)",    # amber
    "COR": "oklch(68% 0.11 330)",    # paars
}
ZONE_LABEL = {"A": "Zone A", "B": "Zone B", "C": "Zone C", "COR": "Corse"}
# Legenda: zone -> (régions in NL-vriendelijke schrijfwijze, herkenbare steden).
LEGENDA = {
    "A": ("Bourgogne-Franche-Comté, Auvergne-Rhône-Alpes, Nouvelle-Aquitaine",
          "Lyon · Bordeaux · Grenoble · Dijon"),
    "B": ("Bretagne, Normandie, Hauts-de-France, Grand Est, Pays de la Loire, "
          "Centre-Val de Loire, Provence-Alpes-Côte d'Azur",
          "Marseille · Nice · Rijsel · Straatsburg · Nantes"),
    "C": ("Île-de-France, Occitanie", "Parijs · Toulouse · Montpellier · Versailles"),
    "COR": ("Corsica", "Ajaccio · Bastia"),
}

W, MARGIN = 560, 12


def rings(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    out = []
    for poly in geom["coordinates"]:
        out.append(poly[0])
    return out


def main():
    data = requests.get(GEO, timeout=60).json()
    cos = math.cos(math.radians(46.6))

    # Projecteer alle ringen (equirectangulair, lat-gecorrigeerd) en bepaal bbox.
    feats = []
    minx = miny = 1e9
    maxx = maxy = -1e9
    for f in data["features"]:
        naam = f["properties"]["nom"]
        zone = ZONE.get(naam)
        if not zone:
            continue
        prings = []
        for ring in rings(f["geometry"]):
            pr = [(lon * cos, -lat) for lon, lat in ring]
            prings.append(pr)
            for x, y in pr:
                minx, miny = min(minx, x), min(miny, y)
                maxx, maxy = max(maxx, x), max(maxy, y)
        feats.append((naam, zone, prings))

    sx = (W - 2 * MARGIN) / (maxx - minx)
    H = round((maxy - miny) * sx + 2 * MARGIN)

    def tx(x): return round((x - minx) * sx + MARGIN, 1)
    def ty(y): return round((y - miny) * sx + MARGIN, 1)

    paths = []
    labels = []
    for naam, zone, prings in feats:
        d = []
        # grootste ring voor het zone-label (centroïde-benadering)
        big = max(prings, key=len)
        cx = sum(p[0] for p in big) / len(big)
        cy = sum(p[1] for p in big) / len(big)
        for ring in prings:
            d.append("M" + " ".join(f"{tx(x)},{ty(y)}" for x, y in ring) + "Z")
        paths.append(
            f'<path d="{"".join(d)}" fill="{KLEUR[zone]}" stroke="#fff" '
            f'stroke-width="1.1" stroke-linejoin="round"><title>{naam} — '
            f'{ZONE_LABEL[zone]}</title></path>')
        labels.append(
            f'<text x="{tx(cx)}" y="{ty(cy)}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="13" font-weight="800" '
            f'fill="#fff" style="paint-order:stroke;stroke:rgba(0,0,0,.18);'
            f'stroke-width:3px">{zone if zone!="COR" else "Co"}</text>')

    svg = (f'<svg viewBox="0 0 {W} {H}" class="fr-zone-map" '
           f'xmlns="http://www.w3.org/2000/svg" role="img" '
           f'aria-label="Kaart van de Franse schoolvakantie-zones A, B en C">\n  '
           + "\n  ".join(paths) + "\n  " + "\n  ".join(labels) + "\n</svg>")

    legenda = []
    for z in ("A", "B", "C", "COR"):
        regs, steden = LEGENDA[z]
        legenda.append(
            f'<li class="fzl-item"><span class="fzl-chip" style="background:{KLEUR[z]}">'
            f'{z if z!="COR" else "Co"}</span>'
            f'<span class="fzl-tx"><b>{ZONE_LABEL[z]}</b>'
            f'<span class="fzl-reg">{regs}</span>'
            f'<span class="fzl-st">{steden}</span></span></li>')

    html = (
        "{# GEGENEREERD door deploy/tools/gen_france_zones.py — niet handmatig "
        "bewerken #}\n"
        '<div class="fr-zones">\n'
        '  <div class="fr-zones-map">\n    ' + svg + "\n  </div>\n"
        '  <ul class="fr-zones-legenda">\n    ' + "\n    ".join(legenda) + "\n  </ul>\n"
        "</div>\n")
    OUT.write_text(html, encoding="utf-8")
    print(f"Geschreven: {OUT}  ({len(feats)} régions, viewBox 0 0 {W} {H})")


if __name__ == "__main__":
    main()
