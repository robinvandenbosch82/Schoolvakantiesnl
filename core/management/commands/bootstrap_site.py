"""
One-shot deploy-bootstrap voor een verse host (lege database).

Vult de site idempotent: importeert de vakantie-/feestdagdata uit OpenHolidays
(best-effort, een API-storing laat de deploy niet falen), seedt de redactionele
data, synct de Page-rijen en maakt een admin-user uit de omgeving. Veilig om bij
elke deploy te draaien.

    python manage.py bootstrap_site
    python manage.py bootstrap_site --skip-import   # alleen seed + pages + superuser
"""
import os

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Vul een verse host: OpenHolidays-import + seed + pages + superuser (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--skip-import", action="store_true",
                            help="Sla de OpenHolidays-import over (alleen seed + pages + superuser).")

    def handle(self, *args, **opts):
        from core.models import Land

        # 1) Volledige vakantie-/feestdagdata (best-effort: nooit de deploy breken).
        #    import_alles = OpenHolidays + nationale bronnen (NL/FR) + feestdagen-only
        #    landen (NO/DK/FI/GB/GR via Nager) + kruiscontrole met --fill.
        if not opts["skip_import"]:
            try:
                self.stdout.write("Vakantie-/feestdagdata importeren (import_alles)…")
                call_command("import_alles", fill=True)
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(self.style.WARNING(
                    f"Import overgeslagen (API niet bereikbaar?): {exc}. "
                    "De cron/handmatige run vult dit later."))
        if not Land.objects.exists():
            self.stderr.write(self.style.WARNING(
                "Nog geen landen in de DB, draai later `manage.py import_alles`."))

        # 2) Redactionele data (landintro's, weer, bestemmingen, reisweken, experts, FAQ).
        self.stdout.write("Redactionele data seeden…")
        call_command("seed_schoolvakanties")

        # 3) Blog uit de WordPress-export in de repo (best-effort).
        try:
            self.stdout.write("Blog importeren (WordPress-export)…")
            call_command("import_wp_blog")
        except Exception as exc:  # noqa: BLE001
            self.stderr.write(self.style.WARNING(f"Blogimport overgeslagen: {exc}."))

        # 3b) Byline-redactie: zeker stellen dat élk artikel een auteur + reviewer
        #     heeft. De seed (stap 2) draait vóór de blog bestaat en de import
        #     dekt alleen de WXR-export; dit vangt al het overige op.
        self._assign_blog_redactie()

        # 3c) Plaats -> regio vullen uit OpenHolidays voor alle landen met
        #     plaatsniveau-data (NL incl. Gelderland-splitsing, CZ okres→kraj, …).
        #     Best-effort: faalt de API, dan blijft de gecureerde seed-set staan.
        if not opts["skip_import"]:
            try:
                self.stdout.write("Plaatsen->regio importeren…")
                call_command("import_plaatsen")
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(self.style.WARNING(f"Plaatsenimport overgeslagen: {exc}."))

        # 4) Page-rijen synchroniseren met de routing-registry.
        call_command("sync_pages")

        # 5) Superuser uit env (DJANGO_SUPERUSER_USERNAME/PASSWORD/EMAIL).
        self._ensure_superuser()

        self.stdout.write(self.style.SUCCESS("bootstrap_site klaar."))

    def _assign_blog_redactie(self):
        """Ken auteur + reviewer toe aan elk artikel zonder auteur (deterministisch
        op slug). Idempotent: laat handmatige toewijzingen in de admin staan."""
        from core.models import BlogArtikel, Expert

        experts = list(Expert.objects.filter(active=True).order_by("order"))
        if not experts:
            return
        n = 0
        for i, art in enumerate(BlogArtikel.objects.filter(author__isnull=True).order_by("slug")):
            art.author = experts[i % len(experts)]
            art.reviewer = experts[(i + 1) % len(experts)]
            art.save(update_fields=["author", "reviewer"])
            n += 1
        if n:
            self.stdout.write(f"Byline-redactie toegekend aan {n} resterend artikel(en).")

    def _ensure_superuser(self):
        from django.contrib.auth import get_user_model

        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")
        if not username or not password:
            return
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' bestaat al.")
            return
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' aangemaakt."))
