"""
Maak landen 'live' op basis van alléén feestdagen (Nager.Date), voor landen die
OpenHolidays niet dekt en waarvoor geen schoolvakantie-bron bestaat: Noorwegen,
Denemarken, Finland, Verenigd Koninkrijk, Griekenland.

Per land wordt een Land aangemaakt (naam/vlag/slug uit europe._EUROPE) en worden
de landelijke feestdagen (Nager.Date `global=true`) als Feestdag opgeslagen
(bron='nager', categorie='officieel'). Idempotent op external_id `nager:{cc}:{datum}`;
vergrendelde rijen blijven met rust. De landenpagina toont dan de feestdagen +
een notitie dat de schoolvakanties nog volgen.

    python manage.py import_feestdaglanden
    python manage.py import_feestdaglanden --countries NO,GR --years 2026,2027,2028
"""
from __future__ import annotations

import datetime as dt
import sys

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from core import europe
from core.models import Feestdag, Land

NAGER = "https://date.nager.at/api/v3/PublicHolidays/{year}/{cc}"
BRON_TEKST = "Feestdagen: Nager.Date · schoolvakanties volgen binnenkort"


class Command(BaseCommand):
    help = "Maak landen live met alléén feestdagen uit Nager.Date (NO/DK/FI/GB/GR)."

    def add_arguments(self, parser):
        parser.add_argument("--countries", default="NO,DK,FI,GB,GR",
                            help="Komma-gescheiden ISO-codes (standaard NO,DK,FI,GB,GR).")
        parser.add_argument("--years", default="2026,2027,2028",
                            help="Komma-gescheiden jaren.")

    def handle(self, *args, **opts):
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

        codes = [c.strip().upper() for c in opts["countries"].split(",") if c.strip()]
        years = [int(y) for y in opts["years"].split(",") if y.strip()]
        meta = {c["code"].upper(): c for c in europe.europe_list()}
        session = requests.Session()
        session.headers.update({"Accept": "application/json",
                                 "User-Agent": "schoolvakanties.nl-importer"})
        now = timezone.now()

        for code in codes:
            m = meta.get(code)
            if not m:
                self.stderr.write(self.style.WARNING(f"{code}: niet in de landenlijst, overgeslagen."))
                continue
            land, _ = Land.objects.get_or_create(
                iso_code=code, defaults={"naam": m["name"], "vlag": m["flag"]})
            changed = []
            if land.naam != m["name"]:
                land.naam = m["name"]; changed.append("naam")
            if land.slug != slugify(m["name"]):
                land.slug = slugify(m["name"]); changed.append("slug")
            if not land.vlag:
                land.vlag = m["flag"]; changed.append("vlag")
            if not land.actief:
                land.actief = True; changed.append("actief")
            if land.bron != BRON_TEKST:
                land.bron = BRON_TEKST; changed.append("bron")
            land.order = 50  # na de volledige landen sorteren in de admin
            changed.append("order")
            land.imported_at = now; changed.append("imported_at")
            land.save(update_fields=list(set(changed)))

            done = 0
            for year in years:
                try:
                    resp = session.get(NAGER.format(year=year, cc=code), timeout=30)
                    resp.raise_for_status()
                    data = resp.json()
                except requests.RequestException:
                    self.stderr.write(self.style.WARNING(f"  {code} {year}: Nager niet bereikbaar."))
                    continue
                for h in data:
                    if not h.get("global"):
                        continue  # alléén landelijke feestdagen
                    try:
                        d = dt.date.fromisoformat(h["date"])
                    except (KeyError, ValueError):
                        continue
                    ext = f"nager:{code}:{d.isoformat()}"
                    existing = Feestdag.objects.filter(external_id=ext).first()
                    if existing and existing.vergrendeld:
                        continue
                    obj, _ = Feestdag.objects.update_or_create(
                        external_id=ext,
                        defaults={"land": land,
                                  "naam": h.get("localName") or h.get("name") or "",
                                  "categorie": "officieel",
                                  "type": (h.get("types") or ["Public"])[0],
                                  "start_datum": d, "landelijk": True,
                                  "bron": "nager", "imported_at": now})
                    obj.regios.clear()
                    done += 1
            self.stdout.write(self.style.SUCCESS(
                f"{land.vlag} {land.naam} ({code}), live met {done} feestdagen."))

        self.stdout.write(self.style.SUCCESS("\nKlaar."))
