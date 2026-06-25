"""Tests voor de embeddable partner-widget: data-endpoint (full/teaser + Origin-
gate), self-service generator en de backlink-controle."""
import datetime as dt
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from core.management.commands.check_backlinks import Command as CheckCmd
from core.models import Land, Schoolvakantie, Widget, WidgetPagina


def _seed_land():
    land = Land.objects.create(iso_code="DE", naam="Duitsland", slug="duitsland", actief=True)
    jaar = timezone.localdate().year
    Schoolvakantie.objects.create(land=land, naam="Zomervakantie", external_id="t-zomer",
                                  start_datum=dt.date(jaar, 7, 20), eind_datum=dt.date(jaar, 9, 1))
    Schoolvakantie.objects.create(land=land, naam="Herfstvakantie", external_id="t-herfst",
                                  start_datum=dt.date(jaar, 10, 12), eind_datum=dt.date(jaar, 10, 26))
    return land


class WidgetDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.land = _seed_land()
        cls.widget = Widget.objects.create(site_key="sv_test123", domein="example.com", land=cls.land)

    def test_onbekend_land_404(self):
        r = self.client.get("/widget/data?land=nergens")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r["Access-Control-Allow-Origin"], "*")

    def test_zonder_widget_teaser(self):
        r = self.client.get("/widget/data?land=duitsland")
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d["mode"], "teaser")
        self.assertIn("volgende", d)
        self.assertEqual(d["bron"]["url"][-10:], "duitsland/")
        # Teaser lekt niet de volledige lijst.
        self.assertNotIn("vakanties", d)
        self.assertEqual(r["Access-Control-Allow-Origin"], "*")

    def test_verkeerde_origin_teaser(self):
        WidgetPagina.objects.create(widget=self.widget, url="https://example.com/p/",
                                    status=WidgetPagina.ACTIEF)
        r = self.client.get("/widget/data?land=duitsland&site=sv_test123&u=https://example.com/p/",
                            HTTP_ORIGIN="https://kwaadwillend.nl")
        self.assertEqual(r.json()["mode"], "teaser")

    def test_geverifieerde_pagina_full(self):
        WidgetPagina.objects.create(widget=self.widget, url="https://example.com/p/",
                                    status=WidgetPagina.ACTIEF)
        r = self.client.get("/widget/data?land=duitsland&site=sv_test123&u=https://example.com/p/",
                            HTTP_ORIGIN="https://www.example.com")
        d = r.json()
        self.assertEqual(d["mode"], "full")
        self.assertEqual(len(d["vakanties"]), 2)

    def test_nieuwe_pagina_wordt_pending_en_full(self):
        # Widget op een nog onbekende pagina van het juiste domein: auto-registreren
        # als pending en vóór de eerste check tóch volledig tonen.
        r = self.client.get("/widget/data?land=duitsland&site=sv_test123&u=https://example.com/nieuw/",
                            HTTP_ORIGIN="https://example.com")
        self.assertEqual(r.json()["mode"], "full")
        p = WidgetPagina.objects.get(widget=self.widget, url="https://example.com/nieuw/")
        self.assertEqual(p.status, WidgetPagina.PENDING)


class WidgetGeneratorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.land = _seed_land()

    def test_get_toont_formulier(self):
        r = self.client.get("/widget/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'name="domein"')
        self.assertContains(r, "Duitsland")

    def test_post_maakt_widget_en_snippet(self):
        r = self.client.post("/widget/", {
            "land": "duitsland", "domein": "https://www.Example.com/x", "email": ""})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "data-sv-widget")
        w = Widget.objects.get()
        self.assertEqual(w.domein, "example.com")        # genormaliseerd
        self.assertContains(r, w.site_key)
        self.assertContains(r, "/duitsland/")            # statische backlink in snippet

    def test_post_ongeldig_domein(self):
        r = self.client.post("/widget/", {"land": "duitsland", "domein": "geen domein"})
        self.assertContains(r, "geldig domein")
        self.assertFalse(Widget.objects.exists())

    def test_honeypot_blokkeert(self):
        r = self.client.post("/widget/", {"land": "duitsland", "domein": "example.com",
                                          "website": "bot"})
        self.assertFalse(Widget.objects.exists())


class BacklinkCheckTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.land = _seed_land()
        cls.widget = Widget.objects.create(site_key="sv_k", domein="example.com",
                                           land=cls.land, email="webmaster@example.com")

    def test_heeft_backlink_herkent_link(self):
        ok = '<p><a href="https://schoolvakanties.nl/duitsland/">bron</a></p>'
        self.assertTrue(CheckCmd._heeft_backlink(ok, "duitsland"))
        self.assertTrue(CheckCmd._heeft_backlink(
            '<a href="http://www.schoolvakanties.nl/duitsland">x</a>', "duitsland"))
        self.assertFalse(CheckCmd._heeft_backlink('<a href="https://elders.nl/duitsland/">x</a>', "duitsland"))
        self.assertFalse(CheckCmd._heeft_backlink('<a href="https://schoolvakanties.nl/spanje/">x</a>', "duitsland"))

    def _resp(self, status, text=""):
        m = mock.Mock(); m.status_code = status; m.text = text
        return m

    def test_gevonden_zet_actief(self):
        p = WidgetPagina.objects.create(widget=self.widget, url="https://example.com/p/")
        html = '<a href="https://schoolvakanties.nl/duitsland/">bron</a>'
        with mock.patch("core.management.commands.check_backlinks.requests.get",
                        return_value=self._resp(200, html)):
            CheckCmd()._check(p)
        p.refresh_from_db()
        self.assertEqual(p.status, WidgetPagina.ACTIEF)
        self.assertTrue(p.backlink_ok)

    def test_afwezig_degradeert_na_grace_en_mailt(self):
        p = WidgetPagina.objects.create(widget=self.widget, url="https://example.com/p/",
                                        status=WidgetPagina.ACTIEF)
        with mock.patch("core.management.commands.check_backlinks.requests.get",
                        return_value=self._resp(200, "<p>geen link</p>")):
            with mock.patch("core.management.commands.check_backlinks.send_mail") as sm:
                CheckCmd()._check(p)   # 1e misser → mail, nog niet teaser
                p.refresh_from_db()
                self.assertEqual(p.fail_count, 1)
                self.assertEqual(p.status, WidgetPagina.ACTIEF)
                self.assertTrue(sm.called)
                CheckCmd()._check(p)   # 2e misser → teaser (GRACE_CHECKS=2)
        p.refresh_from_db()
        self.assertEqual(p.status, WidgetPagina.TEASER)

    def test_serverfout_wordt_overgeslagen(self):
        p = WidgetPagina.objects.create(widget=self.widget, url="https://example.com/p/",
                                        status=WidgetPagina.ACTIEF)
        with mock.patch("core.management.commands.check_backlinks.requests.get",
                        return_value=self._resp(503)):
            self.assertIsNone(CheckCmd()._check(p))
        p.refresh_from_db()
        self.assertEqual(p.status, WidgetPagina.ACTIEF)  # niet bestraft
        self.assertEqual(p.fail_count, 0)
