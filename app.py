from pathlib import Path
import json

from flask import Flask, render_template
from psg_statistik import erstelle_statistik

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data" / "ligue1-2024-25.json"


def ist_psg_spiel(spiel):
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

if __name__ == "__main__":
    app.run(debug=True)
