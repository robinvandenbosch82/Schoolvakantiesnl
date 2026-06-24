"""Vul Plaats (plaats/gemeente/district -> schoolvakantieregio) uit OpenHolidays.

Alleen landen die OpenHolidays op plaatsniveau tagt: een schoolvakantie-entry
draagt dan subdivisioncodes met >=2 streepjes (NL-DR-AS, CZ-JC-CB, …). Twee
strategieën:

- NL: de zomervakantie is per gemeente getagd; de regio (Noord/Midden/Zuid)
  volgt uit de provincie-dekking van de entry — werkt ook voor de Gelderse
  gemeenten, die per stuk over Midden/Zuid zijn verdeeld.
- Overige landen (bv. CZ): de plaats = leaf-subdivision; de regio = de
  bovenliggende subdivision, die 1-op-1 onze Regio is (match op code). De namen
  komen uit /Subdivisions, want in de vakantie-entries zijn de leaf-namen leeg.

Idempotent (upsert op land+naam). Best-effort: faalt de API, dan blijft de
bestaande/gecureerde set staan. Draait op productie via bootstrap_site.

    python manage.py import_plaatsen            # alle in aanmerking komende landen
    python manage.py import_plaatsen --land CZ  # alleen dit land
"""
import datetime as dt

import requests
from django.core.management.base import BaseCommand

from core.management.commands.import_openholidays import (
    API_BASE, NATIVE_LANG, NL_REGIO_PROV, _localized, _province,
)
from core.models import Land, Plaats, Regio


def _nl_regio_label(codes):
    """Dominante NL-regio (Noord/Midden/Zuid) voor een set gemeente-codes,
    o.b.v. dezelfde provincie-dekking als de schoolvakantie-import."""
    counts = {naam: 0 for naam in NL_REGIO_PROV}
    for c in codes:
        p = _province(c)
        for naam, pset in NL_REGIO_PROV.items():
            if p in pset:
                counts[naam] += 1
    best = max(counts, key=counts.get)
    return best if counts[best] else None


class Command(BaseCommand):
    help = "Vul Plaats (plaats -> regio) uit OpenHolidays voor landen met plaatsniveau-data."

    def add_arguments(self, parser):
        parser.add_argument("--land", help="Beperk tot één land (ISO-code, bv. CZ).")

    def handle(self, *args, **opts):
        jaar = dt.date.today().year
        qs = Land.objects.all().order_by("iso_code")
        if opts.get("land"):
            qs = qs.filter(iso_code=opts["land"].upper())
        for land in qs:
            try:
                self._import_land(land, jaar)
            except requests.RequestException as exc:
                self.stderr.write(self.style.WARNING(
                    f"{land.iso_code}: OpenHolidays niet bereikbaar ({exc}); overgeslagen."))

    # ── per land ────────────────────────────────────────────────────────────
    def _import_land(self, land, jaar):
        entries = self._get(f"{API_BASE}/SchoolHolidays",
                            {"countryIsoCode": land.iso_code,
                             "validFrom": f"{jaar}-01-01", "validTo": f"{jaar}-12-31"})
        if land.iso_code == "NL":
            regio_by_leaf = self._resolve_nl(entries)
        else:
            regio_by_leaf = self._resolve_generic(land, entries)
        if not regio_by_leaf:
            return  # land zonder bruikbare plaatsniveau-data: niets te doen

        # In de vakantie-entries zijn de leaf-namen leeg; haal ze uit /Subdivisions.
        names = self._subdivision_names(land.iso_code)
        n = upd = 0
        for code, regio in regio_by_leaf.items():
            naam = (names.get(code) or "").strip()
            if not naam:
                continue
            obj, created = Plaats.objects.get_or_create(
                land=land, naam=naam, defaults={"regio": regio})
            if created:
                n += 1
            elif obj.regio != regio:
                obj.regio = regio
                obj.save(update_fields=["regio"])
                upd += 1
        self.stdout.write(self.style.SUCCESS(
            f"{land.iso_code}: {n} nieuw, {upd} bijgewerkt "
            f"({Plaats.objects.filter(land=land).count()} totaal)."))

    def _resolve_nl(self, entries):
        """NL: code -> regio via de (per regio gedateerde) zomervakanties."""
        regio_by_leaf = {}
        for e in entries:
            if "zomer" not in _localized(e.get("name"), ["NL"]).lower():
                continue
            codes = [s.get("code") for s in (e.get("subdivisions") or []) if s.get("code")]
            regio = _nl_regio_label(codes)
            if not regio:
                continue
            for code in codes:
                if code.count("-") >= 2:
                    regio_by_leaf[code] = regio
        return regio_by_leaf

    def _resolve_generic(self, land, entries):
        """Overig: leaf-subdivision -> bovenliggende Regio (match op code)."""
        regio_by_code = {r.code: r.naam for r in Regio.objects.filter(land=land)}
        if not regio_by_code:
            return {}
        regio_by_leaf = {}
        for e in entries:
            for s in (e.get("subdivisions") or []):
                cd = s.get("code") or ""
                if cd.count("-") < 2:
                    continue
                regio = regio_by_code.get("-".join(cd.split("-")[:2]))
                if regio:
                    regio_by_leaf[cd] = regio
        return regio_by_leaf

    def _subdivision_names(self, iso):
        """code -> naam uit de volledige /Subdivisions-boom (leaf-namen ontbreken
        in de vakantie-entries)."""
        data = self._get(f"{API_BASE}/Subdivisions",
                         {"countryIsoCode": iso, "languageIsoCode": NATIVE_LANG.get(iso, "EN")})
        out = {}

        def walk(node):
            out[node.get("code")] = _localized(node.get("name"), [NATIVE_LANG.get(iso, "EN"), "EN"])
            for child in (node.get("children") or []):
                walk(child)

        for node in data:
            walk(node)
        return out

    def _get(self, url, params):
        r = requests.get(url, params=params, headers={"Accept": "application/json"}, timeout=30)
        r.raise_for_status()
        return r.json()
