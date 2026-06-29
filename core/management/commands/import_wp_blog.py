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

# Handmatige land-koppeling voor blogs waarvan het land niet via de titel wordt
# herkend: óf omdat het land niet letterlijk in de titel staat (Veluwe, Limburg,
# Schotland, Andalusie, Vlamingen), óf omdat de spelling afwijkt ("Italie" zonder
# trema), óf omdat Nederland bewust uit de automatische match is gehouden.
# Sleutel = blog-slug, waarde = tuple van land-slugs. Vult de automatische
# titelmatch aan (unie), zodat bestaande koppelingen blijven staan.
# Genormaliseerde, vaste blogcategorieën. De oudere WordPress-import gebruikte
# rommelige/landgebonden categoriewaarden ('Algemeen', 'finance', 'italie',
# 'schoolvakanties spanje', ...); we mappen die naar deze schone set. Nieuwere
# artikelen in de export gebruiken deze waarden al.
CLEAN_CATS = {"Slim plannen", "Bestemmingen", "Met kinderen",
              "Drukte & prijzen", "Algemeen"}

# Handmatige categorie-toewijzing per slug voor de artikelen waarvan de
# opgeslagen categorie niet in CLEAN_CATS zit. Sleutel = blog-slug.
SLUG_CATEGORIE = {
    # Bestemmingen (specifieke plekken / bestemmingen)
    "ga-op-avontuur-met-een-fly-drive-vakantie": "Bestemmingen",
    "liberte-vakantiehuizen-voor-rust-en-ruimte": "Bestemmingen",
    "op-zoek-naar-slimme-inpaktrucs-zo-ga-je-voorbereid-naar-andalusie": "Bestemmingen",
    "een-reis-langs-de-mooiste-wandelroutes-van-europa": "Bestemmingen",
    "kom-wandelen-door-het-heuvellandschap-van-limburg": "Bestemmingen",
    "zomervakantie-in-zuid-frankrijk-ontdek-de-charme-van-le-lac-bleu-en-lespinet": "Bestemmingen",
    "gezinsavontuur-in-schotland-ontspannen-treinrondreizen-tijdens-de-schoolvakantie": "Bestemmingen",
    "ontsnap-naar-klein-curacao-perfect-voor-een-onvergetelijke-schoolvakantie": "Bestemmingen",
    "ontdek-blauwestad-verborgen-parel-in-groningen-en-schitterend-recreatiegebied": "Bestemmingen",
    "camping-veluwe-met-zwembad-de-voordelen-voor-jong-en-oud": "Bestemmingen",
    "camping-zanderij-in-voorthuizen-perfecte-plek-voor-schoolvakanties": "Bestemmingen",
    "met-de-trein-naar-zwitserland-een-ontspannen-alternatief-voor-vliegreizen-tijdens-de-schoolvakanties": "Bestemmingen",
    "ongerepte-wildernis-en-onvergetelijke-safari-een-safarireis-door-botswanas-prachtige-noorden": "Bestemmingen",
    "op-pad-in-de-schoolvakantie": "Bestemmingen",
    "top-10-verre-vakantiebestemmingen-tijdens-de-zomervakantie": "Bestemmingen",
    # Slim plannen (schoolvakantie-planning, data, beleid)
    "de-toekomst-van-schoolvakanties-wat-als-jij-zelf-de-data-mocht-kiezen": "Slim plannen",
    "indeling-schoolvakantieregios-in-nederland": "Slim plannen",
    "waarom-dit-het-perfecte-moment-is-om-je-zomervakantie-voor-2026-te-boeken": "Slim plannen",
    "de-schoolvakanties-van-2024": "Slim plannen",
    "wat-we-weten-over-de-duitse-schoolvakanties": "Slim plannen",
    "steun-voor-kortere-zomervakantie-onder-vlamingen-maar-weinig-draagvlak-voor-hoger-loon-leerkrachten": "Slim plannen",
    "la-dolce-vita-italie-of-een-lange-vakantiepluim": "Slim plannen",
    "678": "Slim plannen",
    # Met kinderen (gezinsactiviteiten)
    "de-leukste-uitjes-met-kinderen-tijdens-de-schoolvakantie-op-een-rij": "Met kinderen",
    "zo-organiseer-je-een-uitgebreid-kinderfeestje-tijdens-de-schoolvakantie": "Met kinderen",
    "overnachten-in-een-boomhut-leuk-voor-kinderen": "Met kinderen",
    # Drukte & prijzen (kosten, geld, betaalbaar reizen)
    "zoveel-kost-het-je-om-wel-of-niet-in-de-schoolvakantie-te-reizen": "Drukte & prijzen",
    "onontdekte-vlieg-bestemmingen-betaalbare-vliegtickets-tijdens-de-drukke-vakantieperiodes": "Drukte & prijzen",
    "geld-lenen-voor-een-vakantie-slimme-keuzes-voor-extra-vakantieplezier": "Drukte & prijzen",
    "vakantiegeld-en-beleggen-slimme-avonturen-met-je-geld": "Drukte & prijzen",
    # Algemeen (onderwijs / werk / overige niet-reisonderwerpen)
    "een-wereld-in-beweging-vraagt-om-jouw-talent": "Algemeen",
    "fit-en-zelfverzekerd-op-vakantie-met-medisch-afvallen": "Algemeen",
    "hoe-maak-je-een-school-klaar-voor-de-toekomst": "Algemeen",
    "mantelzorg-in-de-schoolvakantie-zo-ontlast-een-zorgwoning-ouders-met-een-zorgvraag-in-de-familie": "Algemeen",
    "ontslagen-worden-tijdens-de-vakantie-mag-dat": "Algemeen",
    "tips-voor-een-opgeruimde-en-veilige-leeromgeving": "Algemeen",
    "opleiding-kiezen-na-de-schoolvakantie-ontdek-de-game-design-opleiding": "Algemeen",
    "werken-in-het-onderwijs-waarom-schoolvakanties-een-onverwacht-carrierevoordeel-zijn": "Algemeen",
    "buiten-spelen-wordt-pas-echt-leuk-met-de-juiste-speeltoestellen-op-het-schoolplein": "Algemeen",
    "op-vakantie-met-je-hond-dit-mag-niet-ontbreken": "Algemeen",
}

# Inline body-afbeeldingen die naar de (offline) oude WordPress-site hotlinkten,
# vervangen door lokale Pexels-foto's in static/img/blog/inline/. Sleutel = de
# dode bron-URL in de body, waarde = lokaal pad onder STATIC_URL. Wordt bij de
# import op de body toegepast, dus deploy-stabiel.
INLINE_IMG_REPLACE = {
    "https://www.schoolvakanties.nl/wp-content/uploads/2025/02/grand-canal-in-venice-with-saint-mary-of-health-basilica-sun-in-italy-1024x682.jpg": "img/blog/inline/ldv-1-venice.jpg",
    "https://www.schoolvakanties.nl/wp-content/uploads/2025/02/happy-kids-playing-with-sand-on-beach-1024x684.jpg": "img/blog/inline/ldv-2-beach.jpg",
    "https://www.schoolvakanties.nl/wp-content/uploads/2025/02/father-plays-guitar-for-kids-at-trailer-camping-1024x681.jpg": "img/blog/inline/ldv-3-camping.jpg",
    "https://www.schoolvakanties.nl/wp-content/uploads/2024/09/traveling-family-looking-on-bled-lake-slovenia-europe-1024x682.jpg": "img/blog/inline/ovb-1-bled.jpg",
    "https://www.schoolvakanties.nl/wp-content/uploads/2024/09/church-of-saint-john-the-theologian-ohrid-north-macedonia--1024x576.jpg": "img/blog/inline/ovb-2-ohrid.jpg",
    "https://www.schoolvakanties.nl/wp-content/uploads/2024/09/kuang-si-waterfa-near-luang-prabang-laos-1024x633.jpg": "img/blog/inline/ovb-3-laos.jpg",
    "https://www.schoolvakanties.nl/wp-content/uploads/2024/09/traveler-enjoying-view-of-sigiriya-rock-in-sri-lanka-1024x682.jpg": "img/blog/inline/ovb-4-sigiriya.jpg",
    "https://www.schoolvakanties.nl/wp-content/uploads/2024/09/young-woman-in-la-paz-bolivia-1024x682.jpg": "img/blog/inline/ovb-5-lapaz.jpg",
}

SLUG_LANDEN = {
    # Nederland (binnenlandse bestemmingen / NL-schoolvakantie-onderwerpen)
    "camping-veluwe-met-zwembad-de-voordelen-voor-jong-en-oud": ("nederland",),
    "camping-zanderij-in-voorthuizen-perfecte-plek-voor-schoolvakanties": ("nederland",),
    "de-leukste-uitjes-met-kinderen-tijdens-de-schoolvakantie-op-een-rij": ("nederland",),
    "de-schoolvakanties-van-2024": ("nederland",),
    "de-toekomst-van-schoolvakanties-wat-als-jij-zelf-de-data-mocht-kiezen": ("nederland",),
    "indeling-schoolvakantieregios-in-nederland": ("nederland",),
    "kom-wandelen-door-het-heuvellandschap-van-limburg": ("nederland",),
    "ontdek-blauwestad-verborgen-parel-in-groningen-en-schitterend-recreatiegebied": ("nederland",),
    "op-pad-in-de-schoolvakantie": ("nederland",),
    "zoveel-kost-het-je-om-wel-of-niet-in-de-schoolvakantie-te-reizen": ("nederland",),
    # Buitenland
    "gezinsavontuur-in-schotland-ontspannen-treinrondreizen-tijdens-de-schoolvakantie": ("engeland",),
    "la-dolce-vita-italie-of-een-lange-vakantiepluim": ("italie",),
    "op-zoek-naar-slimme-inpaktrucs-zo-ga-je-voorbereid-naar-andalusie": ("spanje",),
    "steun-voor-kortere-zomervakantie-onder-vlamingen-maar-weinig-draagvlak-voor-hoger-loon-leerkrachten": ("belgie",),
    "wat-we-weten-over-de-duitse-schoolvakanties": ("duitsland",),
}


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
        alle_landen = list(Land.objects.all())
        land_by_naam = {l.naam.lower(): l for l in alle_landen
                        if l.naam.lower() != "nederland"}
        # Slug → Land (voor de handmatige SLUG_LANDEN-override hieronder).
        land_by_slug = {l.slug: l for l in alle_landen}

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
            # Dode hotlinks naar de oude WP-site vervangen door lokale Pexels-foto's.
            for dead, local in INLINE_IMG_REPLACE.items():
                content = content.replace(dead, settings.STATIC_URL.rstrip("/") + "/" + local)

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
            # Normaliseren naar de schone taxonomie: eerst een expliciete
            # slug-override, anders de bestaande waarde als die al schoon is,
            # anders de restbak 'Algemeen'.
            if slug in SLUG_CATEGORIE:
                categorie = SLUG_CATEGORIE[slug]
            elif categorie not in CLEAN_CATS:
                categorie = "Algemeen"

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
            # Handmatige aanvulling voor blogs die de titelmatch mist.
            for land_slug in SLUG_LANDEN.get(slug, ()):
                land = land_by_slug.get(land_slug)
                if land:
                    obj.landen.add(land)

            gemaakt += created
            bijgewerkt += (not created)
            self.stdout.write(f"  {'+' if created else '~'} {titel[:60]}  ({slug})")

        self.stdout.write(self.style.SUCCESS(
            f"\nKlaar, {gemaakt} nieuw, {bijgewerkt} bijgewerkt "
            f"({len(attach)} bijlagen herkend)."))
