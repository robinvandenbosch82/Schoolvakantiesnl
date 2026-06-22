"""
Kruiscontrole van onze (OpenHolidays-)feestdagen tegen Nager.Date
(date.nager.at) — een tweede, onafhankelijke bron voor officiële feestdagen in
100+ landen. Bedoeld om stil afwijkende of ontbrekende data te signaleren i.p.v.
blind op één bron te vertrouwen.

Per land/jaar wordt gerapporteerd:
  * GAT  — landelijke feestdag die Nager kent maar wij missen.
  * EXTRA — datum die wij hebben maar Nager nergens kent (mogelijk fout/regionaal).

Standaard alleen rapporteren. Met --fill worden ontbrekende landelijke feestdagen
toegevoegd (bron='nager', categorie='officieel'); vergrendelde rijen blijven met
rust.

    python manage.py check_feestdagen
    python manage.py check_feestdagen --years 2026,2027 --fill
    python manage.py check_feestdagen --country NL,DE
"""
from __future__ import annotations

import datetime as dt
import sys

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Feestdag, Land

NAGER_URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/{cc}"


class Command(BaseCommand):
    help = "Vergelijk feestdagen met Nager.Date en rapporteer verschillen."

    def add_arguments(self, parser):
        parser.add_argument("--country", default="",
                            help="Komma-gescheiden ISO-codes; leeg = alle actieve landen.")
        parser.add_argument("--years", default="2026,2027",
                            help="Komma-gescheiden jaren (standaard 2026,2027).")
        parser.add_argument("--fill", action="store_true",
                            help="Voeg ontbrekende landelijke feestdagen toe (bron='nager').")

    def handle(self, *args, **opts):
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

        years = [int(y) for y in opts["years"].split(",") if y.strip()]
        self.fill = opts["fill"]
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json",
                                     "User-Agent": "schoolvakanties.nl-checker"})
        self.now = timezone.now()

        if opts["country"].strip():
            codes = [c.strip().upper() for c in opts["country"].split(",") if c.strip()]
            landen = list(Land.objects.filter(iso_code__in=codes))
        else:
            landen = list(Land.objects.filter(actief=True))

        tot_gap = tot_extra = tot_filled = 0
        for land in sorted(landen, key=lambda l: l.naam):
            gaps, extras, filled = self._check_land(land, years)
            tot_gap += gaps; tot_extra += extras; tot_filled += filled

        self.stdout.write(self.style.SUCCESS(
            f"\nKlaar — {tot_gap} gaten, {tot_extra} extra's"
            + (f", {tot_filled} aangevuld." if self.fill else " (alleen rapport).")))

    def _check_land(self, land, years):
        gaps = extras = filled = 0
        for year in years:
            try:
                data = self.session.get(
                    NAGER_URL.format(year=year, cc=land.iso_code), timeout=30)
                data.raise_for_status()
                nager = data.json()
            except requests.RequestException:
                self.stderr.write(self.style.WARNING(
                    f"  {land.iso_code} {year}: Nager niet bereikbaar — overgeslagen."))
                continue

            nager_global = {dt.date.fromisoformat(h["date"]): h
                            for h in nager if h.get("global")}
            nager_all = {dt.date.fromisoformat(h["date"]) for h in nager}
            ours = set(Feestdag.objects.filter(
                land=land, categorie="officieel",
                start_datum__year=year).values_list("start_datum", flat=True))

            missing = sorted(set(nager_global) - ours)
            extra = sorted(ours - nager_all)
            if missing or extra:
                self.stdout.write(f"\n{land.vlag} {land.naam} ({land.iso_code}) {year}")
            for d in missing:
                self.stdout.write(self.style.WARNING(
                    f"  GAT   {d:%d-%m} {nager_global[d].get('localName')}"))
                gaps += 1
                if self.fill:
                    filled += self._fill(land, d, nager_global[d])
            for d in extra:
                self.stdout.write(f"  EXTRA {d:%d-%m} (niet in Nager.Date)")
                extra_names = Feestdag.objects.filter(
                    land=land, start_datum=d).values_list("naam", flat=True)
                self.stdout.write(f"        → {', '.join(extra_names)}")
                extras += 1
        return gaps, extras, filled

    def _fill(self, land, d, h):
        ext = f"nager:{land.iso_code}:{d.isoformat()}"
        existing = Feestdag.objects.filter(external_id=ext).first()
        if existing and existing.vergrendeld:
            return 0
        obj, _ = Feestdag.objects.update_or_create(
            external_id=ext,
            defaults={"land": land, "naam": h.get("localName") or h.get("name") or "",
                      "categorie": "officieel",
                      "type": (h.get("types") or ["Public"])[0],
                      "start_datum": d, "landelijk": True,
                      "bron": "nager", "imported_at": self.now})
        obj.regios.clear()
        return 1
