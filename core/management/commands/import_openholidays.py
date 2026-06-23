"""
Importeer school- en feestdagen uit de OpenHolidays API (openholidaysapi.org).

Idempotent: upsert op external_id (de GUID van de API). Een rij die in de admin
op `vergrendeld=True` staat, wordt overgeslagen, zo blijven handmatige correcties
in uitzonderingsgevallen behouden. Redactionele velden (Land.intro, weer,
bestemmingen, reisweken) worden NOOIT aangeraakt.

Regio-normalisatie (de API is rommeliger dan de site wil):
  * NL, de API tagt schoolvakanties per gemeente, niet per schoolregio. We
    vouwen dat samen tot de drie officiële regio's Noord / Midden / Zuid door de
    provincie-meerderheid van elke entry te bepalen (Gelderland is gesplitst en
    telt niet mee in de stemming).
  * DE, we koppelen alleen op deelstaat-niveau (DE-XX), niet op de diepere
    Landkreise, en gebruiken Nederlandse deelstaatnamen.

Bedoeld om regelmatig te draaien (cron / scheduled task):

    python manage.py import_openholidays
    python manage.py import_openholidays --countries NL,DE --from 2026-01-01 --to 2027-02-01
"""
from __future__ import annotations

import datetime as dt
import re
import sys

import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from core.models import Feestdag, Land, Regio, Schoolvakantie

API_BASE = "https://openholidaysapi.org"

# Voor deze landen komen de SCHOOLVAKANTIES uit een gezaghebbender nationale bron
# (zie management/commands/import_nationaal.py): NL=Rijksoverheid, FR=Éducation
# nationale (zones A/B/C). OpenHolidays levert hier alléén nog de feestdagen, zodat
# er geen dubbele schoolvakantie-rijen ontstaan.
# DE blijft bewust op OpenHolidays: dat ís de officiële KMK-bron (16 Bundesländer);
# ferien-api.de wordt alleen als kruiscontrole gebruikt (check_ferien_de).
SCHOOL_OVERRIDE = {"NL", "FR"}

# Vlag-emoji per landcode (de API levert die niet).
FLAGS = {
    "NL": "🇳🇱", "DE": "🇩🇪", "BE": "🇧🇪", "FR": "🇫🇷", "IT": "🇮🇹",
    "ES": "🇪🇸", "AT": "🇦🇹", "CH": "🇨🇭", "LU": "🇱🇺", "PT": "🇵🇹",
    "GB": "🇬🇧", "PL": "🇵🇱", "DK": "🇩🇰", "IE": "🇮🇪", "SE": "🇸🇪",
    "CZ": "🇨🇿", "SK": "🇸🇰", "HU": "🇭🇺", "SI": "🇸🇮", "HR": "🇭🇷",
    "LI": "🇱🇮", "MT": "🇲🇹", "EE": "🇪🇪", "LV": "🇱🇻", "LT": "🇱🇹",
    "BG": "🇧🇬", "RO": "🇷🇴",
}

# Nederlandstalige landnamen (de API valt soms terug op Engels).
COUNTRY_NL = {
    "NL": "Nederland", "DE": "Duitsland", "BE": "België", "FR": "Frankrijk",
    "IT": "Italië", "ES": "Spanje", "AT": "Oostenrijk", "CH": "Zwitserland",
    "LU": "Luxemburg", "PT": "Portugal", "GB": "Verenigd Koninkrijk",
    "PL": "Polen", "DK": "Denemarken", "IE": "Ierland", "SE": "Zweden",
    "CZ": "Tsjechië", "SK": "Slowakije", "HU": "Hongarije", "SI": "Slovenië",
    "HR": "Kroatië", "LI": "Liechtenstein", "MT": "Malta", "EE": "Estland",
    "LV": "Letland", "LT": "Litouwen", "BG": "Bulgarije", "RO": "Roemenië",
}

# De drie NL-schoolvakantieregio's (geen API-concept).
NL_REGIOS = [
    ("NL-NOORD", "Noord", "Groningen, Friesland, Drenthe, Overijssel, Noord-Holland en het grootste deel van Flevoland."),
    ("NL-MIDDEN", "Midden", "Zuid-Holland, Utrecht en een deel van Gelderland."),
    ("NL-ZUID", "Zuid", "Zeeland, Limburg, Noord-Brabant en een deel van Gelderland."),
]
# Provincies per regio (Gelderland is gesplitst en telt niet mee in de toewijzing).
NL_REGIO_PROV = {
    "Noord": {"GR", "FR", "DR", "OV", "NH", "FL"},
    "Midden": {"ZH", "UT"},
    "Zuid": {"ZE", "LI", "NB"},
}
# Totaal aantal gemeenten per regio (uit /Subdivisions, GE buiten beschouwing).
# Noemer om te bepalen welk dekkingspercentage van een regio in een entry zit, # robuust tegen losse grensgemeenten die in een andere regio 'lekken'.
NL_REGIO_GEMEENTEN = {"Noord": 115, "Midden": 76, "Zuid": 100}

# Duitse deelstaten in het Nederlands.
DE_BUNDESLAND_NL = {
    "DE-BW": "Baden-Württemberg", "DE-BY": "Beieren", "DE-BE": "Berlijn",
    "DE-BB": "Brandenburg", "DE-HB": "Bremen", "DE-HH": "Hamburg", "DE-HE": "Hessen",
    "DE-NI": "Nedersaksen", "DE-MV": "Mecklenburg-Voor-Pommeren", "DE-NW": "Noordrijn-Westfalen",
    "DE-RP": "Rijnland-Palts", "DE-SL": "Saarland", "DE-SN": "Saksen",
    "DE-ST": "Saksen-Anhalt", "DE-SH": "Sleeswijk-Holstein", "DE-TH": "Thüringen",
}
DE_BUNDESLAND_RE = re.compile(r"^DE-[A-Z]{2}$")

# België: de API tagt geen subdivisie, maar de éérste taal van de naam verraadt
# de taalgemeenschap. We koppelen elke vakantie aan de juiste 'regio' en geven
# een canonieke NL-periodenaam zodat de drie gemeenschappen netjes groeperen.
BE_COMMUNITY = {  # naam-taal -> (regio-code, regio-naam)
    "NL": ("BE-VLG", "Vlaanderen"),
    "FR": ("BE-FR", "Wallonië & Brussel"),
    "DE": ("BE-DE", "Duitstalige Gemeenschap"),
}
BE_CANON = [  # volgorde telt: kerst/noël vóór winter/hiver
    (("zomer", "sommer", "été", "ete"), "Zomervakantie"),
    (("kerst", "noël", "noel", "weihnacht"), "Kerstvakantie"),
    (("herfst", "herbst", "toussaint", "automne"), "Herfstvakantie"),
    (("paas", "oster", "pâque", "paque", "printemps"), "Paasvakantie"),
    (("krokus", "carnaval", "karneval", "détente", "detente", "winter", "hiver"),
     "Krokus-/carnavalsvakantie"),
]


def _be_canon_naam(naam):
    n = (naam or "").lower()
    for keys, canon in BE_CANON:
        if any(k in n for k in keys):
            return canon
    return naam

# De eigen taal per land, gebruikt als terugval voor vakantienamen wanneer er
# geen Nederlandse vertaling is (bv. 'Sommerferien' i.p.v. 'Summer Holidays').
NATIVE_LANG = {"NL": "NL", "DE": "DE", "BE": "NL", "FR": "FR", "IT": "IT",
               "ES": "ES", "AT": "DE", "CH": "DE", "LU": "FR", "PT": "PT",
               "GB": "EN", "PL": "PL", "DK": "DA", "IE": "EN", "SE": "SV",
               "CZ": "CS", "SK": "SK", "HU": "HU", "SI": "SL", "HR": "HR",
               "LI": "DE", "MT": "EN", "EE": "ET", "LV": "LV", "LT": "LT",
               "BG": "EN", "RO": "RO"}


# Spanje: de autonome gemeenschappen noemen de paasvakantie verschillend
# (Pascua / Semana Santa / Descanso). Normaliseren naar één naam, zodat ze als
# één periode groeperen i.p.v. als drie schijn-duplicaten te verschijnen.
ES_PAAS = {"vacaciones de pascua", "descanso de semana santa",
           "vacaciones de semana santa"}
ES_PAAS_NAAM = "Vacaciones de Semana Santa"


def _localized(items, prefer=("NL", "EN")):
    """Pak de tekst in de eerst-beschikbare voorkeurstaal uit een OpenHolidays
    name/comment-lijst (bv. ['NL', 'DE', 'EN'])."""
    if not items:
        return ""
    by_lang = {i.get("language", "").upper(): i.get("text", "") for i in items}
    for lang in prefer:
        if by_lang.get(lang.upper()):
            return by_lang[lang.upper()]
    return by_lang.get("EN") or next(iter(by_lang.values()), "")


def _date(value):
    return dt.date.fromisoformat(value) if value else None


def _province(code):
    """Provincie-code uit een NL-subdivisioncode. De API gebruikt een land-prefix:
    NL-GR-PE -> GR, NL-GR -> GR, en ook GR-PE/GR -> GR."""
    parts = [p for p in (code or "").split("-") if p]
    if parts and parts[0] == "NL":
        parts = parts[1:]
    return parts[0] if parts else ""


class Command(BaseCommand):
    help = "Importeer school- en feestdagen uit de OpenHolidays API (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--countries",
            default="NL,DE,BE,FR,ES,IT,AT,PT,CH,IE,SE,PL,CZ,SK,HU,SI,HR,LU,LI,MT,EE,LV,LT,BG,RO",
            help="Komma-gescheiden ISO-landcodes (standaard: alle door OpenHolidays "
                 "ondersteunde Europese landen uit onze lijst).")
        parser.add_argument("--from", dest="valid_from", default="2026-01-01",
                            help="validFrom (YYYY-MM-DD).")
        parser.add_argument("--to", dest="valid_to", default="2028-02-01",
                            help="validTo (YYYY-MM-DD). Standaard t/m begin 2028 zodat de "
                                 "kerstvakantie van schooljaar 2027-28 meekomt (jaar-switcher).")
        parser.add_argument("--language", default="NL", help="Taal voor namen (standaard NL).")

    def handle(self, *args, **opts):
        # Forceer UTF-8 op de console (Windows draait standaard cp1252).
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

        codes = [c.strip().upper() for c in opts["countries"].split(",") if c.strip()]
        self.lang = opts["language"]
        self.valid_from = opts["valid_from"]
        self.valid_to = opts["valid_to"]
        self.session = requests.Session()
        self.now = timezone.now()

        api_names = self._country_names()

        totals = {"vak": 0, "vak_skip": 0, "feest": 0, "feest_skip": 0}
        for code in codes:
            naam = COUNTRY_NL.get(code) or api_names.get(code, code)
            self.native = NATIVE_LANG.get(code, code)
            land = self._upsert_land(code, naam)
            self._ensure_regios(land)
            v, vs = self._import_school(land)
            f, fs = self._import_public(land)
            totals["vak"] += v; totals["vak_skip"] += vs
            totals["feest"] += f; totals["feest_skip"] += fs
            land.imported_at = self.now
            update = ["imported_at"]
            # Provenance-vermelding bijhouden (behalve voor landen met een nationale
            # schoolvakantie-bron, die zet import_nationaal zelf).
            if code not in SCHOOL_OVERRIDE:
                bron = "Schoolvakanties & feestdagen: OpenHolidays.org"
                if land.bron != bron:
                    land.bron = bron; update.append("bron")
            land.save(update_fields=update)
            self.stdout.write(self.style.SUCCESS(
                f"{land.naam} ({land.iso_code}), {v} schoolvakanties, {f} feestdagen, "
                f"{land.regios.count()} regio's ({vs + fs} vergrendeld overgeslagen)."))

        self.stdout.write(self.style.SUCCESS(
            f"\nKlaar, {totals['vak']} schoolvakanties, {totals['feest']} feestdagen. "
            f"Vergrendeld overgeslagen: {totals['vak_skip'] + totals['feest_skip']}."))

    # ── API helpers ─────────────────────────────────────────────────────────
    def _get(self, path, **params):
        try:
            resp = self.session.get(f"{API_BASE}{path}", params=params,
                                    headers={"Accept": "application/json"}, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            raise CommandError(f"OpenHolidays-aanroep mislukt ({path}): {exc}") from exc

    def _country_names(self):
        data = self._get("/Countries", languageIsoCode=self.lang)
        return {c["isoCode"].upper(): _localized(c.get("name"), [self.lang]) for c in data}

    # ── Land + regio's ────────────────────────────────────────────────────────
    def _upsert_land(self, code, naam):
        land, created = Land.objects.get_or_create(
            iso_code=code, defaults={"naam": naam, "vlag": FLAGS.get(code, "")})
        from django.utils.text import slugify
        changed = []
        # Houd de (canonieke) Nederlandstalige landnaam + slug in sync.
        if code in COUNTRY_NL and land.naam != COUNTRY_NL[code]:
            land.naam = COUNTRY_NL[code]; changed.append("naam")
        gewenste_slug = slugify(land.naam)
        if land.slug != gewenste_slug:
            land.slug = gewenste_slug; changed.append("slug")
        if not land.vlag and FLAGS.get(code):
            land.vlag = FLAGS[code]; changed.append("vlag")
        if changed:
            land.save(update_fields=changed)
        return land

    def _ensure_regios(self, land):
        """Maak de relevante regio-laag aan (curated voor NL/DE)."""
        if land.iso_code == "NL":
            for i, (code, naam, uitleg) in enumerate(NL_REGIOS):
                Regio.objects.update_or_create(
                    code=code, defaults={"land": land, "naam": naam, "korte_naam": naam,
                                         "uitleg": uitleg, "order": i})
        elif land.iso_code == "DE":
            for i, (code, naam) in enumerate(DE_BUNDESLAND_NL.items()):
                Regio.objects.update_or_create(
                    code=code, defaults={"land": land, "naam": naam, "korte_naam": code[-2:],
                                         "order": i})
        elif land.iso_code == "BE":
            for i, (code, naam) in enumerate([BE_COMMUNITY["NL"], BE_COMMUNITY["FR"], BE_COMMUNITY["DE"]]):
                Regio.objects.update_or_create(
                    code=code, defaults={"land": land, "naam": naam, "korte_naam": naam, "order": i})
        elif land.iso_code == "FR":
            # FR-regio's = de schoolzones (A/B/C/Corse); die maakt import_nationaal aan.
            return
        else:
            # Generiek: top-level subdivisions in de eigen landstaal (bv. Andalucía,
            # Toscana, Île-de-France), leesbaarder/authentieker dan de Engelse naam.
            for i, node in enumerate(self._get("/Subdivisions", countryIsoCode=land.iso_code,
                                               languageIsoCode=self.native)):
                code = node.get("code") or node.get("isoCode")
                if code:
                    Regio.objects.update_or_create(
                        code=code, defaults={"land": land,
                                             "naam": _localized(node.get("name"), [self.native, self.lang]) or code,
                                             "korte_naam": node.get("shortName", "")[:60], "order": i})

    # ── Regio-koppeling per entry ─────────────────────────────────────────────
    def _regios_for(self, land, subdivisions):
        codes = [s.get("code") for s in subdivisions if s.get("code")]
        if not codes:
            return []
        if land.iso_code == "NL":
            namen = self._nl_regions(codes)
            if not namen:
                return []
            return list(Regio.objects.filter(land=land, naam__in=namen))
        if land.iso_code == "DE":
            bl = {c for c in codes if DE_BUNDESLAND_RE.match(c)}
            return list(Regio.objects.filter(land=land, code__in=bl))
        # Generiek: koppel op exact bekende codes; voor sub-codes die niet bestaan
        # (bv. ES-AN-CO = Córdoba) valt het terug op de ouder-regio (ES-AN).
        found = list(Regio.objects.filter(land=land, code__in=codes))
        found_codes = {r.code for r in found}
        parents = {c.rsplit("-", 1)[0] for c in codes
                   if c not in found_codes and c.count("-") >= 2}
        if parents:
            extra = Regio.objects.filter(land=land, code__in=parents).exclude(code__in=found_codes)
            found = found + list(extra)
        return found

    @staticmethod
    def _nl_regions(codes):
        """Bepaal alle regio's (Noord/Midden/Zuid) die een entry dekt, op basis
        van hoeveel gemeenten van elke regio in de entry zitten. Een regio matcht
        als ≥50% van zijn gemeenten aanwezig is, zo komen landelijke vakanties
        (kerst/mei → alle 3) en gedeelde periodes (bv. Midden + Zuid) goed uit,
        terwijl losse grensgemeenten die 'lekken' geen valse match geven."""
        counts = {naam: 0 for naam in NL_REGIO_PROV}
        for c in codes:
            p = _province(c)
            for naam, pset in NL_REGIO_PROV.items():
                if p in pset:
                    counts[naam] += 1
        namen = [naam for naam, n in counts.items()
                 if n / NL_REGIO_GEMEENTEN[naam] >= 0.5]
        if namen:
            return namen
        best = max(counts, key=counts.get)
        return [best] if counts[best] else []

    # ── Imports ───────────────────────────────────────────────────────────────
    def _import_school(self, land):
        # Schoolvakanties van deze landen komen uit een nationale bron.
        if land.iso_code in SCHOOL_OVERRIDE:
            return 0, 0
        params = dict(countryIsoCode=land.iso_code,
                      validFrom=self.valid_from, validTo=self.valid_to)
        # BE: géén languageIsoCode, zodat de eerste taal van de naam de
        # taalgemeenschap blijft verraden (anders zet de API overal NL vooraan).
        if land.iso_code != "BE":
            params["languageIsoCode"] = self.native
        data = self._get("/SchoolHolidays", **params)
        done = skip = 0
        for e in data:
            ext = e.get("id")
            existing = Schoolvakantie.objects.filter(external_id=ext).first()
            if existing and existing.vergrendeld:
                skip += 1
                continue
            if land.iso_code == "BE":
                comm_lang = (e.get("name") or [{}])[0].get("language", "").upper()
                naam = _be_canon_naam(_localized(e.get("name"), [comm_lang]))
            else:
                naam = _localized(e.get("name"), [self.native, self.lang])
            if land.iso_code == "ES" and naam.strip().lower() in ES_PAAS:
                naam = ES_PAAS_NAAM
            obj, _ = Schoolvakantie.objects.update_or_create(
                external_id=ext,
                defaults={
                    "land": land,
                    "naam": naam,
                    "type": e.get("type", ""),
                    "start_datum": _date(e.get("startDate")),
                    "eind_datum": _date(e.get("endDate")),
                    "landelijk": bool(e.get("nationwide")),
                    "comment": _localized(e.get("comment"), [self.native, self.lang])[:300],
                    "bron": "api",
                    "imported_at": self.now,
                },
            )
            self._link(obj, land, e)
            done += 1
        if land.iso_code == "ES":
            done += self._es_zomer(land)
        return done, skip

    def _es_zomer(self, land):
        """Spanje kent in OpenHolidays geen aparte zomervakantie-periode, alleen
        losse 'Fin de lecciones'-markers (laatste lesdag) per gemeenschap. We
        leiden er per regio/jaar een zomervakantie uit af: start = laatste lesdag
        (autoritatief), einde indicatief begin september (scholen hervatten ± 8
        sep, verschilt per gemeenschap)."""
        fin = {}  # (regio_id, jaar) -> (regio, vroegste laatste-lesdag)
        for v in (Schoolvakantie.objects.filter(land=land, naam__icontains="Fin de lecciones")
                  .prefetch_related("regios")):
            if v.start_datum.month < 5:  # alleen einde-schooljaar (mei–juli)
                continue
            for r in v.regios.all():
                key = (r.id, v.start_datum.year)
                cur = fin.get(key)
                if cur is None or v.start_datum < cur[1]:
                    fin[key] = (r, v.start_datum)
        n = 0
        for (rid, jaar), (regio, datum) in fin.items():
            ext = f"synth-es-verano:{regio.code}:{jaar}"
            existing = Schoolvakantie.objects.filter(external_id=ext).first()
            if existing and existing.vergrendeld:
                continue
            obj, _ = Schoolvakantie.objects.update_or_create(
                external_id=ext,
                defaults={
                    "land": land, "naam": "Vacaciones de verano", "type": "Summer",
                    "start_datum": datum, "eind_datum": dt.date(jaar, 9, 8),
                    "landelijk": False,
                    "note": "Einddatum indicatief, Spaanse scholen hervatten begin "
                            "september (± 8 sep, verschilt per gemeenschap).",
                    "comment": "Afgeleid uit de laatste lesdag (Fin de lecciones).",
                    "bron": "api", "imported_at": self.now,
                })
            obj.regios.set([regio])
            n += 1
        return n

    def _import_public(self, land):
        data = self._get("/PublicHolidays", countryIsoCode=land.iso_code,
                         languageIsoCode=self.native, validFrom=self.valid_from, validTo=self.valid_to)
        done = skip = 0
        for e in data:
            ext = e.get("id")
            existing = Feestdag.objects.filter(external_id=ext).first()
            if existing and existing.vergrendeld:
                skip += 1
                continue
            obj, _ = Feestdag.objects.update_or_create(
                external_id=ext,
                defaults={
                    "land": land,
                    "naam": _localized(e.get("name"), [self.native, self.lang]),
                    "categorie": "officieel",
                    "type": e.get("type", ""),
                    "start_datum": _date(e.get("startDate")),
                    "eind_datum": _date(e.get("endDate")),
                    "landelijk": bool(e.get("nationwide")),
                    "comment": _localized(e.get("comment"), [self.native, self.lang])[:300],
                    "bron": "api",
                    "imported_at": self.now,
                },
            )
            self._link(obj, land, e)
            done += 1
        return done, skip

    def _link(self, obj, land, entry):
        # BE: koppel aan de taalgemeenschap o.b.v. de eerste taal van de naam.
        if land.iso_code == "BE":
            lang = (entry.get("name") or [{}])[0].get("language", "").upper()
            comm = BE_COMMUNITY.get(lang)
            if comm:
                obj.regios.set(Regio.objects.filter(land=land, code=comm[0]))
            else:
                obj.regios.clear()
            return
        if entry.get("nationwide"):
            obj.regios.clear()
            return
        obj.regios.set(self._regios_for(land, entry.get("subdivisions") or []))
