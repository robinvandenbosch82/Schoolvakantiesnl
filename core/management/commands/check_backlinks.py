"""Verifieer periodiek of de statische backlink naar de landpagina nog op elke
widget-pagina staat, en zet de modus.

Simpele HTML-fetch (geen headless): we zoeken een <a href> naar de juiste
landpagina op onze eigen origin. CSS-verbergen glipt er bewust doorheen — de
'data verdwijnt'-hefboom (teaser-modus) doet het zware werk.

Hysterese tegen valse positieven:
- backlink gevonden        -> status 'actief', teller terug naar 0.
- backlink (herhaald) weg  -> 1e keer: waarschuwingsmail (indien e-mail bekend);
                              vanaf GRACE_CHECKS opeenvolgende missers: 'teaser'.
- netwerk-/serverfout      -> overslaan (geen straf voor een tijdelijke storing);
                              een echte 4xx (pagina weg) telt wél als misser.

    python manage.py check_backlinks            # alle pagina's die toe zijn aan een check
    python manage.py check_backlinks --all      # forceer: check alle pagina's nu
    python manage.py check_backlinks --interval 6   # minimaal 6 uur tussen checks
"""
import datetime as dt
import re

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import WidgetPagina

GRACE_CHECKS = 2          # aantal opeenvolgende missers vóór degradatie naar teaser
DEFAULT_INTERVAL_H = 24   # minimaal aantal uur tussen twee checks van dezelfde pagina
UA = "SchoolvakantiesBacklinkBot/1.0 (+https://schoolvakanties.nl/widget/)"


class Command(BaseCommand):
    help = "Controleer de backlinks van alle widget-pagina's en zet de modus."

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true",
                            help="Forceer een check van álle pagina's, ongeacht het interval.")
        parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_H,
                            help=f"Minimaal aantal uur tussen checks (default {DEFAULT_INTERVAL_H}).")

    def handle(self, *args, **opts):
        qs = WidgetPagina.objects.select_related("widget", "widget__land")
        if not opts["all"]:
            grens = timezone.now() - dt.timedelta(hours=opts["interval"])
            qs = qs.filter(models_q(grens))

        n_ok = n_fail = n_skip = 0
        for pagina in qs:
            uitkomst = self._check(pagina)
            if uitkomst is None:
                n_skip += 1
            elif uitkomst:
                n_ok += 1
            else:
                n_fail += 1
        self.stdout.write(self.style.SUCCESS(
            f"Backlink-check klaar: {n_ok} ok, {n_fail} mislukt, {n_skip} overgeslagen."))

    def _check(self, pagina):
        """True=backlink gezien, False=afwezig (telt als misser), None=overgeslagen."""
        gevonden = self._fetch_en_zoek(pagina)
        now = timezone.now()
        if gevonden is None:
            return None  # transiënte fout: niets wijzigen
        pagina.laatst_gecheckt = now
        if gevonden:
            pagina.backlink_ok = True
            pagina.fail_count = 0
            pagina.laatst_ok = now
            pagina.grace_mail_op = None
            pagina.status = WidgetPagina.ACTIEF
            pagina.save()
            return True
        # backlink afwezig
        pagina.backlink_ok = False
        pagina.fail_count = (pagina.fail_count or 0) + 1
        if pagina.fail_count == 1 and pagina.widget.email and not pagina.grace_mail_op:
            self._waarschuw(pagina)
            pagina.grace_mail_op = now
        if pagina.fail_count >= GRACE_CHECKS:
            pagina.status = WidgetPagina.TEASER
        pagina.save()
        return False

    def _fetch_en_zoek(self, pagina):
        try:
            r = requests.get(pagina.url, headers={"User-Agent": UA, "Accept": "text/html"},
                             timeout=20, allow_redirects=True)
        except requests.RequestException:
            return None
        if r.status_code >= 500:
            return None              # serverstoring: niet bestraffen
        if r.status_code >= 400:
            return False             # pagina weg/verboden: backlink effectief afwezig
        return self._heeft_backlink(r.text, pagina.widget.land.slug)

    @staticmethod
    def _heeft_backlink(html, slug):
        """Staat er een <a href> naar onze landpagina in de HTML? Host-onafhankelijk
        (schoolvakanties.nl met/zonder www/https), pad eindigt op /<slug>/."""
        for m in re.finditer(r'<a\b[^>]*\bhref\s*=\s*["\']([^"\']+)["\']', html, re.I):
            href = m.group(1)
            if re.search(r'schoolvakanties\.nl/+' + re.escape(slug) + r'/?(?:[?#]|$)', href, re.I):
                return True
        return False

    def _waarschuw(self, pagina):
        land = pagina.widget.land
        onderwerp = "Je Schoolvakanties.nl-widget mist de bronvermelding"
        bericht = (
            f"Hoi,\n\nWe zien de bron-link naar Schoolvakanties.nl niet meer op:\n"
            f"  {pagina.url}\n\n"
            f"Zolang die link ontbreekt, schakelt de widget na de volgende controle over "
            f"naar een beperkte weergave (met een doorklik naar onze site). Plaats de link "
            f"terug en de volledige vakantiekalender komt vanzelf weer tevoorschijn.\n\n"
            f"De bron-link hoort zo te luiden:\n"
            f'  <a href="{settings.SITE_ORIGIN}/{land.slug}/">Schoolvakanties {land.naam} '
            f"– bron: Schoolvakanties.nl</a>\n\n"
            f"Vragen? Beantwoord gerust deze mail.\n\nTeam Schoolvakanties.nl"
        )
        try:
            send_mail(onderwerp, bericht, settings.DEFAULT_FROM_EMAIL,
                      [pagina.widget.email], fail_silently=True)
        except Exception:  # noqa: BLE001
            pass


def models_q(grens):
    """Pagina's die nog nooit of lang geleden gecheckt zijn."""
    from django.db.models import Q
    return Q(laatst_gecheckt__isnull=True) | Q(laatst_gecheckt__lt=grens)
