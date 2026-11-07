"""C2I: Funktion als Argument, Lambda und verkettetes Filter/Map/Reduce."""
import copy
import json
import unittest
from unittest.mock import patch

from app import DATA_FILE, app, ist_psg_spiel
from heim_auswaerts import (
    VergleichsStatistik, berechne_vergleich, ist_heimspiel,
    ist_auswaertsspiel, spielbeitrag,
)


def beispielspiele():
    return [
        {"team1": "Paris Saint-Germain FC", "team2": "Lyon", "score": {"ft": [2, 0]}},
        {"team1": "Monaco", "team2": "Paris Saint-Germain FC", "score": {"ft": [1, 1]}},
        {"team1": "Paris Saint-Germain FC", "team2": "Lille", "score": {"ft": [0, 0]}},
        {"team1": "Lens", "team2": "Paris Saint-Germain FC", "score": {"ft": [2, 0]}},
    ]


class C2ITests(unittest.TestCase):
    def test_points_for_win_draw_and_loss(self):
        for tore, gegentore, punkte in [(2, 0, 3), (1, 1, 1), (0, 2, 0), (0, 0, 1)]:
            with self.subTest(tore=tore, gegentore=gegentore):
                self.assertEqual(spielbeitrag(tore, gegentore), VergleichsStatistik(1, punkte, tore, gegentore))

    def test_home_and_away_chain(self):
        spiele = beispielspiele()
        heim = berechne_vergleich(spiele, ist_heimspiel)
        auswaerts = berechne_vergleich(spiele, ist_auswaertsspiel)
        self.assertEqual(heim, VergleichsStatistik(2, 4, 2, 0))
        self.assertEqual(auswaerts, VergleichsStatistik(2, 1, 1, 3))
        self.assertEqual(heim.punkte_pro_spiel, 2.0)
        self.assertEqual(auswaerts.punkte_pro_spiel, 0.5)

    def test_supplied_predicate_controls_selection(self):
        def nichts_auswaehlen(spiel):
            return False
        self.assertEqual(berechne_vergleich(beispielspiele(), nichts_auswaehlen), VergleichsStatistik(0, 0, 0, 0))

    def test_empty_generator_has_zero_average(self):
        statistik = berechne_vergleich(iter(()), ist_heimspiel)
        self.assertEqual(statistik, VergleichsStatistik(0, 0, 0, 0))
        self.assertEqual(statistik.punkte_pro_spiel, 0.0)

    def test_source_is_not_mutated(self):
        spiele = beispielspiele()
        vorher = copy.deepcopy(spiele)
        berechne_vergleich(spiele, ist_heimspiel)
        berechne_vergleich(spiele, ist_auswaertsspiel)
        self.assertEqual(spiele, vorher)

    def test_route_excludes_other_teams_and_displays_both_groups(self):
        spiele = beispielspiele() + [{"team1": "Lyon", "team2": "Monaco", "score": {"ft": [9, 9]}}]
        with patch('app.json.load', return_value={"matches": spiele}):
            response = app.test_client().get('/heim-auswaerts')
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        for row in [
            '<th scope="row">Spiele</th><td>2</td><td>2</td>',
            '<th scope="row">Punkte</th><td>4</td><td>1</td>',
            '<th scope="row">Erzielte Tore</th><td>2</td><td>1</td>',
            '<th scope="row">Gegentore</th><td>0</td><td>3</td>',
            '<th scope="row">Punkte pro Spiel</th><td>2.00</td><td>0.50</td>',
        ]:
            self.assertIn(row, page)

    def test_route_handles_empty_away_group(self):
        with patch('app.json.load', return_value={"matches": beispielspiele()[:1]}):
            response = app.test_client().get('/heim-auswaerts')
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn('<th scope="row">Spiele</th><td>1</td><td>0</td>', page)
        self.assertIn('<th scope="row">Punkte pro Spiel</th><td>3.00</td><td>0.00</td>', page)

    def test_real_season_and_totals(self):
        with DATA_FILE.open(encoding='utf-8') as file:
            spiele = list(filter(ist_psg_spiel, json.load(file)['matches']))
        heim = berechne_vergleich(spiele, ist_heimspiel)
        auswaerts = berechne_vergleich(spiele, ist_auswaertsspiel)
        self.assertEqual(heim, VergleichsStatistik(17, 44, 45, 16))
        self.assertEqual(auswaerts, VergleichsStatistik(17, 40, 47, 19))
        self.assertEqual(heim.spiele + auswaerts.spiele, 34)
        self.assertEqual(heim.punkte + auswaerts.punkte, 84)
        self.assertEqual(heim.tore + auswaerts.tore, 92)
        self.assertEqual(heim.gegentore + auswaerts.gegentore, 35)
        response = app.test_client().get('/heim-auswaerts')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<th scope="row">Punkte</th><td>44</td><td>40</td>', response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
