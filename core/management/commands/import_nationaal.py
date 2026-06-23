"""
Importeer SCHOOLVAKANTIES uit de gezaghebbende nationale bronnen, als override op
OpenHolidays (dat voor deze landen rommeliger/minder precies is):

  * NL, Rijksoverheid open data (opendata.rijksoverheid.nl). De officiële
    adviesdata per regio Noord/Midden/Zuid (+ 'heel Nederland'), inclusief of de
    periode wettelijk verplicht is. Loopt meerdere schooljaren vooruit.
  * FR, Éducation nationale open data (data.education.gouv.fr). Het échte
    Franse model: schoolzones A / B / C (+ Corse). Overzeese gebieden worden
    bewust overgeslagen (alleen métropole).

(DE blijft op OpenHolidays, dat is al de officiële KMK-bron; ferien-api.de
dient als losse kruiscontrole, zie check_ferien_de.)

Idempotent: upsert op een genamespacede external_id (bv. 'rijksoverheid:…'),
vergrendelde rijen blijven met rust. Na de upsert worden de oude OpenHolidays-
schoolvakanties (bron='api', niet vergrendeld) van dat land verwijderd, zodat er
geen dubbele periodes overblijven. Redactionele Land-velden blijven ongemoeid;
alleen Land.bron (provenance-vermelding) en imported_at worden gezet.

    python manage.py import_nationaal
    python manage.py import_nationaal --country FR
"""
from __future__ import annotations

import datetime as dt
import sys

import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.text import slugify

from core.models import Land, Regio, Schoolvakantie

RIJKS_URL = "https://opendata.rijksoverheid.nl/v1/infotypes/schoolholidays"
FR_URL = ("https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/"
          "fr-en-calendrier-scolaire/records")

LAND_META = {  # iso -> (naam, vlag, provenance-vermelding)
    "NL": ("Nederland", "🇳🇱", "Schoolvakanties: Rijksoverheid.nl · feestdagen: OpenHolidays.org"),
    "FR": ("Frankrijk", "🇫🇷", "Schoolvakanties: Éducation nationale (data.education.gouv.fr) · feestdagen: OpenHolidays.org"),
}

# ── NL ──────────────────────────────────────────────────────────────────────
NL_REGIOS = [
    ("NL-NOORD", "Noord", "Groningen, Friesland, Drenthe, Overijssel, Noord-Holland en het grootste deel van Flevoland."),
    ("NL-MIDDEN", "Midden", "Zuid-Holland, Utrecht en een deel van Gelderland."),
    ("NL-ZUID", "Zuid", "Zeeland, Limburg, Noord-Brabant en een deel van Gelderland."),
]
NL_REGIO_CODE = {"noord": "NL-NOORD", "midden": "NL-MIDDEN", "zuid": "NL-ZUID"}

# ── FR ──────────────────────────────────────────────────────────────────────
# Officiële zone-indeling (geldend 2023–2026). Overzee blijft buiten beschouwing.
FR_ZONES = {
    "Zone A": ("FR-ZA", "Zone A",
               "Académies Besançon, Bordeaux, Clermont-Ferrand, Dijon, Grenoble, Limoges, Lyon en Poitiers."),
    "Zone B": ("FR-ZB", "Zone B",
               "Académies Aix-Marseille, Amiens, Lille, Nancy-Metz, Nantes, Nice, Normandie, Orléans-Tours, Reims, Rennes en Strasbourg."),
    "Zone C": ("FR-ZC", "Zone C",
               "Académies Créteil, Montpellier, Paris, Toulouse en Versailles."),
    "Corse": ("FR-COR", "Corse", "Corse-du-Sud en Haute-Corse."),
}
FR_POP_OK = {"-", "Élèves"}


def _clean(s):
    return " ".join((s or "").split())


class Command(BaseCommand):
    help = "Importeer schoolvakanties uit de nationale bronnen (NL/FR/DE)."

    def add_arguments(self, parser):
        parser.add_argument("--country", default="NL,FR",
                            help="Komma-gescheiden: NL,FR (standaard beide).")
        parser.add_argument("--from", dest="dfrom", default="2025-08-01",
                            help="Vroegste startdatum die we bewaren (YYYY-MM-DD).")
        parser.add_argument("--to", dest="dto", default="2028-08-01",
                            help="Laatste startdatum die we ophalen (YYYY-MM-DD).")

    def handle(self, *args, **opts):
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

        self.dfrom = dt.date.fromisoformat(opts["dfrom"])
        self.dto = dt.date.fromisoformat(opts["dto"])
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json",
                                     "User-Agent": "schoolvakanties.nl-importer"})
        self.now = timezone.now()

        codes = [c.strip().upper() for c in opts["country"].split(",") if c.strip()]
        handlers = {"NL": self._import_nl, "FR": self._import_fr}
        for code in codes:
            if code not in handlers:
                self.stderr.write(self.style.WARNING(f"Land {code} heeft geen nationale bron, overgeslagen."))
                continue
            land = self._ensure_land(code)
            done = handlers[code](land)
            removed = self._purge_openholidays(land)
            land.imported_at = self.now
            land.save(update_fields=["imported_at"])
            self.stdout.write(self.style.SUCCESS(
                f"{land.naam} ({code}), {done} schoolvakanties geïmporteerd, "
                f"{removed} oude OpenHolidays-rijen opgeruimd."))

    # ── HTTP ──────────────────────────────────────────────────────────────────
    def _get(self, url, **params):
        resp = self.session.get(url, params=params, timeout=40)
        resp.raise_for_status()
        return resp.json()

    # ── Land + regio's ──────────────────────────────────────────────────────
    def _ensure_land(self, code):
        naam, vlag, bron = LAND_META[code]
        land, _ = Land.objects.get_or_create(
            iso_code=code, defaults={"naam": naam, "vlag": vlag})
        changed = []
        if land.naam != naam:
            land.naam = naam; changed.append("naam")
        gewenste = slugify(naam)
        if land.slug != gewenste:
            land.slug = gewenste; changed.append("slug")
        if not land.vlag:
            land.vlag = vlag; changed.append("vlag")
        if land.bron != bron:
            land.bron = bron; changed.append("bron")
        if changed:
            land.save(update_fields=changed)
        return land

    def _regio(self, land, code, naam, uitleg="", order=0):
        regio, _ = Regio.objects.update_or_create(
            code=code, defaults={"land": land, "naam": naam, "korte_naam": naam[:60],
                                 "uitleg": uitleg, "order": order})
        return regio

    def _save_vakantie(self, ext, land, naam, start, eind, regios, *, landelijk,
                       bron, status="", typ=""):
        """Upsert één periode; respecteert vergrendeld. Geeft 1 terug bij verwerkt."""
        existing = Schoolvakantie.objects.filter(external_id=ext).first()
        if existing and existing.vergrendeld:
            return 0
        obj, _ = Schoolvakantie.objects.update_or_create(
            external_id=ext,
            defaults={"land": land, "naam": naam, "type": typ,
                      "start_datum": start, "eind_datum": eind,
                      "landelijk": landelijk, "status": status,
                      "bron": bron, "imported_at": self.now})
        if landelijk:
            obj.regios.clear()
        else:
            obj.regios.set(regios)
        return 1

    def _purge_openholidays(self, land):
        """Verwijder oude OpenHolidays-schoolvakanties van dit land (niet vergrendeld);
        voor FR ook de oude regio-regio's die nu door zones vervangen zijn."""
        n, _ = Schoolvakantie.objects.filter(
            land=land, bron="api", vergrendeld=False).delete()
        if land.iso_code == "FR":
            zone_codes = [v[0] for v in FR_ZONES.values()]
            Regio.objects.filter(land=land).exclude(code__in=zone_codes).delete()
        return n

    # ── NL: Rijksoverheid ─────────────────────────────────────────────────────
    def _import_nl(self, land):
        for i, (code, naam, uitleg) in enumerate(NL_REGIOS):
            self._regio(land, code, naam, uitleg, i)
        regio_obj = {c: Regio.objects.get(code=c) for c in NL_REGIO_CODE.values()}

        try:
            data = self._get(RIJKS_URL, output="json")
        except requests.RequestException as exc:
            raise CommandError(f"Rijksoverheid-aanroep mislukt: {exc}") from exc

        done = 0
        for item in data:
            for content in item.get("content", []):
                jaar = _clean(content.get("schoolyear"))
                for vak in content.get("vacations", []):
                    typ = _clean(vak.get("type"))
                    verplicht = str(vak.get("compulsorydates")).lower() == "true"
                    status = "Wettelijk verplicht" if verplicht else "Adviesdata"
                    for reg in vak.get("regions", []):
                        rnaam = (reg.get("region") or "").strip().lower()
                        start = dt.date.fromisoformat((reg.get("startdate") or "")[:10])
                        eind = dt.date.fromisoformat((reg.get("enddate") or "")[:10])
                        if eind < self.dfrom or start.year > self.dto.year:
                            continue
                        landelijk = rnaam == "heel nederland"
                        regios = [] if landelijk else [regio_obj[NL_REGIO_CODE[rnaam]]]
                        ext = f"rijksoverheid:{jaar}:{slugify(typ)}:{rnaam.replace(' ', '')}"
                        done += self._save_vakantie(
                            ext, land, typ, start, eind, regios,
                            landelijk=landelijk, bron="rijksoverheid", status=status)
        return done

    # ── FR: Éducation nationale ───────────────────────────────────────────────
    def _import_fr(self, land):
        for i, (code, naam, uitleg) in enumerate(
                [(v[0], v[1], v[2]) for v in FR_ZONES.values()]):
            self._regio(land, code, naam, uitleg, i)
        zone_regio = {label: Regio.objects.get(code=meta[0])
                      for label, meta in FR_ZONES.items()}

        where = f"start_date>='{self.dfrom}' and start_date<'{self.dto}'"
        done = offset = 0
        while True:
            try:
                page = self._get(FR_URL, limit=100, offset=offset, where=where)
            except requests.RequestException as exc:
                raise CommandError(f"Éducation nationale-aanroep mislukt: {exc}") from exc
            results = page.get("results") or []
            if not results:
                break
            for r in results:
                zone = r.get("zones")
                desc = (r.get("description") or "").strip()
                if zone not in FR_ZONES or r.get("population") not in FR_POP_OK:
                    continue
                if desc.startswith("Début des") or not desc:
                    continue
                start = self._fr_date(r.get("start_date"))
                eind = self._fr_date(r.get("end_date")) - dt.timedelta(days=1)
                if not start or eind < start:
                    continue
                jaar = _clean(r.get("annee_scolaire"))
                ext = f"edu-fr:{jaar}:{FR_ZONES[zone][0]}:{slugify(desc)}"
                done += self._save_vakantie(
                    ext, land, desc, start, eind, [zone_regio[zone]],
                    landelijk=False, bron="edu-fr")
            offset += 100
        return done

    @staticmethod
    def _fr_date(s):
        """De API codeert de lokale middernacht als UTC (winter T23:00Z, zomer
        T22:00Z). +2u tilt dat altijd naar de juiste kalenderdatum."""
        if not s:
            return None
        d = dt.datetime.fromisoformat(s)
        return (d + dt.timedelta(hours=2)).date()
