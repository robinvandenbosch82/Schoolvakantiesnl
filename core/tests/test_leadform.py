"""Samenwerken lead-form: opslaan, honeypot, validatie, rate-limiting."""
from django.core.cache import cache
from django.test import TestCase

from core.models import Samenwerkingsaanvraag as Lead


class LeadFormTests(TestCase):
    def setUp(self):
        cache.clear()  # rate-limit-teller resetten per test

    def _post(self, **extra):
        data = {"naam": "Test BV", "email": "a@b.nl", "bericht": "Hallo",
                "soort": "Data / API"}
        data.update(extra)
        return self.client.post("/samenwerken/", data)

    def test_geldig_slaat_lead_op(self):
        resp = self._post()
        self.assertContains(resp, "Bedankt voor je aanvraag")
        self.assertEqual(Lead.objects.count(), 1)

    def test_honeypot_dropt_stil(self):
        resp = self._post(website="http://spam.example")
        self.assertContains(resp, "Bedankt voor je aanvraag")  # bot merkt niets
        self.assertEqual(Lead.objects.count(), 0)              # maar geen lead

    def test_ongeldig_email(self):
        resp = self._post(email="geen-email")
        self.assertContains(resp, "geldig e-mailadres")
        self.assertEqual(Lead.objects.count(), 0)

    def test_ontbrekend_bericht(self):
        resp = self._post(bericht="")
        self.assertContains(resp, "Vul je naam")
        self.assertEqual(Lead.objects.count(), 0)

    def test_rate_limit(self):
        for _ in range(5):
            self._post()
        resp = self._post()  # 6e binnen het uur
        self.assertContains(resp, "over een uurtje")
        self.assertEqual(Lead.objects.count(), 5)

    def test_onbekend_type_wordt_geleegd(self):
        self._post(soort="<script>")
        self.assertEqual(Lead.objects.get().soort, "")
