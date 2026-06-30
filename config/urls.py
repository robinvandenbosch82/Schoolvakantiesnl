"""Root URL configuration for Schoolvakanties.nl."""

from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.static import serve as _serve_static

from core.sitemaps import SITEMAPS
from core.views import llms_txt, news_sitemap


def media_serve(request, path, document_root=None):
    """Serve a media file + set a Cache-Control header (Django's static serve
    sets none, which shows up in Lighthouse as 'Cache-TTL: None'). Variants under
    /media/cache/ are immutable (the width is baked into the filename), so they
    get a far-future cache; originals can change, so they get a shorter TTL."""
    response = _serve_static(request, path, document_root=document_root)
    if path.startswith("cache/"):
        response["Cache-Control"] = "public, max-age=31536000, immutable"
    else:
        response["Cache-Control"] = "public, max-age=604800"
    return response


# AI-zoekmachines/-crawlers die we expliciet welkom heten (GEO: zonder fetch geen
# citatie). De allowlist is een positief signaal voor bots die per-UA regels lezen;
# commerciële scrapers (Bright Data/Oxylabs) negeren robots sowieso, dus de echte
# poort is de WAF/Cloudflare-config, niet dit bestand.
AI_USER_AGENTS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User",      # OpenAI / ChatGPT
    "ClaudeBot", "anthropic-ai", "Claude-Web",        # Anthropic
    "PerplexityBot", "Perplexity-User",               # Perplexity
    "Google-Extended",                                 # Google (Gemini/AI Overviews opt-in)
    "Applebot-Extended",                               # Apple Intelligence
    "CCBot",                                           # Common Crawl (voedt training)
]


def robots_txt(request):
    # Advertise the sitemap on the canonical origin (host-independent), keep
    # crawlers uit de admin, en sta AI-bots expliciet toe.
    origin = settings.SITE_ORIGIN
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "",
        "# AI-zoekmachines en -crawlers expliciet toegestaan",
    ]
    for ua in AI_USER_AGENTS:
        lines += [f"User-agent: {ua}", "Allow: /", ""]
    lines += [
        f"Sitemap: {origin}/sitemap.xml",
        f"Sitemap: {origin}/news-sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS},
         name="django.contrib.sitemaps.views.sitemap"),
    path("news-sitemap.xml", news_sitemap, name="news_sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("llms.txt", llms_txt, name="llms_txt"),
]

# Serve uploaded/generated media directly from Django, in dev AND production —
# BEFORE the core catch-all so /media/ is never shadowed by the content-page
# route. WhiteNoise only serves /static/, and the image pipeline writes WebP/JPEG
# variants to disk at runtime, so serving must be dynamic (per-request disk read)
# rather than a startup scan. On a single instance with a persistent volume this
# is fine; front it with object storage + a CDN if traffic ever warrants it.
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", media_serve, {"document_root": settings.MEDIA_ROOT}),
]

urlpatterns += [path("", include("core.urls"))]
