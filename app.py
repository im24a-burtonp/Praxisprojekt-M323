from pathlib import Path
import json

from flask import Flask, abort, render_template, request
from psg_statistik import erstelle_statistik
from torbilanz import Torbilanz, berechne_torbilanz
from spielsuche import ERGEBNIS_FILTER, suche_spiele
from heim_auswaerts import berechne_vergleich, ist_heimspiel, ist_auswaertsspiel
from monatsuebersicht import SORTIERUNGEN, erstelle_monatsuebersicht

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data" / "ligue1-2024-25.json"


def ist_psg_spiel(spiel: dict) -> bool:
    return (spiel["team1"] == "Paris Saint-Germain FC"
            or spiel["team2"] == "Paris Saint-Germain FC")


def psg_ergebnis(spiel):
    heimtore, auswaertstore = spiel["score"]["ft"]
    if spiel["team1"] == "Paris Saint-Germain FC":
        psg_tore, gegner_tore = heimtore, auswaertstore
    else:
        psg_tore, gegner_tore = auswaertstore, heimtore

    if psg_tore > gegner_tore:
        return "Sieg"
    if psg_tore < gegner_tore:
        return "Niederlage"
    return "Unentschieden"


def protokolliere_psg_statistik(ergebnisse):
    """Prozedur: schreibt die Statistik ins Terminal, ohne Rückgabewert."""
    print(
        f"PSG: Siege={ergebnisse.count('Sieg')}, "
        f"Unentschieden={ergebnisse.count('Unentschieden')}, "
        f"Niederlagen={ergebnisse.count('Niederlage')}"
    )


@app.route("/")
def index():
    with DATA_FILE.open(encoding="utf-8") as file:
        season = json.load(file)
    psg_spiele = list(filter(ist_psg_spiel, season["matches"]))
    ergebnisse = list(map(psg_ergebnis, psg_spiele))
    statistik = erstelle_statistik(ergebnisse)
    protokolliere_psg_statistik(ergebnisse)
    return render_template(
        "index.html", season=season, psg_spiele=psg_spiele,
        siege=statistik.siege,
        unentschieden=statistik.unentschieden,
        niederlagen=statistik.niederlagen,
    )

@app.route("/tore")
def torbilanz_deklarativ():
    with DATA_FILE.open(encoding="utf-8") as file:
        season = json.load(file)
    psg_spiele = filter(ist_psg_spiel, season["matches"])
    bilanz = berechne_torbilanz(psg_spiele)
    return render_template("torbilanz.html", bilanz=bilanz)


@app.route("/tore-imperativ")
def torbilanz_imperativ():
    with DATA_FILE.open(encoding="utf-8") as file:
        season = json.load(file)
    spiele = 0
    tore = 0
    gegentore = 0
    for spiel in season["matches"]:
        if not ist_psg_spiel(spiel):
            continue
        spiele += 1
        if spiel["team1"] == "Paris Saint-Germain FC":
            tore += spiel["score"]["ft"][0]
            gegentore += spiel["score"]["ft"][1]
        else:
            tore += spiel["score"]["ft"][1]
            gegentore += spiel["score"]["ft"][0]
    bilanz = Torbilanz(spiele, tore, gegentore)
    return render_template("torbilanz.html", bilanz=bilanz)


@app.route("/spiele")
def spielsuche():
    ergebnis = request.args.get("ergebnis", "alle")
    gegner = request.args.get("gegner", "").strip()
    if ergebnis not in ERGEBNIS_FILTER:
        abort(400, description="Unbekannter Ergebnisfilter.")
    with DATA_FILE.open(encoding="utf-8") as file:
        season = json.load(file)
    psg_spiele = list(filter(ist_psg_spiel, season["matches"]))
    treffer, gesamt_tore = suche_spiele(psg_spiele, ergebnis, gegner)
    return render_template(
        "spielsuche.html", spiele=treffer, gesamt_tore=gesamt_tore,
        ergebnis=ergebnis, gegner=gegner,
    )


@app.route("/heim-auswaerts")
def heim_auswaerts_vergleich():
    with DATA_FILE.open(encoding="utf-8") as file:
        season = json.load(file)
    psg_spiele = list(filter(ist_psg_spiel, season["matches"]))
    heim = berechne_vergleich(psg_spiele, ist_heimspiel)
    auswaerts = berechne_vergleich(psg_spiele, ist_auswaertsspiel)
    return render_template("heim_auswaerts.html", heim=heim, auswaerts=auswaerts)


@app.route("/monate")
def monatsuebersicht():
    sortierung = request.args.get("sortierung", "monat")
    if sortierung not in SORTIERUNGEN:
        abort(400, description="Unbekannte Monatssortierung.")
    with DATA_FILE.open(encoding="utf-8") as file:
        season = json.load(file)
    psg_spiele = filter(ist_psg_spiel, season["matches"])
    monate = erstelle_monatsuebersicht(psg_spiele, sortierung)
    return render_template("monatsuebersicht.html", monate=monate, sortierung=sortierung)


if __name__ == "__main__":
    app.run(debug=True)
