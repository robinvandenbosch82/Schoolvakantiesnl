# Schoolvakanties.nl

Standalone Django-site — de slimme reisplanner voor gezinnen. Niet zomaar
vakantiedata, maar betekenis bovenop de data: schoolvakanties, feestdagen,
drukte en de slimste reisweken van heel Europa, op één plek.

Zustersites met dezelfde conventies: **vliegtickets.com** (`:8000`),
**cruises.nl** (`:8001`), **bestelautoverzekering** (`:8002`),
**motorverzekering** (`:8003`). Deze site draait op **`:8004`**.

> Het ontwerp komt uit een Claude Design-handoff (v3) en is hier server-side
> gerenderd nagebouwd in Django, met vanilla-JS voor de interactieve tools.

---

## Stack

- **Django 5.1** · Python 3.12 · 100% server-side rendering (SSR).
- **WhiteNoise** voor static files (manifest-hashing in prod).
- **python-dotenv** voor env-gedreven secrets.
- Geen frontend-buildstap: design-CSS in `static/css/` + één `static/js/site.js`
  (vanilla progressive enhancement).
- SQLite in dev; Postgres via `DATABASE_URL` in productie.
- **Databron:** vakantie- & feestdagdata uit de **OpenHolidays API** (idempotente
  import), redactioneel verrijkt in de admin.

## Snel starten

```bash
cd C:\Users\robin\schoolvakanties
pip install -r requirements.txt
copy .env.example .env                       # zet DEBUG=True
python manage.py migrate
python manage.py import_openholidays         # vakantie-/feestdagdata (NL, DE + 23 EU-landen)
python manage.py seed_schoolvakanties        # redactionele data (intro's, weer, bestemmingen, blog, experts, FAQ)
python manage.py sync_pages                  # Page-rij per route
python manage.py createsuperuser
python manage.py runserver 8004
# → http://127.0.0.1:8004/  ·  admin → /admin/
```

## Pagina's (routes)

| Route | Inhoud |
|-------|--------|
| `/` | Homepage: hero + **Reisweek-radar** (Slim-score 0–100) + mini-druktekaart + bestemmingen + SEO-secties |
| `/planner/` | Vakantieplanner: invoer + grote radar + slim-vertrekadvies |
| `/druktekaart/` | Europese druktekaart: kaart + week-slider + land-detail |
| `/landen/` | Overzicht alle Europese landen (live / binnenkort) |
| `/landen/<slug>/` | Landenpagina: schoolvakanties per regio/deelstaat, feestdagen, weer, jaar-switcher |
| `/blog/`, `/blog/<slug>/` | Blogoverzicht + artikel (block-content, TOC, gerelateerd) |
| `/over-ons/` | Redactie / E-E-A-T / werkwijze / bronnen |

## Datamodel & import

De **Django-admin (`/admin/`)** is de bron van waarheid. Domeinmodellen:
`Land`, `Regio` (deelstaat), `Schoolvakantie`, `Feestdag`, `WeerMaand`,
`Bestemming`, `Reisweek` + de generieke CMS-laag (`SiteSettings`, `Page`, `Faq`,
`Review`, `Expert`, `BlogArtikel`, `Kennisbank*`, `ContentPagina`, `MenuItem`,
`SectieTekst`, `Kaart`).

```bash
python manage.py import_openholidays                      # alle EU-landen, 2026 + 2027
python manage.py import_openholidays --countries NL,DE    # selectie
python manage.py import_openholidays --from 2026-01-01 --to 2028-02-01
```

- **Idempotent** — upsert op `external_id` (de OpenHolidays-GUID).
- **Handmatige correcties blijven staan**: zet een rij in de admin op
  `vergrendeld=True`, dan slaat de import die over.
- NL-gemeentedata wordt teruggevouwen naar de regio's Noord/Midden/Zuid; DE naar
  de 16 deelstaten (Nederlandse namen). Franse overzeese gebieden worden verborgen.

## Tests & smoke-test

```bash
python manage.py check                       # Django system check
python manage.py check_pages --verbose       # rendert alle routes, checkt chrome + fouten
```

Draai `check_pages` **na elke template-/view-wijziging** (conform de zustersites).

> **Let op:** bij wijzigingen in `static/js/site.js` de cache-bust-versie
> ophogen (`?v=N` op de script-src in `templates/base.html`) — browsers cachen
> het bestand anders hardnekkig.

## Afbeeldingen & Pexels

`PhotoMixin` (Expert, Review, BlogArtikel, Bestemming, Kennisbank): upload een
foto, plak een externe URL, of zoek via de **Pexels-widget** in de admin. De
responsive `{% picture %}`-pipeline (`core/services/image_pipeline.py`) genereert
WebP/JPEG-varianten. Pexels-sleutel: admin → *Site-instellingen* of `PEXELS_API_KEY`.

## Deploy naar Render (Blueprint)

`render.yaml` zet web (gunicorn) + Postgres + de **wekelijkse OpenHolidays-import
(cron)** in één keer op:

1. **Blueprint koppelen** — Render → *New* → *Blueprint* → kies deze repo.
2. **Secret invullen** — env-group `schoolvakanties-env`: `DJANGO_SUPERUSER_PASSWORD`
   (`sync:false`). `SECRET_KEY` en `DATABASE_URL` vult Render zelf.
3. **Verse host vult automatisch** — `preDeployCommand` draait `migrate` +
   `bootstrap_site` (import + seed + sync_pages + superuser, idempotent en
   deploy-veilig: een API-storing breekt de deploy niet).
4. **Vers blijven** — de cron `openholidays-import` draait wekelijks
   (`manage.py import_openholidays`, ma 04:00 UTC).
5. **Domein** — koppel `schoolvakanties.nl`; `ALLOWED_HOSTS`/`SITE_ORIGIN` staan goed.

> Railway: `railway.json` draait `migrate && bootstrap_site && gunicorn`. Plan de
> import daar als losse scheduled job. Lokaal/eigen server: cron op
> `manage.py import_openholidays`.

## Architectuur-principes

- **SSR-first** voor SEO; interactieve tools (radar, kaart, planner) zijn lichte
  JS-verrijking bovenop server-gerenderde data.
- **Structured data**: `base.html` heeft Organization + WebSite; per pagina komt
  er FAQPage / Article / BreadcrumbList bij (gebouwd in de views).
- **Jaar-switcher**: de landenpagina toont één kalenderjaar (`TOON_JAAR`, default
  2026) zodat vakanties van twee schooljaren niet als duplicaat verschijnen.
- **E-E-A-T**: vaste redactie (experts), bronvermelding, "gecontroleerd door"-balk.
