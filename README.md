# Ligue 1 – Saisonrückblick 2024/25

Ein Flask-Praxisprojekt für Modul 323. Die Anwendung soll die Saison 2024/25 der französischen Ligue 1 übersichtlich auswerten, mit besonderem Blick auf Paris Saint-Germain.

## Lokal starten (Windows PowerShell)

Voraussetzung ist eine installierte Version von Python. Öffne PowerShell im Projektordner und führe die folgenden Befehle aus:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Öffne danach <http://127.0.0.1:5000/> im Browser. Mit `Strg+C` im Terminal stoppst du die Anwendung. Bei späteren Starts genügt es, die virtuelle Umgebung wieder zu aktivieren und `python app.py` auszuführen.

## Daten

Die Datei `data/ligue1-2024-25.json` stammt aus [OpenFootball football.json](https://github.com/openfootball/football.json/blob/master/2024-25/fr.1.json). OpenFootball stellt die Daten als CC0/Public Domain bereit. Die Datei enthält 306 Spiele mit Endresultaten von 18 Teams. Verfügbar sind unter anderem Spieltag, Datum, Teams und Resultate. Spielerstatistiken wie Torschützen sind in diesem Datensatz nicht enthalten. Die lokale Kopie ermöglicht die Nutzung ohne API-Schlüssel oder Internetverbindung.

## Funktionen

- PSG- und Saisonübersicht
- Spielsuche und Filter
- Teamstatistiken und Teamvergleich
- Berechnete Rangliste
