"""Pure logica rond de druktekaart/planner — geen DB of netwerk."""
from django.test import SimpleTestCase

from core import europe


class EuropeLogicTests(SimpleTestCase):
    def test_band_drempels(self):
        self.assertEqual(europe.band(80), "rustig")
        self.assertEqual(europe.band(50), "matig")
        self.assertEqual(europe.band(20), "druk")

    def test_drukte_profiel_piek_en_bereik(self):
        prof = europe.drukte_profile(peak=10, spread=2.5, base=20, n=20)
        self.assertEqual(len(prof), 20)
        self.assertEqual(max(range(20), key=lambda i: prof[i]), 10)  # piek op index 10
        self.assertTrue(all(0 <= v <= 100 for v in prof))

    def test_prijs_curve_hoger_niveau_is_duurder(self):
        drukte = [10] * 20
        overlap = [10] * 20
        goedkoop = europe.prijs_curve(drukte, overlap, 36)
        duur = europe.prijs_curve(drukte, overlap, 82)
        self.assertTrue(all(g <= d for g, d in zip(goedkoop, duur)))
        self.assertTrue(all(5 <= v <= 100 for v in goedkoop + duur))

    def test_europe_list_live_en_slug(self):
        rows = europe.europe_list(live_codes=["nl"])
        nl = next(r for r in rows if r["code"] == "nl")
        self.assertTrue(nl["live"])
        self.assertEqual(nl["slug"], "nederland")
        de = next(r for r in rows if r["code"] == "de")
        self.assertFalse(de["live"])
