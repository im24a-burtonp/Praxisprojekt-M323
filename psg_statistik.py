"""Statistikwerte und Berechnungen ohne Abhängigkeit von Flask."""
from typing import NamedTuple


class PSGStatistik(NamedTuple):
    siege: int
    unentschieden: int
    niederlagen: int


def erstelle_statistik_mutierend(ergebnisse):
    """Vergleichsvariante: verändert ein neu angelegtes Dictionary."""
    statistik = {}
    statistik["siege"] = ergebnisse.count("Sieg")
    statistik["unentschieden"] = ergebnisse.count("Unentschieden")
    statistik["niederlagen"] = ergebnisse.count("Niederlage")
    return statistik


def erstelle_statistik(ergebnisse):
    """Erstellt einen unveränderlichen Statistikwert für die Anzeige."""
    return PSGStatistik(
        siege=ergebnisse.count("Sieg"),
        unentschieden=ergebnisse.count("Unentschieden"),
        niederlagen=ergebnisse.count("Niederlage"),
    )
