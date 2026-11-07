"""A1B: pure Funktion, Prozedur und Einbindung in die Flask-Route prüfen."""
import copy
import io
import unittest
from contextlib import redirect_stdout

from app import app, ist_psg_spiel, protokolliere_psg_statistik


class A1BTests(unittest.TestCase):
    def test_filter_handles_home_away_and_other_teams(self):
        cases = (
            ({"team1": "Paris Saint-Germain FC", "team2": "Lyon"}, True),
            ({"team1": "Lyon", "team2": "Paris Saint-Germain FC"}, True),
            ({"team1": "Lyon", "team2": "Monaco"}, False),
        )
        for spiel, expected in cases:
            with self.subTest(spiel=spiel):
                before = copy.deepcopy(spiel)
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(ist_psg_spiel(spiel), expected)
                    self.assertEqual(ist_psg_spiel(spiel), expected)
                self.assertEqual(spiel, before)
                self.assertEqual(output.getvalue(), "")

    def test_procedure_prints_summary_and_returns_none(self):
        results = ["Sieg", "Unentschieden", "Niederlage", "Sieg"]
        before = results.copy()
        output = io.StringIO()
        with redirect_stdout(output):
            returned = protokolliere_psg_statistik(results)
        self.assertIsNone(returned)
        self.assertEqual(output.getvalue(), "PSG: Siege=2, Unentschieden=1, Niederlagen=1\n")
        self.assertEqual(results, before)

    def test_empty_results(self):
        output = io.StringIO()
        with redirect_stdout(output):
            returned = protokolliere_psg_statistik([])
        self.assertIsNone(returned)
        self.assertEqual(output.getvalue(), "PSG: Siege=0, Unentschieden=0, Niederlagen=0\n")

    def test_route_preserves_season_statistics(self):
        output = io.StringIO()
        with redirect_stdout(output):
            response = app.test_client().get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("PSG: Siege=26, Unentschieden=6, Niederlagen=2", output.getvalue())
        page = response.get_data(as_text=True)
        self.assertIn("34 Ligaspiele", page)
        self.assertIn("Siege: 26 | Unentschieden: 6 | Niederlagen: 2", page)


if __name__ == "__main__":
    unittest.main()
