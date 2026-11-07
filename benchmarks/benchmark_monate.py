r"""D1A: beide Monatsalgorithmen direkt aus ihren Commits vergleichen.

Aufruf im Projektordner:
.\.venv\Scripts\python.exe benchmarks/benchmark_monate.py
Dateilesen, Git-Zugriff, Imports und HTML-Rendering liegen ausserhalb der Messung.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import timeit
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
VORHER = "79ae97f8bc344aac0c4f80f4cd92f5f5039a46dc"
NACHHER = "4f687695291b5a48ab92328ebfdc8963248506b4"


def git_datei(commit, dateiname):
    return subprocess.check_output(["git", "show", f"{commit}:{dateiname}"], cwd=ROOT)


def lade_monatsmodul(commit, modulname):
    source = git_datei(commit, "monatsuebersicht.py")
    modul = types.ModuleType(modulname)
    modul.__file__ = str(ROOT / "monatsuebersicht.py")
    sys.modules[modulname] = modul
    exec(compile(source, f"{commit}:monatsuebersicht.py", "exec"), modul.__dict__)
    return modul, hashlib.sha256(source).hexdigest()


def messfall(name, daten, vorher, nachher, anzahl, wiederholungen):
    erwartet = vorher.aggregiere_monate(daten)
    assert nachher.aggregiere_monate(daten) == erwartet
    vor_daten = json.dumps(daten, sort_keys=True)
    for _ in range(3):
        vorher.aggregiere_monate(daten)
        nachher.aggregiere_monate(daten)
    timer = {
        "vorher": timeit.Timer(lambda: vorher.aggregiere_monate(daten)),
        "nachher": timeit.Timer(lambda: nachher.aggregiere_monate(daten)),
    }
    pro_aufruf = {"vorher": [], "nachher": []}
    for runde in range(wiederholungen):
        reihenfolge = ("vorher", "nachher") if runde % 2 == 0 else ("nachher", "vorher")
        for variante in reihenfolge:
            pro_aufruf[variante].append(timer[variante].timeit(number=anzahl) / anzahl)
    assert json.dumps(daten, sort_keys=True) == vor_daten
    assert nachher.aggregiere_monate(daten) == erwartet
    alt = statistics.median(pro_aufruf["vorher"])
    neu = statistics.median(pro_aufruf["nachher"])
    return {
        "name": name, "spiele": len(daten), "monate": len(erwartet),
        "aufrufe_pro_messreihe": anzahl, "messreihen_pro_variante": wiederholungen,
        "sekunden_pro_aufruf": pro_aufruf,
        "median_ms": {"vorher": alt * 1000, "nachher": neu * 1000},
        "min_ms": {key: min(values) * 1000 for key, values in pro_aufruf.items()},
        "max_ms": {key: max(values) * 1000 for key, values in pro_aufruf.items()},
        "faktor_vorher_durch_nachher": alt / neu,
        "zeitreduktion_prozent": (1 - neu / alt) * 100,
        "gleiche_ergebnisse": True, "eingaben_unveraendert": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "lernportfolio/nachweise/d1/benchmark_monate.json")
    parser.add_argument("--repeats", type=int, default=10)
    args = parser.parse_args()
    if args.repeats < 2:
        parser.error("Mindestens zwei Messreihen erforderlich.")
    # Gemeinsam importierte Fachregeln müssen zu beiden verglichenen Ständen passen.
    for dateiname in ("heim_auswaerts.py", "torbilanz.py"):
        alt = git_datei(VORHER, dateiname).decode("utf-8").replace("\r\n", "\n")
        neu = git_datei(NACHHER, dateiname).decode("utf-8").replace("\r\n", "\n")
        aktuell = (ROOT / dateiname).read_text(encoding="utf-8")
        if alt != neu or neu != aktuell:
            raise RuntimeError(f"Gemeinsame Fachregeln verändert: {dateiname}")
    vorher, vorher_hash = lade_monatsmodul(VORHER, "_m323_benchmark_vorher")
    nachher, nachher_hash = lade_monatsmodul(NACHHER, "_m323_benchmark_nachher")
    daten_bytes = git_datei(NACHHER, "data/ligue1-2024-25.json")
    saison = json.loads(daten_bytes)
    spiele = [s for s in saison["matches"] if "Paris Saint-Germain FC" in (s["team1"], s["team2"])]
    assert len(spiele) == 34
    faelle = [
        messfall("Echte PSG-Saison", spiele, vorher, nachher, 2000, args.repeats),
        messfall("Künstlicher Lasttest: Saison 100-fach wiederholt", spiele * 100, vorher, nachher, 20, args.repeats),
    ]
    bericht = {
        "gemessen_am_utc": datetime.now(timezone.utc).isoformat(),
        "vorher_commit": VORHER, "nachher_commit": NACHHER,
        "python": sys.version, "system": platform.platform(), "prozessor": platform.processor(),
        "timer": "timeit / perf_counter", "timer_aufloesung_sekunden": time.get_clock_info("perf_counter").resolution,
        "aufwaermaufrufe_pro_variante": 3, "reihenfolge": "abwechselnd vorher/nachher und nachher/vorher",
        "gc_waehrend_timeit": "deaktiviert durch timeit; danach wiederhergestellt",
        "messumfang": "Nur aggregiere_monate; ohne Datei-I/O, Imports, Git und HTML",
        "quellcode_sha256": {"vorher": vorher_hash, "nachher": nachher_hash},
        "datensatz_sha256": hashlib.sha256(daten_bytes).hexdigest(), "faelle": faelle,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bericht, ensure_ascii=False, indent=2), encoding="utf-8")
    for fall in faelle:
        print(f"{fall['spiele']} Spiele: vorher {fall['median_ms']['vorher']:.6f} ms, "
              f"nachher {fall['median_ms']['nachher']:.6f} ms, "
              f"Faktor {fall['faktor_vorher_durch_nachher']:.3f}, "
              f"Zeitreduktion {fall['zeitreduktion_prozent']:.2f}%")
    print(f"Rohmessungen: {args.output}")


if __name__ == "__main__":
    main()
