"""
Kruiscontrole van onze Duitse schoolvakanties (OpenHolidays / KMK) tegen
ferien-api.de, een tweede, onafhankelijke bron per Bundesland. Report-only en
niet-destructief: het signaleert alleen periodes die in één van beide bronnen
ontbreken of afwijken, zodat we afwijkingen zien zonder blind één bron te volgen.

ferien-api.de rate-limit't (HTTP 429); daarom met throttling + backoff en
standaard maar twee jaren.

    python manage.py check_ferien_de
    python manage.py check_ferien_de --years 2026,2027,2028
"""
from __future__ import annotations

import datetime as dt
import sys
import time

import requests
from django.core.management.base import BaseCommand

from core.models import Land, Schoolvakantie

FERIEN_URL = "https://ferien-api.de/api/v1/holidays/{state}/{year}"
# ferien-api stateCode -> onze Regio-code.
STATES = ["BW", "BY", "BE", "BB", "HB", "HH", "HE", "NI",
          "MV", "NW", "RP", "SL", "SN", "ST", "SH", "TH"]
THROTTLE = 0.7  # seconden tussen calls, beleefd tegen de rate-limit.


class Command(BaseCommand):
    help = "Vergelijk de Duitse schoolvakanties met ferien-api.de (report-only)."

    def add_arguments(self, parser):
        parser.add_argument("--years", default="2026,2027",
                            help="Komma-gescheiden jaren (standaard 2026,2027).")

    def handle(self, *args, **opts):
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

        years = [int(y) for y in opts["years"].split(",") if y.strip()]
        land = Land.objects.filter(iso_code="DE").first()
        if not land:
            self.stderr.write(self.style.ERROR("Geen land DE in de database."))
            return
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

        # Onze periodes per Bundesland (DE-XX) als set van (start, eind).
        ours = {st: set() for st in STATES}
        for v in Schoolvakantie.objects.filter(land=land).prefetch_related("regios"):
            for r in v.regios.all():
                st = r.code.replace("DE-", "")
                if st in ours:
                    ours[st].add((v.start_datum, v.eind_datum))

        gaten = afwijk = ok = onbereikbaar = 0
        for year in years:
            for st in STATES:
                data = self._fetch(st, year)
                if data is None:
                    onbereikbaar += 1
                    continue
                theirs = set()
                for e in data:
                    if "beweglich" in (e.get("name") or "").lower():
                        continue
                    try:
                        theirs.add((dt.date.fromisoformat(e["start"][:10]),
                                    dt.date.fromisoformat(e["end"][:10])))
                    except (KeyError, ValueError):
                        continue
                theirs_year = {p for p in theirs if p[0].year == year or p[1].year == year}
                ours_year = {p for p in ours[st] if p[0].year == year or p[1].year == year}
                missing = theirs_year - ours_year
                extra = ours_year - theirs_year
                if missing or extra:
                    self.stdout.write(f"\n{st} {year}")
                    for s, e in sorted(missing):
                        self.stdout.write(self.style.WARNING(
                            f"  GAT   {s:%d-%m}–{e:%d-%m} (wel ferien-api, niet bij ons)"))
                        gaten += 1
                    for s, e in sorted(extra):
                        self.stdout.write(
                            f"  EXTRA {s:%d-%m}–{e:%d-%m} (wel bij ons, niet ferien-api)")
                        afwijk += 1
                else:
                    ok += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nKlaar, {ok} deelstaat/jaar exact gelijk, {gaten} gaten, "
            f"{afwijk} afwijkingen, {onbereikbaar} niet bereikbaar."))

    def _fetch(self, state, year):
        """GET met throttling en backoff op 429. Geeft een lijst of None."""
        for poging in range(4):
            try:
                r = self.session.get(FERIEN_URL.format(state=state, year=year), timeout=40)
                if r.status_code == 429:
                    wacht = int(r.headers.get("Retry-After", 2 * (poging + 1)))
                    time.sleep(min(wacht, 10))
                    continue
                r.raise_for_status()
                data = r.json()
                time.sleep(THROTTLE)
                return data if isinstance(data, list) else None
            except requests.RequestException:
                time.sleep(1.5 * (poging + 1))
        return None
