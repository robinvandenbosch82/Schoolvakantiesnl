"""Core URL patterns.

De homepage is gebouwd; landenpagina's, planner, druktekaart, blog en over-ons
volgen in latere fasen (die routes geven nu nog 404). De PAGES-registry in
views.py voedt de sitemap + de admin-bewerkbare Page-rijen (sync_pages)."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("planner/", views.planner, name="planner"),
    path("druktekaart/", views.druktekaart, name="druktekaart"),
    path("blog/", views.blog_overzicht, name="blog"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("over-ons/", views.over_ons, name="over_ons"),
    path("samenwerken/", views.samenwerken, name="samenwerken"),
    path("landen/", views.landen_overzicht, name="landen"),
    path("landen/<slug:slug>/", views.land_detail, name="land_detail"),
    path("privacy/", views.privacy, name="privacy"),
    path("cookies/", views.cookies, name="cookies"),
    path("voorwaarden/", views.voorwaarden, name="voorwaarden"),
]
