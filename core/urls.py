"""Core URL patterns.

Landenpagina's staan op root-niveau (/<slug>/), zoals de geïndexeerde live-site:
/duitsland/, /engeland/, /spanje/… De root-slugroute staat daarom als laatste en
vangt elke losse segment-URL; vaste routes hierboven hebben voorrang.

Read-only contentpagina's worden server-side gecachet (cache_page) zodat de
DB-queries + render niet per request gebeuren (snelle TTFB op productie). Het
samenwerken-formulier (POST/CSRF) en de redirects worden NIET gecachet. Een
admin-edit leegt de cache direct via core.signals.

Legacy-redirects houden oud verkeer vast:
- /landen/<slug>/  -> /<slug>/        (oude dev-URL's)
- /kennisbank/...   -> /<land>/        (kennisbankartikelen zijn er nu niet; komen terug)
- /blog/jjjj/mm/dd/<slug>/ -> /blog/<slug>/  (oude datum-URL's)
"""

from django.conf import settings
from django.urls import path
from django.views.decorators.cache import cache_page

from . import views, widget_views

_TTL = settings.PAGE_CACHE_SECONDS


def _cached(view):
    """Server-side page-cache voor een read-only GET-view."""
    return cache_page(_TTL)(view)


urlpatterns = [
    path("", _cached(views.home), name="home"),
    path("planner/", _cached(views.planner), name="planner"),
    path("druktekaart/", _cached(views.druktekaart), name="druktekaart"),
    path("blog/", _cached(views.blog_overzicht), name="blog"),
    path("blog/<int:jaar>/<int:maand>/<int:dag>/<slug:slug>/", views.blog_datum_redirect),
    path("blog/<slug:slug>/", _cached(views.blog_detail), name="blog_detail"),
    path("over-ons/", _cached(views.over_ons), name="over_ons"),
    path("samenwerken/", views.samenwerken, name="samenwerken"),  # POST-formulier: niet cachen
    path("landen/", _cached(views.landen_overzicht), name="landen"),
    path("landen/<slug:slug>/", views.land_legacy_redirect),
    path("privacy/", _cached(views.privacy), name="privacy"),
    path("cookies/", _cached(views.cookies), name="cookies"),
    path("voorwaarden/", _cached(views.voorwaarden), name="voorwaarden"),
    path("kennisbank/", _cached(views.kennisbank_index), name="kennisbank"),
    path("kennisbank/land/<slug:slug>/", _cached(views.kennisbank_land), name="kennisbank_land"),
    path("kennisbank/<slug:slug>/", _cached(views.kennisbank_detail), name="kennisbank_detail"),
    path("kennisbank/<path:rest>", views.kennisbank_redirect),  # vangnet oude/onbekende URL's
    # Embeddable widget voor partnersites (vóór de slug-catch-all).
    path("widget.js", widget_views.widget_js, name="widget_js"),
    path("widget/data", widget_views.widget_data, name="widget_data"),
    path("widget/", widget_views.widget_generator, name="widget_generator"),
    # Root-level landpagina's — moet als laatste (vangt /<slug>/).
    path("<slug:slug>/", _cached(views.land_detail), name="land_detail"),
]
