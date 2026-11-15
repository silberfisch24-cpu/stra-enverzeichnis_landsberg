# Gemischte Baulast: Einzelfallprüfung

Stand 15.11.2026. Der Wert `gemischt` entsteht in `skripte/01_extrahieren.py`, wenn die Baulast keiner der Klassen L/K/S/P entspricht. Es sind 7 Einträge. Nur 1 davon ist ein echtes Gemisch mit Ortsangabe. Die Zuordnung steht in `daten/gemischt_abschnitte.csv`, die Screenshots in `docs/pruefung/gemischt/`.

| Ortsteil | Straße | Verzeichnis sagt | Ursache | Ergebnis |
|---|---|---|---|---|
| Bageritz | Queiser Straße | innerorts ab Kreuzung: S; Umgehungsstraße: K | echte Teilung mit Ortsangabe | Ortsdurchfahrt ab Kreuzung K 2142 = Stadt (4 Wege), Umgehungsstraße = K 2142 am Dorf = Kreis (3 Wege) |
| Peißen, Queis | Orionstraße | Stadt Halle | fremder Baulastträger, kein Gemisch | alle 13 Wege Orionstraße = neue Klasse „Stadt Halle“ |
| Zöberitz | Zur Straßenmeisterei | Teilweise S und P | „teilweise“ ohne Ortsangabe | Vermutung: Zufahrt S, Gelände der Meisterei P; bitte bestätigen |
| Zöberitz | Autobahnsiedlung | Teilweise S, BRD, DB Netz AG | „teilweise“ ohne Ortsangabe, ein einziger OSM-Weg | nicht teilbar, bleibt gemischt bis zur Klärung |
| Niemberg | Alte Gärtnerei | Baulast A | Eintrag ungültig (A ist Anlieger) | Baulast unbekannt |
| Oppin | Maschwitzer Straße Hausnr. 7 bis 8 a | Baulast leer | fehlt im PDF | Baulast unbekannt |

## Auftrag an Claude Code

1. `skripte/01_extrahieren.py`: „Stadt Halle“ als eigene Baulast erkennen (zum Beispiel Kürzel `H`), leere oder ungültige Baulast (`A`) als `unbekannt` statt `gemischt` führen. `gemischt` bleibt nur für Freitext mit mehreren Trägern.
2. `skripte/03_karte_bauen.py` und `docs/index.html`: Klassen „Stadt Halle“ (eigene Farbe) und „Baulast nicht angegeben“ (hell, getrennt von „nicht im Verzeichnis“). Der Text im Popup bleibt.
3. `daten/gemischt_abschnitte.csv` einlesen: Die Baulast eines Weges kommt dort aus der Spalte `baulast`, sie hat Vorrang vor dem Haupteintrag. Wege mit `ref` bleiben bei ihrer Baulast (Regel 10 in `docs/ZUORDNUNGSREGELN.md`).
4. Test: Jede Zeile in `gemischt_abschnitte.csv` verweist auf einen vorhandenen Weg, und Bageritz Queiser Straße hat sowohl S als auch K.

## Offene Fragen an das Projekt

- Zur Straßenmeisterei: Wo endet der öffentliche Teil (Stadt), wo beginnt das Gelände (privat)?
- Autobahnsiedlung: Welcher Teil gehört der Stadt, dem Bund (BRD) und der DB Netz AG?
- Alte Gärtnerei und Maschwitzer Straße 7 bis 8 a: Wem gehört die Baulast? Eine Anliegerstraße ohne öffentlichen Träger wäre privat.
- Queiser Straße: Wo endet die Ortsdurchfahrt im Westen (1213846719 ist 312 m lang)?
