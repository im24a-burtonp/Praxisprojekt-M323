"""C2A: Monatsaggregation, Komposition und mehrstufige Sortierkriterien."""
import copy
import json
import unittest
from unittest.mock import patch

from app import DATA_FILE, app, ist_psg_spiel
from monatsuebersicht import (
    MonatsStatistik, aggregiere_monate, erstelle_monatsuebersicht,
    erweitere_monat, komponiere, punkte_schluessel, tore_schluessel,
)


def beispielspiele():
    return [
        {"date": "2024-08-01", "team1": "Paris Saint-Germain FC", "team2": "Lyon", "score": {"ft": [2, 0]}},
        {"date": "2024-08-08", "team1": "Monaco", "team2": "Paris Saint-Germain FC", "score": {"ft": [1, 1]}},
        {"date": "2024-09-01", "team1": "Paris Saint-Germain FC", "team2": "Lille", "score": {"ft": [4, 0]}},
        {"date": "2024-09-08", "team1": "Lens", "team2": "Paris Saint-Germain FC", "score": {"ft": [2, 0]}},
        {"date": "2025-01-01", "team1": "Paris Saint-Germain FC", "team2": "Lyon", "score": {"ft": [1, 0]}},
    ]


class C2ATests(unittest.TestCase):
    def test_month_aggregation_across_years_and_generator_input(self):
        result = aggregiere_monate(iter(beispielspiele()))
        self.assertEqual(result, (
            MonatsStatistik('2024-08', 2, 4, 3, 1),
            MonatsStatistik('2024-09', 2, 3, 4, 2),
            MonatsStatistik('2025-01', 1, 3, 1, 0),
        ))

    def test_selected_sorting_changes_order_not_values(self):
        spiele = beispielspiele()
        zeitlich = erstelle_monatsuebersicht(reversed(spiele), 'monat')
        punkte = erstelle_monatsuebersicht(spiele, 'punkte')
        tore = erstelle_monatsuebersicht(spiele, 'tore')
        self.assertEqual([m.monat for m in zeitlich], ['2024-08', '2024-09', '2025-01'])
        self.assertEqual([m.monat for m in punkte], ['2024-08', '2024-09', '2025-01'])
        self.assertEqual([m.monat for m in tore], ['2024-09', '2024-08', '2025-01'])
        self.assertEqual(set(zeitlich), set(punkte))
        self.assertEqual(set(zeitlich), set(tore))

    def test_sorting_tie_breakers(self):
        august = MonatsStatistik('2024-08', 2, 6, 5, 2)
        september = MonatsStatistik('2024-09', 2, 6, 6, 2)
        januar = MonatsStatistik('2025-01', 2, 6, 5, 1)
        monate = (januar, august, september)
        self.assertEqual(tuple(sorted(monate, key=punkte_schluessel)), (september, januar, august))
        self.assertEqual(tuple(sorted(monate, key=tore_schluessel)), (september, januar, august))

    def test_composition_order(self):
        auswertung = komponiere(lambda zahl: zahl + 2, lambda zahl: zahl * 3)
        self.assertEqual(auswertung(4), 18)

    def test_inputs_and_accumulator_are_not_mutated(self):
        spiele = beispielspiele()
        vorher = copy.deepcopy(spiele)
        start = MonatsStatistik('2024-08', 0, 0, 0, 0)
        erweitert = erweitere_monat(start, spiele[0])
        self.assertEqual(erweitert, MonatsStatistik('2024-08', 1, 3, 2, 0))
        self.assertEqual(start, MonatsStatistik('2024-08', 0, 0, 0, 0))
        erstelle_monatsuebersicht(spiele, 'tore')
        self.assertEqual(spiele, vorher)

    def test_empty_and_invalid_sorting(self):
        self.assertEqual(erstelle_monatsuebersicht(iter(())), ())
        with self.assertRaises(ValueError):
            erstelle_monatsuebersicht([], 'unbekannt')

    def test_route_groups_psg_and_retains_selected_sort(self):
        spiele = beispielspiele() + [{"date": "2024-08-10", "team1": "Lyon", "team2": "Monaco", "score": {"ft": [9, 9]}}]
        with patch('saisondaten.json.load', return_value={"matches": spiele}):
            response = app.test_client().get('/monate?sortierung=tore')
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn('Angezeigte Monate: 3', page)
        self.assertIn('value="tore" selected', page)
        self.assertLess(page.index('<th scope="row">2024-09'), page.index('<th scope="row">2024-08'))
        self.assertIn('<th scope="row">2024-08</th><td>2</td><td>4</td><td>3</td><td>1</td>', page)

    def test_route_invalid_sorting_and_empty_state(self):
        client = app.test_client()
        self.assertEqual(client.get('/monate?sortierung=falsch').status_code, 400)
        with patch('saisondaten.json.load', return_value={"matches": []}):
            response = client.get('/monate')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Keine PSG-Spiele für die Monatsübersicht vorhanden.', response.get_data(as_text=True))

    def test_real_season_totals_and_top_month(self):
        with DATA_FILE.open(encoding='utf-8') as file:
            spiele = list(filter(ist_psg_spiel, json.load(file)['matches']))
        monate = erstelle_monatsuebersicht(spiele)
        self.assertEqual(len(monate), 10)
        self.assertEqual(sum(m.spiele for m in monate), 34)
        self.assertEqual(sum(m.punkte for m in monate), 84)
        self.assertEqual(sum(m.tore for m in monate), 92)
        self.assertEqual(sum(m.gegentore for m in monate), 35)
        self.assertEqual(erstelle_monatsuebersicht(spiele, 'punkte')[0].monat, '2025-03')
        self.assertEqual(erstelle_monatsuebersicht(spiele, 'tore')[0].monat, '2025-03')
        self.assertEqual(app.test_client().get('/monate').status_code, 200)


if __name__ == '__main__':
    unittest.main()
