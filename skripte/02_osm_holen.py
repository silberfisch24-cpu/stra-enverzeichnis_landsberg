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
    # unbenannte Wege (Zufahrten, Stichwege): Abschnitte mit Hausnummern hängen oft an solchen Wegen
    "osm_unbenannt.json": f'[out:json][timeout:180];{GEBIET}way(area.g)["highway"][!"name"]["highway"!~"^(footway|cycleway|steps|corridor|bridleway|proposed|construction|platform|elevator)$"];out geom tags;',
    # Adresspunkte (Hausnummern) mit Mittelpunkt
    "osm_adressen_roh.json": f'[out:json][timeout:180];{GEBIET}nwr(area.g)["addr:housenumber"];out center tags;',
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
    if datei == "osm_adressen_roh.json":  # nur nutzbare Felder behalten (Größe)
        a = []
        for e in d.get("elements", []):
            c = e if "lat" in e else e.get("center", {})
            t = e.get("tags", {})
            if "lat" in c:
                a.append({"lat": c["lat"], "lon": c["lon"], "hn": t.get("addr:housenumber", ""),
                          "strasse": t.get("addr:street", ""), "ort": t.get("addr:place", "") or t.get("addr:suburb", "")})
        d, datei = {"elements": a}, "osm_adressen.json"
    elif datei == "osm_unbenannt.json":  # Tags auf das Nötige kürzen
        for e in d.get("elements", []):
            e["tags"] = {k: v for k, v in e.get("tags", {}).items() if k in ("highway", "service", "access", "ref", "surface")}
    (DATEN / datei).write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print(datei, len(d.get("elements", [])), "Elemente")


# Wege aus daten/abschnitte.csv, die weder benannte Straße noch unbenannter Weg sind (z. B. Mittelinseln als Fläche)
import csv  # noqa: E402

pa = DATEN / "abschnitte.csv"
sonst = {"elements": []}
if pa.exists():
    bekannt = set()
    for f in ("osm_strassen.json", "osm_unbenannt.json"):
        bekannt |= {e["id"] for e in json.loads((DATEN / f).read_text("utf-8"))["elements"]}
    with open(pa, encoding="utf-8") as f:
        ids = sorted({int(r["osm_way_id"]) for r in csv.DictReader(f) if r["osm_way_id"].strip().isdigit()} - bekannt)
    if ids:
        sonst = holen(f'[out:json][timeout:60];way(id:{",".join(map(str, ids))});out geom tags;')
        for e in sonst.get("elements", []):
            e["tags"] = {k: v for k, v in e.get("tags", {}).items() if k in ("highway", "landuse", "leisure", "area", "name", "ref")}
(DATEN / "osm_sonstige.json").write_text(json.dumps(sonst, ensure_ascii=False), encoding="utf-8")
print("osm_sonstige.json", len(sonst.get("elements", [])), "Elemente")
