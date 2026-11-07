# Ligue 1 – Saisonrückblick 2024/25

Ein Flask-Praxisprojekt für Modul 323. Die Anwendung soll die Saison 2024/25 der französischen Ligue 1 übersichtlich auswerten, mit besonderem Blick auf Paris Saint-Germain.

## Lokal starten (Windows PowerShell)

Voraussetzung ist eine installierte Version von Python. Öffne PowerShell im Projektordner und führe die folgenden Befehle aus:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Öffne danach <http://127.0.0.1:5000/> im Browser. Mit `Strg+C` im Terminal stoppst du die Anwendung. Bei späteren Starts genügt `.\.venv\Scripts\python.exe app.py`. Die Aktivierung der virtuellen Umgebung ist bei diesen Befehlen nicht nötig.

## Daten

Die Datei `data/ligue1-2024-25.json` stammt aus [OpenFootball football.json](https://github.com/openfootball/football.json/blob/master/2024-25/fr.1.json). OpenFootball stellt die Daten als CC0/Public Domain bereit. Die Datei enthält 306 Spiele mit Endresultaten von 18 Teams. Verfügbar sind unter anderem Spieltag, Datum, Teams und Resultate. Spielerstatistiken wie Torschützen sind in diesem Datensatz nicht enthalten. Die lokale Kopie ermöglicht die Nutzung ohne API-Schlüssel oder Internetverbindung.

## Funktionen

- PSG-Saisonstatistik mit Siegen, Unentschieden und Niederlagen
- Torbilanz mit erzielten Toren, Gegentoren und Tordifferenz
- Spielsuche nach Ergebnis aus PSG-Sicht und Gegnername
- Heim-/Auswärtsvergleich mit Spielen, Punkten und Toren
- Monatsübersicht mit Sortierung nach Monat, Punkten oder Toren

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Die Historientests lesen den Ausgangscode aus Git. Dafür müssen Git und die vollständige Repository-Historie mit den Commits `79ae97f` und `4f68769` verfügbar sein. Die Tests prüfen Berechnungen, Randfälle und die Flask-Routen.

## Performance-Messung

```powershell
.\.venv\Scripts\python.exe benchmarks/benchmark_monate.py --output lernportfolio/nachweise/d1/benchmark_neu.json
```

Das Skript vergleicht die Monatsaggregation aus beiden Commits. Dateizugriff und HTML-Rendering werden nicht mitgemessen. Der zusätzliche Lasttest wiederholt vorhandene Spiele künstlich; er enthält keine weiteren historischen Spiele. Der separate Ausgabepfad lässt die ursprünglichen Messdaten für D1A unverändert.
