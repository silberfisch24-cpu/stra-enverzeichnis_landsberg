"""Geometrie-Hilfen: Wege (Listen aus (lon, lat)) an Bogenlängen teilen.

Alle Längen in Metern (lokale ebene Näherung, für Stadtgebiet ausreichend).
"""
import math

M_LAT = 110540.0
M_LON = 111320.0


def _xy(p, lat0):
    return (p[0] * M_LON * math.cos(math.radians(lat0)), p[1] * M_LAT)


def kumuliert(geo):
    """Bogenlänge am Anfang jedes Stützpunkts (Liste gleicher Länge wie geo)."""
    lat0 = geo[0][1]
    s = [0.0]
    for a, b in zip(geo, geo[1:]):
        (ax, ay), (bx, by) = _xy(a, lat0), _xy(b, lat0)
        s.append(s[-1] + math.hypot(bx - ax, by - ay))
    return s


def laenge(geo):
    return kumuliert(geo)[-1]


def projektion(geo, p):
    """Bogenlänge des dem Punkt p=(lon, lat) nächsten Punktes auf dem Weg und dessen Abstand in m."""
    lat0 = geo[0][1]
    cum = kumuliert(geo)
    px, py = _xy(p, lat0)
    beste = (float("inf"), 0.0)
    for i in range(len(geo) - 1):
        ax, ay = _xy(geo[i], lat0)
        bx, by = _xy(geo[i + 1], lat0)
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
        d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
        if d < beste[0]:
            beste = (d, cum[i] + t * math.sqrt(l2))
    return beste[1], beste[0]


def punkt_bei(geo, cum, s):
    """Punkt (lon, lat) bei Bogenlänge s."""
    if s <= 0:
        return geo[0]
    if s >= cum[-1]:
        return geo[-1]
    for i in range(len(cum) - 1):
        if cum[i] <= s <= cum[i + 1]:
            l = cum[i + 1] - cum[i]
            t = 0 if l == 0 else (s - cum[i]) / l
            return (geo[i][0] + t * (geo[i + 1][0] - geo[i][0]), geo[i][1] + t * (geo[i + 1][1] - geo[i][1]))
    return geo[-1]


def teilstueck(geo, s0, s1):
    """Polylinie zwischen den Bogenlängen s0 und s1 (mit exakten Endpunkten)."""
    cum = kumuliert(geo)
    if s0 > s1:
        s0, s1 = s1, s0
    s0, s1 = max(0.0, s0), min(cum[-1], s1)
    out = [punkt_bei(geo, cum, s0)]
    out += [p for p, c in zip(geo, cum) if s0 < c < s1]
    out.append(punkt_bei(geo, cum, s1))
    return out


def zerlege(geo, intervalle, mindest=0.5):
    """Teilt einen Weg an den Rändern der Intervalle [(s0, s1, nutzlast), …].

    Ergebnis: Liste (Teil-Polylinie, Nutzlast oder None) in Wegrichtung. Wo sich Intervalle überlappen,
    gilt das kürzeste (das genaueste). Aneinandergrenzende Teile mit gleicher Nutzlast werden vereinigt.
    """
    cum = kumuliert(geo)
    L = cum[-1]
    iv = [(min(a, b), max(a, b), n) for a, b, n in intervalle]
    punkte = sorted({0.0, L, *[max(0.0, min(L, x)) for a, b, _ in iv for x in (a, b)]})
    stuecke = []
    for a, b in zip(punkte, punkte[1:]):
        if b - a < mindest:
            continue
        mitte = (a + b) / 2
        deck = [(e - s, n) for s, e, n in iv if s <= mitte <= e]
        n = min(deck, key=lambda x: x[0])[1] if deck else None
        if stuecke and stuecke[-1][2] is n and abs(stuecke[-1][1] - a) < 1e-6:
            stuecke[-1] = (stuecke[-1][0], b, n)
        else:
            stuecke.append((a, b, n))
    return [(teilstueck(geo, a, b), n) for a, b, n in stuecke]
