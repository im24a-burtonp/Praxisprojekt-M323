"""Datenwert und pure Berechnung der PSG-Torbilanz."""
from typing import NamedTuple


class Torbilanz(NamedTuple):
    spiele: int
    tore: int
    gegentore: int

    @property
    def tordifferenz(self):
        return self.tore - self.gegentore


def tore_aus_psg_sicht(spiel):
    """Gibt (PSG-Tore, Gegentore) für genau ein PSG-Spiel zurück."""
    heimtore, auswaertstore = spiel["score"]["ft"]
    if spiel["team1"] == "Paris Saint-Germain FC":
        return heimtore, auswaertstore
    if spiel["team2"] == "Paris Saint-Germain FC":
        return auswaertstore, heimtore
    raise ValueError("Das Spiel muss ein PSG-Spiel sein.")


def berechne_torbilanz(psg_spiele):
    """Transformiert bereits ausgewählte PSG-Spiele und summiert deren Tore."""
    torpaare = tuple(map(tore_aus_psg_sicht, psg_spiele))
    return Torbilanz(
        spiele=len(torpaare),
        tore=sum(map(lambda paar: paar[0], torpaare)),
        gegentore=sum(map(lambda paar: paar[1], torpaare)),
    )
