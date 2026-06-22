"""WordPress-blogimport: parset een mini-WXR-fixture (geen netwerk) en is idempotent."""
import os
import tempfile

from django.core.management import call_command
from django.test import TestCase

from core.models import BlogArtikel

WXR = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:wp="http://wordpress.org/export/1.2/"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/">
<channel>
  <item>
    <title>Mijn testpost</title>
    <content:encoded><![CDATA[<p>Hallo <a href="https://x.nl">link</a></p>]]></content:encoded>
    <wp:post_name>mijn-testpost</wp:post_name>
    <wp:post_type>post</wp:post_type>
    <wp:status>publish</wp:status>
    <wp:post_date>2026-05-01 10:00:00</wp:post_date>
    <category domain="category" nicename="reistips">Reistips</category>
  </item>
  <item>
    <title>Concept</title>
    <content:encoded><![CDATA[<p>x</p>]]></content:encoded>
    <wp:post_name>concept</wp:post_name>
    <wp:post_type>post</wp:post_type>
    <wp:status>draft</wp:status>
    <wp:post_date>2026-05-02 10:00:00</wp:post_date>
  </item>
</channel></rss>"""


class WpBlogImportTests(TestCase):
    def _run(self):
        with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False, encoding="utf-8") as fh:
            fh.write(WXR)
            path = fh.name
        try:
            call_command("import_wp_blog", file=path)
        finally:
            os.unlink(path)

    def test_parst_gepubliceerde_post(self):
        self._run()
        post = BlogArtikel.objects.get(slug="mijn-testpost")
        self.assertEqual(post.titel, "Mijn testpost")
        self.assertIn("link", post.body_html)       # links blijven behouden
        self.assertEqual(post.categorie, "Reistips")
        self.assertTrue(post.active)

    def test_slaat_concepten_over(self):
        self._run()
        self.assertFalse(BlogArtikel.objects.filter(slug="concept").exists())

    def test_idempotent(self):
        self._run()
        self._run()
        self.assertEqual(BlogArtikel.objects.filter(slug="mijn-testpost").count(), 1)
