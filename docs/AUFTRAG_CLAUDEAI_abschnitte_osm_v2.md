# Auftrag an claude.ai (mit Netzzugriff auf OSM): Verzeichnisabschnitte als Kartengeometrie bestimmen (v2)

Ersetzt `AUFTRAG_CLAUDEAI_zusatzfaelle_osm.md`. Das Ergebnis der ersten Runde (`daten/zusatz_zuordnung.csv`, 44 Zusatzzeilen, 29 ganze Wege zugeordnet, 15 offen) bleibt als Vorlage erhalten.

## 1. Problem (allgemein)

Das Straßenverzeichnis der Stadt Landsberg (Saalekreis) beschreibt Zuständigkeiten (Baulast, Reinigung, Winterdienst) **je Straße oder je Abschnitt einer Straße**.
Die Karte (https://silberfisch24-cpu.github.io/stra-enverzeichnis_landsberg/) färbt bisher **ganze OSM-Wege** nach Straßenname. Das scheitert, wenn eine Verzeichniszeile etwas beschreibt, das OSM nicht als benanntes, ganzes Objekt führt.
Die Ursachen sind immer eine dieser Abweichungen zwischen Verzeichnis und OSM:

| Art | Beschreibung | Beispiel |
|---|---|---|
| **A** Teil eines Weges | Der Abschnitt ist nur ein Teil eines OSM-Weges (der Weg reicht über den Abschnitt hinaus). | Brunnenstraße (Hausnr. 4 – 6) in Braschwitz: liegt auf einem Teil von Weg 292033808. |
| **B** Unbenannter Weg | Der Abschnitt liegt auf Zufahrten, Stichwegen oder Hofzufahrten, die in OSM **keinen Namen** haben (`highway=service/residential/living_street` ohne `name`). | Zöberitzer Weg (Hausnr. 17 – 18): Die Häuser hängen an weißen, unbenannten Wegen abseits des benannten Weges. |
| **C** Abweichender Name | Der Weg trägt in OSM einen anderen Namen oder nur die Adressen tragen `addr:street`. | Schultze-Gallera-Weg (Zufahrtsstraße Wohngebiet). |
| **D** Orientierungspunkte | Die Zeile nennt Strecken („ab Kreuzung X bis Y“, „ab Kirche“, „zwischen A und B“) statt Hausnummern. | Steinbruch (ab Kreuzung Schwarzer Weg bis Mühlberg). |
| **E** Keine Datengrundlage | OSM kennt weder passende Hausnummern noch Wege. | Anger (Hausnr. 6 – 22) in Dammendorf. |

Dieselben Abweichungen erklären auch die 5 Straßen, die dem Verzeichnis nach ohne OSM-Weg bleiben (`daten/offene_strassen.csv`: Am Bahnübergang, An der Bahn, Rosenhain, Am Berge, Alte Salzstraße). Möglicherweise liegen sie auf unbenannten Wegen (Art B).

**Ziel:** Für jede betroffene Verzeichniszeile die **kleinste zutreffende Kartengeometrie** angeben: einen oder mehrere OSM-Wege, bei Art A mit Schnittpunkten, damit der Abschnitt exakt gefärbt werden kann.

## 2. Eingaben

Im Repository `silberfisch24-cpu/stra-enverzeichnis_landsberg` (Branch `main`):
- `daten/zusatzfaelle.csv`: die 44 Zusatzzeilen (Ortsteil, Straße, Zusatz, Zuständigkeit des Zusatzes, Haupteintrag, OSM-Weg-IDs der Straße).
- `daten/offene_strassen.csv`: die 5 Straßen ohne OSM-Weg.
- `daten/zusatz_zuordnung.csv`: Ergebnis der ersten Runde mit Begründungen.
- `daten/verzeichnis.csv`: das gesamte Verzeichnis (458 Zeilen; Spalten wie in `skripte/01_extrahieren.py` beschrieben).
- `daten/osm_strassen.json`: benannte Wege der Stadt (Geometrie). `daten/osm_unbenannt.json` und `daten/osm_adressen.json` (unbenannte Wege, Adresspunkte) liegen nach dem nächsten Workflow-Lauf ebenfalls dort. Sie dürfen jederzeit zusätzlich selbst per OSM-API/Overpass abgefragt werden.
- Zuständigkeiten: Baulast L = Land, K = Kreis, S = Stadt, P = Privat; Reinigung/Winterdienst A = Anlieger, B = Baulastträger.

## 3. Vorgehen je Zeile

1. **Hausnummernzeilen** („Hausnr. 4 – 6“, „2 A bis 2 E“, „1, 4 – 8 A“, „Zufahrt Hausnr. …“): Adresspunkte (`addr:housenumber`, `addr:street`, Gebäude und Knoten) im Ortsteil suchen. Die Nummernmenge sauber auflösen (Bereiche, Buchstabenfolgen, Aufzählungen). Zu jeder gefundenen Adresse den **nächstgelegenen Weg** bestimmen, **auch wenn er keinen oder einen anderen Namen trägt**, sofern er die Hausanbindung ist (Zufahrt). Die Wege der Adressen bilden den Abschnitt.
2. **Streckenzeilen** („ab … bis …“, „zwischen …“): Verlauf zwischen den Kreuzungen/Punkten bestimmen. Die benannten Querstraßen und Punkte (Kirche, Feuerwehr, Bahnübergang) über OSM auflösen.
3. **Teil eines Weges (Art A):** Gehört nur ein Teil eines Weges zum Abschnitt, **Anfang und Ende des Abschnitts als Koordinaten auf dem Weg** angeben (Projektion der äußersten Adressen bzw. die Kreuzungsknoten; ein Puffer von höchstens 15 m an den Enden ist erlaubt). Nach Möglichkeit die OSM-Knoten-IDs der Kreuzungen nennen.
4. **Mehrere Wege:** Ein Abschnitt darf aus mehreren Wegen bestehen (je Weg eine Zeile).
5. **Art E:** Ist nichts bestimmbar, die Zeile mit leerer `osm_way_id` und Begründung eintragen. **Nicht raten.**
6. **Die 5 offenen Straßen:** Prüfen, ob es unbenannte Wege, Wege mit anderem Namen (`old_name`, `alt_name`, `loc_name`, `ref`) oder Adressen mit `addr:street` gibt. Wege gleichen Namens in anderen Orten (Frößnitz, Neukyhna) sind nicht gemeint.
7. **Bereits zugeordnete Zeilen** (Spalte `wege` in `docs/zusatz.json`, Datei `daten/zusatz_zuordnung.csv`): nur dann überarbeiten, wenn der Abschnitt deutlich kürzer ist als der zugeordnete Weg (Art A). Sonst unverändert übernehmen.

## 4. Ausgabe

Datei `daten/abschnitte.csv` (UTF-8, Kopf wie unten), **eine Zeile je Verzeichniszeile und OSM-Weg**:

```
ortsteil,strasse,zusatz,osm_way_id,von_lat,von_lon,bis_lat,bis_lon,art,konfidenz,grundlage,notiz
Braschwitz,Brunnenstraße,(Hausnr. 4 - 6),292033808,51.4234,12.1812,51.4236,12.1815,A,mittel,Adressen,"4 und 6 liegen an diesem Weg, 5 fehlt in OSM"
Braschwitz,Zöberitzer Weg,(Hausnr. 17 - 18),1234567890,,,,,B,hoch,Adressen,"unbenannter Weg (service), beide Hausnummern anliegend"
```

- `ortsteil`, `strasse`, `zusatz` **exakt** wie in `daten/zusatzfaelle.csv`. Bei den 5 offenen Straßen ist `zusatz` leer und `ortsteil`/`strasse` stammen aus `daten/offene_strassen.csv`.
- `osm_way_id`: beliebige OSM-Weg-ID aus der Stadt, **auch unbenannte Wege**.
- `von_*`/`bis_*`: Anfang und Ende des Abschnitts **auf dem Weg**. Leer = ganzer Weg.
- `art`: A bis E wie in der Tabelle oben (bei Mischfällen die ausschlaggebende).
- `konfidenz`: `hoch` (Hausnummern/Kreuzungen eindeutig), `mittel` (plausibel, kleine Lücken), `niedrig` (nur Nähe).
- `grundlage`: `Adressen`, `Kreuzungen`, `Name`, `Nähe` oder `sonstiges`.
- `notiz`: kurz, in einem Satz, ohne Personenbezug.
- Nur Wege der Stadt Landsberg; keine Wege außerhalb.

Zusätzlich ein **Kurzbericht** (im Pull-Request-Text):
- Anzahl der Zeilen je Art A bis E und je Konfidenz.
- Welche Regeln sich **automatisch** anwenden lassen (z. B. „Adresse → nächster Weg, unbenannte Zufahrten eingeschlossen, Abschnitt = Spanne der äußersten Adressen“) und wo Handarbeit nötig war. Daran messen wir, was die Pipeline künftig selbst übernehmen kann.
- 5 Stichproben mit Begründung (Kurzform).

## 5. Abnahme und Ablage

- Jede der 44 Zusatzzeilen und jede der 5 offenen Straßen kommt mindestens einmal vor (mit oder ohne Weg-ID).
- Eine Weg-ID wird nur einer Verzeichniszeile derselben Straße zugeordnet. Überlappen sich zwei Abschnitte auf einem Weg, die Überlappung in `notiz` nennen.
- Ablage per Pull Request gegen `main` auf einem Branch `abschnitte`. **Nur** `daten/abschnitte.csv` ändern.
- Danach liest der Workflow „Karte bauen“ die Datei ein (Auftrag an die Pipeline: Weg an den Schnittpunkten teilen; Teilstücke mit den Zuständigkeiten der Zeile färben).

## 6. Hinweise

- Nutzungsbedingungen von Overpass und Nominatim beachten (wenige Abfragen pro Minute, eigener User-Agent ohne Personenbezug). Datenlizenz ODbL, © OpenStreetMap-Mitwirkende.
- Keine personenbezogenen Daten übernehmen (Hausnummern ja, Namen von Bewohnern nein).
- Anlass: Auf der Karte erscheinen offene Fälle wie Brunnenstraße (Hausnr. 4 – 6) und Zöberitzer Weg (Hausnr. 17 – 18) bisher nur als markierter Weg ohne die Ausnahme. Die Ursache sind Art A und B.
