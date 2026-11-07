"""B1B: Datenfluss von Spielauswahl über Transformation bis zur Anzeige."""
import copy
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from app import app


class FunctionalDesignTests(unittest.TestCase):
    def test_pipeline_filters_transforms_and_counts_without_mutation(self):
        season = {"matches": [
            {"team1": "Paris Saint-Germain FC", "team2": "Lyon", "score": {"ft": [2, 0]}},
            {"team1": "Monaco", "team2": "Paris Saint-Germain FC", "score": {"ft": [1, 1]}},
            {"team1": "Lyon", "team2": "Monaco", "score": {"ft": [4, 3]}},
        ]}
        before = copy.deepcopy(season)
        with patch("app.json.load", return_value=season), redirect_stdout(io.StringIO()):
            response = app.test_client().get("/")
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn("2 Ligaspiele", page)
        self.assertIn("Siege: 1 | Unentschieden: 1 | Niederlagen: 0", page)
        self.assertEqual(season, before)

    def test_pipeline_handles_no_psg_matches(self):
        season = {"matches": [
            {"team1": "Lyon", "team2": "Monaco", "score": {"ft": [4, 3]}},
        ]}
        with patch("app.json.load", return_value=season), redirect_stdout(io.StringIO()):
            response = app.test_client().get("/")
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn("0 Ligaspiele", page)
        self.assertIn("Siege: 0 | Unentschieden: 0 | Niederlagen: 0", page)


if __name__ == "__main__":
    unittest.main()
