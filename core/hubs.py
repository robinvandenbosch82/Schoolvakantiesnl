"""
Content hubs: per-content-type overview pages that list imported ContentPagina
items by slug-prefix. Single source of truth, add a hub here and it gets a
route (core.urls), a nav entry (context_processors), and a sitemap entry.

Backbone stub: empty until the new design defines the hub structure (e.g. per
regio / per schooljaar). Keep it a list (never None) so iteration is always safe.
"""

HUBS: list[dict] = []
