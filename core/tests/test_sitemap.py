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
        self.assertIn("https://schoolvakanties.nl/nederland/", body)
        self.assertIn("https://schoolvakanties.nl/blog/t-post/", body)
        self.assertIn("https://schoolvakanties.nl/samenwerken/", body)
        self.assertIn("https://schoolvakanties.nl/", body)

    def test_sluit_inactieve_uit(self):
        body = self.client.get("/sitemap.xml").content.decode()
        self.assertNotIn("/landen/inactief/", body)
        self.assertNotIn("/blog/verborgen/", body)
