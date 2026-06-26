"""Laad de kennisbank-backlog (content/kennisbank/backlog.json) in de database.

Idempotent (upsert op kb_id). Elke rij wordt een KennisbankArtikel:
- metadata + redactie-briefing komen altijd uit de backlog (bron van waarheid);
- staat er een body in content/kennisbank/articles/<slug>.html, dan wordt die
  ingeladen en het artikel op 'gepubliceerd' + active gezet (met auteur/reviewer,
  leestijd en inhoudsopgave). Anders blijft het een (verborgen) concept.

Zo werkt 'lokaal schrijven -> committen -> Railway laadt in': de teksten staan
als bestanden in de repo en deze command draait mee in bootstrap_site.

    python manage.py import_kennisbank
"""
import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from core.models import Expert, KennisbankArtikel, KennisbankCategorie, Land

BACKLOG = Path(settings.BASE_DIR) / "content" / "kennisbank" / "backlog.json"
ARTICLES = Path(settings.BASE_DIR) / "content" / "kennisbank" / "articles"

# Sheet-landnaam -> afwijkende mapping. Rest matcht op Land.naam.
LAND_ALIAS = {"Verenigd Koninkrijk": "Engeland", "Europa": None}

# Categorie -> tegel-icoon (KennisbankCategorie) voor de hub.
CAT_ICON = {
    "Vakantiestructuur": "square", "Regionale spreiding": "diamond",
    "Onderwijsritme": "bars", "Regels & verlof": "ring", "Regels & boetes": "triangle",
    "Reizen & drukte": "pill", "Cultuur & feestdagen": "square-fill",
    "Ouders & werk": "ring", "Vergelijking": "diamond",
}


def _toc_en_anchors(html):
    """Geef (html-met-id's-op-h2, [{id, titel}]) terug voor de inhoudsopgave."""
    toc = []

    def repl(m):
        attrs, tekst = m.group(1), m.group(2)
        if re.search(r'\bid=', attrs):           # al een id -> laat staan
            anchor = re.search(r'id="([^"]+)"', attrs).group(1)
        else:
            anchor = slugify(re.sub(r"<[^>]+>", "", tekst))[:60] or f"sec-{len(toc)+1}"
            attrs = f'{attrs} id="{anchor}"'
        toc.append({"id": anchor, "titel": re.sub(r"<[^>]+>", "", tekst).strip()})
        return f"<h2{attrs}>{tekst}</h2>"

    html = re.sub(r"<h2([^>]*)>(.*?)</h2>", repl, html, flags=re.S | re.I)
    return html, toc


def _leestijd(html):
    woorden = len(re.sub(r"<[^>]+>", " ", html).split())
    return f"{max(1, round(woorden / 200))} min"


class Command(BaseCommand):
    help = "Laad de kennisbank-backlog + beschikbare artikelteksten in de database."

    def handle(self, *args, **opts):
        if not BACKLOG.exists():
            self.stderr.write(self.style.WARNING(f"Geen backlog gevonden: {BACKLOG}"))
            return
        items = json.loads(BACKLOG.read_text(encoding="utf-8"))
        landen = {l.naam: l for l in Land.objects.all()}
        experts = list(Expert.objects.filter(active=True).order_by("order"))

        n_new = n_pub = 0
        cats = {}
        for i, it in enumerate(items):
            land = self._resolve_land(it["land"], landen)
            art, created = KennisbankArtikel.objects.get_or_create(
                kb_id=it["kb_id"], defaults={"titel": it["vraag"], "slug": it["slug"]})
            n_new += int(created)
            art.titel = it["vraag"]
            art.slug = it["slug"]
            art.seo_title = it["seo_title"]
            art.categorie = it["categorie"]
            art.land = land
            art.prioriteit = it["prioriteit"]
            art.commerciele_waarde = it["commerciele_waarde"]
            art.bron_url = it["bron_url"]
            art.order = i
            art.briefing = self._briefing(it)

            body_file = ARTICLES / f"{it['slug']}.html"
            if body_file.exists():
                html, toc = _toc_en_anchors(body_file.read_text(encoding="utf-8").strip())
                art.body_html = html
                art.toc = toc
                art.leestijd = _leestijd(html)
                art.status = "gepubliceerd"
                art.active = True
                if not art.gepubliceerd_op:
                    art.gepubliceerd_op = timezone.now()
                if experts and not art.author:
                    art.author = experts[i % len(experts)]
                    art.reviewer = experts[(i + 1) % len(experts)]
                n_pub += 1
            else:
                art.status = "concept"
                art.active = False
            art.save()
            cats[it["categorie"]] = cats.get(it["categorie"], 0) + (1 if art.active else 0)

        self._sync_categorieen(cats)
        self.stdout.write(self.style.SUCCESS(
            f"Kennisbank: {len(items)} backlog-items ({n_new} nieuw), "
            f"{n_pub} gepubliceerd, {len(items) - n_pub} concept."))

    def _resolve_land(self, naam, landen):
        if naam in LAND_ALIAS:
            alias = LAND_ALIAS[naam]
            return landen.get(alias) if alias else None
        return landen.get(naam)

    def _briefing(self, it):
        return (f"Zoekintentie: {it['zoekintentie']}\n"
                f"Briefing: {it['briefing']}\n"
                f"Invalshoek (niet kannibaliseren): {it['invalshoek']}\n"
                f"Aanbevolen interne links: {it['interne_links']}\n"
                f"Cluster (origineel): {it['cluster_orig']} | moeilijkheid: {it['moeilijkheid']}")

    def _sync_categorieen(self, cats):
        """Houd de KennisbankCategorie-tegels in sync met de aanwezige clusters."""
        for order, (naam, aantal) in enumerate(sorted(cats.items())):
            KennisbankCategorie.objects.update_or_create(
                naam=naam,
                defaults={"icon": CAT_ICON.get(naam, "square"), "order": order,
                          "link": f"/kennisbank/?categorie={slugify(naam)}",
                          "aantal": f"{aantal} artikel" + ("" if aantal == 1 else "en")})
