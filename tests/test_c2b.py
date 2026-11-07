"""C2B: Funktionsauswahl, einzelne Operatoren und Suchformular."""
import copy
import unittest
from unittest.mock import patch

from app import app
from spielsuche import suche_spiele


def beispielspiele():
    return [
        {"date": "2024-08-01", "team1": "Paris Saint-Germain FC", "team2": "Lyon", "score": {"ft": [2, 0]}},
        {"date": "2024-08-08", "team1": "Monaco", "team2": "Paris Saint-Germain FC", "score": {"ft": [1, 3]}},
        {"date": "2024-08-15", "team1": "Paris Saint-Germain FC", "team2": "Lille", "score": {"ft": [0, 0]}},
        {"date": "2024-08-22", "team1": "Lens", "team2": "Paris Saint-Germain FC", "score": {"ft": [2, 1]}},
    ]


class C2BTests(unittest.TestCase):
    def test_result_filters_and_goal_totals(self):
        spiele = beispielspiele()
        for ergebnis, anzahl, tore in [('alle', 4, 9), ('sieg', 2, 6), ('unentschieden', 1, 0), ('niederlage', 1, 3)]:
            with self.subTest(ergebnis=ergebnis):
                treffer, gesamt = suche_spiele(spiele, ergebnis)
                self.assertEqual(len(treffer), anzahl)
                self.assertEqual(gesamt, tore)

    def test_opponent_search_ignores_case_and_outer_spaces(self):
        spiele = beispielspiele()
        treffer, tore = suche_spiele(spiele, gegner="  MONA  ")
        self.assertEqual(treffer, (spiele[1],))
        self.assertEqual(tore, 4)
        self.assertEqual(suche_spiele(spiele, gegner="Paris"), ((), 0))

    def test_combined_filters_and_no_match(self):
        spiele = beispielspiele()
        self.assertEqual(suche_spiele(spiele, 'sieg', 'Lyon'), ((spiele[0],), 2))
        self.assertEqual(suche_spiele(spiele, 'niederlage', 'Lyon'), ((), 0))

    def test_empty_input_and_unknown_filter(self):
        self.assertEqual(suche_spiele([], 'alle'), ((), 0))
        with self.assertRaises(ValueError):
            suche_spiele([], 'unbekannt')

    def test_input_is_not_mutated(self):
        spiele = beispielspiele()
        vorher = copy.deepcopy(spiele)
        suche_spiele(spiele, 'sieg', 'Monaco')
        self.assertEqual(spiele, vorher)

    def test_route_excludes_non_psg_match_and_retains_filters(self):
        spiele = beispielspiele() + [
            {"date": "2024-08-25", "team1": "Lyon", "team2": "Monaco", "score": {"ft": [9, 9]}},
        ]
        with patch('saisondaten.json.load', return_value={"matches": spiele}):
            response = app.test_client().get('/spiele?ergebnis=sieg&gegner=Monaco')
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn('Gefundene PSG-Spiele: 1', page)
        self.assertIn('Tore insgesamt in diesen Spielen: 4', page)
        self.assertIn('value="Monaco"', page)
        self.assertIn('value="sieg" selected', page)
        self.assertNotIn('9 : 9', page)

    def test_route_empty_state(self):
        with patch('saisondaten.json.load', return_value={"matches": beispielspiele()}):
            response = app.test_client().get('/spiele?gegner=NichtVorhanden')
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn('Gefundene PSG-Spiele: 0', page)
        self.assertIn('Tore insgesamt in diesen Spielen: 0', page)
        self.assertIn('Keine Spiele für diese Auswahl gefunden.', page)

    def test_route_rejects_unknown_filter(self):
        self.assertEqual(app.test_client().get('/spiele?ergebnis=falsch').status_code, 400)

    def test_real_season_counts_and_goals(self):
        client = app.test_client()
        for ergebnis, anzahl in [('alle', 34), ('sieg', 26), ('unentschieden', 6), ('niederlage', 2)]:
            with self.subTest(ergebnis=ergebnis):
                response = client.get('/spiele', query_string={'ergebnis': ergebnis})
                self.assertEqual(response.status_code, 200)
                self.assertIn(f'Gefundene PSG-Spiele: {anzahl}', response.get_data(as_text=True))
        self.assertIn('Tore insgesamt in diesen Spielen: 127', client.get('/spiele').get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
