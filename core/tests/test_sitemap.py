"""Sitemap dekt de echte content (landen + blog + vaste pagina's) op de
canonical host."""
from django.test import TestCase

from core.models import BlogArtikel, Land


class SitemapTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Land.objects.create(iso_code="NL", naam="Nederland", slug="nederland", actief=True)
        Land.objects.create(iso_code="XX", naam="Inactief", slug="inactief", actief=False)
        BlogArtikel.objects.create(titel="T", slug="t-post", active=True, body_html="", excerpt="")
        BlogArtikel.objects.create(titel="Verborgen", slug="verborgen", active=False,
                                   body_html="", excerpt="")

    def test_bevat_land_blog_en_vaste_paginas(self):
        body = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("https://www.schoolvakanties.nl/nederland/", body)
        self.assertIn("https://www.schoolvakanties.nl/blog/t-post/", body)
        self.assertIn("https://www.schoolvakanties.nl/samenwerken/", body)
        self.assertIn("https://www.schoolvakanties.nl/", body)

    def test_sluit_inactieve_uit(self):
        body = self.client.get("/sitemap.xml").content.decode()
        self.assertNotIn("/landen/inactief/", body)
        self.assertNotIn("/blog/verborgen/", body)

    def test_news_sitemap(self):
        """Google News-sitemap: alleen artikelen van de laatste 2 dagen, met
        news-namespace + publication_date + title."""
        import datetime as dt
        from django.utils import timezone
        vers = BlogArtikel.objects.create(
            titel="Vers nieuws", slug="vers-nieuws", active=True, body_html="", excerpt="",
            gepubliceerd_op=timezone.now())
        BlogArtikel.objects.create(
            titel="Oud nieuws", slug="oud-nieuws", active=True, body_html="", excerpt="",
            gepubliceerd_op=timezone.now() - dt.timedelta(days=10))
        resp = self.client.get("/news-sitemap.xml")
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode()
        self.assertIn("http://www.google.com/schemas/sitemap-news/0.9", body)
        self.assertIn("https://www.schoolvakanties.nl/blog/vers-nieuws/", body)
        self.assertIn("<news:title>Vers nieuws</news:title>", body)
        self.assertIn("<news:publication_date>", body)
        self.assertNotIn("/blog/oud-nieuws/", body)        # >2 dagen oud -> eruit
        self.assertNotIn("/blog/t-post/", body)            # geen gepubliceerd_op -> eruit
