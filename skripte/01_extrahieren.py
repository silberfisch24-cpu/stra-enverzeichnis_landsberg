"""Straßenverzeichnis (PDF) -> daten/verzeichnis.csv

Spalten: ortsteil, strasse_original, strasse (ohne Zusatz), zusatz, baulast, baulast_text,
strassenart, reinigung_fahrbahn, reinigung_gehweg, winterdienst
Der Ortsteil steht im PDF nur in der ersten Zeile eines Blocks und wird fortgeschrieben.
baulast = L/K/S/P; bei gemischter Baulast ("innerorts ab Kreuzung: S; Umgehungsstraße: K")
steht 'gemischt' und der Originaltext in baulast_text.
"""
import csv, re
from pathlib import Path
import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
PDF = sorted((ROOT / "daten").glob("strassenverzeichnis_*.pdf"))[-1]
AUS = ROOT / "daten" / "verzeichnis.csv"


def sauber(s):
    return re.sub(r"\s+", " ", (s or "").replace("\n", " ")).strip()


def zerlegen(name):
    """'Anger (Hausnr. 6 - 22)' -> ('Anger', '(Hausnr. 6 - 22)'); 'X ab Y bis Z' -> ('X', 'ab Y bis Z')"""
    name = re.sub(r"\s*/\s*Ortsteil\s.*$", "", name)  # "Leipziger Straße/ Ortsteil Sietzsch"
    name = re.sub(r"(\w)- (\w)", r"\1\2", name)  # Silbentrennung im PDF
    m = re.match(r"^(.*?)\s*(\(.*\))$", name)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r"^(.*?)\s+((?:ab|bis|Hausnr\.|zwischen|Einmündung|Rondell)\s.*)$", name)
    if m:
        return m.group(1), m.group(2)
    return name, ""


rows, ortsteil = [], ""
with pdfplumber.open(PDF) as pdf:
    for seite in pdf.pages:
        for tab in seite.extract_tables():
            for r in tab:
                r = [sauber(c) for c in r] + [""] * 7
                if r[0] == "Ortsteil" or not r[1] or r[1].startswith("Fahrbahn") or r[4] in ("Fahrbahn",):
                    continue
                if r[0]:
                    ortsteil = r[0]
                name = r[1]
                strasse, zusatz = zerlegen(name)
                b = r[2]
                baulast = b if b in ("L", "K", "S", "P") else "gemischt"
                rows.append({
                    "ortsteil": ortsteil, "strasse_original": name, "strasse": strasse, "zusatz": zusatz,
                    "baulast": baulast, "baulast_text": b if baulast == "gemischt" else "",
                    "strassenart": r[3], "reinigung_fahrbahn": r[4], "reinigung_gehweg": r[5], "winterdienst": r[6],
                })

with open(AUS, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)

from collections import Counter
print(len(rows), "Zeilen,", len({r["ortsteil"] for r in rows}), "Ortsteile")
print(Counter(r["baulast"] for r in rows))
print("ohne Reinigung:", [r["strasse_original"] for r in rows if r["reinigung_fahrbahn"] not in ("A", "B")][:10])
