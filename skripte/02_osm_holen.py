"""OSM-Straßen und Ortsteil-Punkte der Stadt Landsberg (Saalekreis) per Overpass holen -> daten/osm_*.json
Braucht Netz (Overpass); läuft lokal oder im GitHub-Workflow."""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

DATEN = Path(__file__).resolve().parent.parent / "daten"
SERVER = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]
# Gemeindegebiet: Verwaltungsgrenze 'Landsberg' (admin_level 8) im Saalekreis
GEBIET = 'area["boundary"="administrative"]["admin_level"="8"]["name"="Landsberg"]["de:amtlicher_gemeindeschluessel"~"^15088"]->.g;'
ABFRAGEN = {
    "osm_strassen.json": f'[out:json][timeout:180];{GEBIET}way(area.g)["highway"]["name"];out geom tags;',
    "osm_orte.json": f'[out:json][timeout:60];{GEBIET}(node(area.g)["place"];);out tags center;',
}


def holen(q):
    letzte = None
    for url in SERVER:
        for versuch in range(3):
            try:
                req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(),
                                             headers={"User-Agent": "strassenverzeichnis-landsberg/1.0"})
                with urllib.request.urlopen(req, timeout=240) as r:
                    return json.load(r)
            except Exception as e:  # noqa: BLE001
                letzte = e; time.sleep(5 * (versuch + 1))
    sys.exit(f"Overpass nicht erreichbar: {letzte}")


for datei, q in ABFRAGEN.items():
    d = holen(q)
    (DATEN / datei).write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print(datei, len(d.get("elements", [])), "Elemente")
