"""C1A: Komposition mit einmalig durchlaufbaren Eingaben und Randfällen."""
import copy
import unittest

from app import ist_psg_spiel
from torbilanz import Torbilanz, berechne_torbilanz


class C1ATests(unittest.TestCase):
    def test_composition_with_single_pass_source_and_scoreless_match(self):
        spiele = [
            {"team1": "Paris Saint-Germain FC", "team2": "Lyon", "score": {"ft": [2, 0]}},
            {"team1": "Monaco", "team2": "Paris Saint-Germain FC", "score": {"ft": [1, 3]}},
            {"team1": "Lyon", "team2": "Monaco", "score": {"ft": [4, 3]}},
            {"team1": "Paris Saint-Germain FC", "team2": "Lille", "score": {"ft": [0, 0]}},
        ]
        vorher = copy.deepcopy(spiele)
        quelle = (spiel for spiel in spiele)
        bilanz = berechne_torbilanz(filter(ist_psg_spiel, quelle))
        self.assertEqual(bilanz, Torbilanz(3, 5, 1))
        self.assertEqual(bilanz.tordifferenz, 4)
        self.assertEqual(spiele, vorher)
        self.assertEqual(list(quelle), [])

    def test_composition_with_empty_generator(self):
        quelle = (spiel for spiel in [])
        bilanz = berechne_torbilanz(filter(ist_psg_spiel, quelle))
        self.assertEqual(bilanz, Torbilanz(0, 0, 0))
        self.assertEqual(bilanz.tordifferenz, 0)

    def test_result_does_not_depend_on_match_order(self):
        spiele = [
            {"team1": "Paris Saint-Germain FC", "team2": "Lyon", "score": {"ft": [2, 0]}},
            {"team1": "Monaco", "team2": "Paris Saint-Germain FC", "score": {"ft": [1, 3]}},
        ]
        vorwaerts = berechne_torbilanz(filter(ist_psg_spiel, iter(spiele)))
        rueckwaerts = berechne_torbilanz(filter(ist_psg_spiel, reversed(spiele)))
        self.assertEqual(vorwaerts, Torbilanz(2, 5, 1))
        self.assertEqual(rueckwaerts, vorwaerts)


if __name__ == "__main__":
    unittest.main()
