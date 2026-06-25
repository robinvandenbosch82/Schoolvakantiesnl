"""
Django admin for the Schoolvakanties.nl CMS.

Goal: every page is visible and per-page content is editable here. Pages are
synced from the routing registry (see `sync_pages`), so the page list always
matches the live site; editors fill in SEO + copy, and manage the shared
content models (FAQ, reviews, experts, blog & knowledge-base articles, generic
section copy + cards, imported content pages, menus).
"""

from django.contrib import admin

from .admin_mixins import PexelsPhotoMixin
from .models import (
    Bestemming,
    BlogArtikel,
    ContentPagina,
    Expert,
    Faq,
    Feestdag,
    Kaart,
    KennisbankArtikel,
    KennisbankCategorie,
    Land,
    MenuItem,
    Page,
    Plaats,
    Regio,
    Reisweek,
    Review,
    Samenwerkingsaanvraag,
    Schoolvakantie,
    SectieTekst,
    SiteSettings,
    WeerMaand,
    Widget,
    WidgetPagina,
)

admin.site.site_header = "Schoolvakanties.nl, beheer"
admin.site.site_title = "Schoolvakanties.nl"
admin.site.index_title = "Content & instellingen"


@admin.register(SectieTekst)
class SectieTekstAdmin(admin.ModelAdmin):
    list_display = ("naam", "pagina", "sleutel", "kop", "order")
    list_filter = ("pagina",)
    list_editable = ("order",)
    search_fields = ("naam", "sleutel", "kop", "tekst")
    fields = ("pagina", "sleutel", "naam", "order", "eyebrow", "kop", "tekst",
              "cta_label", "cta_url")


@admin.register(Kaart)
class KaartAdmin(admin.ModelAdmin):
    list_display = ("blok", "volgorde", "tag", "titel", "meta", "actief")
    list_filter = ("blok", "actief")
    list_editable = ("volgorde", "actief")
    search_fields = ("titel", "tekst", "meta", "tag")
    fields = ("blok", "volgorde", "actief", "tag", "titel", "tekst", "meta", "url")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Vertrouwen & cijfers", {"fields": ("review_score", "review_count")}),
        ("Contact", {"fields": ("phone", "show_phone", "whatsapp", "email")}),
        ("Bedrijfsgegevens", {"fields": ("kvk_nummer",)}),
        ("Vestigingsadres (optioneel, voor LocalBusiness-schema)",
         {"fields": ("adres_straat", "adres_postcode", "adres_plaats"),
          "classes": ("collapse",)}),
        ("Footer", {"fields": ("footer_blurb",)}),
        ("Merk & structured data (logo + social)",
         {"fields": ("logo", "sameas", "default_og_image")}),
        ("Integraties", {"fields": ("pexels_api_key",)}),
    )

    def has_add_permission(self, request):
        # Singleton: only one row allowed.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("label", "key", "path", "noindex", "updated_at")
    list_filter = ("noindex",)
    search_fields = ("label", "key", "seo_title", "seo_description")
    readonly_fields = ("key", "path", "updated_at")
    fieldsets = (
        (None, {"fields": ("label", "key", "path", "updated_at")}),
        ("SEO", {"fields": ("seo_title", "seo_description", "og_image", "noindex")}),
        ("Hero / introtekst (waar de pagina dit ondersteunt)",
         {"fields": ("eyebrow", "heading", "intro")}),
        ("Inhoud (losse pagina's: privacy, cookies, voorwaarden)",
         {"fields": ("body_html",)}),
        ("Byline (voor artikel-pagina's)",
         {"fields": ("author", "reviewer", "byline_date", "leestijd"),
          "classes": ("collapse",)}),
    )
    autocomplete_fields = ("author", "reviewer")

    def has_add_permission(self, request):
        # Pages are created by the sync_pages command, not by hand.
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ("question", "page_key", "order", "active")
    list_filter = ("page_key", "active")
    list_editable = ("order", "active")
    search_fields = ("question", "answer")


@admin.register(Review)
class ReviewAdmin(PexelsPhotoMixin, admin.ModelAdmin):
    list_display = ("name", "role", "order", "active")
    list_editable = ("order", "active")
    search_fields = ("name", "role", "quote")
    readonly_fields = ("pexels_widget",)
    pexels_download_subdir = "photos/reviews"
    pexels_filename_prefix = "review"


@admin.register(Expert)
class ExpertAdmin(PexelsPhotoMixin, admin.ModelAdmin):
    list_display = ("name", "role", "order", "active")
    list_editable = ("order", "active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "role", "bio")
    readonly_fields = ("pexels_widget",)
    pexels_download_subdir = "photos/experts"
    pexels_filename_prefix = "expert"
    fieldsets = (
        (None, {"fields": ("name", "slug", "role", "kort", "mono", "sinds", "order", "active")}),
        ("Bio & E-E-A-T", {"fields": ("bio", "credentials", "tags", "sameas")}),
        ("Foto", {"classes": ("collapse",),
                  "fields": ("pexels_widget", "photo_upload", "photo_url", "photo_local",
                             "photo_credit", "photo_pexels_id", "photo_alt")}),
    )


@admin.register(BlogArtikel)
class BlogArtikelAdmin(PexelsPhotoMixin, admin.ModelAdmin):
    list_display = ("titel", "categorie", "author", "reviewer", "datum", "gepubliceerd_op",
                    "featured", "order", "active")
    list_editable = ("featured", "order", "active")
    prepopulated_fields = {"slug": ("titel",)}
    search_fields = ("titel", "excerpt")
    autocomplete_fields = ("author", "reviewer")
    filter_horizontal = ("landen",)
    list_filter = ("categorie", "featured", "active", "landen")
    readonly_fields = ("pexels_widget",)
    pexels_download_subdir = "photos/blog"
    pexels_filename_prefix = "blog"


@admin.register(ContentPagina)
class ContentPaginaAdmin(admin.ModelAdmin):
    list_display = ("titel", "contenttype", "slug", "published", "imported_at")
    list_filter = ("contenttype", "published", "gate_status")
    list_editable = ("published",)
    search_fields = ("titel", "slug", "focus_keyword", "meta_description")
    readonly_fields = ("imported_at",)
    fieldsets = (
        (None, {"fields": ("titel", "slug", "contenttype", "published", "imported_at")}),
        ("SEO", {"fields": ("meta_title", "meta_description", "focus_keyword", "zoekintentie")}),
        ("Afbeelding", {"fields": ("image_url", "image_alt", "image_credit", "image_credit_url")}),
        ("Inhoud (HTML)", {"fields": ("intro_html", "body_html", "faq_html", "conclusie_html",
                                      "cta_html", "interne_links_html")}),
        ("Geavanceerd", {"classes": ("collapse",),
                         "fields": ("toc", "schema_jsonld", "bronnen", "gate_status")}),
    )


@admin.register(KennisbankCategorie)
class KennisbankCategorieAdmin(admin.ModelAdmin):
    list_display = ("naam", "aantal", "link", "order")
    list_editable = ("aantal", "link", "order")


@admin.register(KennisbankArtikel)
class KennisbankArtikelAdmin(PexelsPhotoMixin, admin.ModelAdmin):
    list_display = ("titel", "categorie", "order", "active")
    list_editable = ("order", "active")
    prepopulated_fields = {"slug": ("titel",)}
    search_fields = ("titel", "excerpt")
    readonly_fields = ("pexels_widget",)
    pexels_download_subdir = "photos/kennisbank"
    pexels_filename_prefix = "kb"


class MenuChildInline(admin.TabularInline):
    model = MenuItem
    fk_name = "parent"
    extra = 1
    fields = ("label", "url", "order", "active")
    verbose_name = "Sub-item / link"
    verbose_name_plural = "Sub-items / links onder dit item"


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("label", "menu", "parent", "url", "order", "active")
    list_filter = ("menu", "active")
    list_editable = ("url", "order", "active")
    search_fields = ("label", "url")
    inlines = [MenuChildInline]

    def get_queryset(self, request):
        # Show only top-level rows in the list; children are managed inline.
        return super().get_queryset(request).filter(parent__isnull=True)


# ── Domein: schoolvakanties / feestdagen / landen / reisplanner ──────────────
class RegioInline(admin.TabularInline):
    model = Regio
    extra = 0
    fields = ("naam", "code", "korte_naam", "uitleg", "order")


class WeerMaandInline(admin.TabularInline):
    model = WeerMaand
    extra = 0
    fields = ("maand", "temp", "zon", "regen")
    ordering = ("maand",)


@admin.register(Land)
class LandAdmin(admin.ModelAdmin):
    list_display = ("__str__", "iso_code", "order", "actief", "imported_at")
    list_editable = ("order", "actief")
    prepopulated_fields = {"slug": ("naam",)}
    search_fields = ("naam", "iso_code")
    readonly_fields = ("imported_at",)
    inlines = [RegioInline, WeerMaandInline]
    fieldsets = (
        (None, {"fields": ("naam", "iso_code", "slug", "vlag", "order", "actief", "imported_at")}),
        ("Redactionele duiding", {"fields": ("intro", "regio_info", "studiedagen_uitleg")}),
        ("Weer", {"fields": ("weer_bron", "weer_beste")}),
        ("Bronvermelding", {"fields": ("bron", "bijgewerkt")}),
    )


@admin.register(Regio)
class RegioAdmin(admin.ModelAdmin):
    list_display = ("naam", "land", "code", "korte_naam", "order")
    list_filter = ("land",)
    list_editable = ("order",)
    search_fields = ("naam", "code", "korte_naam")


@admin.register(Plaats)
class PlaatsAdmin(admin.ModelAdmin):
    list_display = ("naam", "land", "regio")
    list_filter = ("land", "regio")
    list_editable = ("regio",)
    search_fields = ("naam", "regio")
    list_select_related = ("land",)


class WidgetPaginaInline(admin.TabularInline):
    model = WidgetPagina
    extra = 0
    readonly_fields = ("status", "backlink_ok", "fail_count", "laatst_gecheckt",
                       "laatst_ok", "grace_mail_op", "aangemaakt")
    fields = ("url",) + readonly_fields


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ("domein", "land", "site_key", "email", "actief", "aangemaakt")
    list_filter = ("actief", "land")
    search_fields = ("domein", "site_key", "email")
    readonly_fields = ("site_key", "aangemaakt")
    list_select_related = ("land",)
    inlines = [WidgetPaginaInline]


@admin.register(WidgetPagina)
class WidgetPaginaAdmin(admin.ModelAdmin):
    list_display = ("url", "widget", "status", "backlink_ok", "fail_count", "laatst_gecheckt")
    list_filter = ("status", "backlink_ok")
    search_fields = ("url", "widget__domein")
    list_select_related = ("widget", "widget__land")
    readonly_fields = ("laatst_gecheckt", "laatst_ok", "grace_mail_op", "aangemaakt")


@admin.register(Schoolvakantie)
class SchoolvakantieAdmin(admin.ModelAdmin):
    list_display = ("naam", "land", "start_datum", "eind_datum", "landelijk",
                    "bron", "vergrendeld")
    list_filter = ("land", "type", "bron", "vergrendeld", "landelijk")
    list_editable = ("vergrendeld",)
    search_fields = ("naam", "alias", "comment")
    filter_horizontal = ("regios",)
    date_hierarchy = "start_datum"
    readonly_fields = ("external_id", "imported_at")
    fieldsets = (
        (None, {"fields": ("land", "naam", "type", "start_datum", "eind_datum",
                           "landelijk", "regios", "comment")}),
        ("Redactioneel (blijft bij import behouden)",
         {"fields": ("alias", "status", "note")}),
        ("Herkomst", {"fields": ("bron", "vergrendeld", "external_id", "imported_at")}),
    )


@admin.register(Feestdag)
class FeestdagAdmin(admin.ModelAdmin):
    list_display = ("naam", "land", "categorie", "start_datum", "landelijk",
                    "emoji", "bron", "vergrendeld")
    list_filter = ("land", "categorie", "bron", "vergrendeld", "landelijk")
    list_editable = ("vergrendeld",)
    search_fields = ("naam", "comment")
    filter_horizontal = ("regios",)
    date_hierarchy = "start_datum"
    readonly_fields = ("external_id", "imported_at")
    fieldsets = (
        (None, {"fields": ("land", "naam", "categorie", "start_datum", "eind_datum",
                           "type", "landelijk", "regios", "emoji", "comment")}),
        ("Herkomst", {"fields": ("bron", "vergrendeld", "external_id", "imported_at")}),
    )


@admin.register(WeerMaand)
class WeerMaandAdmin(admin.ModelAdmin):
    list_display = ("land", "maand", "temp", "zon", "regen")
    list_filter = ("land",)
    ordering = ("land", "maand")


@admin.register(Bestemming)
class BestemmingAdmin(PexelsPhotoMixin, admin.ModelAdmin):
    list_display = ("naam", "land_naam", "slim_score", "gezin_score", "tag", "order", "actief")
    list_editable = ("slim_score", "gezin_score", "order", "actief")
    prepopulated_fields = {"slug": ("naam",)}
    search_fields = ("naam", "land_naam", "tag")
    readonly_fields = ("pexels_widget",)
    pexels_download_subdir = "photos/bestemmingen"
    pexels_filename_prefix = "bestemming"
    fieldsets = (
        (None, {"fields": ("naam", "slug", "land", "land_naam", "tag", "beste_week",
                           "slim_score", "gezin_score", "order", "actief")}),
        ("Foto", {"fields": ("pexels_widget", "photo_upload", "photo_url", "photo_local",
                             "photo_credit", "photo_pexels_id", "photo_alt")}),
    )


@admin.register(Reisweek)
class ReisweekAdmin(admin.ModelAdmin):
    list_display = ("weeknr", "jaar", "start_label", "drukte", "prijs", "weer",
                    "overlap", "slim_score", "band")
    list_filter = ("jaar",)
    list_editable = ("drukte", "prijs", "weer", "overlap")
    ordering = ("jaar", "weeknr")

    @admin.display(description="Slim-score")
    def slim_score(self, obj):
        return obj.slim_score

    @admin.display(description="Band")
    def band(self, obj):
        return obj.band


@admin.register(Samenwerkingsaanvraag)
class SamenwerkingsaanvraagAdmin(admin.ModelAdmin):
    list_display = ("aangemaakt", "naam", "bedrijf", "soort", "email", "verwerkt")
    list_filter = ("verwerkt", "soort", "aangemaakt")
    list_editable = ("verwerkt",)
    search_fields = ("naam", "bedrijf", "email", "bericht")
    date_hierarchy = "aangemaakt"
    # Inkomende leads zijn read-only data; alleen 'verwerkt' is een werkstatus.
    readonly_fields = ("naam", "bedrijf", "email", "soort", "bericht", "ip", "aangemaakt")
