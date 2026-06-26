"""
XML-sitemap voor Google Search Console.

Drie secties, allemaal gepind op de canonical productie-host (SITE_ORIGIN) + https,
zodat de URL's identiek zijn aan de on-page rel=canonical, ongeacht hoe de sitemap
wordt opgehaald (www/non-www/dev-host):

  * static, de vaste pagina's (home, landen, planner, druktekaart, blog,
             over-ons, samenwerken).
  * landen, elke actieve Land (/landen/<slug>/), met <lastmod> = laatste import.
  * blog, elk gepubliceerd BlogArtikel (/blog/<slug>/).

Bereikbaar op /sitemap.xml en geadverteerd in robots.txt.
"""
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


def _site_lastmod():
    """Meest recente site-brede update: laatste data-import of Page-bewerking.
    Voor de hub-/toolpagina's die geen eigen contentdatum hebben."""
    from .models import Land, Page
    kandidaten = [Land.objects.order_by("-imported_at")
                  .values_list("imported_at", flat=True).first(),
                  Page.objects.order_by("-updated_at")
                  .values_list("updated_at", flat=True).first()]
    kandidaten = [d for d in kandidaten if d]
    return max(kandidaten) if kandidaten else None


class _CanonicalSitemap(Sitemap):
    """Basis die elke URL pint op SITE_ORIGIN's host + https i.p.v. de request-host.
    Houdt de sitemap-URL's gelijk aan de on-page rel=canonical."""
    protocol = "https"

    def get_urls(self, page=1, site=None, protocol=None):
        host = urlparse(settings.SITE_ORIGIN).netloc

        class _Site:
            domain = host
            name = host

        return super().get_urls(page=page, site=_Site(), protocol=self.protocol)


class StaticViewSitemap(_CanonicalSitemap):
    """De vaste, niet-data-gedreven pagina's. (url-naam, priority, changefreq)."""
    ROUTES = [
        ("home", 1.0, "weekly"),
        ("landen", 0.9, "weekly"),
        ("planner", 0.8, "weekly"),
        ("druktekaart", 0.8, "weekly"),
        ("kennisbank", 0.7, "weekly"),
        ("blog", 0.7, "weekly"),
        ("over_ons", 0.4, "monthly"),
        ("samenwerken", 0.4, "monthly"),
    ]

    def items(self):
        return self.ROUTES

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]

    def lastmod(self, item):
        # Hub-/toolpagina's aggregeren site-brede data; gebruik de meest recente
        # site-update (laatste data-import of Page-bewerking) als versdatum.
        return _site_lastmod()


class LandSitemap(_CanonicalSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        from .models import Land
        return list(Land.objects.filter(actief=True).order_by("order", "naam"))

    def location(self, land):
        return reverse("land_detail", kwargs={"slug": land.slug})

    def lastmod(self, land):
        return land.imported_at


class BlogSitemap(_CanonicalSitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        from .models import BlogArtikel
        return list(BlogArtikel.objects.filter(active=True).order_by("-order"))

    def location(self, post):
        return reverse("blog_detail", kwargs={"slug": post.slug})

    def lastmod(self, post):
        return post.gepubliceerd_op or _site_lastmod()


class KennisbankSitemap(_CanonicalSitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        from .models import KennisbankArtikel
        return list(KennisbankArtikel.objects.filter(active=True).order_by("order"))

    def location(self, art):
        return reverse("kennisbank_detail", kwargs={"slug": art.slug})

    def lastmod(self, art):
        return art.gepubliceerd_op or _site_lastmod()


SITEMAPS = {
    "static": StaticViewSitemap,
    "landen": LandSitemap,
    "kennisbank": KennisbankSitemap,
    "blog": BlogSitemap,
}
