"""D1I: Verhalten gegen echten Commit-Code und gezielte Arbeitszählung prüfen."""
import copy
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from app import app, ist_psg_spiel
from monatsuebersicht import aggregiere_monate, erstelle_monatsuebersicht
from saisondaten import lade_saison
from tests.historie import VERGLEICHS_URLS, vorher_module


def beispielspiele():
    return [
        {"date": "2024-08-01", "team1": "Paris Saint-Germain FC", "team2": "Lyon", "score": {"ft": [2, 0]}},
        {"date": "2024-08-08", "team1": "Monaco", "team2": "Paris Saint-Germain FC", "score": {"ft": [1, 1]}},
        {"date": "2024-09-01", "team1": "Paris Saint-Germain FC", "team2": "Lille", "score": {"ft": [0, 0]}},
    ]


class GezaehltesSpiel(dict):
    def __init__(self, daten):
        super().__init__(daten)
        self.datumszugriffe = 0

    def __getitem__(self, key):
        if key == "date":
            self.datumszugriffe += 1
        return super().__getitem__(key)


class D1ITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.alte_routes, cls.alte_monate = vorher_module()

    def test_shared_loader_reads_original_season(self):
        saison = lade_saison()
        self.assertEqual(len(saison["matches"]), 306)
        self.assertEqual(sum(ist_psg_spiel(s) for s in saison["matches"]), 34)

    def test_real_months_match_commit_for_all_sortings(self):
        spiele = list(filter(ist_psg_spiel, lade_saison()["matches"]))
        vorher = copy.deepcopy(spiele)
        for sortierung in ("monat", "punkte", "tore"):
            with self.subTest(sortierung=sortierung):
                alt = self.alte_monate.erstelle_monatsuebersicht(iter(spiele), sortierung)
                neu = erstelle_monatsuebersicht(iter(spiele), sortierung)
                self.assertEqual(neu, alt)
        self.assertEqual(spiele, vorher)

    def test_synthetic_and_empty_months_match_commit(self):
        for spiele in (beispielspiele(), [], list(reversed(beispielspiele()))):
            for sortierung in ("monat", "punkte", "tore"):
                with self.subTest(spiele=len(spiele), sortierung=sortierung):
                    self.assertEqual(
                        erstelle_monatsuebersicht(iter(spiele), sortierung),
                        self.alte_monate.erstelle_monatsuebersicht(iter(spiele), sortierung),
                    )

    def test_index_reads_month_key_once_per_game(self):
        alt = [GezaehltesSpiel(s) for s in beispielspiele()]
        neu = [GezaehltesSpiel(s) for s in beispielspiele()]
        self.assertEqual(aggregiere_monate(neu), self.alte_monate.aggregiere_monate(alt))
        self.assertEqual(sum(s.datumszugriffe for s in alt), 9)
        self.assertEqual(sum(s.datumszugriffe for s in neu), 3)

    def assert_same_responses(self):
        alt_client = self.alte_routes.app.test_client()
        neu_client = app.test_client()
        with redirect_stdout(io.StringIO()):
            for url in VERGLEICHS_URLS:
                with self.subTest(url=url):
                    alt = alt_client.get(url)
                    neu = neu_client.get(url)
                    self.assertEqual(neu.status_code, alt.status_code)
                    self.assertEqual(neu.content_type, alt.content_type)
                    self.assertEqual(neu.data, alt.data)

    def test_real_http_responses_match_commit(self):
        self.assert_same_responses()

    def test_synthetic_http_responses_match_commit(self):
        saison = {"matches": beispielspiele() + [
            {"date": "2024-08-10", "team1": "Lyon", "team2": "Monaco", "score": {"ft": [9, 9]}},
        ]}
        vorher = copy.deepcopy(saison)
        with patch("saisondaten.json.load", return_value=saison):
            self.assert_same_responses()
        self.assertEqual(saison, vorher)

    def test_each_route_uses_shared_loader_once(self):
        for url in ("/", "/tore", "/tore-imperativ", "/spiele", "/heim-auswaerts", "/monate"):
            with self.subTest(url=url), patch("app.lade_saison", return_value={"matches": []}) as loader:
                with redirect_stdout(io.StringIO()):
                    response = app.test_client().get(url)
                self.assertEqual(response.status_code, 200)
                loader.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
