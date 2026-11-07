"""A1I: gleiche Zahlen, Referenzen und unveränderliche Statistikwerte."""
import unittest

from psg_statistik import PSGStatistik, erstelle_statistik, erstelle_statistik_mutierend


class A1ITests(unittest.TestCase):
    def test_both_variants_count_the_same_results(self):
        results = ["Sieg", "Unentschieden", "Niederlage", "Sieg"]
        before = results.copy()
        mutable = erstelle_statistik_mutierend(results)
        immutable = erstelle_statistik(results)
        self.assertEqual(immutable, PSGStatistik(2, 1, 1))
        self.assertEqual(mutable, immutable._asdict())
        self.assertEqual(results, before)

    def test_dictionary_alias_observes_mutation(self):
        original = erstelle_statistik_mutierend(["Sieg"])
        alias = original
        alias["siege"] = 99
        self.assertIs(alias, original)
        self.assertEqual(original["siege"], 99)

    def test_named_tuple_rejects_mutation_through_alias(self):
        original = erstelle_statistik(["Sieg"])
        alias = original
        self.assertIs(alias, original)
        with self.assertRaises(AttributeError):
            alias.siege = 99
        self.assertEqual(original.siege, 1)

    def test_new_value_leaves_previous_value_unchanged(self):
        original = erstelle_statistik(["Sieg"])
        updated = original._replace(siege=2)
        self.assertEqual(original.siege, 1)
        self.assertEqual(updated.siege, 2)
        self.assertIsNot(updated, original)

    def test_empty_results(self):
        self.assertEqual(erstelle_statistik([]), PSGStatistik(0, 0, 0))
        self.assertEqual(erstelle_statistik_mutierend([]), {"siege": 0, "unentschieden": 0, "niederlagen": 0})


if __name__ == "__main__":
    unittest.main()
