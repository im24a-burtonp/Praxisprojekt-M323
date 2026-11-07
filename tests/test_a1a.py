"""A1A: gleiche Aufgabe, drei Ansätze, identisches Ergebnis."""
import json
import unittest

from app import DATA_FILE, ist_psg_spiel, psg_ergebnis
from psg_statistik import PSGStatistik, erstelle_statistik
from statistik_vergleich import (
    PSGStatistikRechner,
    erstelle_statistik_oo,
    erstelle_statistik_prozedural,
)


VARIANTEN = (erstelle_statistik, erstelle_statistik_prozedural, erstelle_statistik_oo)


class A1ATests(unittest.TestCase):
    def test_same_counts_and_unchanged_input(self):
        ergebnisse = ["Sieg", "Unentschieden", "Niederlage", "Sieg"]
        vorher = ergebnisse.copy()
        for variante in VARIANTEN:
            with self.subTest(variante=variante.__name__):
                self.assertEqual(variante(ergebnisse), PSGStatistik(2, 1, 1))
                self.assertEqual(variante(ergebnisse), PSGStatistik(2, 1, 1))
                self.assertEqual(ergebnisse, vorher)

    def test_empty_input(self):
        for variante in VARIANTEN:
            with self.subTest(variante=variante.__name__):
                self.assertEqual(variante([]), PSGStatistik(0, 0, 0))

    def test_only_draws(self):
        for variante in VARIANTEN:
            with self.subTest(variante=variante.__name__):
                self.assertEqual(variante(["Unentschieden"] * 3), PSGStatistik(0, 3, 0))

    def test_real_season(self):
        with DATA_FILE.open(encoding="utf-8") as file:
            spiele = json.load(file)["matches"]
        ergebnisse = list(map(psg_ergebnis, filter(ist_psg_spiel, spiele)))
        self.assertEqual(len(ergebnisse), 34)
        for variante in VARIANTEN:
            with self.subTest(variante=variante.__name__):
                self.assertEqual(variante(ergebnisse), PSGStatistik(26, 6, 2))

    def test_objects_have_independent_state_and_snapshots(self):
        erster = PSGStatistikRechner()
        zweiter = PSGStatistikRechner()
        erster.erfasse("Sieg")
        vorher = erster.als_statistik()
        erster.erfasse("Niederlage")
        self.assertEqual(vorher, PSGStatistik(1, 0, 0))
        self.assertEqual(erster.als_statistik(), PSGStatistik(1, 0, 1))
        self.assertEqual(zweiter.als_statistik(), PSGStatistik(0, 0, 0))


if __name__ == "__main__":
    unittest.main()
