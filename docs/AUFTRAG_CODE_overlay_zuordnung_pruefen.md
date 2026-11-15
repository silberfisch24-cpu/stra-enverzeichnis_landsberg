# Auftrag an Claude Code: Overlay „Zuordnung prüfen“ und Teilstücke in der Karte

Voraussetzung: PR #2 (`daten/abschnitte.csv`, Branch `abschnitte`) ist gemergt.

## Ziel

Die Zusatzzeilen und die 5 offenen Straßen werden in der Karte auf das passende Wegstück gezeichnet. Zeilen, deren Zuordnung nur eine Interpretation ist, werden in einem eigenen, ein- und ausschaltbaren Overlay **„Zuordnung prüfen“** markiert, damit sie vor Ort oder im Rathaus geprüft werden können.

## Eingabedaten

`daten/abschnitte.csv` (104 Zeilen, 44 Zusatzzeilen + 5 offene Straßen). Spalten:
`ortsteil,strasse,zusatz,osm_way_id,von_lat,von_lon,bis_lat,bis_lon,art,konfidenz,grundlage,notiz`

- Schlüssel zur Verzeichniszeile: `ortsteil` + `strasse` + `zusatz` (exakt wie in `daten/zusatzfaelle.csv`; bei den 5 offenen Straßen ist `zusatz` leer und der Schlüssel ist `daten/offene_strassen.csv`).
- `osm_way_id`: Weg aus `osm_strassen.json` bzw. `osm_unbenannt.json`. Leer nur bei Art E.
- `von_*`/`bis_*` leer = ganzer Weg. Gefüllt = Teilstück: Linie von `von` nach `bis` entlang der Stützpunkte des Weges (nächster Stützpunkt zu `von` bzw. `bis`, dazwischen den Weg folgen, an den Enden den exakten Punkt setzen). Die Richtung von `von` nach `bis` kann entgegen der Wegrichtung liegen.
- Pro Verzeichniszeile können mehrere Zeilen (mehrere Wege) vorkommen; alle gehören zusammen.
- Ein Weg kann bei mehreren Zeilen derselben Straße als Teilstück vorkommen (z. B. 27517011 in Zwebendorf, 188144125 in Hohenthurm, 31966337 in Maschwitz). Überlappungen stehen in `notiz`.

### Bedeutung der Spalten

| art | Bedeutung | Anzahl |
|---|---|---|
| A | Teil eines Weges oder ganzer Weg mit dem Straßennamen | 40 |
| B | unbenannter Weg (in `osm_unbenannt.json`) | 30 |
| C | Weg mit anderem Namen (z. B. Friedrich-Hoffmann-Straße für Hoffmannplatz 8, 9) | 6 |
| D | Landmarke oder Strecke (Rondell, Zufahrt, „ab Kirche“, Kreuzung bis Kreuzung) | 21 |
| E | keine Datengrundlage, kein Weg | 7 |

konfidenz: hoch 39 · mittel 49 · niedrig 16. grundlage: Adressen / Kreuzungen / Name / Nähe / sonstiges.

## Umsetzung in der Karte

1. **Normale Darstellung:** Zeilen mit `konfidenz = hoch` und Art A, B, C werden wie die Haupteinträge gefärbt (Baulast und Reinigung/Winterdienst aus `zusatzfaelle.csv`), auf dem Weg bzw. Teilstück. Vorsicht: Die Zusatzzeile überlagert den Haupteintrag nur auf dem Teilstück, nicht auf dem ganzen Weg.
2. **Overlay „Zuordnung prüfen“** (eigene Ebene, über der Verzeichnisfarbe, per Schalter ein/aus, standardmäßig an): alle Zeilen mit `konfidenz` mittel oder niedrig sowie alle Art D und E.
   - Linien: Verzeichnisfarbe plus Schraffur/Strichelung oder auffälliger Rand. niedrig deutlicher als mittel (z. B. orange gestrichelt vs. gelb gepunktet).
   - Popup beim Anklicken: Ortsteil, Straße, `zusatz` im Wortlaut des Verzeichnisses, Art (als Klartext), Konfidenz, Grundlage, `notiz`, Baulast und Reinigung/Winterdienst der Zeile.
   - **Art E** hat keine Linie. Im Overlay-Panel als Liste anzeigen („Keine Zuordnung möglich“) mit Straße, Ortsteil und `notiz`, bei Klick auf die Ortsteilmitte zoomen (`osm_orte.json`).
3. **Legende** um die Overlay-Signaturen ergänzen und einen Satz: „Zuordnung vermutet – bitte prüfen“.
4. **Zusatzfälle ohne Zeile in `abschnitte.csv`** dürfen nicht entstehen; ein Test in `tests/` soll prüfen, dass alle Schlüssel aus `zusatzfaelle.csv` und `offene_strassen.csv` mindestens einmal vorkommen und dass jede `osm_way_id` in den OSM-Dateien existiert.
5. `abschnitte.csv` ist die Quelle. Nicht von Hand ändern, sondern Korrekturen als Pull Request einbringen (die Zeile mit `konfidenz` ändern, wenn sie vor Ort bestätigt wurde, z. B. auf `hoch`; dann verschwindet sie aus dem Overlay).

## Wichtige Erkenntnisse aus der Recherche (nicht noch einmal suchen)

### Die 5 offenen Straßen (Art E)
Webrecherche und Suche in OpenStreetMap (Namens-, Adress- und `alt_name`-Suche in den Ortsteilen) fanden für diese Straßen keinen zuordenbaren Weg:
- Niemberg: Am Bahnübergang, An der Bahn (im Ortsteil gibt es Bahnübergänge, aber keine zuordenbare Zufahrt)
- Plößnitz: Rosenhain
- Schwerz: Am Berge (Am Teich in Schwerz entspricht „Zum Teich“ in Kneipe und gehört nicht zur Liste)
- Sietzsch: Alte Salzstraße
Gleichnamige Wege in Frößnitz (Am Berge) und Neukyhna (Alte Salzstraße) sind nicht gemeint. Weitere Fälle mit Art E: Hohenthurm Berliner Straße (Hausnr. 41, 42; in OSM keine Adressen mit diesen Nummern) und Hohenthurm Niemberger Weg, Zufahrt 4, 8, 10, 12 (Zufahrt nicht als Weg erfasst).

### Rondell Dorfplatz (Dammendorf, Blumenstraße)
**Korrigiert 15.11.2026 (Auftraggeber):** Die Zeile meint den **Ring** (Wege 28731056, 975460640, 390526327, zusammen etwa 67 m) und den **nördlichen Zubringer** (28731058, 18 m), nicht die Mittelinsel (Fläche 1104039294). Der südliche Zubringer (28731059) bleibt beim Haupteintrag. Stadt ist für Räumung und Säuberung zuständig; das PDF nennt bei der Fahrbahnreinigung A, die Abweichung steht begründet in `daten/korrekturen_verzeichnis.csv`.

### Grundsatz: Stichstraße statt durchgehende Straße
Wenn Hausnummern an einem Stichweg liegen, wird nur der Stichweg zugeordnet. Die durchgehende Straße bleibt in der übergeordneten Verantwortung, auch wenn eine Hausnummer näher an ihr liegt (Beispiel Am Landrain 8 A bis 8 E). Gibt es keinen Stichweg in OSM (Niemberger Weg, Zufahrt 4, 8, 10, 12), wird Art E vergeben statt die durchgehende Straße zu färben.

### Zuordnung der Hausnummernfälle (31 Zusatzzeilen, automatisierbar)
Regel: Adresse (Knoten oder Gebäudemittelpunkt, `addr:street` gleich Straßenname) dem nächsten Highway-Weg bis 45 m zuordnen; Wege mit anderem Namen bekommen 15 m Strafzuschlag. Ein Weg gilt als ganz, wenn alle seine Adressen dieser Straße zum Fall gehören, die Spanne mit 15 m Puffer mindestens 85 % der Länge deckt oder er höchstens 70 m lang ist; sonst Teilstück über die äußersten Adressen mit 15 m Puffer. `highway=bus_stop` wird ausgeschlossen. Konfidenz: hoch bei mindestens 2 Adressen und höchstens 30 m Abstand; mittel bis 45 m oder genau eine Adresse an unbenanntem Weg; niedrig bei reiner Nähe.

### Streckenangaben (Art D), von Hand interpretiert
- Maschwitz, An der Schenke (Weg 31966337): „ab Kreuzung Siedlung bis Hausnr. 13“ und „ab Hausnr. 13“ sind aneinandergrenzende Teilstücke. Die Richtung bei „ab Hausnr. 13“ ist unklar, Hausnr. 13 liegt an der Ecke nahe Hausnr. 2 (niedrig).
- Oppin, Am Domhof: drei Wege in Reihe von der Einmündung Alte Hauptstraße bis Hausnr. 6 a.
- Oppin, Maschwitzer Straße: vier Wege von der Einmündung Alte Hauptstraße bis zur Kreuzung Singdrosselweg. (Schreibweise im Verzeichnis „Krezuzung“ ist so in der Datei, nicht korrigieren.)
- Oppin, Windmühlenweg: „zwischen Lindenstraße und Maschwitzer Straße“. In OSM gibt es keine Lindenstraße, nur Lindenallee am Westende.
- Zwebendorf, Reideburger Straße: „zwischen Kreuzung L168 und Hausnr. 5 a“ und „Am Mühlteich bis FFW“ überlappen auf Weg 27517011 um etwa 22 m. Hausnr. 5 a fehlt in OSM.
- Hohenthurm, Berliner Straße „ab Kreuzung Steinbruch bis Sackgasse“: Weg 1422256661, eindeutig (hoch).
- Hohenthurm, Steinbruch „ab Kreuzung Schwarzer Weg bis Mühlberg“: Weg 186919779, niedrig (Strecke unklar).
- Klepzig, Kirchstraße „ab Kirche“: Weg 224875935, niedrig (Richtung unklar; alternativ der südliche Teil).
- Gütz, Zörbiger Straße „Zufahrt EKZ“: Weg 41123482, mittel (Wege durch den Parkplatz von Penny/Edeka).
- Braschwitz, Schultze-Gallera-Weg „Zufahrtsstraße Wohngebiet“: Weg 151603582 (Verbindung zum Brühlweg), mittel.

### Bekannte Schwachstellen (niedrig, bitte vor Ort prüfen)
Hohenthurm Niemberger Weg (Zufahrt 4, 8, 10, 12; Hausnr. 8 ohne eigenen Weg), Dammendorf Anger Hausnr. 11, Zöberitz Zum Rittergut Hausnr. 13 (Weg heißt Mötzlicher Straße), Hohenthurm Alte Bahnhofstraße 42 c, Steinbruch, Klepzig Kirchstraße.

### Prüfstand
Jeder Fall wurde als Kartenausschnitt gezeichnet (OSM-Straßennetz, Adresspunkte mit Hausnummern, zugeordnete Wege, Teilstücke) und einzeln gesichtet. Die Screenshots (12 Übersichtsblätter, 10 Detailblätter mit Gebäuden) und die Einzelanalyse aller Fälle stehen in `docs/pruefung/` (README.md). Korrekturen daraus stehen in PR #2.

## Hinweise zu OSM-Daten

- Die OSM-API (`/api/0.6/map.json?bbox=`) ist von der Cloud-Umgebung nur über den eingebauten Browser erreichbar, Overpass liefert dort 406. Neue OSM-Daten holt Claude.ai als Helfer (Auftrag in `docs/AUFTRAG_*.md`).
- Datenstand von `osm_unbenannt.json` und `osm_adressen.json`: erst nach dem nächsten Lauf des Workflows „Karte bauen“ im Repo vorhanden.


## Nachtrag: gleichnamige Abzweige von L/K-Straßen

Wenn die Hauptstraße eine L/K ist und der Abzweig (in der Regel Stadt) denselben Namen trägt, darf die Karte nicht allein über den Straßennamen färben. Ablauf: erst Wege aus `daten/abschnitte.csv` (per `osm_way_id`) mit der Baulast der Zusatzzeile färben, danach den Rest über den Namen. Wege mit `ref` L/K/B dürfen nie durch eine Zusatzzeile umgefärbt werden. Details und betroffene Straßen: `docs/ZUORDNUNGSREGELN.md`, Regel 10. Test: Kein Weg mit `ref` in `abschnitte.csv`.
