"""C2B: PSG-Spiele auswählen und die Tore der Treffer zusammenzählen."""
from functools import reduce

from torbilanz import tore_aus_psg_sicht


def alle_spiele(spiel: dict) -> bool:
    return True


def ist_sieg(spiel: dict) -> bool:
    tore, gegentore = tore_aus_psg_sicht(spiel)
    return tore > gegentore


def ist_unentschieden(spiel: dict) -> bool:
    tore, gegentore = tore_aus_psg_sicht(spiel)
    return tore == gegentore


def ist_niederlage(spiel: dict) -> bool:
    tore, gegentore = tore_aus_psg_sicht(spiel)
    return tore < gegentore


# Die Werte sind Funktionsobjekte, keine Ergebnisse von Funktionsaufrufen.
ERGEBNIS_FILTER = {
    "alle": alle_spiele,
    "sieg": ist_sieg,
    "unentschieden": ist_unentschieden,
    "niederlage": ist_niederlage,
}


def gegner_name(spiel: dict) -> str:
    if spiel["team1"] == "Paris Saint-Germain FC":
        return spiel["team2"]
    if spiel["team2"] == "Paris Saint-Germain FC":
        return spiel["team1"]
    raise ValueError("Die Spielsuche erwartet bereits ausgewählte PSG-Spiele.")


def spiel_tore(spiel: dict) -> int:
    return spiel["score"]["ft"][0] + spiel["score"]["ft"][1]


def addiere_tore(summe: int, tore: int) -> int:
    return summe + tore


def suche_spiele(psg_spiele, ergebnis: str = "alle", gegner: str = ""):
    """Filter, Map und Reduce bewusst als einzelne Schritte anwenden."""
    if ergebnis not in ERGEBNIS_FILTER:
        raise ValueError("Unbekannter Ergebnisfilter.")
    auswahlfunktion = ERGEBNIS_FILTER[ergebnis]
    treffer = list(filter(auswahlfunktion, psg_spiele))

    suchtext = gegner.strip().casefold()
    if suchtext:
        def passt_zum_gegner(spiel):
            return suchtext in gegner_name(spiel).casefold()
        treffer = list(filter(passt_zum_gegner, treffer))

    torfunktion = spiel_tore
    torzahlen = list(map(torfunktion, treffer))
    gesamt_tore = reduce(addiere_tore, torzahlen, 0)
    return tuple(treffer), gesamt_tore
