"""Genereer realistische SVG-landpaden uit de Europa-GeoJSON -> core/europe_geo.py."""
import json
import math

W = 720.0                 # doel-breedte van de viewBox
EPS = 1.3                 # min. afstand tussen punten (SVG-eenheden) = simplificatie
MIN_RING_AREA = 10.0      # kleinere ringen (eilandjes) overslaan
BBOX = (-11.0, 35.0, 30.0, 60.5)  # lon_min, lat_min, lon_max, lat_max — West/Centraal/Zuid-Europa

geo = json.load(open("_europe.geojson", encoding="utf-8"))


def merc(lon, lat):
    lat = max(-85.0, min(85.0, lat))
    return math.radians(lon), math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def in_focus(props):
    return BBOX[0] <= props.get("LON", 0) <= BBOX[2] and BBOX[1] <= props.get("LAT", 0) <= BBOX[3]

feats = [f for f in geo["features"] if in_focus(f["properties"]) and f["properties"].get("ISO2")]

# 1) projecteer alles, bepaal grenzen
allpts = []
for f in feats:
    g = f["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        for ring in poly:
            for lon, lat in ring:
                allpts.append(merc(lon, lat))
minx = min(p[0] for p in allpts); maxx = max(p[0] for p in allpts)
miny = min(p[1] for p in allpts); maxy = max(p[1] for p in allpts)
scale = W / (maxx - minx)
H = round((maxy - miny) * scale, 1)


def sx(x): return round((x - minx) * scale)
def sy(y): return round((maxy - y) * scale)


def ring_to_pts(ring):
    pts = []
    for lon, lat in ring:
        mx, my = merc(lon, lat)
        x, y = sx(mx), sy(my)
        if not pts or (abs(x - pts[-1][0]) + abs(y - pts[-1][1])) >= EPS:
            pts.append((x, y))
    return pts


def bbox_area(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return (max(xs) - min(xs)) * (max(ys) - min(ys)) if pts else 0


PATHS, LABELS, NAMES = {}, {}, {}
for f in feats:
    code = f["properties"]["ISO2"]
    name = f["properties"]["NAME"]
    g = f["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    subpaths = []
    for poly in polys:
        outer = poly[0]
        pts = ring_to_pts(outer)
        if len(pts) < 3 or bbox_area(pts) < MIN_RING_AREA:
            continue
        d = "M" + " ".join(f"{x},{y}" for x, y in pts) + "Z"
        subpaths.append(d)
    if not subpaths:
        continue
    PATHS[code] = "".join(subpaths)
    mx, my = merc(f["properties"]["LON"], f["properties"]["LAT"])
    LABELS[code] = (sx(mx), sy(my))
    NAMES[code] = name

with open("core/europe_geo.py", "w", encoding="utf-8") as out:
    out.write('"""Realistische Europa-landpaden (gegenereerd uit GeoJSON, Mercator).\n')
    out.write('Niet handmatig bewerken — zie _gen_geo.py."""\n\n')
    out.write(f"VIEWBOX = (0, 0, {round(W,1)}, {H})\n\n")
    out.write("COUNTRY_PATHS = {\n")
    for code in sorted(PATHS):
        out.write(f'    "{code.lower()}": "{PATHS[code]}",\n')
    out.write("}\n\n")
    out.write("LABEL_POS = {\n")
    for code in sorted(LABELS):
        out.write(f'    "{code.lower()}": ({LABELS[code][0]}, {LABELS[code][1]}),\n')
    out.write("}\n\n")
    out.write("NAMES = {\n")
    for code in sorted(NAMES):
        out.write(f'    "{code.lower()}": {json.dumps(NAMES[code], ensure_ascii=False)},\n')
    out.write("}\n")

size = sum(len(p) for p in PATHS.values())
print(f"landen: {len(PATHS)} | viewBox 0 0 {round(W,1)} {H} | totaal pad-chars: {size}")
print("codes:", ", ".join(sorted(PATHS)))
