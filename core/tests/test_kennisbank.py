"""Tests voor de kennisbank: hub, detailpagina (alleen gepubliceerd), schema,
en de redirect-vangnetten."""
from django.test import TestCase
from django.utils import timezone

from core.models import KennisbankArtikel, KennisbankCategorie, Land


class KennisbankTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nl = Land.objects.create(iso_code="NL", naam="Nederland", slug="nederland", actief=True)
        KennisbankCategorie.objects.create(naam="Regels & verlof", order=0,
                                           link="/kennisbank/?categorie=regels-verlof")
        cls.pub = KennisbankArtikel.objects.create(
            kb_id="FAQ-0001", titel="Mag je buiten de schoolvakantie op reis?",
            slug="nederland-verlof", categorie="Regels & verlof", land=cls.nl,
            seo_title="Verlof buiten de schoolvakantie", excerpt="Wanneer mag het wel.",
            body_html="<h2>Wettelijk kader</h2><p>Inhoud.</p>", active=True,
            status="gepubliceerd", gepubliceerd_op=timezone.now(), bron_url="https://example.gov/regels")
        cls.concept = KennisbankArtikel.objects.create(
            kb_id="FAQ-0002", titel="Concept-artikel", slug="nederland-concept",
            categorie="Regels & verlof", land=cls.nl, active=False, status="concept")

    def test_hub_rendert(self):
        r = self.client.get("/kennisbank/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Regels &amp; verlof")          # categorietegel
        self.assertContains(r, "/kennisbank/nederland-verlof/")  # gepubliceerd artikel
        self.assertNotContains(r, "/kennisbank/nederland-concept/")  # concept verborgen

    def test_categorie_filter(self):
        r = self.client.get("/kennisbank/?categorie=regels-verlof")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "nederland-verlof")

    def test_detail_gepubliceerd(self):
        r = self.client.get("/kennisbank/nederland-verlof/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Wettelijk kader")
        self.assertContains(r, '"@type": "Article"')
        self.assertContains(r, '"@type": "BreadcrumbList"')
        self.assertContains(r, "/nederland/")                  # link naar vakantiedata

    def test_concept_niet_zichtbaar(self):
        r = self.client.get("/kennisbank/nederland-concept/")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["Location"], "/kennisbank/")

    def test_oude_meersegment_url_301_naar_land(self):
        r = self.client.get("/kennisbank/nederland/wanneer-zomervakantie/")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["Location"], "/nederland/")

    def test_in_sitemap(self):
        body = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("/kennisbank/nederland-verlof/", body)

    def test_landpagina_toont_kennisbank_blok(self):
        """De landpagina toont een blok met kennisbankartikelen van dát land,
        met een link naar de gefilterde hub. Concepten staan er niet in."""
        r = self.client.get("/nederland/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Verdieping over schoolvakanties in Nederland")
        self.assertContains(r, "/kennisbank/nederland-verlof/")
        self.assertContains(r, "/kennisbank/?land=nederland")
        self.assertNotContains(r, "/kennisbank/nederland-concept/")

    def test_gecombineerde_filter(self):
        """Onderwerp- en landfilter werken samen en behouden elkaar."""
        r = self.client.get("/kennisbank/?categorie=regels-verlof&land=nederland")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "nederland-verlof")
