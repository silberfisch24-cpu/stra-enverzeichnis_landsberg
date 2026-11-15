"""Verzeichnis + OSM -> docs/strassen.geojson (Simplestyle-Farben) + daten/nicht_zugeordnet.csv

Ablauf: jeder benannte OSM-Weg wird dem nächstgelegenen Ortsteil-Punkt zugeordnet (Mittelpunkt des Wegs);
dann wird (Ortsteil, normalisierter Name) mit dem Verzeichnis verknüpft. Gleiche Straße in mehreren Ortsteilen
bleibt dadurch getrennt. Einträge mit Zusatz (Hausnr./ab/bis) lassen sich nicht auf Wegstücke aufteilen:
es gilt der Eintrag ohne Zusatz; gibt es nur Zusatz-Einträge, der erste.
"""
import csv, json, math, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FARBE = {"S": "#1f77d4", "K": "#f08a00", "P": "#d62728", "L": "#2ca02c", "gemischt": "#8e44ad", None: "#9e9e9e"}
NAME = {"S": "Stadt", "K": "Kreis", "P": "Privat", "L": "Land", "gemischt": "gemischt (Text beachten)", None: "nicht im Verzeichnis"}


def norm(s):
    s = s.lower().replace("ß", "ss").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    s = re.sub(r"str\b\.?", "strasse", s)
    s = re.sub(r"(?<=\w)(strasse)\b", r"\1", s)
    return re.sub(r"[^a-z0-9]", "", s)


def lesen():
    with open(ROOT / "daten/verzeichnis.csv", encoding="utf-8") as f:
        verz = list(csv.DictReader(f))
    anp = {}
    p = ROOT / "daten/namensanpassungen.csv"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                anp[(r["ortsteil"], norm(r["strasse_osm"]))] = r["strasse_verzeichnis"]
    return verz, anp


def abstand(a, b):
    return math.hypot((a[0] - b[0]) * math.cos(math.radians(a[1])), a[1] - b[1])


def main():
    verz, anp = lesen()
    eintrag = {}
    for r in verz:
        k = (r["ortsteil"], norm(r["strasse"]))
        if k not in eintrag or (eintrag[k]["zusatz"] and not r["zusatz"]):
            eintrag[k] = r
    orte_osm = json.loads((ROOT / "daten/osm_orte.json").read_text("utf-8"))["elements"]
    ortsteile = {r["ortsteil"] for r in verz}
    punkte = {}
    for e in orte_osm:
        n = e.get("tags", {}).get("name")
        if n in ortsteile and "lon" in e:
            punkte[n] = (e["lon"], e["lat"])
    fehlend = sorted(ortsteile - set(punkte))
    if fehlend:
        print("Ortsteil ohne OSM-Punkt:", fehlend)
    wege = json.loads((ROOT / "daten/osm_strassen.json").read_text("utf-8"))["elements"]

    feats, genutzt, offen = [], set(), []
    for w in wege:
        geo = [(p["lon"], p["lat"]) for p in w.get("geometry", [])]
        if len(geo) < 2:
            continue
        name = w["tags"]["name"]
        mitte = geo[len(geo) // 2]
        ort = min(punkte, key=lambda o: abstand(mitte, punkte[o])) if punkte else ""
        k = (ort, norm(name))
        if k in anp:
            k = (ort, norm(anp[k]))
        r = eintrag.get(k)
        if r:
            genutzt.add(k)
        b = r["baulast"] if r else None
        feats.append({"type": "Feature",
                      "properties": {"name": name, "ortsteil": ort, "baulast": NAME[b],
                                     "hinweis": (r["baulast_text"] or r["zusatz"]) if r else "",
                                     "stroke": FARBE[b], "stroke-width": 4 if r else 2, "stroke-opacity": 0.9 if r else 0.5},
                      "geometry": {"type": "LineString", "coordinates": geo}})
        if not r:
            offen.append((ort, name))
    feats.sort(key=lambda f: f["properties"]["baulast"] == NAME[None], reverse=True)  # unzugeordnet unten
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/strassen.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False), encoding="utf-8")

    ohne_osm = [(k[0], v["strasse_original"]) for k, v in eintrag.items() if k not in genutzt]
    with open(ROOT / "daten/nicht_zugeordnet.csv", "w", newline="", encoding="utf-8") as f:
        w_ = csv.writer(f); w_.writerow(["art", "ortsteil", "strasse"])
        w_.writerows(("Verzeichnis ohne OSM-Weg", o, s) for o, s in sorted(ohne_osm))
        w_.writerows(("OSM-Weg ohne Verzeichnis", o, s) for o, s in sorted(set(offen)))
    print(f"{len(eintrag)} Straßen im Verzeichnis, davon {len(genutzt)} in OSM gefunden; "
          f"{len(ohne_osm)} ohne OSM-Weg, {len(set(offen))} OSM-Namen ohne Verzeichniseintrag")


if __name__ == "__main__":
    main()
