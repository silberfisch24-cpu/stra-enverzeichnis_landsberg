"""Verzeichnis + OSM -> docs/strassen.geojson (Simplestyle-Farben) + daten/nicht_zugeordnet.csv

Ablauf: jeder benannte OSM-Weg wird dem nächstgelegenen Ortsteil-Punkt zugeordnet (Mittelpunkt des Wegs);
dann wird (Ortsteil, normalisierter Name) mit dem Verzeichnis verknüpft. Kommt der Name im Verzeichnis nur in
bestimmten Ortsteilen vor, entscheidet unter diesen die Nähe (sonst der nächste Ortsteil überhaupt).
Gleiche Straße in mehreren Ortsteilen bleibt dadurch getrennt. Einträge mit Zusatz (Hausnr./ab/bis) lassen sich nicht auf Wegstücke aufteilen:
es gilt der Eintrag ohne Zusatz; gibt es nur Zusatz-Einträge, der erste.
"""
import csv, json, math, re, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import laenge as weg_laenge, projektion, zerlege  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FARBE = {"S": "#1f77d4", "K": "#f08a00", "P": "#d62728", "L": "#2ca02c", "gemischt": "#8e44ad", None: "#9e9e9e"}
# OSM-Ortsnamen, die im Verzeichnis anders heißen (Ortsteil mit mehreren Punkten möglich)
ORT_ALIAS = {"Wölls-Petersdorf": "Petersdorf", "Obermaschwitz": "Maschwitz", "Untermaschwitz": "Maschwitz"}
ZUST = {"A": "Anlieger", "B": "Baulastträger"}
# Ab welcher Einstufung aus abschnitte.csv eine Zuordnung auf der Karte als "unsicher" gilt (hoch < mittel < niedrig)
UNSICHER = {"niedrig"}
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
    # Abweichungen vom PDF, die der Auftraggeber ausdrücklich festgelegt hat (mit Begründung)
    pk = ROOT / "daten/korrekturen_verzeichnis.csv"
    if pk.exists():
        with open(pk, encoding="utf-8") as f:
            for k in csv.DictReader(f):
                for r in verz:
                    if (r["ortsteil"], r["strasse"], r["zusatz"]) == (k["ortsteil"], k["strasse"], k["zusatz"]):
                        r[k["feld"]] = k["wert"]
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
    # Abschnitte (Ergebnis des OSM-Auftrags v2): Weg, optional Teilstück von/bis, Art, Konfidenz
    absch = []
    p = ROOT / "daten/abschnitte.csv"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            absch = list(csv.DictReader(f))
    return verz, anp, offen_manuell, absch


def abstand(a, b):
    return math.hypot((a[0] - b[0]) * math.cos(math.radians(a[1])), a[1] - b[1])


def merkmal(wid, name, ort, teil, r, hinweis, status, pl, flaeche=False):
    """Ein Kartenmerkmal; pl = Abschnitt (Nutzlast aus abschnitte.csv) überschreibt die Verzeichniszeile."""
    extra = {}
    if pl:
        z, a = pl["zeile"], pl["a"]
        r, hinweis, status = z, f'Abschnitt {z["zusatz"].strip("()")}', "Abschnitt"
        ort = z["ortsteil"]  # der Ortsteil der Verzeichniszeile gilt, nicht der nächstgelegene Ortsteil-Punkt
        extra = {"fall": pl["fall"], "a_art": a["art"], "a_konf": a["konfidenz"], "a_grund": a["grundlage"],
                 "a_notiz": a["notiz"], "pruefen": a["konfidenz"] in UNSICHER or a["art"] == "E"}
    b = r["baulast"] if r else None
    return {"type": "Feature",
            "properties": {"osm_id": wid, "name": name, "ortsteil": ort, "baulast": NAME[b], "hinweis": hinweis,
                           "reinigung": r["reinigung_fahrbahn"] if r else "", "winterdienst": r["winterdienst"] if r else "",
                           "gehweg": r["reinigung_gehweg"] if r else "", "art": r["strassenart"] if r else "",
                           "osm_status": status if r else "nicht im Verzeichnis",
                           "stroke": FARBE[b], "stroke-width": 4 if r else 2, "stroke-opacity": 0.9 if r else 0.5, **extra},
            "geometry": ({"type": "Polygon", "coordinates": [[list(q) for q in teil]]} if flaeche
                         else {"type": "LineString", "coordinates": [list(q) for q in teil]})}


def main():
    verz, anp, offen_manuell, absch = lesen()
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
    unben = {}
    pu = ROOT / "daten/osm_unbenannt.json"
    if pu.exists():
        for e in json.loads(pu.read_text("utf-8"))["elements"]:
            g = [(q["lon"], q["lat"]) for q in e.get("geometry", [])]
            if len(g) >= 2:
                unben[e["id"]] = g
    geom = {w["id"]: [(q["lon"], q["lat"]) for q in w.get("geometry", [])] for w in wege}
    geom.update(unben)
    flaechen = set()  # geschlossene Wege ohne highway (z. B. landuse=grass): als Fläche zeichnen
    ps = ROOT / "daten/osm_sonstige.json"
    if ps.exists():
        for e in json.loads(ps.read_text("utf-8"))["elements"]:
            g = [(q["lon"], q["lat"]) for q in e.get("geometry", [])]
            if len(g) >= 2:
                geom[e["id"]] = g
                if "highway" not in e.get("tags", {}) and len(g) >= 4 and g[0] == g[-1]:
                    flaechen.add(e["id"])
    zeilen = {(r["ortsteil"], r["strasse"], r["zusatz"]): r for r in verz if r["zusatz"]}
    faelle = {k: i for i, k in enumerate(sorted(zeilen))}
    schnitte = defaultdict(list)  # Weg-ID -> [(s0, s1, Nutzlast)] (Bogenlängen in m)
    for a in absch:
        key = (a["ortsteil"], a["strasse"], a["zusatz"])
        wid = a["osm_way_id"].strip()
        if key not in zeilen or not wid.isdigit():
            continue
        if int(wid) not in geom:
            print("Weg nicht in den OSM-Daten:", wid, a["strasse"], a["zusatz"])
            continue
        g = geom[int(wid)]
        if a["von_lat"].strip() and a["bis_lat"].strip():
            s0 = projektion(g, (float(a["von_lon"]), float(a["von_lat"])))[0]
            s1 = projektion(g, (float(a["bis_lon"]), float(a["bis_lat"])))[0]
        else:
            s0, s1 = 0.0, weg_laenge(g)  # ganzer Weg (Regel: Stichwege werden immer ganz zugeordnet)
        schnitte[int(wid)].append((min(s0, s1), max(s0, s1), {"zeile": zeilen[key], "a": a, "fall": faelle[key]}))

    def stuecke(wid, geo):
        return zerlege(geo, schnitte[wid]) if wid in schnitte else [(geo, None)]

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
        if not r and w["tags"].get("highway") in KEINE_STRASSE and w["id"] not in schnitte:
            continue
        for teil, pl in stuecke(w["id"], geo):
            feats.append(merkmal(w["id"], name, ort, teil, r, hinweis, status, pl))
        if not r:
            offen_osm.append((ort, name, w["tags"].get("highway", "")))
    benannt = {w["id"] for w in wege}
    for wid in schnitte:  # unbenannte Wege und Flächen: nur die Abschnitte zeichnen, Rest hat keine Verzeichnisangabe
        if wid in benannt:
            continue
        for teil, pl in stuecke(wid, geom[wid]):
            if pl:
                z = pl["zeile"]
                nm = f'{z["strasse"]} ({"Fläche" if wid in flaechen else "unbenannter Weg"})'
                feats.append(merkmal(wid, nm, z["ortsteil"], teil, None, "", "", pl, flaeche=wid in flaechen))
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
    # Überlagerung "geteilte Straßen": je Zusatzzeile die gezeichneten Linien, Art und Sicherheit aus abschnitte.csv
    linien = defaultdict(list)
    for f_ in feats:
        if "fall" in f_["properties"]:
            cc = f_["geometry"]["coordinates"]
            cc = cc[0] if f_["geometry"]["type"] == "Polygon" else cc
            linien[f_["properties"]["fall"]].append([[c[1], c[0]] for c in cc])
    rang = {"hoch": 0, "mittel": 1, "niedrig": 2}
    zj = []
    for key, i in sorted(faelle.items(), key=lambda kv: kv[1]):
        z = zeilen[key]
        rows = [a for a in absch if (a["ortsteil"], a["strasse"], a["zusatz"]) == key]
        h = eintrag.get((z["ortsteil"], norm(z["strasse"])))
        konf = max((a["konfidenz"] for a in rows), key=lambda c: rang.get(c, 3), default="niedrig")
        arten = sorted({a["art"] for a in rows})
        status = "keine" if not linien[i] else ("pruefen" if konf in UNSICHER else "sicher")
        zj.append({"id": i, "ortsteil": z["ortsteil"], "strasse": z["strasse"], "zusatz": z["zusatz"].strip("()"),
                   "baulast": NAME[z["baulast"]], "reinigung": ZUST[z["reinigung_fahrbahn"]], "winterdienst": ZUST[z["winterdienst"]],
                   "haupt": (None if not h or h["zusatz"] else
                             {"baulast": NAME[h["baulast"]], "reinigung": ZUST[h["reinigung_fahrbahn"]], "winterdienst": ZUST[h["winterdienst"]]}),
                   "art": arten, "konfidenz": konf, "status": status,
                   "grundlage": sorted({a["grundlage"] for a in rows if a["grundlage"]}),
                   "notiz": " | ".join(dict.fromkeys(a["notiz"] for a in rows if a["notiz"])),
                   "linien": linien[i]})
    with open(ROOT / "daten/zusatzfaelle.csv", "w", newline="", encoding="utf-8") as f:
        w_ = csv.DictWriter(f, fieldnames=list(zf[0])); w_.writeheader(); w_.writerows(zf)
    print("Abschnitte:", sum(1 for f_ in feats if "fall" in f_["properties"]), "Teilstücke,",
          sum(1 for f_ in feats if f_["properties"].get("pruefen")), "davon zu prüfen; Zusatzfälle:", {s_: sum(z_["status"] == s_ for z_ in zj) for s_ in ("sicher", "pruefen", "keine")})
    print("Zusatzfälle:", len(zf), "davon abweichend vom Haupteintrag:", sum(x["abweichend"] == "ja" for x in zf))
    ohne_osm = [(k, v) for k, v in eintrag.items() if k not in genutzt]
    offene = []
    for (o, n), v in sorted(ohne_osm):
        st, notiz = offen_manuell.get((o, n), ("nicht vorhanden", ""))
        recherche = next((a["notiz"] for a in absch if a["ortsteil"] == o and norm(a["strasse"]) == n and not a["zusatz"] and a["notiz"]), "")
        offene.append({"ortsteil": o, "strasse": v["strasse_original"], "osm_status": st, "notiz": recherche or notiz,
                       "baulast": NAME[v["baulast"]]})
    for z_ in zj:  # Zusatzzeilen, für die sich keine Linie bestimmen ließ (Art E)
        if z_["status"] == "keine":
            offene.append({"ortsteil": z_["ortsteil"], "strasse": f'{z_["strasse"]} ({z_["zusatz"]})', "osm_status": "keine Zuordnung",
                           "notiz": z_["notiz"], "baulast": z_["baulast"]})
    # Problemfälle für die Karte: nur Unsicheres und Nicht-Zuordenbares; alles andere erscheint einfach korrekt gefärbt
    def mitte(o):
        q = punkte.get(o)
        return [round(sum(c[1] for c in q) / len(q), 5), round(sum(c[0] for c in q) / len(q), 5)] if q else None

    probleme = []
    for z_ in zj:
        if z_["status"] in ("pruefen", "keine"):
            probleme.append({"art": "unsicher" if z_["status"] == "pruefen" else "keine", "ortsteil": z_["ortsteil"],
                             "strasse": z_["strasse"], "zusatz": z_["zusatz"], "baulast": z_["baulast"], "reinigung": z_["reinigung"],
                             "winterdienst": z_["winterdienst"], "haupt": z_["haupt"], "grund": z_["notiz"],
                             "linien": z_["linien"], "mitte": mitte(z_["ortsteil"])})
    for (o, n), v in sorted(ohne_osm):
        x = next(y for y in offene if y["ortsteil"] == o and y["strasse"] == v["strasse_original"])
        probleme.append({"art": "keine", "ortsteil": o, "strasse": v["strasse_original"], "zusatz": "", "baulast": NAME[v["baulast"]],
                         "reinigung": ZUST[v["reinigung_fahrbahn"]], "winterdienst": ZUST[v["winterdienst"]], "haupt": None,
                         "grund": x["notiz"], "linien": [], "mitte": mitte(o)})
    probleme.sort(key=lambda x: (x["ortsteil"], x["strasse"], x["zusatz"]))
    for i, x in enumerate(probleme):
        x["id"] = i
    (ROOT / "docs/probleme.json").write_text(json.dumps(probleme, ensure_ascii=False), encoding="utf-8")
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
