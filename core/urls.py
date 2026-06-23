"""Core URL patterns.

Landenpagina's staan op root-niveau (/<slug>/), zoals de geïndexeerde live-site:
/duitsland/, /engeland/, /spanje/… De root-slugroute staat daarom als laatste en
vangt elke losse segment-URL; vaste routes hierboven hebben voorrang.

Legacy-redirects houden oud verkeer vast:
- /landen/<slug>/  -> /<slug>/        (oude dev-URL's)
- /kennisbank/...   -> /<land>/        (kennisbankartikelen zijn er nu niet; komen terug)
- /blog/jjjj/mm/dd/<slug>/ -> /blog/<slug>/  (oude datum-URL's)
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("planner/", views.planner, name="planner"),
    path("druktekaart/", views.druktekaart, name="druktekaart"),
    path("blog/", views.blog_overzicht, name="blog"),
    path("blog/<int:jaar>/<int:maand>/<int:dag>/<slug:slug>/", views.blog_datum_redirect),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("over-ons/", views.over_ons, name="over_ons"),
    path("samenwerken/", views.samenwerken, name="samenwerken"),
    path("landen/", views.landen_overzicht, name="landen"),
    path("landen/<slug:slug>/", views.land_legacy_redirect),
    path("privacy/", views.privacy, name="privacy"),
    path("cookies/", views.cookies, name="cookies"),
    path("voorwaarden/", views.voorwaarden, name="voorwaarden"),
    path("kennisbank/<path:rest>", views.kennisbank_redirect),
    # Root-level landpagina's — moet als laatste (vangt /<slug>/).
    path("<slug:slug>/", views.land_detail, name="land_detail"),
]
