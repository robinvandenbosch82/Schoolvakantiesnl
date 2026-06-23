"""Smoke-/render-tests voor alle publieke routes (200 + basis-chrome), plus de
landen-edge-cases (live / binnenkort / onbekend)."""
from django.test import TestCase

from core.models import BlogArtikel, Land, Reisweek


def _seed_weeks():
    for i, wk in enumerate(range(19, 39)):
        Reisweek.objects.create(jaar=2026, weeknr=wk, start_label=f"{wk} wk",
                                drukte=40 + (i % 30), prijs=45, weer=60, overlap=30, order=i)


class PageRenderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        _seed_weeks()
        Land.objects.create(iso_code="NL", naam="Nederland", slug="nederland", actief=True,
                            weer_beste="Mei, juni en september: zacht en relatief droog.")
        BlogArtikel.objects.create(titel="Testpost", slug="testpost", active=True,
                                   body_html="<p>Hoi</p>", excerpt="Korte intro")

    def assertChrome(self, resp):
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'class="topbar"')
        self.assertContains(resp, "<title>")

    def test_home(self):
        self.assertChrome(self.client.get("/"))

    def test_landen_overzicht(self):
        self.assertChrome(self.client.get("/landen/"))

    def test_planner(self):
        self.assertChrome(self.client.get("/planner/"))

    def test_druktekaart(self):
        self.assertChrome(self.client.get("/druktekaart/"))

    def test_blog_overzicht(self):
        self.assertChrome(self.client.get("/blog/"))

    def test_blog_detail(self):
        self.assertChrome(self.client.get("/blog/testpost/"))

    def test_over_ons(self):
        self.assertChrome(self.client.get("/over-ons/"))

    def test_samenwerken(self):
        self.assertChrome(self.client.get("/samenwerken/"))

    def test_land_live(self):
        self.assertChrome(self.client.get("/landen/nederland/"))

    def test_land_seo(self):
        """Landpagina: keyword-H1, kerngegevens-tabel en verrijkte JSON-LD
        (WebPage + BreadcrumbList + FAQPage uit de afgeleide FAQ)."""
        resp = self.client.get("/landen/nederland/")
        self.assertContains(resp, "<h1>Schoolvakanties Nederland 2026</h1>")
        self.assertContains(resp, 'class="kern-tabel"')
        self.assertContains(resp, '"@type": "WebPage"')
        self.assertContains(resp, '"@type": "BreadcrumbList"')
        # Zonder admin-FAQ levert de afgeleide FAQ (o.a. beste reistijd) tóch een
        # zichtbare FAQ-sectie + FAQPage-schema.
        self.assertContains(resp, '"@type": "FAQPage"')
        self.assertContains(resp, "Vragen over schoolvakanties in Nederland")

    def test_land_binnenkort(self):
        # 'duitsland' staat in de landenlijst maar niet als actief Land in de test-DB
        # -> nette binnenkort-pagina (200), geen 404.
        resp = self.client.get("/landen/duitsland/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Binnenkort")

    def test_land_onbekend_404(self):
        self.assertEqual(self.client.get("/landen/atlantis/").status_code, 404)

    def test_robots_txt(self):
        resp = self.client.get("/robots.txt")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Sitemap:")

    def test_sitemap_xml(self):
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)

    def test_security_headers(self):
        resp = self.client.get("/")
        self.assertIn("Content-Security-Policy", resp.headers)
        self.assertIn("Permissions-Policy", resp.headers)
