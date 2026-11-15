import importlib.util, pathlib
s = importlib.util.spec_from_file_location("k", pathlib.Path(__file__).parent.parent / "skripte/03_karte_bauen.py")
k = importlib.util.module_from_spec(s); s.loader.exec_module(k)

def test_norm():
    assert k.norm("Ewald-Brand-Straße") == k.norm("Ewald-Brand-Str.") == k.norm("Ewald Brand Strasse")
    assert k.norm("Zöberitzer Weg") == k.norm("Zoeberitzer Weg")
