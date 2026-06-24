"""Vul NlPlaats (gemeente -> schoolvakantieregio Noord/Midden/Zuid) uit OpenHolidays.

De API tagt de NL-zomervakantie per gemeente, en publiceert 3 los-gedateerde
zomervakantie-entries (één per schoolregio). De regio van een gemeente = de regio
van de zomervakantie-entry waarin de gemeente voorkomt. Dat werkt voor álle
gemeenten — óók Gelderland, dat per gemeente over Midden/Zuid is verdeeld en in de
gewone provincie-regel buiten beschouwing blijft.

Idempotent (upsert op naam). Draait op productie (cron + bootstrap); lokaal is de
API meestal niet bereikbaar, dan blijft de gecureerde seed-set staan.

    python manage.py import_nl_plaatsen
"""
import datetime as dt

import requests
from django.core.management.base import BaseCommand

from core.management.commands.import_openholidays import (
    API_BASE, NL_REGIO_GEMEENTEN, NL_REGIO_PROV, _localized, _province,
)
from core.models import NlPlaats


def _regio_label(codes):
    """De dominante regio (Noord/Midden/Zuid) voor een set gemeente-codes —
    zelfde provincie-dekkingslogica als de schoolvakantie-import."""
    counts = {naam: 0 for naam in NL_REGIO_PROV}
    for c in codes:
        p = _province(c)
        for naam, pset in NL_REGIO_PROV.items():
            if p in pset:
                counts[naam] += 1
    best = max(counts, key=counts.get)
    return best if counts[best] else None


class Command(BaseCommand):
    help = "Vul NlPlaats (gemeente -> regio) uit OpenHolidays (incl. Gelderland-splitsing)."

    def handle(self, *args, **opts):
        jaar = dt.date.today().year
        try:
            data = requests.get(
                f"{API_BASE}/SchoolHolidays",
                params={"countryIsoCode": "NL", "languageIsoCode": "NL",
                        "validFrom": f"{jaar}-01-01", "validTo": f"{jaar}-12-31"},
                headers={"Accept": "application/json"}, timeout=30,
            )
            data.raise_for_status()
            entries = data.json()
        except requests.RequestException as exc:
            self.stderr.write(self.style.WARNING(
                f"OpenHolidays niet bereikbaar ({exc}); gecureerde seed-set blijft staan."))
            return

        # Alleen de (per regio gedateerde) zomervakantie-entries.
        zomer = [e for e in entries
                 if "zomer" in _localized(e.get("name"), ["NL"]).lower()]
        toegekend = {}
        for e in zomer:
            subs = e.get("subdivisions") or []
            codes = [s.get("code") for s in subs if s.get("code")]
            regio = _regio_label(codes)
            if not regio:
                continue
            for s in subs:
                naam = _localized(s.get("name"), ["NL"]).strip()
                # Alleen gemeente-niveau (NL-XX-yyy), niet de losse provincie (NL-XX).
                if naam and (s.get("code") or "").count("-") >= 2:
                    toegekend[naam] = regio

        n = upd = 0
        for naam, regio in toegekend.items():
            obj, created = NlPlaats.objects.get_or_create(naam=naam, defaults={"regio": regio})
            if created:
                n += 1
            elif obj.regio != regio:
                obj.regio = regio
                obj.save(update_fields=["regio"])
                upd += 1
        self.stdout.write(self.style.SUCCESS(
            f"NL plaatsen->regio uit OpenHolidays: {n} nieuw, {upd} bijgewerkt "
            f"({NlPlaats.objects.count()} totaal)."))
