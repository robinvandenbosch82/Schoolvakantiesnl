"""
CMS data models for Schoolvakanties.nl.

Design decision (mirrors the sibling sites motorverzekering / bestelauto­
verzekering / cruises.nl): a *structured* CMS where the Django admin is the
source of truth.

- SiteSettings, one editable row of global brand/contact/trust values.
- Page, one row per route (synced from the PAGES registry), holding
                  per-page SEO + hero copy. Makes every page editable in admin.
- Content models, the repeatable/rich content (FAQ, reviews, experts, blog &
                  knowledge-base articles, generic section copy + cards).
- ContentPagina, ready-to-render pages imported from the contentfabriek.

Domain models specific to school holidays (vakanties / regio's / schooljaren /
feestdagen) are added in a later step once the new design is in.

Templates read from these models with a fallback to the seeded defaults, so the
site renders identically before and after editing.
"""

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def _photo_upload_to(instance, filename):
    """Per-model upload subdir, e.g. photos/expert/<file>."""
    return f"photos/{instance._meta.model_name}/{filename}"


class PhotoMixin(models.Model):
    """
    Reusable image block + resolver, ported 1-on-1 from the sibling sites. Lets
    an editor upload a photo, paste an external URL, or pick one via the admin
    Pexels-widget (which fills photo_url/photo_local/credit/pexels_id).
    get_photo_url() resolves the best source: upload > local file > external URL.
    """
    photo_upload = models.ImageField("Foto uploaden", upload_to=_photo_upload_to, blank=True, null=True)
    photo_url = models.URLField("Foto URL (extern)", max_length=500, blank=True)
    photo_local = models.CharField("Foto lokaal pad", max_length=300, blank=True,
                                   help_text="Wordt automatisch ingevuld door de Pexels-widget.")
    photo_credit = models.CharField("Fotocredit", max_length=200, blank=True)
    photo_pexels_id = models.CharField("Pexels foto-ID", max_length=20, blank=True)
    photo_alt = models.CharField("Alt-tekst", max_length=300, blank=True,
                                 help_text="Beschrijf de foto voor SEO en screenreaders.")

    class Meta:
        abstract = True

    def get_photo_url(self):
        if self.photo_upload:
            return self.photo_upload.url
        if self.photo_local:
            return settings.MEDIA_URL + self.photo_local
        return self.photo_url

    def get_photo_source(self):
        """The value to pass to {% picture %}: local path (pipeline) or URL."""
        if self.photo_upload:
            return self.photo_upload.name
        return self.photo_local or self.photo_url

    def get_photo_alt(self):
        return self.photo_alt or self.default_photo_alt()

    def default_photo_alt(self):
        return str(self)


# ── Global settings (singleton) ────────────────────────────────────────────
class SiteSettings(models.Model):
    review_score = models.CharField("Reviewscore", max_length=10, default="9,1")
    review_count = models.CharField("Aantal reviews", max_length=20, default="2.840")

    phone = models.CharField("Telefoon", max_length=40, blank=True, default="085 060 0043")
    show_phone = models.BooleanField("Telefoonnummer tonen", default=True,
                                     help_text="Uit = nergens een telefoonnummer tonen.")
    whatsapp = models.CharField("WhatsApp-nummer", max_length=40, blank=True, default="")
    email = models.EmailField("E-mail", default="partner@travelnerds.nl")

    bedrijfsnaam = models.CharField("Bedrijfsnaam (juridisch)", max_length=160, blank=True, default="",
                                    help_text="Rechtspersoon achter de site, bijv. 'Travel Nerds B.V.'.")
    kvk_nummer = models.CharField("KvK-nummer", max_length=40, blank=True, default="")
    vestigingsnummer = models.CharField("Vestigingsnummer", max_length=40, blank=True, default="")

    footer_blurb = models.TextField(
        "Footer-tekst",
        default="Alle schoolvakanties en feestdagen in Nederland, overzichtelijk per "
                "regio en schooljaar. Onafhankelijk en altijd up-to-date.",
    )

    pexels_api_key = models.CharField(
        "Pexels API-sleutel", max_length=100, blank=True,
        help_text="Gratis via pexels.com/api, heeft voorrang boven PEXELS_API_KEY in .env.")
    default_og_image = models.ImageField(
        "Standaard deelafbeelding (OG)", upload_to="og/", blank=True, null=True,
        help_text="Gebruikt als een pagina zelf geen OG-afbeelding heeft.")

    # ── Structured-data / Knowledge Graph ──
    logo = models.ImageField(
        "Logo (vierkant, ≥112px)", upload_to="brand/", blank=True, null=True,
        help_text="Gebruikt als Organization-logo in de JSON-LD (verplicht voor "
                  "artikel-rich-results) en in het Google Knowledge Panel.")
    sameas = models.TextField(
        "Social-profielen (sameAs)", blank=True,
        help_text="Eén volledige URL per regel: LinkedIn, Facebook, X… "
                  "Verschijnen als sameAs in de Organization-graaf.")
    # Optioneel vestigingsadres, alleen ingevuld weergeven (geen lege PostalAddress).
    adres_straat = models.CharField("Vestiging · straat + nr.", max_length=160, blank=True)
    adres_postcode = models.CharField("Vestiging · postcode", max_length=16, blank=True)
    adres_plaats = models.CharField("Vestiging · plaats", max_length=120, blank=True)

    class Meta:
        verbose_name = "Site-instellingen"
        verbose_name_plural = "Site-instellingen"

    def __str__(self):
        return "Site-instellingen"

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    # Alias used by the ported Pexels service.
    @classmethod
    def get(cls):
        return cls.load()

    @property
    def whatsapp_link(self):
        import re
        digits = re.sub(r"\D", "", self.whatsapp or "")
        return f"https://wa.me/{digits}" if digits else ""

    @property
    def sameas_list(self):
        """Social/profile URLs for the Organization.sameAs array (one per line)."""
        return [u.strip() for u in (self.sameas or "").splitlines() if u.strip().startswith("http")]


# ── Per-page record ─────────────────────────────────────────────────────────
class Page(models.Model):
    key = models.SlugField("Pagina-sleutel", max_length=60, unique=True,
                           help_text="Technische sleutel (= URL-naam). Niet wijzigen.")
    label = models.CharField("Naam", max_length=120)
    path = models.CharField("URL-pad", max_length=200, blank=True,
                            help_text="Alleen ter info, wordt door de routing bepaald.")

    seo_title = models.CharField("SEO-titel", max_length=200, blank=True)
    seo_description = models.TextField("SEO-omschrijving", max_length=320, blank=True)
    og_image = models.ImageField("Deelafbeelding (OG)", upload_to="og/", blank=True)
    noindex = models.BooleanField("Uitsluiten van Google (noindex)", default=False)

    # Optional hero copy overrides (used where the template supports it).
    eyebrow = models.CharField("Bovenkop", max_length=120, blank=True)
    heading = models.CharField("Titel (H1)", max_length=200, blank=True)
    intro = models.TextField("Intro", blank=True)
    body_html = models.TextField("Inhoud (HTML)", blank=True,
                                 help_text="Hoofdtekst voor losse pagina's (privacy, cookies, "
                                           "voorwaarden). HTML toegestaan.")

    # Byline (admin = source of truth; shown on article-style pages). Author/
    # reviewer reference the Expert team so a name change in one place updates
    # every byline. Empty = template fallback.
    author = models.ForeignKey("Expert", verbose_name="Auteur", on_delete=models.SET_NULL,
                               null=True, blank=True, related_name="+")
    reviewer = models.ForeignKey("Expert", verbose_name="Gecontroleerd door", on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name="+")
    byline_date = models.CharField("Datum (weergave)", max_length=40, blank=True,
                                   help_text="bijv. '12 juni 2026'")
    leestijd = models.CharField("Leestijd", max_length=20, blank=True, help_text="bijv. '5 min'")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pagina"
        verbose_name_plural = "Pagina's"
        ordering = ["label"]

    def __str__(self):
        return self.label

    def get_seo_title(self, default=""):
        return self.seo_title or default

    def get_seo_description(self, default=""):
        return self.seo_description or default


# ── Shared / homepage content ───────────────────────────────────────────────
class Faq(models.Model):
    """Veelgestelde vraag. `page_key` groups FAQs per page (e.g. 'home')."""
    page_key = models.SlugField("Pagina", max_length=60, default="home")
    question = models.CharField("Vraag", max_length=255)
    answer = models.TextField("Antwoord")
    order = models.PositiveIntegerField("Volgorde", default=0)
    active = models.BooleanField("Actief", default=True)

    class Meta:
        verbose_name = "FAQ-item"
        verbose_name_plural = "FAQ-items"
        ordering = ["page_key", "order"]

    def __str__(self):
        return self.question


class Review(PhotoMixin):
    name = models.CharField("Naam", max_length=120)
    role = models.CharField("Plaats / functie", max_length=160,
                            help_text="Wordt onder de review getoond, bijv. 'Utrecht'.")
    quote = models.TextField("Review")
    score = models.CharField("Cijfer", max_length=5, blank=True, help_text="bijv. '10' of '9'")
    datum = models.CharField("Datum (weergave)", max_length=40, blank=True, help_text="bijv. '4 juni 2026'")
    order = models.PositiveIntegerField("Volgorde", default=0)
    active = models.BooleanField("Actief", default=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["order"]

    def __str__(self):
        return f"{self.name}, {self.role}"

    def default_photo_alt(self):
        return f"Foto van {self.name}, {self.role}"


class Expert(PhotoMixin):
    name = models.CharField("Naam", max_length=120)
    slug = models.SlugField("Slug", max_length=140, unique=True, blank=True,
                            help_text="Voor het Person-@id in de JSON-LD. Leeg = automatisch uit de naam.")
    role = models.CharField("Functie", max_length=160)
    kort = models.CharField("Korte functie", max_length=60, blank=True,
                            help_text="bijv. 'Hoofdredacteur' (compacte weergave).")
    mono = models.CharField("Initialen", max_length=6, blank=True,
                            help_text="Mono-label, bijv. 'SdV'.")
    sinds = models.PositiveIntegerField("Werkzaam sinds (jaar)", null=True, blank=True)
    bio = models.TextField("Bio")
    credentials = models.TextField("Credentials", blank=True,
                                   help_text="Eén per regel, bijv. '14 jaar reisredactie'.")
    tags = models.CharField("Focus / tags", max_length=255, blank=True,
                            help_text="Komma-gescheiden, bijv. 'Redactie, Slim plannen'.")
    sameas = models.TextField("Profielen (sameAs)", blank=True,
                              help_text="Eén URL per regel (LinkedIn enz.) voor de Person-entiteit / E-E-A-T.")
    order = models.PositiveIntegerField("Volgorde", default=0)
    active = models.BooleanField("Actief", default=True)

    class Meta:
        verbose_name = "Expert"
        verbose_name_plural = "Experts"
        ordering = ["order"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "expert"
            slug, n = base, 2
            while Expert.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def tags_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    @property
    def credentials_list(self):
        return [c.strip() for c in (self.credentials or "").splitlines() if c.strip()]

    @property
    def sameas_list(self):
        return [u.strip() for u in (self.sameas or "").splitlines() if u.strip().startswith("http")]

    def person_id(self, origin=""):
        """Stable @id for this expert's Person entity (defined on /over-ons/)."""
        return f"{origin}/over-ons/#person-{self.slug}"

    def default_photo_alt(self):
        return f"{self.name}, {self.role} bij {settings.SITE_NAME}"


# ── Blog & knowledge base ───────────────────────────────────────────────────
class BlogArtikel(PhotoMixin):
    titel = models.CharField("Titel", max_length=200)
    slug = models.SlugField("Slug", max_length=220, unique=True, blank=True)
    categorie = models.CharField("Categorie", max_length=80, blank=True)
    leestijd = models.CharField("Leestijd", max_length=20, blank=True, help_text="bijv. '5 min'")
    datum = models.CharField("Datum (weergave)", max_length=40, blank=True)
    gepubliceerd_op = models.DateTimeField("Gepubliceerd op", null=True, blank=True,
                                           help_text="Echte publicatiedatum (voor de Google "
                                                     "News-sitemap). Leeg = niet in news-sitemap.")
    author = models.ForeignKey("Expert", verbose_name="Auteur", on_delete=models.SET_NULL,
                               null=True, blank=True, related_name="+")
    reviewer = models.ForeignKey("Expert", verbose_name="Gecontroleerd door", on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name="+",
                                 help_text="Toont de 'Gecontroleerd door … · bijgewerkt' regel in de byline.")
    excerpt = models.TextField("Samenvatting", blank=True)
    body_html = models.TextField("Inhoud (HTML)", blank=True)
    toc = models.JSONField("Inhoudsopgave", default=list, blank=True)
    landen = models.ManyToManyField("Land", verbose_name="Gekoppelde landen", blank=True,
                                    related_name="blogartikelen",
                                    help_text="Toon dit artikel in het blogblok op deze landenpagina's.")
    featured = models.BooleanField("Uitgelicht", default=False)
    order = models.PositiveIntegerField("Volgorde", default=0)
    active = models.BooleanField("Actief", default=True)

    class Meta:
        verbose_name = "Blogartikel"
        verbose_name_plural = "Blogartikelen"
        ordering = ["order"]

    def __str__(self):
        return self.titel

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titel)[:220]
        super().save(*args, **kwargs)

    def default_photo_alt(self):
        return self.titel


class KennisbankCategorie(models.Model):
    ICON_CHOICES = [
        ("square", "Vierkant (lijn)"), ("square-fill", "Vierkant (vol)"),
        ("triangle", "Driehoek"), ("pill", "Pil"), ("diamond", "Ruit"),
        ("bars", "Strepen"), ("ring", "Ring"),
    ]
    naam = models.CharField("Categorie", max_length=120)
    aantal = models.CharField("Aantal (weergave)", max_length=40, blank=True,
                              help_text="bijv. '214 artikelen'")
    icon = models.CharField("Icoon", max_length=20, choices=ICON_CHOICES, default="square")
    link = models.CharField("Link (pad of URL)", max_length=200, blank=True,
                            help_text="Waar de tegel naartoe gaat. Leeg = naar de kennisbank.")
    order = models.PositiveIntegerField("Volgorde", default=0)

    class Meta:
        verbose_name = "Kennisbank-categorie"
        verbose_name_plural = "Kennisbank-categorieën"
        ordering = ["order"]

    def __str__(self):
        return self.naam


class KennisbankArtikel(PhotoMixin):
    titel = models.CharField("Titel", max_length=200)
    slug = models.SlugField("Slug", max_length=220, unique=True, blank=True)
    categorie = models.CharField("Categorie", max_length=80, blank=True)
    excerpt = models.TextField("Samenvatting", blank=True)
    leestijd = models.CharField("Leestijd", max_length=20, blank=True, help_text="bijv. '4 min'")
    gelezen = models.CharField("Aantal keer gelezen", max_length=20, blank=True, help_text="bijv. '12.4k'")
    featured = models.BooleanField("Uitgelicht", default=False)
    order = models.PositiveIntegerField("Volgorde", default=0)
    active = models.BooleanField("Actief", default=True)

    class Meta:
        verbose_name = "Kennisbank-artikel"
        verbose_name_plural = "Kennisbank-artikelen"
        ordering = ["order"]

    def __str__(self):
        return self.titel

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titel)[:220]
        super().save(*args, **kwargs)

    def default_photo_alt(self):
        return self.titel


# ── Content-fabriek pages (imported from content-systeem CSV) ───────────────
class ContentPagina(models.Model):
    """
    A content page imported from the content-systeem (contentfabriek) WP-import
    CSV. Holds ready-to-render HTML (intro/body/faq/conclusie/cta/internal links)
    plus SEO metadata, image and JSON-LD. Served by a catch-all route on `slug`.
    """
    slug = models.SlugField("Slug (pad)", max_length=255, unique=True, allow_unicode=False,
                            help_text="Pad zonder voor-/achter-slash, bv. zomervakantie/noord-2026")
    contenttype = models.CharField("Contenttype", max_length=40, blank=True)
    titel = models.CharField("Titel", max_length=300)
    focus_keyword = models.CharField("Focus-keyword", max_length=200, blank=True)
    zoekintentie = models.CharField("Zoekintentie", max_length=40, blank=True)

    meta_title = models.CharField("SEO-titel", max_length=300, blank=True)
    meta_description = models.TextField("SEO-omschrijving", blank=True)

    image_url = models.URLField("Afbeelding-URL", max_length=600, blank=True)
    image_local = models.CharField("Afbeelding lokaal pad", max_length=300, blank=True,
                                   help_text="Wordt gevuld door download_content_images; "
                                             "voert de {% picture %}-pipeline (WebP/JPEG).")
    image_alt = models.CharField("Afbeelding alt", max_length=400, blank=True)
    image_credit = models.CharField("Fotocredit", max_length=300, blank=True)
    image_credit_url = models.URLField("Fotocredit-URL", max_length=600, blank=True)

    intro_html = models.TextField("Intro (HTML)", blank=True)
    body_html = models.TextField("Body (HTML)", blank=True)
    faq_html = models.TextField("FAQ (HTML)", blank=True)
    conclusie_html = models.TextField("Conclusie (HTML)", blank=True)
    cta_html = models.TextField("CTA (HTML)", blank=True)
    interne_links_html = models.TextField("Interne links (HTML)", blank=True)

    toc = models.JSONField("Inhoudsopgave", default=list, blank=True)
    schema_jsonld = models.TextField("Schema JSON-LD", blank=True)
    bronnen = models.TextField("Bronnen", blank=True)

    gate_status = models.CharField("Gate-status", max_length=20, blank=True)
    published = models.BooleanField("Gepubliceerd", default=True)
    imported_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Content-pagina"
        verbose_name_plural = "Content-pagina's"
        ordering = ["contenttype", "slug"]
        indexes = [models.Index(fields=["contenttype"])]

    def __str__(self):
        return self.titel

    def get_absolute_url(self):
        return f"/{self.slug}/"

    def get_image_source(self):
        """Value for {% picture %}: the locally-downloaded path (optimised via the
        pipeline) when available, otherwise the original external URL."""
        return self.image_local or self.image_url

    def get_seo_title(self):
        return self.meta_title or self.titel

    def get_seo_description(self):
        return self.meta_description

    @property
    def excerpt(self):
        """Plain-text teaser from the intro (for hub/overview cards)."""
        import re
        text = re.sub(r"<[^>]+>", "", self.intro_html or "")
        text = re.sub(r"\s+", " ", text).strip()
        return (text[:150].rsplit(" ", 1)[0] + "…") if len(text) > 150 else text

    @property
    def tagline(self):
        """Short one-liner for compact cards (first ~70 chars of the intro)."""
        text = self.excerpt
        return (text[:70].rsplit(" ", 1)[0] + "…") if len(text) > 72 else text

    @property
    def korte_titel(self):
        """Display name derived from the slug's last segment."""
        seg = self.slug.rsplit("/", 1)[-1]
        seg = seg.replace("-", " ").strip()
        return seg.title() if seg else self.titel


# ── Admin-editable menus (main nav + footer) ────────────────────────────────
class MenuItem(models.Model):
    """One navigation/footer entry. Top-level rows (parent empty) are the nav
    items / footer columns; their children are the dropdown links / column
    links. Read by core.context_processors (with a hardcoded fallback)."""

    MENU_CHOICES = [("nav", "Hoofdmenu (bovenbalk)"), ("footer", "Footer")]

    menu = models.CharField("Menu", max_length=10, choices=MENU_CHOICES, default="nav")
    parent = models.ForeignKey("self", verbose_name="Valt onder", null=True, blank=True,
                               on_delete=models.CASCADE, related_name="children")
    label = models.CharField("Label", max_length=80)
    url = models.CharField("Link (pad of URL)", max_length=200, blank=True,
                           help_text="bijv. '/zomervakantie/'. Leeg = alleen kop "
                                     "(footer-kolom of dropdown-groep zonder eigen link).")
    order = models.PositiveIntegerField("Volgorde", default=0)
    active = models.BooleanField("Actief", default=True)

    class Meta:
        verbose_name = "Menu-item"
        verbose_name_plural = "Menu's (nav + footer)"
        ordering = ["menu", "order", "id"]

    def __str__(self):
        return f"[{self.get_menu_display()}] {'↳ ' if self.parent_id else ''}{self.label}"

    def save(self, *args, **kwargs):
        if self.parent_id:  # children always live in the same menu as their parent
            self.menu = self.parent.menu
        super().save(*args, **kwargs)


# ── Generic editable content: section copy + repeatable cards ───────────────
# Two friendly, label-driven models that make every remaining hardcoded bit of
# template copy editable in the admin. The choice-lists below are intentionally
# minimal placeholders; they are expanded per the new design once it lands.
PAGINA_CHOICES = [
    ("home", "Homepage"),
    ("over_ons", "Over ons"),
    ("samenwerken", "Samenwerken"),
    ("planner", "Vakantieplanner"),
    ("druktekaart", "Druktekaart"),
]


class SectieTekst(models.Model):
    """One block of section copy on a page (eyebrow + heading + text + optional
    CTA). Keyed by (pagina, sleutel). The hero of each page uses the Page model's
    eyebrow/heading/intro; everything else uses this."""

    pagina = models.CharField("Pagina", max_length=40, choices=PAGINA_CHOICES)
    sleutel = models.SlugField("Sectie-sleutel", max_length=60,
                               help_text="Technische naam binnen de pagina, bv. 'waarom', 'cta'.")
    naam = models.CharField("Omschrijving", max_length=160, blank=True,
                            help_text="Alleen ter herkenning in de admin.")
    eyebrow = models.CharField("Bovenkop (eyebrow)", max_length=120, blank=True)
    kop = models.CharField("Kop", max_length=255, blank=True)
    tekst = models.TextField("Tekst", blank=True,
                             help_text="Mag meerdere alinea's bevatten (gescheiden door een lege regel).")
    cta_label = models.CharField("Knop-tekst", max_length=120, blank=True)
    cta_url = models.CharField("Knop-link (pad of URL)", max_length=200, blank=True)
    order = models.PositiveIntegerField("Volgorde", default=0)

    class Meta:
        verbose_name = "Sectietekst"
        verbose_name_plural = "Sectieteksten"
        unique_together = [("pagina", "sleutel")]
        ordering = ["pagina", "order", "sleutel"]

    def __str__(self):
        return f"{self.get_pagina_display()}, {self.naam or self.sleutel}"

    @property
    def alineas(self):
        """Tekst split into paragraphs on blank lines (for templates)."""
        import re
        return [p.strip() for p in re.split(r"\n\s*\n", self.tekst or "") if p.strip()]


class Kaart(models.Model):
    """A repeatable card / list item, grouped by `blok`. One model covers every
    homepage/marketing list so the admin stays compact but labelled. The choice-
    list is a minimal placeholder, expanded per the new design once it lands."""

    BLOK_CHOICES = [
        ("home_waarom", "Home, Waarom-kaarten"),
        ("home_stappen", "Home, In drie stappen"),
    ]

    blok = models.CharField("Blok", max_length=50, choices=BLOK_CHOICES)
    volgorde = models.PositiveIntegerField("Volgorde", default=0)
    tag = models.CharField("Tag/label", max_length=40, blank=True,
                           help_text="Klein mono-label of nummer, bv. '01'.")
    titel = models.CharField("Titel", max_length=200, blank=True)
    tekst = models.TextField("Tekst", blank=True)
    meta = models.CharField("Subtekst / meta", max_length=200, blank=True)
    url = models.CharField("Link (pad of URL)", max_length=200, blank=True)
    actief = models.BooleanField("Actief", default=True)

    class Meta:
        verbose_name = "Kaart / lijst-item"
        verbose_name_plural = "Kaarten & lijst-items"
        ordering = ["blok", "volgorde"]

    def __str__(self):
        return f"{self.get_blok_display()}, {self.titel or self.tag or self.meta}"


# ════════════════════════════════════════════════════════════════════════════
# DOMEIN: schoolvakanties, feestdagen, landen & reisplanner-data
# ════════════════════════════════════════════════════════════════════════════
# Vakantie- en feestdagdata worden automatisch geïmporteerd uit de OpenHolidays
# API (manage.py import_openholidays, idempotent op external_id). Redactie kan
# in uitzonderingsgevallen handmatig corrigeren: zet dan `vergrendeld=True`, dan
# slaat de import die rij over. Editorial velden (intro, weer, bestemmingen,
# reisweken) worden NOOIT door de import aangeraakt.

BRON_CHOICES = [
    ("api", "OpenHolidays API"),
    ("rijksoverheid", "Rijksoverheid.nl (NL)"),
    ("edu-fr", "Éducation nationale (FR)"),
    ("ferien-de", "ferien-api.de (DE)"),
    ("nager", "Nager.Date"),
    ("handmatig", "Handmatig"),
]


class Land(models.Model):
    """Een land met schoolvakanties (OpenHolidays-country) + redactionele duiding."""
    iso_code = models.CharField("ISO-landcode", max_length=2, unique=True,
                                help_text="Hoofdletters, bv. NL, DE (OpenHolidays countryIsoCode).")
    slug = models.SlugField("Slug", max_length=80, unique=True, blank=True)
    naam = models.CharField("Naam", max_length=80)
    vlag = models.CharField("Vlag (emoji)", max_length=8, blank=True)

    # Redactioneel (handmatig, blijft bij import behouden)
    intro = models.TextField("Intro", blank=True)
    regio_info = models.TextField("Regio-uitleg (algemeen)", blank=True)
    studiedagen_uitleg = models.TextField("Studiedagen, uitleg", blank=True)
    weer_bron = models.CharField("Weer, bron", max_length=160, blank=True)
    weer_beste = models.CharField("Weer, beste periode", max_length=255, blank=True)
    bron = models.CharField("Databron-vermelding", max_length=300, blank=True)
    bijgewerkt = models.CharField("Bijgewerkt (weergave)", max_length=40, blank=True,
                                  help_text="bijv. 'mei 2026'.")

    order = models.PositiveIntegerField("Volgorde", default=0)
    actief = models.BooleanField("Actief", default=True)
    imported_at = models.DateTimeField("Laatst geïmporteerd", null=True, blank=True)

    class Meta:
        verbose_name = "Land"
        verbose_name_plural = "Landen"
        ordering = ["order", "naam"]

    def __str__(self):
        return f"{self.vlag} {self.naam}".strip()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.naam) or self.iso_code.lower()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/{self.slug}/"


class Regio(models.Model):
    """Een deel-regio van een land: NL Noord/Midden/Zuid of een Duitse deelstaat
    (OpenHolidays-subdivision)."""
    land = models.ForeignKey(Land, verbose_name="Land", on_delete=models.CASCADE,
                             related_name="regios")
    code = models.CharField("Subdivision-code", max_length=20, unique=True,
                            help_text="OpenHolidays-code, bv. DE-BY of NL-NoordNederland.")
    naam = models.CharField("Naam", max_length=120)
    korte_naam = models.CharField("Korte naam", max_length=60, blank=True)
    uitleg = models.TextField("Uitleg / dekking", blank=True,
                              help_text="Welke provincies/gebieden vallen eronder (redactioneel).")
    order = models.PositiveIntegerField("Volgorde", default=0)

    class Meta:
        verbose_name = "Regio / deelstaat"
        verbose_name_plural = "Regio's & deelstaten"
        ordering = ["land", "order", "naam"]

    def __str__(self):
        return f"{self.naam} ({self.land.iso_code})"


class Schoolvakantie(models.Model):
    """Eén schoolvakantie-periode (OpenHolidays SchoolHoliday-entry). Eén rij per
    voorkomen; landelijke vakanties hebben geen regio's, regionale wél."""
    external_id = models.CharField("OpenHolidays-ID", max_length=64, unique=True, blank=True,
                                   help_text="GUID uit de API. Leeg bij handmatige rijen.")
    land = models.ForeignKey(Land, verbose_name="Land", on_delete=models.CASCADE,
                             related_name="schoolvakanties")
    naam = models.CharField("Naam", max_length=160)
    type = models.CharField("Type", max_length=40, blank=True)
    start_datum = models.DateField("Startdatum")
    eind_datum = models.DateField("Einddatum")
    landelijk = models.BooleanField("Landelijk (alle regio's)", default=False)
    regios = models.ManyToManyField(Regio, verbose_name="Regio's", blank=True,
                                    related_name="schoolvakanties")
    comment = models.CharField("Toelichting (API)", max_length=300, blank=True)

    # Redactioneel
    alias = models.CharField("Alias", max_length=120, blank=True,
                             help_text="bijv. 'Krokus- / carnavalsvakantie'.")
    status = models.CharField("Status", max_length=80, blank=True,
                              help_text="bijv. 'Wettelijk verplicht' of 'Adviesdata'.")
    note = models.CharField("Redactionele noot", max_length=400, blank=True)

    bron = models.CharField("Bron", max_length=16, choices=BRON_CHOICES, default="api")
    vergrendeld = models.BooleanField("Vergrendeld (import overslaan)", default=False,
                                      help_text="Aan = handmatige correctie; de import laat deze rij met rust.")
    imported_at = models.DateTimeField("Laatst geïmporteerd", null=True, blank=True)

    class Meta:
        verbose_name = "Schoolvakantie"
        verbose_name_plural = "Schoolvakanties"
        ordering = ["land", "start_datum"]
        indexes = [models.Index(fields=["land", "start_datum"])]

    def __str__(self):
        return f"{self.naam}, {self.land.iso_code} ({self.start_datum:%d-%m-%Y})"


class Feestdag(models.Model):
    """Een feestdag. Officiële dagen komen uit OpenHolidays (PublicHoliday);
    officieuze dagen (Sinterklaas, Halloween…) worden handmatig toegevoegd."""
    CATEGORIE_CHOICES = [
        ("officieel", "Officieel (vrije dag)"),
        ("officieus", "Officieus / themadag"),
    ]
    external_id = models.CharField("OpenHolidays-ID", max_length=64, unique=True, blank=True, null=True,
                                   help_text="GUID uit de API. Leeg bij handmatige rijen.")
    land = models.ForeignKey(Land, verbose_name="Land", on_delete=models.CASCADE,
                             related_name="feestdagen")
    naam = models.CharField("Naam", max_length=160)
    categorie = models.CharField("Categorie", max_length=12, choices=CATEGORIE_CHOICES, default="officieel")
    start_datum = models.DateField("Datum")
    eind_datum = models.DateField("Einddatum", null=True, blank=True,
                                  help_text="Alleen invullen als de dag meerdere dagen beslaat.")
    type = models.CharField("Type (API)", max_length=40, blank=True)
    landelijk = models.BooleanField("Landelijk", default=True)
    regios = models.ManyToManyField(Regio, verbose_name="Regio's", blank=True,
                                    related_name="feestdagen")
    emoji = models.CharField("Emoji", max_length=8, blank=True)
    comment = models.CharField("Toelichting", max_length=300, blank=True)

    bron = models.CharField("Bron", max_length=16, choices=BRON_CHOICES, default="api")
    vergrendeld = models.BooleanField("Vergrendeld (import overslaan)", default=False)
    imported_at = models.DateTimeField("Laatst geïmporteerd", null=True, blank=True)

    class Meta:
        verbose_name = "Feestdag"
        verbose_name_plural = "Feestdagen"
        ordering = ["land", "start_datum"]
        indexes = [models.Index(fields=["land", "categorie", "start_datum"])]

    def __str__(self):
        return f"{self.naam}, {self.land.iso_code} ({self.start_datum:%d-%m})"


class WeerMaand(models.Model):
    """Langjarig klimaatgemiddelde per maand voor een land (redactioneel)."""
    MAAND_CHOICES = [(i, m) for i, m in enumerate(
        ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"], start=1)]
    land = models.ForeignKey(Land, verbose_name="Land", on_delete=models.CASCADE,
                             related_name="weermaanden")
    maand = models.PositiveSmallIntegerField("Maand", choices=MAAND_CHOICES)
    temp = models.DecimalField("Temperatuur (°C)", max_digits=4, decimal_places=1)
    zon = models.DecimalField("Zon (uren/dag)", max_digits=4, decimal_places=1)
    regen = models.DecimalField("Regendagen", max_digits=4, decimal_places=1)

    class Meta:
        verbose_name = "Weer, maand"
        verbose_name_plural = "Weer (per maand)"
        ordering = ["land", "maand"]
        unique_together = [("land", "maand")]

    def __str__(self):
        return f"{self.land.iso_code}, {self.get_maand_display()}"


class Bestemming(PhotoMixin):
    """Een warme bestemmings-card: foto-eerst, met Slim- en gezinsscore."""
    naam = models.CharField("Naam", max_length=120)
    slug = models.SlugField("Slug", max_length=140, unique=True, blank=True)
    land = models.ForeignKey(Land, verbose_name="Land (gekoppeld)", on_delete=models.SET_NULL,
                             null=True, blank=True, related_name="bestemmingen")
    land_naam = models.CharField("Land (weergave)", max_length=80, blank=True,
                                 help_text="Vrije tekst, bv. 'Portugal' als er geen landpagina is.")
    slim_score = models.PositiveSmallIntegerField("Slim-score (0–100)", default=0)
    gezin_score = models.PositiveSmallIntegerField("Gezinsscore (0–100)", default=0)
    tag = models.CharField("Tag", max_length=60, blank=True, help_text="bijv. 'Rustig in september'.")
    beste_week = models.CharField("Beste week", max_length=40, blank=True, help_text="bijv. 'wk 37 · 7 sep'.")
    order = models.PositiveIntegerField("Volgorde", default=0)
    actief = models.BooleanField("Actief", default=True)

    class Meta:
        verbose_name = "Bestemming"
        verbose_name_plural = "Bestemmingen"
        ordering = ["order", "naam"]

    def __str__(self):
        return self.naam

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.naam)[:140]
        super().save(*args, **kwargs)

    def default_photo_alt(self):
        return f"{self.naam}{', ' + self.land_naam if self.land_naam else ''}"


class Reisweek(models.Model):
    """Eén week in de Reisweek-radar. De Slim-score wordt berekend uit drukte,
    prijs, weer en overlap (gewogen, hoog = slim om te gaan)."""
    jaar = models.PositiveSmallIntegerField("Jaar", default=2026)
    weeknr = models.PositiveSmallIntegerField("Weeknummer")
    start_label = models.CharField("Startdatum (weergave)", max_length=20, help_text="bijv. '7 sep'.")
    drukte = models.PositiveSmallIntegerField("Drukte (0–100, hoog = druk)")
    prijs = models.PositiveSmallIntegerField("Prijsindex (0–100, hoog = duur)")
    weer = models.PositiveSmallIntegerField("Weer (0–100, hoog = mooi)")
    overlap = models.PositiveSmallIntegerField("Overlap (0–100, hoog = veel landen vrij)")
    order = models.PositiveIntegerField("Volgorde", default=0)

    class Meta:
        verbose_name = "Reisweek"
        verbose_name_plural = "Reisweken (radar)"
        ordering = ["jaar", "weeknr"]
        unique_together = [("jaar", "weeknr")]

    def __str__(self):
        return f"{self.jaar} · wk {self.weeknr}, slim {self.slim_score}"

    @property
    def slim_score(self):
        return round(
            (100 - self.drukte) * 0.34
            + (100 - self.prijs) * 0.30
            + self.weer * 0.22
            + (100 - self.overlap) * 0.14
        )

    @property
    def band(self):
        s = self.slim_score
        if s >= 70:
            return "rustig"
        if s >= 45:
            return "matig"
        return "druk"


class Samenwerkingsaanvraag(models.Model):
    """Een lead uit het samenwerken-formulier. Elke aanvraag wordt opgeslagen
    (zodat er nooit één verloren gaat als de e-mail faalt) en best-effort
    doorgemaild naar de partner-inbox."""
    naam = models.CharField("Naam", max_length=120)
    bedrijf = models.CharField("Bedrijf", max_length=160, blank=True)
    email = models.EmailField("E-mail", max_length=254)
    soort = models.CharField("Type samenwerking", max_length=80, blank=True)
    bericht = models.TextField("Bericht")
    ip = models.GenericIPAddressField("IP-adres", null=True, blank=True)
    verwerkt = models.BooleanField("Verwerkt", default=False)
    aangemaakt = models.DateTimeField("Ontvangen", auto_now_add=True)

    class Meta:
        verbose_name = "Samenwerkingsaanvraag"
        verbose_name_plural = "Samenwerkingsaanvragen"
        ordering = ["-aangemaakt"]
        indexes = [models.Index(fields=["-aangemaakt"])]

    def __str__(self):
        return f"{self.naam}, {self.aangemaakt:%d-%m-%Y}"
