"""Liest den echten Ausgangscode für D1 aus der lokalen Git-Historie."""
from functools import lru_cache
from pathlib import Path
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "79ae97f8bc344aac0c4f80f4cd92f5f5039a46dc"
VERGLEICHS_URLS = (
    "/", "/tore", "/tore-imperativ", "/spiele", "/spiele?ergebnis=sieg",
    "/spiele?gegner=Marseille", "/spiele?ergebnis=falsch", "/heim-auswaerts",
    "/monate", "/monate?sortierung=punkte", "/monate?sortierung=tore",
    "/monate?sortierung=falsch",
)


def lade_historisches_modul(dateiname, modulname):
    source = subprocess.check_output(
        ["git", "show", f"{BASELINE_COMMIT}:{dateiname}"], cwd=ROOT,
    ).decode("utf-8")
    modul = types.ModuleType(modulname)
    modul.__file__ = str(ROOT / dateiname)
    sys.modules[modulname] = modul
    exec(compile(source, f"{BASELINE_COMMIT}:{dateiname}", "exec"), modul.__dict__)
    return modul


@lru_cache(maxsize=1)
def vorher_module():
    monate = lade_historisches_modul("monatsuebersicht.py", "_m323_monate_vorher")
    routes = lade_historisches_modul("app.py", "_m323_app_vorher")
    # Die alte Route muss auch die alte Aggregation aufrufen, nicht den aktuellen Import.
    routes.erstelle_monatsuebersicht = monate.erstelle_monatsuebersicht
    return routes, monate
