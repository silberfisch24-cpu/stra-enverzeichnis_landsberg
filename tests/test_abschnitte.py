import csv, json, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skripte"))
import geo  # noqa: E402


def _lesen(name):
    with open(ROOT / "daten" / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_teilen_einfach():
    # gerade Linie nach Osten, ca. 223 m (0.003° Länge bei 0° Breite ~ 334 m)
    g = [(0.0, 0.0), (0.001, 0.0), (0.002, 0.0)]
    L = geo.laenge(g)
    teile = geo.zerlege(g, [(L * 0.25, L * 0.75, "x")])
    assert [n for _, n in teile] == [None, "x", None]
    assert abs(geo.laenge(teile[1][0]) - L / 2) < 0.5
    assert teile[0][0][-1] == teile[1][0][0]  # lückenlos


def test_teilen_ueberlappung_kuerzestes_gewinnt():
    g = [(0.0, 0.0), (0.004, 0.0)]
    L = geo.laenge(g)
    teile = geo.zerlege(g, [(0, L, "lang"), (L * 0.4, L * 0.6, "kurz")])
    assert [n for _, n in teile] == ["lang", "kurz", "lang"]


def test_projektion_und_ganzer_weg():
    g = [(0.0, 0.0), (0.002, 0.0)]
    s, d = geo.projektion(g, (0.001, 0.0001))
    assert abs(s - geo.laenge(g) / 2) < 1 and 10 < d < 12
    assert [n for _, n in geo.zerlege(g, [(0, geo.laenge(g), "ganz")])] == ["ganz"]


def test_abschnitte_vollstaendig_und_wege_vorhanden():
    if not (ROOT / "daten/abschnitte.csv").exists():
        pytest.skip("abschnitte.csv fehlt")
    absch = _lesen("abschnitte.csv")
    erwartet = {(r["ortsteil"], r["strasse"], r["zusatz"]) for r in _lesen("zusatzfaelle.csv")}
    erwartet |= {(r["ortsteil"], r["strasse"], "") for r in _lesen("offene_strassen.csv")}
    vorhanden = {(r["ortsteil"], r["strasse"], r["zusatz"]) for r in absch}
    assert erwartet <= vorhanden, f"ohne Zeile: {sorted(erwartet - vorhanden)}"
    ids = {e["id"] for e in json.loads((ROOT / "daten/osm_strassen.json").read_text("utf-8"))["elements"]}
    pu = ROOT / "daten/osm_unbenannt.json"
    if not pu.exists():
        pytest.skip("osm_unbenannt.json fehlt (Workflow noch nicht gelaufen)")
    ids |= {e["id"] for e in json.loads(pu.read_text("utf-8"))["elements"]}
    fehlt = [r["osm_way_id"] for r in absch if r["osm_way_id"].strip() and int(r["osm_way_id"]) not in ids]
    assert not fehlt, f"Weg-IDs nicht in den OSM-Dateien: {fehlt}"


def test_hausnummern_filter():
    f = geo.hausnummern_filter("(Hausnr. 1, 4 - 8 A)")
    assert [f(x) for x in ("1", "2", "4", "8a", "8b", "9")] == [True, False, True, True, False, False]
    f = geo.hausnummern_filter("(Hausnr. 2 A bis 2 E)")
    assert f("2c") and not f("2") and not f("2f")
    assert geo.hausnummern_filter("Zufahrt Hausnr. 4, 8")("8")
    # Strecken und offene Angaben sind keine Nummernlisten
    assert geo.hausnummern_filter("ab Einmündung Alte Hauptstraße bis Am Domhof Hausnr. 6 a") is None
    assert geo.hausnummern_filter("(Hausnr. 43 bis Bahnhof)") is None
