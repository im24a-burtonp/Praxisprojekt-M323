"""C2A: PSG-Spiele nach Monat aggregieren und gezielt sortieren."""
from functools import reduce
from typing import NamedTuple

from heim_auswaerts import spielbeitrag
from torbilanz import tore_aus_psg_sicht


class MonatsStatistik(NamedTuple):
    monat: str
    spiele: int
    punkte: int
    tore: int
    gegentore: int

    @property
    def tordifferenz(self) -> int:
        return self.tore - self.gegentore

    @property
    def punkte_pro_spiel(self) -> float:
        return round(self.punkte / self.spiele, 2) if self.spiele else 0.0


def erweitere_monat(gesamt: MonatsStatistik, spiel: dict) -> MonatsStatistik:
    beitrag = spielbeitrag(*tore_aus_psg_sicht(spiel))
    return MonatsStatistik(
        gesamt.monat,
        gesamt.spiele + 1,
        gesamt.punkte + beitrag.punkte,
        gesamt.tore + beitrag.tore,
        gesamt.gegentore + beitrag.gegentore,
    )


def berechne_monat(monat: str, psg_spiele) -> MonatsStatistik:
    return reduce(
        erweitere_monat,
        filter(lambda spiel: spiel["date"][:7] == monat, psg_spiele),
        MonatsStatistik(monat, 0, 0, 0, 0),
    )


def aggregiere_monate(psg_spiele) -> tuple[MonatsStatistik, ...]:
    spiele = tuple(psg_spiele)
    monate = sorted({spiel["date"][:7] for spiel in spiele})
    return tuple(map(lambda monat: berechne_monat(monat, spiele), monate))


def punkte_schluessel(statistik: MonatsStatistik) -> tuple:
    return (-statistik.punkte, -statistik.tordifferenz, statistik.monat)


def tore_schluessel(statistik: MonatsStatistik) -> tuple:
    return (-statistik.tore, statistik.gegentore, statistik.monat)


SORTIERUNGEN = {
    "monat": lambda statistik: statistik.monat,
    "punkte": punkte_schluessel,
    "tore": tore_schluessel,
}


def komponiere(erster_schritt, zweiter_schritt):
    return lambda daten: zweiter_schritt(erster_schritt(daten))


def erstelle_monatsuebersicht(psg_spiele, sortierung: str = "monat") -> tuple[MonatsStatistik, ...]:
    if sortierung not in SORTIERUNGEN:
        raise ValueError("Unbekannte Monatssortierung.")

    def sortiere(monate):
        return tuple(sorted(monate, key=SORTIERUNGEN[sortierung]))

    auswertung = komponiere(aggregiere_monate, sortiere)
    return auswertung(psg_spiele)
