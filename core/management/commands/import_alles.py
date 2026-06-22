"""
Eén commando dat de hele dataketen in de juiste volgorde draait. Geschikt voor
de cron / scheduled task:

  1. import_openholidays  — feestdagen (alle landen) + schoolvakanties (behalve
                            NL/FR/DE, die door de nationale bron worden gedekt).
  2. import_nationaal     — schoolvakanties NL (Rijksoverheid), FR (zones),
                            DE (ferien-api.de) — leidend, en ruimt oude
                            OpenHolidays-rijen op.
  3. check_feestdagen     — kruiscontrole van de feestdagen tegen Nager.Date
                            (alleen rapport; voeg --fill toe om gaten te vullen).

    python manage.py import_alles
    python manage.py import_alles --fill
"""
from __future__ import annotations

import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Draai de volledige import: OpenHolidays + nationale bronnen + Nager-check."

    def add_arguments(self, parser):
        parser.add_argument("--fill", action="store_true",
                            help="Laat de Nager-check ontbrekende feestdagen aanvullen.")

    def handle(self, *args, **opts):
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

        self.stdout.write(self.style.MIGRATE_HEADING("\n[1/3] OpenHolidays …"))
        call_command("import_openholidays")
        self.stdout.write(self.style.MIGRATE_HEADING("\n[2/3] Nationale bronnen (NL/FR/DE) …"))
        call_command("import_nationaal")
        self.stdout.write(self.style.MIGRATE_HEADING("\n[3/3] Kruiscontrole Nager.Date …"))
        call_command("check_feestdagen", fill=opts["fill"])
        self.stdout.write(self.style.SUCCESS("\nVolledige import klaar."))
