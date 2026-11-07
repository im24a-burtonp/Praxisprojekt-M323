"""Gemeinsamer Datei-Zugriff; fachliche Berechnungen bleiben in ihren Modulen."""
from pathlib import Path
import json

DATA_FILE = Path(__file__).parent / "data" / "ligue1-2024-25.json"


def lade_saison() -> dict:
    """Liest pro Aufruf die Saisondatei; kein Cache und keine globalen Spieldaten."""
    with DATA_FILE.open(encoding="utf-8") as file:
        return json.load(file)
