"""C2I: unabhängiger PSG-Heim-/Auswärtsvergleich mit einer Verarbeitungskette."""
from collections.abc import Callable, Iterable
from functools import reduce
from typing import NamedTuple

from torbilanz import tore_aus_psg_sicht


class VergleichsStatistik(NamedTuple):
    spiele: int
    punkte: int
    tore: int
    gegentore: int

    @property
    def punkte_pro_spiel(self) -> float:
        return round(self.punkte / self.spiele, 2) if self.spiele else 0.0


def ist_heimspiel(spiel: dict) -> bool:
    return spiel["team1"] == "Paris Saint-Germain FC"


def ist_auswaertsspiel(spiel: dict) -> bool:
    return spiel["team2"] == "Paris Saint-Germain FC"


def spielbeitrag(tore: int, gegentore: int) -> VergleichsStatistik:
    if tore > gegentore:
        punkte = 3
    elif tore == gegentore:
        punkte = 1
    else:
        punkte = 0
    return VergleichsStatistik(1, punkte, tore, gegentore)


def addiere_statistiken(links: VergleichsStatistik, rechts: VergleichsStatistik) -> VergleichsStatistik:
    return VergleichsStatistik(
        links.spiele + rechts.spiele,
        links.punkte + rechts.punkte,
        links.tore + rechts.tore,
        links.gegentore + rechts.gegentore,
    )


def berechne_vergleich(psg_spiele: Iterable[dict], auswahlfunktion: Callable[[dict], bool]) -> VergleichsStatistik:
    """Auswahlfunktion weitergeben; Filter, Map und Reduce direkt verketten."""
    return reduce(
        addiere_statistiken,
        map(
            lambda spiel: spielbeitrag(*tore_aus_psg_sicht(spiel)),
            filter(auswahlfunktion, psg_spiele),
        ),
        VergleichsStatistik(0, 0, 0, 0),
    )
