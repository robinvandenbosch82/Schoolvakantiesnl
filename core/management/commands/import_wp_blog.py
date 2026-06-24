"""
Importeer de oude blogberichten uit een WordPress-export (WXR/XML) naar
BlogArtikel. Idempotent op slug. Afbeeldingen blijven voorlopig hotlinks: de
uitgelichte afbeelding wordt als externe `photo_url` opgeslagen en de <img>'s in
de tekst verwijzen naar de oude WordPress-URL's (later vervangen we die).

    python manage.py import_wp_blog --file "C:/Users/robin/Downloads/schoolvakantiesopzoekenperland.WordPress.2026-06-22.xml"
"""
from __future__ import annotations

import datetime as dt
import re
import sys
import xml.etree.ElementTree as ET

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from core.models import BlogArtikel, Land

NS = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
    "dc": "http://purl.org/dc/elements/1.1/",
}
MND_NL = ["", "januari", "februari", "maart", "april", "mei", "juni", "juli",
          "augustus", "september", "oktober", "november", "december"]

# De WXR-export staat in de repo zodat de import ook op de server (Render) kan
# draaien; lokaal overschrijfbaar met --file.
DEFAULT_FILE = str(settings.BASE_DIR / "deploy" / "data" / "wp_blog_export.xml")


def _txt(el, path):
    return (el.findtext(path, namespaces=NS) or "").strip()


def _datum(raw):
    try:
        d = dt.datetime.strptime(raw[:10], "%Y-%m-%d").date()
        return f"{d.day} {MND_NL[d.month]} {d.year}"
    except (ValueError, IndexError):
        return ""


def _pubdate(raw):
    """WP post_date ('2023-11-03 10:30:00') -> tijdzone-bewuste datetime (voor de
    Google News-sitemap). Leeg/onparsebaar -> None."""
    from django.utils import timezone
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            naive = dt.datetime.strptime((raw or "").strip()[:19], fmt)
            return timezone.make_aware(naive)
        except (ValueError, IndexError):
            continue
    return None


def _geen_streepjes(s):
    """Gedachtestreepjes (—) vervangen door een komma; en-streepjes (reeksen) blijven."""
    return re.sub(r"\s*—\s*", ", ", s or "")


def _clean_html(html):
    # Verwijder de onzichtbare WordPress-blok-commentaren (<!-- wp:... -->).
    html = re.sub(r"<!--\s*/?wp:.*?-->", "", html, flags=re.S)
    return _geen_streepjes(html).strip()


def _excerpt(raw_excerpt, content):
    if raw_excerpt:
        return _geen_streepjes(re.sub(r"<[^>]+>", "", raw_excerpt).strip())[:300]
    tekst = re.sub(r"<[^>]+>", " ", content)
    tekst = _geen_streepjes(re.sub(r"\s+", " ", tekst).strip())
    return tekst[:200].rsplit(" ", 1)[0] + ("…" if len(tekst) > 200 else "")


class Command(BaseCommand):
    help = "Importeer oude blogberichten uit een WordPress-XML (WXR)."

    def add_arguments(self, parser):
        parser.add_argument("--file", default=DEFAULT_FILE, help="Pad naar de WXR-XML.")

    def handle(self, *args, **opts):
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

        try:
            root = ET.parse(opts["file"]).getroot()
        except (ET.ParseError, FileNotFoundError, OSError) as exc:
            raise CommandError(f"Kan de XML niet lezen ({opts['file']}): {exc}") from exc
        channel = root.find("channel")
        items = channel.findall("item") if channel is not None else []

        # Bijlage-ID → URL (voor de uitgelichte afbeelding via _thumbnail_id).
        attach = {}
        for it in items:
            if _txt(it, "wp:post_type") == "attachment":
                pid, url = _txt(it, "wp:post_id"), _txt(it, "wp:attachment_url")
                if pid and url:
                    attach[pid] = url

        # Posts verzamelen (gepubliceerd), sorteren op datum (nieuwste eerst).
        posts = []
        for it in items:
            if _txt(it, "wp:post_type") != "post" or _txt(it, "wp:status") != "publish":
                continue
            posts.append(it)
        posts.sort(key=lambda it: _txt(it, "wp:post_date"), reverse=True)

        # Landnaam → Land (voor het koppelen van buitenlandse bestemmingen).
        land_by_naam = {l.naam.lower(): l for l in Land.objects.all()
                        if l.naam.lower() != "nederland"}

        # Redactie voor de E-E-A-T byline: auteur + reviewer over de experts
        # verdelen. Cruciaal: de blog wordt na de seed geïmporteerd, dus de
        # auteur móét hier worden gezet (anders blijft de byline op een verse
        # deploy leeg). We zetten 'm alleen als die nog niet bestaat, zodat een
        # handmatige toewijzing in de admin bij her-import blijft staan.
        from core.models import Expert
        experts = list(Expert.objects.filter(active=True).order_by("order"))

        gemaakt = bijgewerkt = 0
        for order, it in enumerate(posts):
            titel = _geen_streepjes((it.findtext("title") or "").strip())
            slug = _txt(it, "wp:post_name") or slugify(titel)
            slug = slug[:220]
            content = _clean_html(it.findtext("content:encoded", namespaces=NS) or "")

            # uitgelichte afbeelding: _thumbnail_id → bijlage, anders 1e <img> in tekst
            thumb = ""
            for pm in it.findall("wp:postmeta", NS):
                if (pm.findtext("wp:meta_key", namespaces=NS) or "") == "_thumbnail_id":
                    thumb = attach.get((pm.findtext("wp:meta_value", namespaces=NS) or "").strip(), "")
            if not thumb:
                m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
                thumb = m.group(1) if m else ""
            # Is de afbeelding al lokaal gedownload (static/img/blog/<slug>.jpg)?
            # Dan die laten winnen: photo_url leeg, template gebruikt de static-versie.
            if (settings.BASE_DIR / "static" / "img" / "blog" / f"{slug}.jpg").exists():
                thumb = ""

            cats = [c.text for c in it.findall("category")
                    if c.get("domain") == "category" and c.text]
            categorie = cats[0] if cats else ""
            if categorie.lower() in ("", "uncategorized", "geen categorie", "niet gecategoriseerd"):
                categorie = "Reistips"

            obj, created = BlogArtikel.objects.update_or_create(
                slug=slug,
                defaults={
                    "titel": titel,
                    "categorie": categorie,
                    "datum": _datum(_txt(it, "wp:post_date")),
                    "gepubliceerd_op": _pubdate(_txt(it, "wp:post_date")),
                    "excerpt": _excerpt(it.findtext("excerpt:encoded", namespaces=NS) or "", content),
                    "body_html": content,
                    "photo_url": thumb,
                    "photo_alt": titel,
                    "active": True,
                    "order": order,
                },
            )
            # Byline-redactie toekennen als die nog ontbreekt.
            if experts and not obj.author_id:
                obj.author = experts[order % len(experts)]
                obj.reviewer = experts[(order + 1) % len(experts)]
                obj.save(update_fields=["author", "reviewer"])

            # Koppel aan landen waarvan de naam in de titel voorkomt.
            obj.landen.clear()
            for naam, land in land_by_naam.items():
                if re.search(r"\b" + re.escape(naam) + r"\b", titel, re.I):
                    obj.landen.add(land)

            gemaakt += created
            bijgewerkt += (not created)
            self.stdout.write(f"  {'+' if created else '~'} {titel[:60]}  ({slug})")

        self.stdout.write(self.style.SUCCESS(
            f"\nKlaar, {gemaakt} nieuw, {bijgewerkt} bijgewerkt "
            f"({len(attach)} bijlagen herkend)."))
