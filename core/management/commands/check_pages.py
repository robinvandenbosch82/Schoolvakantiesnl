"""
Smoke-test: render elke echte route en controleer op een gezonde HTML-respons.

Mirrors de `check_pages`-conventie van de zustersites. Draai na elke template-/
view-wijziging en in CI vóór deploy:

    python manage.py check_pages
    python manage.py check_pages --verbose
"""
import sys

from django.core.management.base import BaseCommand
from django.test import Client

# Mag NOOIT in de HTML voorkomen (template-/render-fouten die doorlekken).
FORBIDDEN = [
    "TemplateSyntaxError", "Traceback (most recent call last)",
    "Invalid block tag", "Could not parse", "VariableDoesNotExist",
    "TemplateDoesNotExist",
]
# Gedeelde chrome die op elke HTML-pagina hoort te staan.
REQUIRED = ['class="topbar"', 'class="foot"', "<title>", 'name="description"']


class Command(BaseCommand):
    help = "Render alle routes en controleer op 200 + gezonde HTML."

    def add_arguments(self, parser):
        parser.add_argument("--verbose", action="store_true", help="Print elke geslaagde pagina.")

    def handle(self, *args, **options):
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

        from core.models import BlogArtikel, Land
        client = Client(SERVER_NAME="localhost")
        verbose = options["verbose"]

        targets = [
            ("home", "/"),
            ("landen-overzicht", "/landen/"),
            ("planner", "/planner/"),
            ("druktekaart", "/druktekaart/"),
            ("blog-overzicht", "/blog/"),
            ("over-ons", "/over-ons/"),
            ("samenwerken", "/samenwerken/"),
        ]
        # Steekproef landen: NL + DE + (indien aanwezig) regio-landen.
        for code in ("NL", "DE", "FR", "ES"):
            land = Land.objects.filter(iso_code=code, actief=True).first()
            if land:
                targets.append((f"land-{code}", f"/landen/{land.slug}/"))
        # Jaar-switcher: tweede jaar van NL meenemen.
        nl = Land.objects.filter(iso_code="NL").first()
        if nl:
            targets.append(("land-NL-2027", f"/landen/{nl.slug}/?jaar=2027"))
        # Eén blogartikel.
        post = BlogArtikel.objects.filter(active=True).first()
        if post:
            targets.append((f"blog:{post.slug}", f"/blog/{post.slug}/"))
        # Niet-HTML: robots + sitemap (apart gecontroleerd).
        special = [("robots.txt", "/robots.txt"), ("sitemap.xml", "/sitemap.xml")]

        failures = 0
        for label, url in targets:
            try:
                resp = client.get(url)
            except Exception as exc:  # noqa: BLE001
                failures += 1
                self.stderr.write(self.style.ERROR(f"FAIL {url}, raised {exc!r}"))
                continue
            problems = []
            if resp.status_code != 200:
                problems.append(f"status {resp.status_code}")
            html = resp.content.decode("utf-8", errors="replace")
            for m in REQUIRED:
                if m not in html:
                    problems.append(f"mist {m!r}")
            for m in FORBIDDEN:
                if m in html:
                    problems.append(f"bevat {m!r}")
            if problems:
                failures += 1
                self.stderr.write(self.style.ERROR(f"FAIL {url}, {', '.join(problems)}"))
            elif verbose:
                self.stdout.write(self.style.SUCCESS(f"OK   {url} ({label})"))

        for label, url in special:
            resp = client.get(url)
            if resp.status_code != 200:
                failures += 1
                self.stderr.write(self.style.ERROR(f"FAIL {url}, status {resp.status_code}"))
            elif verbose:
                self.stdout.write(self.style.SUCCESS(f"OK   {url} ({label})"))

        total = len(targets) + len(special)
        if failures:
            self.stderr.write(self.style.ERROR(f"\n{failures}/{total} routes gefaald."))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS(f"\nAlle {total} routes OK."))
