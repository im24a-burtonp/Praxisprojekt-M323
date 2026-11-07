"""A1A: ausführbare Alternativen zur funktionalen PSG-Statistik.

Die Webseite verwendet weiterhin erstelle_statistik aus psg_statistik.py.
Die Alternativen werden mit denselben Daten in tests/test_a1a.py geprüft.
"""
from psg_statistik import PSGStatistik


def erstelle_statistik_prozedural(ergebnisse):
    """Ein Ablauf mit lokalen Zählern und einer Schleife."""
    siege = 0
    unentschieden = 0
    niederlagen = 0
    for ergebnis in ergebnisse:
        if ergebnis == "Sieg":
            siege += 1
        elif ergebnis == "Unentschieden":
            unentschieden += 1
        elif ergebnis == "Niederlage":
            niederlagen += 1
    return PSGStatistik(siege, unentschieden, niederlagen)


class PSGStatistikRechner:
    """OO-Variante: ein Objekt kapselt Zähler und deren Aktualisierung."""

    def __init__(self):
        self.siege = 0
        self.unentschieden = 0
        self.niederlagen = 0

    def erfasse(self, ergebnis):
        if ergebnis == "Sieg":
            self.siege += 1
        elif ergebnis == "Unentschieden":
            self.unentschieden += 1
        elif ergebnis == "Niederlage":
            self.niederlagen += 1

    def als_statistik(self):
        return PSGStatistik(self.siege, self.unentschieden, self.niederlagen)


def erstelle_statistik_oo(ergebnisse):
    rechner = PSGStatistikRechner()
    for ergebnis in ergebnisse:
        rechner.erfasse(ergebnis)
    return rechner.als_statistik()
