"""B1A: imperative und deklarative Route müssen dasselbe anzeigen."""
import copy
import unittest
from unittest.mock import patch

from app import app
from torbilanz import Torbilanz, berechne_torbilanz, tore_aus_psg_sicht


def spiel(heim, auswaerts, tore):
    return {"team1": heim, "team2": auswaerts, "score": {"ft": tore}}


class B1ATests(unittest.TestCase):
    def test_goal_perspective_home_and_away(self):
        self.assertEqual(tore_aus_psg_sicht(spiel("Paris Saint-Germain FC", "Lyon", [2, 0])), (2, 0))
        self.assertEqual(tore_aus_psg_sicht(spiel("Monaco", "Paris Saint-Germain FC", [1, 3])), (3, 1))

    def test_transform_rejects_non_psg_match(self):
        with self.assertRaises(ValueError):
            tore_aus_psg_sicht(spiel("Lyon", "Monaco", [4, 3]))

    def test_empty_aggregation(self):
        self.assertEqual(berechne_torbilanz([]), Torbilanz(0, 0, 0))

    def test_routes_match_and_preserve_input(self):
        season = {"matches": [
            spiel("Paris Saint-Germain FC", "Lyon", [2, 0]),
            spiel("Monaco", "Paris Saint-Germain FC", [1, 3]),
            spiel("Lyon", "Monaco", [4, 3]),
        ]}
        before = copy.deepcopy(season)
        client = app.test_client()
        with patch("saisondaten.json.load", return_value=season):
            declarative = client.get("/tore")
            imperative = client.get("/tore-imperativ")
        self.assertEqual(declarative.status_code, 200)
        self.assertEqual(imperative.status_code, 200)
        self.assertEqual(declarative.data, imperative.data)
        page = declarative.get_data(as_text=True)
        for text in ("Ligaspiele: 2", "Erzielte Tore: 5", "Gegentore: 1", "Tordifferenz: +4"):
            self.assertIn(text, page)
        self.assertEqual(season, before)

    def test_routes_with_no_psg_matches(self):
        client = app.test_client()
        with patch("saisondaten.json.load", return_value={"matches": [spiel("Lyon", "Monaco", [4, 3])]}):
            declarative = client.get("/tore")
            imperative = client.get("/tore-imperativ")
        self.assertEqual(declarative.status_code, 200)
        self.assertEqual(imperative.status_code, 200)
        self.assertEqual(declarative.data, imperative.data)
        page = declarative.get_data(as_text=True)
        for text in ("Ligaspiele: 0", "Erzielte Tore: 0", "Gegentore: 0", "Tordifferenz: +0"):
            self.assertIn(text, page)

    def test_real_season_and_navigation(self):
        client = app.test_client()
        declarative = client.get("/tore")
        imperative = client.get("/tore-imperativ")
        self.assertEqual(declarative.status_code, 200)
        self.assertEqual(imperative.status_code, 200)
        self.assertEqual(declarative.data, imperative.data)
        page = declarative.get_data(as_text=True)
        for text in ("Ligaspiele: 34", "Erzielte Tore: 92", "Gegentore: 35", "Tordifferenz: +57"):
            self.assertIn(text, page)
        self.assertIn('href="/"', page)


if __name__ == "__main__":
    unittest.main()
