# Auftrag an claude.ai (mit Netzzugriff auf OSM): Zusatz-Zeilen des Straßenverzeichnisses Wegstücken zuordnen

## Hintergrund
Das Repository `silberfisch24-cpu/stra-enverzeichnis_landsberg` färbt die Straßen der Stadt Landsberg (Saalekreis) nach den Angaben
des Straßenverzeichnisses (Baulast, Reinigung, Winterdienst). Das Verzeichnis enthält neben der Hauptzeile je Straße auch
**Zusatzzeilen** („Hausnr. 4 - 6“, „ab Kreuzung X bis Y“, „Zufahrt EKZ“, „Rondell Dorfplatz“) mit abweichender Zuständigkeit.
Diese lassen sich nicht automatisch auf einzelne OSM-Wegstücke abbilden. Das soll mit OSM-Zugriff gelöst werden.

## Eingabe
`daten/zusatzfaelle.csv` (44 Zeilen; Lesehilfe `docs/zusatzfaelle.md`). Spalten: Ortsteil, Straße, Zusatz, Zuständigkeit der Zusatzzeile,
Haupteintrag, `osm_way_ids` (alle Wege der Straße, wie im Repository zugeordnet) und Länge. Karte: https://silberfisch24-cpu.github.io/stra-enverzeichnis_landsberg/

## Aufgabe
Bestimme für jede Zusatzzeile, **welche der `osm_way_ids` (oder Teile davon) zum Zusatz gehören**.

Mittel (nur öffentlich zugängliche OSM-Daten, Overpass-API und Nominatim, höchstens wenige Abfragen je Minute, eigener User-Agent ohne Personenbezug):
- **Hausnummern:** `addr:housenumber` / `addr:street` (Knoten und Gebäude) im Ortsteil; den Weg wählen, dem die genannten Nummern am nächsten liegen.
- **„ab Kreuzung X bis Y“, „zwischen A und B“:** Verlauf des Weges zwischen den benannten Kreuzungen (gemeinsame Knoten mit den Querstraßen).
- **„Zufahrt …“, „Rondell“, „bis Bahnhof“:** Wege mit passendem `highway=service`/`place=square` oder benannten Zielen in Nähe.
- Weitere Hinweise: `name`-Varianten, `ref`, `old_name`; Luftbild nur, wenn ausdrücklich mit Quelle erlaubt (hier nicht nötig).

## Ausgabe
Datei `daten/zusatz_zuordnung.csv` (UTF-8, Kopf wie unten), **eine Zeile je Zusatzzeile und OSM-Weg**:

```
ortsteil,strasse,zusatz,osm_way_id,teilstueck,konfidenz,notiz
Braschwitz,Brunnenstraße,(Hausnr. 4 - 6),123456789,ganz,hoch,"Hausnummern 4, 5, 6 liegen an diesem Weg"
```

- `ortsteil`, `strasse`, `zusatz` **exakt** wie in `daten/zusatzfaelle.csv` (Schlüssel).
- `osm_way_id`: Nur Weg-IDs aus der Spalte `osm_way_ids` derselben Zeile. Ein Weg darf nur einer Zusatzzeile derselben Straße zugeordnet werden.
- `teilstueck`: `ganz`, wenn der ganze Weg zum Zusatz gehört; `teil`, wenn nur ein Abschnitt (dann in `notiz` Knoten-IDs oder Koordinaten der Grenze nennen).
  Die Karte färbt vorerst nur ganze Wege; bei `teil` gilt: nur eintragen, wenn die Mehrheit des Weges zum Zusatz gehört.
- `konfidenz`: `hoch` (Hausnummern/Kreuzungen eindeutig), `mittel` (plausibel), `niedrig` (geraten). **Nicht raten:** Ist ein Fall nicht entscheidbar,
  Zeile mit leerer `osm_way_id` und Begründung in `notiz` (z. B. „keine Hausnummern in OSM“).
- Bitte keine Namensähnlichkeiten außerhalb des Ortsteils verwenden (Wege gleichen Namens in anderen Orten sind nicht gemeint).

## Abnahme
- Jede der 44 Zeilen von `zusatzfaelle.csv` kommt mindestens einmal vor (mit oder ohne Weg-ID).
- Stichprobe: 5 Fälle mit Weg-IDs und Begründung nennen (im Bericht, Kurzform).
- Ablage: Pull Request gegen `main` oder neue Datei auf dem Branch `zusatz-zuordnung`; nur diese Datei ändern.
  Danach läuft der Workflow „Karte bauen“ (liest die Datei automatisch, Zeilen mit leerer `osm_way_id` werden ignoriert).

## Hinweise
- Nutzungsbedingungen von Overpass/Nominatim beachten; Datenlizenz ODbL (© OpenStreetMap-Mitwirkende).
- Keine personenbezogenen Daten übernehmen (Hausnummern ja, Namen von Bewohnern nein).
- Zuständigkeiten sind: Baulast L=Land, K=Kreis, S=Stadt, P=Privat; Reinigung/Winterdienst A=Anlieger, B=Baulastträger.
