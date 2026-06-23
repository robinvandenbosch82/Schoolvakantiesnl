"""
Site-wide template context.

Single source of truth for navigation, footer columns and per-request SEO
defaults. The menus are admin-editable (core.models.MenuItem); when no menu
rows exist yet, we fall back to the hardcoded structure below so the site
always renders. Templates use plain `{{ item.url }}` links (not {% url %}),
so both the DB rows and the resolved fallback share one shape.
"""

from django.conf import settings
from django.core.cache import cache
from django.urls import NoReverseMatch, reverse

from .europe import europe_list
from .models import SiteSettings

# Menus change rarely but are read on every request; cache the built structures
# and invalidate them on MenuItem save/delete (see core.signals). The TTL is a
# safety net for multi-process setups where a signal only clears one worker.
NAV_CACHE_KEY = "menu_nav_v1"
FOOTER_CACHE_KEY = "menu_footer_v1"
MENU_CACHE_TTL = 3600

# ── Hardcoded fallback (used only until the menus are seeded/edited) ─────────
# Empty for now: the new design defines the nav/footer structure, and editors
# manage the live menus via the admin (core.models.MenuItem). Until a menu row
# exists the site simply renders no nav/footer links.
_NAV_FALLBACK = []
_FOOTER_FALLBACK = []


def _resolve(entry):
    """Resolve a fallback entry to a plain URL string. Supports {url_name} or
    {path}; returns '' when there's no destination (a header-only group)."""
    if entry.get("path"):
        return entry["path"]
    name = entry.get("url_name")
    if not name:
        return ""
    try:
        return reverse(name)
    except NoReverseMatch:
        return ""


def _fallback_nav():
    return [{"label": it["label"], "url": _resolve(it),
             "children": [{"label": c["label"], "url": _resolve(c)} for c in it["children"]]}
            for it in _NAV_FALLBACK]


def _fallback_footer():
    return [{"title": col["title"],
             "links": [{"label": ln["label"], "url": _resolve(ln)} for ln in col["links"]]}
            for col in _FOOTER_FALLBACK]


def _nav_from_db():
    cached = cache.get(NAV_CACHE_KEY)
    if cached is not None:
        return cached
    from .models import MenuItem
    tops = (MenuItem.objects.filter(menu="nav", active=True, parent__isnull=True)
            .prefetch_related("children"))
    nav = []
    for t in tops:
        children = [{"label": c.label, "url": c.url} for c in t.children.all() if c.active]
        nav.append({"label": t.label, "url": t.url, "children": children})
    cache.set(NAV_CACHE_KEY, nav, MENU_CACHE_TTL)
    return nav


def _footer_from_db():
    cached = cache.get(FOOTER_CACHE_KEY)
    if cached is not None:
        return cached
    from .models import MenuItem
    tops = (MenuItem.objects.filter(menu="footer", active=True, parent__isnull=True)
            .prefetch_related("children"))
    cols = []
    for t in tops:
        links = [{"label": c.label, "url": c.url} for c in t.children.all() if c.active]
        cols.append({"title": t.label, "links": links})
    cache.set(FOOTER_CACHE_KEY, cols, MENU_CACHE_TTL)
    return cols


def _org_jsonld(site, origin, name):
    """Bouw de Organization + WebSite @graph uit de site-instellingen, zodat
    legalName, adres en KvK/vestigingsnummer in de Knowledge Graph komen."""
    import json

    org = {"@type": "Organization", "@id": f"{origin}/#organization",
           "name": name, "url": f"{origin}/"}
    if getattr(site, "bedrijfsnaam", ""):
        org["legalName"] = site.bedrijfsnaam
    try:
        if site.logo:
            org["logo"] = origin + site.logo.url
    except Exception:  # geen logo / media niet beschikbaar
        pass
    sameas = [u.strip() for u in (site.sameas or "").splitlines()
              if u.strip().startswith("http")]
    if sameas:
        org["sameAs"] = sameas
    if site.adres_plaats:
        org["address"] = {
            "@type": "PostalAddress",
            "streetAddress": site.adres_straat,
            "postalCode": site.adres_postcode,
            "addressLocality": site.adres_plaats,
            "addressCountry": "NL",
        }
    ids = []
    if site.kvk_nummer:
        ids.append({"@type": "PropertyValue", "propertyID": "KvK", "value": site.kvk_nummer})
    if getattr(site, "vestigingsnummer", ""):
        ids.append({"@type": "PropertyValue", "propertyID": "Vestigingsnummer",
                    "value": site.vestigingsnummer})
    if ids:
        org["identifier"] = ids

    website = {"@type": "WebSite", "@id": f"{origin}/#website", "name": name,
               "url": f"{origin}/", "publisher": {"@id": f"{origin}/#organization"},
               "inLanguage": "nl-NL"}
    return json.dumps({"@context": "https://schema.org", "@graph": [org, website]},
                      ensure_ascii=False)


def site_context(request):
    """Inject brand defaults, navigation, SiteSettings and a canonical URL."""
    try:
        site = SiteSettings.load()
    except Exception:  # DB not migrated yet (e.g. first run), fall back gracefully
        site = SiteSettings()

    try:
        nav_items = _nav_from_db() or _fallback_nav()
        footer_columns = _footer_from_db() or _fallback_footer()
    except Exception:
        nav_items, footer_columns = _fallback_nav(), _fallback_footer()

    # Stable, host-independent origin for structured-data @id's and canonical
    # URLs. In dev this points at the production domain on purpose: a canonical
    # URL should always be the production one, and @id's must be identical on
    # every page so Google can reconcile the entity graph.
    site_origin = settings.SITE_ORIGIN
    canonical_url = site_origin + request.path

    # Europa-landen voor de header (mega-menu) + footer. `live` = land staat in
    # de DB, dus toont al echte vakantiedata.
    try:
        from .models import Land
        live_codes = list(Land.objects.filter(actief=True).values_list("iso_code", flat=True))
    except Exception:  # DB nog niet gemigreerd
        live_codes = []
    europe = europe_list(live_codes)

    return {
        "site_name": settings.SITE_NAME,
        "site_domain": settings.SITE_DOMAIN,
        "site_origin": site_origin,
        "default_seo_title": settings.DEFAULT_SEO_TITLE,
        "default_seo_description": settings.DEFAULT_SEO_DESCRIPTION,
        "nav_items": nav_items,
        "footer_columns": footer_columns,
        "site": site,
        "review_score": site.review_score,
        "review_count": site.review_count,
        "canonical_url": canonical_url,
        "europe": europe,
        "europe_popular": [c for c in europe if c["pop"]],
        "org_jsonld": _org_jsonld(site, site_origin, settings.SITE_NAME),
    }
