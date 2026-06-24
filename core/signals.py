"""
Image post-processing on upload (ported pattern from the sibling sites).

When a content object with a PhotoMixin is saved with a freshly uploaded photo:
  1. sync photo_local to the uploaded file's path (so get_photo_url/source and
     the {% picture %} pipeline use it),
  2. compress the original in place if it's very large,
  3. pre-warm the responsive WebP/JPEG variants so the first page render is fast.

All steps are best-effort and never block a save. The `.update()` write avoids
triggering this signal recursively.
"""

import logging

from django.db.models.signals import post_save

from core.services.image_pipeline import compress_if_needed, get_variant_urls

logger = logging.getLogger(__name__)


def _models():
    """Models carrying a PhotoMixin, resolved lazily to avoid import cycles."""
    from core.models import (
        BlogArtikel, Expert, KennisbankArtikel, Review,
    )
    return [BlogArtikel, Expert, KennisbankArtikel, Review]


def _process_photo(instance):
    upload = getattr(instance, "photo_upload", None)
    if not upload:
        return
    rel = upload.name
    if getattr(instance, "photo_local", "") != rel:
        type(instance).objects.filter(pk=instance.pk).update(photo_local=rel)
        instance.photo_local = rel
    try:
        compress_if_needed(upload.path)
    except Exception as exc:  # noqa: BLE001, never block a save on imaging
        logger.warning("compress_if_needed failed for %s: %s", rel, exc)
    try:
        get_variant_urls(rel)
    except Exception as exc:  # noqa: BLE001
        logger.warning("variant pre-warm failed for %s: %s", rel, exc)


def _on_save(sender, instance, **kwargs):
    _process_photo(instance)


def _clear_menu_cache(*args, **kwargs):
    from django.core.cache import cache

    from core.context_processors import FOOTER_CACHE_KEY, NAV_CACHE_KEY
    cache.delete_many([NAV_CACHE_KEY, FOOTER_CACHE_KEY])


def _clear_page_cache(*args, **kwargs):
    """Leeg de volledige (page-)cache zodat een admin-edit meteen zichtbaar is.
    LocMemCache.clear() is goedkoop; pagina's renderen daarna opnieuw."""
    from django.core.cache import cache
    cache.clear()


def _editorial_models():
    """Admin-bewerkte modellen waarvan een wijziging de page-cache moet legen.
    Import-gestuurde bulkdata (Schoolvakantie/Feestdag/…) niet — die leunt op de
    TTL, anders leegt elke geïmporteerde rij de cache duizenden keren."""
    from core.models import (
        Bestemming, BlogArtikel, Expert, Faq, Land, Page, Regio, Review,
        SectieTekst, SiteSettings,
    )
    return [Bestemming, BlogArtikel, Expert, Faq, Land, Page, Regio, Review,
            SectieTekst, SiteSettings]


def register():
    from django.db.models.signals import post_delete

    for model in _models():
        post_save.connect(_on_save, sender=model, dispatch_uid=f"photo_{model.__name__}")

    # Invalidate the cached nav/footer whenever a menu item changes.
    from core.models import MenuItem
    post_save.connect(_clear_menu_cache, sender=MenuItem, dispatch_uid="menu_cache_save")
    post_delete.connect(_clear_menu_cache, sender=MenuItem, dispatch_uid="menu_cache_delete")

    # Leeg de page-cache zodra redactionele content wijzigt (directe weergave).
    for model in _editorial_models():
        post_save.connect(_clear_page_cache, sender=model, dispatch_uid=f"pgc_save_{model.__name__}")
        post_delete.connect(_clear_page_cache, sender=model, dispatch_uid=f"pgc_del_{model.__name__}")
