"""
Haal de (gehotlinkte) blog-afbeeldingen lokaal binnen, zodat de blog niet
afhankelijk is van de oude WordPress-site (perf/LCP, privacy, beschikbaarheid).

Elke BlogArtikel.photo_url wordt gedownload, genormaliseerd naar geoptimaliseerde
JPEG en opgeslagen als `static/img/blog/<slug>.jpg`. Dat pad zit al in de
templates (de `{% static %}`-fallback) én in de Article-structured-data, en wordt
door WhiteNoise met far-future cache geserveerd. Bij succes wordt `photo_url`
geleegd zodat de lokale versie wint; faalt het, dan blijft de hotlink als terugval
staan.

De bestanden zijn statische assets (in git), dus deploy-stabiel, geen
afhankelijkheid van een persistente media-volume.

    python manage.py download_blog_images
    python manage.py download_blog_images --force   # ook al bestaande opnieuw
"""
import sys
from io import BytesIO

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image

from core.models import BlogArtikel

DEST = settings.BASE_DIR / "static" / "img" / "blog"
MAX_WIDTH = 1280
MAX_BYTES = 12 * 1024 * 1024
QUALITY = 82


class Command(BaseCommand):
    help = "Download blog-afbeeldingen naar static/img/blog/ en leeg photo_url."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true",
                            help="Download ook als het lokale bestand al bestaat.")

    def handle(self, *args, **opts):
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

        DEST.mkdir(parents=True, exist_ok=True)
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (schoolvakanties.nl)"})

        done = failed = skipped = 0
        for post in BlogArtikel.objects.filter(active=True).exclude(photo_url=""):
            path = DEST / f"{post.slug}.jpg"
            if path.exists() and not opts["force"]:
                # Lokaal bestand bestaat al → laat de lokale versie winnen.
                BlogArtikel.objects.filter(pk=post.pk).update(photo_url="")
                skipped += 1
                continue
            try:
                resp = session.get(post.photo_url, timeout=30)
                resp.raise_for_status()
                if not resp.headers.get("Content-Type", "").startswith("image/"):
                    raise ValueError("geen afbeelding (Content-Type)")
                if len(resp.content) > MAX_BYTES:
                    raise ValueError("afbeelding te groot")
                im = Image.open(BytesIO(resp.content)).convert("RGB")
                if im.width > MAX_WIDTH:
                    h = round(im.height * MAX_WIDTH / im.width)
                    im = im.resize((MAX_WIDTH, h), Image.LANCZOS)
                im.save(path, "JPEG", quality=QUALITY, optimize=True)
                # Lokale versie wint; hotlink niet meer nodig.
                BlogArtikel.objects.filter(pk=post.pk).update(photo_url="")
                done += 1
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(self.style.WARNING(
                    f"  faalde: {post.slug} ({exc}), hotlink blijft als terugval."))
                failed += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nKlaar, {done} gedownload, {skipped} bestond al, {failed} mislukt. "
            f"Map: {DEST}"))
