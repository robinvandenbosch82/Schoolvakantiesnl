"""Smoke-/render-tests voor alle publieke routes (200 + basis-chrome), plus de
landen-edge-cases (live / binnenkort / onbekend)."""
from django.test import TestCase

from core.models import BlogArtikel, Land, Plaats, Regio, Reisweek


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
        nl = Land.objects.get(iso_code="NL")
        # NL-regio's (kolommen waarop de zoeker highlight) + plaatsen over 3 regio's,
        # zodat de zoeker-gate (≥3 regio's) aanslaat.
        for i, naam in enumerate(["Noord", "Midden", "Zuid"]):
            Regio.objects.create(land=nl, code=f"NL-{naam[:1]}", naam=naam, order=i)
        Plaats.objects.create(land=nl, naam="Amsterdam", regio="Noord")
        Plaats.objects.create(land=nl, naam="Utrecht", regio="Midden")
        Plaats.objects.create(land=nl, naam="Eindhoven", regio="Zuid")

    def setUp(self):
        from django.core.cache import cache
        cache.clear()  # page-cache niet tussen tests laten lekken

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
        self.assertChrome(self.client.get("/nederland/"))

    def test_land_legacy_redirect(self):
        # Oude dev-URL /landen/<slug>/ -> 301 root /<slug>/.
        resp = self.client.get("/landen/nederland/")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp.headers["Location"], "/nederland/")

    def test_kennisbank_redirect(self):
        # Kennisbankartikelen bestaan nu niet -> 301 naar de landhome.
        resp = self.client.get("/kennisbank/nederland/wanneer-zomervakantie/")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp.headers["Location"], "/nederland/")

    def test_land_seo(self):
        """Landpagina: keyword-H1, kerngegevens-tabel en verrijkte JSON-LD
        (WebPage + BreadcrumbList + FAQPage uit de afgeleide FAQ)."""
        resp = self.client.get("/nederland/")
        self.assertContains(resp, "<h1>Schoolvakanties Nederland 2026</h1>")
        self.assertContains(resp, 'class="kern-tabel"')
        self.assertContains(resp, '"@type": "WebPage"')
        self.assertContains(resp, '"@type": "BreadcrumbList"')
        # Zonder admin-FAQ levert de afgeleide FAQ (o.a. beste reistijd) tóch een
        # zichtbare FAQ-sectie + FAQPage-schema.
        self.assertContains(resp, '"@type": "FAQPage"')
        self.assertContains(resp, "Vragen over schoolvakanties in Nederland")

    def test_nl_plaats_zoeker(self):
        """NL-pagina: de plaats→regio-zoeker rendert (zoekveld + JSON-payload met
        de plaatsen). De regio-kolommen dragen data-regio voor de highlight."""
        resp = self.client.get("/nederland/")
        self.assertContains(resp, 'data-plaats-zoek')
        self.assertContains(resp, 'id="plaatsen-data"')
        self.assertContains(resp, '"n": "Eindhoven"')
        self.assertContains(resp, '"r": "Zuid"')
        self.assertContains(resp, 'data-regio="Noord"')

    def test_plaats_zoeker_generiek_land(self):
        """Niet-NL land met plaatsniveau-data over ≥3 regio's: de zoeker
        verschijnt ook daar, met data-regio op de off-chips voor de highlight.
        Bij <3 regio's blijft de zoeker weg."""
        cz = Land.objects.create(iso_code="CZ", naam="Tsjechië", slug="tsjechie", actief=True)
        for code, naam in [("CZ-JC", "Zuid-Bohemen"), ("CZ-JM", "Zuid-Moravië"),
                           ("CZ-ST", "Midden-Bohemen")]:
            Regio.objects.create(land=cz, code=code, naam=naam)
            Plaats.objects.create(land=cz, naam=f"Stad-{code}", regio=naam)
        resp = self.client.get("/tsjechie/")
        self.assertContains(resp, 'data-plaats-zoek')
        self.assertContains(resp, 'id="plaatsen-data"')
        self.assertContains(resp, 'data-regio="Zuid-Bohemen"')

        # Eén regio te weinig -> geen zoeker.
        Land.objects.create(iso_code="IT", naam="Italië", slug="italie", actief=True,
                            )  # zonder Plaats-rijen
        resp_it = self.client.get("/italie/")
        self.assertNotContains(resp_it, 'data-plaats-zoek')

    def test_heading_order(self):
        """Elke pagina heeft precies één h1 en slaat geen heading-niveau over
        (a11y / SEO). Beschermt tegen regressies in de heading-hiërarchie."""
        import re
        routes = ["/", "/planner/", "/druktekaart/", "/blog/", "/over-ons/",
                  "/samenwerken/", "/landen/", "/nederland/", "/blog/testpost/"]
        for r in routes:
            html = self.client.get(r).content.decode()
            levels = [int(m.group(1)) for m in re.finditer(r"<h([1-6])\b", html)]
            self.assertEqual(levels.count(1), 1, f"{r}: verwacht precies één h1, kreeg {levels.count(1)}")
            prev = 0
            for lv in levels:
                if prev:
                    self.assertLessEqual(lv, prev + 1, f"{r}: heading-sprong h{prev}->h{lv} in {levels}")
                prev = lv

    def test_land_binnenkort(self):
        # 'duitsland' staat in de landenlijst maar niet als actief Land in de test-DB
        # -> nette binnenkort-pagina (200) op root, geen 404.
        resp = self.client.get("/duitsland/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Binnenkort")

    def test_land_onbekend_404(self):
        self.assertEqual(self.client.get("/atlantis/").status_code, 404)

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
