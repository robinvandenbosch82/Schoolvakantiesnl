"""Stuur een testmail om de SMTP-configuratie te controleren.

Gebruikt de actieve e-mailinstellingen (EMAIL_HOST/PORT/USER/PASSWORD/TLS) en
toont de echte fout als versturen mislukt, in plaats van die stil te houden.

    python manage.py mailtest                 # naar DEFAULT_FROM_EMAIL
    python manage.py mailtest jij@example.com # naar een specifiek adres
"""
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Verstuur een testmail om de SMTP-instellingen te verifiëren."

    def add_arguments(self, parser):
        parser.add_argument("to", nargs="?", default=settings.DEFAULT_FROM_EMAIL,
                            help="Ontvanger (default: DEFAULT_FROM_EMAIL).")

    def handle(self, *args, **opts):
        to = opts["to"]
        self.stdout.write(
            f"Backend: {settings.EMAIL_BACKEND}\n"
            f"Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT} (TLS={settings.EMAIL_USE_TLS})\n"
            f"Auth-gebruiker: {settings.EMAIL_HOST_USER}\n"
            f"Afzender: {settings.DEFAULT_FROM_EMAIL}\n"
            f"Naar: {to}\n")
        try:
            verstuurd = send_mail(
                "Schoolvakanties.nl, SMTP-test",
                "Dit is een testmail. Komt deze aan, dan werkt de uitgaande mail.",
                settings.DEFAULT_FROM_EMAIL, [to], fail_silently=False)
        except Exception as exc:  # noqa: BLE001
            self.stderr.write(self.style.ERROR(f"MISLUKT: {type(exc).__name__}: {exc}"))
            return
        self.stdout.write(self.style.SUCCESS(
            f"OK, {verstuurd} bericht(en) verstuurd. Controleer de inbox van {to}."))
