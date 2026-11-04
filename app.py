from pathlib import Path
import json

from flask import Flask, render_template

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


@app.route("/")
def index():
    with DATA_FILE.open(encoding="utf-8") as file:
        season = json.load(file)
    psg_spiele = list(filter(ist_psg_spiel, season["matches"]))
    ergebnisse = list(map(psg_ergebnis, psg_spiele))
    return render_template(
        "index.html", season=season, psg_spiele=psg_spiele,
        siege=ergebnisse.count("Sieg"),
        unentschieden=ergebnisse.count("Unentschieden"),
        niederlagen=ergebnisse.count("Niederlage"),
    )

if __name__ == "__main__":
    app.run(debug=True)
