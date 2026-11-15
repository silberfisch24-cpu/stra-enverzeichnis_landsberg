"""Verzeichnis + OSM -> docs/strassen.geojson (Simplestyle-Farben) + daten/nicht_zugeordnet.csv

Ablauf: jeder benannte OSM-Weg wird dem nächstgelegenen Ortsteil-Punkt zugeordnet (Mittelpunkt des Wegs);
dann wird (Ortsteil, normalisierter Name) mit dem Verzeichnis verknüpft. Kommt der Name im Verzeichnis nur in
bestimmten Ortsteilen vor, entscheidet unter diesen die Nähe (sonst der nächste Ortsteil überhaupt).
Gleiche Straße in mehreren Ortsteilen bleibt dadurch getrennt. Einträge mit Zusatz (Hausnr./ab/bis) lassen sich nicht auf Wegstücke aufteilen:
es gilt der Eintrag ohne Zusatz; gibt es nur Zusatz-Einträge, der erste.
"""
import csv, json, math, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FARBE = {"S": "#1f77d4", "K": "#f08a00", "P": "#d62728", "L": "#2ca02c", "gemischt": "#8e44ad", None: "#9e9e9e"}
# OSM-Ortsnamen, die im Verzeichnis anders heißen (Ortsteil mit mehreren Punkten möglich)
ORT_ALIAS = {"Wölls-Petersdorf": "Petersdorf", "Obermaschwitz": "Maschwitz", "Untermaschwitz": "Maschwitz"}
ZUST = {"A": "Anlieger", "B": "Baulastträger"}
KEINE_STRASSE = {"platform", "rest_area", "services", "steps"}  # Haltestellen, Rastplätze …: nur zeichnen, wenn im Verzeichnis
NAME = {"S": "Stadt", "K": "Kreis", "P": "Privat", "L": "Land", "gemischt": "gemischt (Text beachten)", None: "nicht im Verzeichnis"}


def norm(s):
    s = s.lower().replace("ß", "ss").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    s = re.sub(r"str\b\.?", "strasse", s)
    s = re.sub(r"(?<=\w)(strasse)\b", r"\1", s)
    return re.sub(r"[^a-z0-9]", "", s)


def lesen():
    with open(ROOT / "daten/verzeichnis.csv", encoding="utf-8") as f:
        verz = list(csv.DictReader(f))
    anp = defaultdict(list)  # norm(OSM-Name) -> [(Ortsteil oder "", Verzeichnisname, vermutet)]
    p = ROOT / "daten/namensanpassungen.csv"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                anp[norm(r["strasse_osm"])].append((r["ortsteil"], r["strasse_verzeichnis"], r.get("vermutet", "") == "ja"))
    offen_manuell = {}
    p = ROOT / "daten/offene_strassen.csv"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                offen_manuell[(r["ortsteil"], norm(r["strasse"]))] = (r["osm_status"], r["notiz"])
    # Abschnittszuordnung (Ergebnis des OSM-Auftrags): einzelne Wege bekommen die Zeile mit Zusatz
    abschnitt = {}
    p = ROOT / "daten/zusatz_zuordnung.csv"
    if p.exists():
        zeilen = {(r["ortsteil"], r["strasse"], r["zusatz"]): r for r in verz if r["zusatz"]}
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                z = zeilen.get((r["ortsteil"], r["strasse"], r["zusatz"]))
                if z and r.get("osm_way_id", "").strip().isdigit():
                    abschnitt[int(r["osm_way_id"])] = z
    return verz, anp, offen_manuell, abschnitt


def abstand(a, b):
    return math.hypot((a[0] - b[0]) * math.cos(math.radians(a[1])), a[1] - b[1])


def main():
    verz, anp, offen_manuell, abschnitt = lesen()
    eintrag, zusaetze = {}, defaultdict(list)
    for r in verz:
        k = (r["ortsteil"], norm(r["strasse"]))
        if r["zusatz"]:  # Zusätze (Hausnr., Rondell …) bleiben als Hinweis erhalten, werden aber nicht gematcht
            zusaetze[k].append(f'{r["zusatz"]}: {NAME[r["baulast"]]}, Reinigung {ZUST[r["reinigung_fahrbahn"]]}, Winterdienst {ZUST[r["winterdienst"]]}')
        if k not in eintrag or (eintrag[k]["zusatz"] and not r["zusatz"]):
            eintrag[k] = r
    orte_osm = json.loads((ROOT / "daten/osm_orte.json").read_text("utf-8"))["elements"]
    ortsteile = {r["ortsteil"] for r in verz}
    punkte = defaultdict(list)
    for e in orte_osm:
        n = ORT_ALIAS.get(e.get("tags", {}).get("name"), e.get("tags", {}).get("name"))
        if n in ortsteile and "lon" in e:
            punkte[n].append((e["lon"], e["lat"]))
    fehlend = sorted(ortsteile - set(punkte))
    if fehlend:
        print("Ortsteil ohne OSM-Punkt:", fehlend)
    wege = json.loads((ROOT / "daten/osm_strassen.json").read_text("utf-8"))["elements"]

    feats, genutzt, offen_osm = [], {}, []
    wege_je_strasse = defaultdict(list)
    for w in wege:
        geo = [(p["lon"], p["lat"]) for p in w.get("geometry", [])]
        if len(geo) < 2:
            continue
        name = w["tags"]["name"]
        mitte = geo[len(geo) // 2]
        # Namensvarianten (Name, nur in diesem Ortsteil, Status): OSM-Schreibweise und Namensliste.
        # Ein Alias gilt nur im angegebenen Ortsteil (leer = überall), damit gleichnamige Straßen anderer Orte nicht greifen.
        varianten = [(norm(name), "", "gefunden")] + [
            (norm(v), o, "Alias (wahrscheinlich)" if verm else "Alias") for o, v, verm in anp.get(norm(name), [])]
        # Ortsteile, in denen das Verzeichnis eine Variante kennt; unter ihnen entscheidet die Nähe
        def passt(o):
            return [(n, st) for n, nur, st in varianten if (o, n) in eintrag and nur in ("", o)]
        kand = [o for o in punkte if passt(o)]
        dist = lambda o: min(abstand(mitte, q) for q in punkte[o])
        ort = min(kand or punkte, key=dist) if punkte else ""
        k, status = ((ort, passt(ort)[0][0]), passt(ort)[0][1]) if kand else ((ort, varianten[0][0]), "")
        r = eintrag.get(k)
        if r:
            genutzt[k] = status
            wege_je_strasse[k].append((w["id"], geo))
        hinweis = "; ".join(filter(None, [r["baulast_text"]] + zusaetze[k])) if r else ""
        if r and w["id"] in abschnitt:  # Abschnitt laut Zusatzzeile
            r = abschnitt[w["id"]]
            hinweis = f'Abschnitt {r["zusatz"].strip("()")}'
        if not r and w["tags"].get("highway") in KEINE_STRASSE:
            continue
        b = r["baulast"] if r else None
        feats.append({"type": "Feature",
                      "properties": {"osm_id": w["id"], "name": name, "ortsteil": ort, "baulast": NAME[b],
                                     "hinweis": hinweis,
                                     "reinigung": r["reinigung_fahrbahn"] if r else "", "winterdienst": r["winterdienst"] if r else "",
                                     "gehweg": r["reinigung_gehweg"] if r else "", "art": r["strassenart"] if r else "",
                                     "osm_status": status if r else "nicht im Verzeichnis",
                                     "stroke": FARBE[b], "stroke-width": 4 if r else 2, "stroke-opacity": 0.9 if r else 0.5},
                      "geometry": {"type": "LineString", "coordinates": geo}})
        if not r:
            offen_osm.append((ort, name, w["tags"].get("highway", "")))
    feats.sort(key=lambda f: f["properties"]["baulast"] == NAME[None], reverse=True)  # unzugeordnet unten
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/strassen.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False), encoding="utf-8")

    # Zusatz-Fälle: Zeilen mit Hausnr./ab/bis/Rondell – nicht automatisch auf Wegstücke aufteilbar
    zf = []
    for r in verz:
        k = (r["ortsteil"], norm(r["strasse"]))
        if not r["zusatz"] or k not in genutzt:
            continue
        h = eintrag[k]
        ids = [i for i, _ in wege_je_strasse[k]]
        laenge = sum(sum(abstand(a, b) for a, b in zip(g, g[1:])) for _, g in wege_je_strasse[k]) * 111.2
        zf.append({"ortsteil": r["ortsteil"], "strasse": r["strasse"], "zusatz": r["zusatz"],
                   "baulast": NAME[r["baulast"]], "reinigung": ZUST[r["reinigung_fahrbahn"]], "winterdienst": ZUST[r["winterdienst"]],
                   "haupteintrag": f'{NAME[h["baulast"]]}, Reinigung {ZUST[h["reinigung_fahrbahn"]]}, Winterdienst {ZUST[h["winterdienst"]]}' if not h["zusatz"] else "(nur Zusatzzeilen)",
                   "abweichend": "ja" if (not h["zusatz"] and (h["baulast"], h["reinigung_fahrbahn"], h["winterdienst"]) != (r["baulast"], r["reinigung_fahrbahn"], r["winterdienst"])) else "nein",
                   "osm_wege": len(ids), "laenge_km": round(laenge, 2), "osm_way_ids": " ".join(map(str, ids))})
    with open(ROOT / "daten/zusatzfaelle.csv", "w", newline="", encoding="utf-8") as f:
        w_ = csv.DictWriter(f, fieldnames=list(zf[0])); w_.writeheader(); w_.writerows(zf)
    print("Zusatzfälle:", len(zf), "davon abweichend vom Haupteintrag:", sum(x["abweichend"] == "ja" for x in zf))
    ohne_osm = [(k, v) for k, v in eintrag.items() if k not in genutzt]
    offene = []
    for (o, n), v in sorted(ohne_osm):
        st, notiz = offen_manuell.get((o, n), ("nicht vorhanden", ""))
        offene.append({"ortsteil": o, "strasse": v["strasse_original"], "osm_status": st, "notiz": notiz,
                       "baulast": NAME[v["baulast"]]})
    (ROOT / "docs/offene.json").write_text(json.dumps(offene, ensure_ascii=False), encoding="utf-8")
    md = ["# Offene Straßen (im Verzeichnis, aber ohne OSM-Weg)", "",
          "Wird vom Skript `03_karte_bauen.py` erzeugt. Status und Notizen pflegt man in `daten/offene_strassen.csv`.", "",
          "| Ortsteil | Straße | Baulast | Status | Notiz |", "|---|---|---|---|---|"]
    md += [f"| {x['ortsteil']} | {x['strasse']} | {x['baulast']} | {x['osm_status']} | {x['notiz']} |" for x in offene]
    (ROOT / "docs/offene-strassen.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    ohne_osm = [(k[0], v["strasse_original"]) for k, v in ohne_osm]
    with open(ROOT / "daten/nicht_zugeordnet.csv", "w", newline="", encoding="utf-8") as f:
        w_ = csv.writer(f); w_.writerow(["art", "ortsteil", "strasse", "osm_typ"])
        w_.writerows(("Verzeichnis ohne OSM-Weg", o, s_, "") for o, s_ in sorted(ohne_osm))
        w_.writerows(("OSM-Weg ohne Verzeichnis", o, s_, t_) for o, s_, t_ in sorted(set(offen_osm)))
    from collections import Counter
    print("Status:", dict(Counter(genutzt.values())))
    print(f"{len(eintrag)} Straßen im Verzeichnis, davon {len(genutzt)} in OSM gefunden; "
          f"{len(ohne_osm)} ohne OSM-Weg, {len({(a, b_) for a, b_, _ in offen_osm})} OSM-Namen ohne Verzeichniseintrag")


if __name__ == "__main__":
    main()
