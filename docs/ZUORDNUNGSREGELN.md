# Zuordnungsregeln für Zusatzzeilen (aus den Korrekturen des Projekts abgeleitet)

Stand 15.11.2026 (Gesamtdurchgang, vollständige Systematik). Diese Regeln gelten für `daten/abschnitte.csv` und für alle künftigen Zuordnungen. Sie sind aus den Beispielen des Projekts verallgemeinert.

## Grundsätze

1. **Die durchgehende Straße bleibt beim Haupteintrag.** Eine Zusatzzeile gilt für das, was von der übergeordneten Straße abzweigt (Stichstraße, Nebenstraße, Zufahrt), nicht für die durchgehende Straße selbst, auch wenn eine genannte Hausnummer näher an ihr liegt. (Beispiele: Am Landrain 8 A bis 8 E; Schkeuditzer Straße; Otto-Quandt-Straße; Hauptstraße Reußen.) Als durchgehend gelten Wege mit `ref` L oder K, `secondary`, `tertiary`, `primary` und die lange Hauptachse eines Ortes.
2. **Eine Zusatzzeile meint ein zusammenhängendes Teilnetz, nicht einzelne Wege.** Die Hausnummern zeigen nur, welches Teilnetz gemeint ist. Zugeordnet wird dann das gesamte Netz, das abseits der durchgehenden Straße liegt, bis zu ihr, mit allen Verbindungsstücken und Wegen ohne Hausnummer. (Beispiele: Dammendorf Anger: gesamter Abschnitt östlich der Nord-Süd-Straße; Zöberitzer Weg: ganzer Teil bis zum Feldweg; Alte Bahnhofstraße 42: gesamter Bereich westlich der L 168.)
3. **Lücken in der Nummernfolge gehören dazu.** Liegen Hausnummern zwischen zwei Zusatzbereichen (zum Beispiel 12 und 13 zwischen „1 - 11“ und „14 - 17“) an Wegen, die das Teilnetz verbinden, gehört dieser Weg zur Zusatzzeile, wenn das Projekt ihn als Stadt/Anlieger bestätigt. (Beispiel: Diagonale der Alten Bahnhofstraße in Hohenthurm.)
4. **Nur Straßen, keine Pfade.** Wege mit `highway` path, footway, track, steps, cycleway oder bridleway (Fußweg, Grasweg, Feldweg) werden nicht zugeordnet. Hausnummern an solchen Wegen stehen nur in der notiz. (Beispiele: 224882490, 604661716, 923134922, 53512820.) Zugeordnet werden service, residential, living_street, unclassified.
5. **Teilstücke nur ausnahmsweise.** Ein Teilstück einer Straße wird nur vergeben, wenn die Zusatzzeile erkennbar ein Stück derselben Straße meint (Hausnummern an der Straße selbst, keine Stichstraße). Ein Stichweg wird immer ganz zugeordnet, nicht nur sein Anfang.
6. **Rondell und Platz (korrigiert 15.11.2026).** Die Zeile „Rondell“ meint die Fahrbahn des Rondells (der Ring) und den Zubringer, der zu ihm führt, **nicht** die Mittelinsel. Die Mittelinsel (Grünfläche, Bushaltestelle) ist keine Straße und wird nicht gefärbt. Beispiel: Dammendorf, Blumenstraße „Rondell Dorfplatz“: Ring (28731056, 975460640, 390526327) und nördlicher Zubringer (28731058). Der südliche Zubringer (28731059) bleibt beim Haupteintrag.
7. **Kein Stichweg in OSM: Art E.** Wenn eine Zufahrt in OSM nicht als Weg erfasst ist, wird nicht die durchgehende Straße gefärbt, sondern Art E vergeben. Die Hausnummern stehen in der notiz.
8. **Der Straßenname ist nachrangig.** Abweichende Schreibweisen (Anger / Am Anger) zählen als derselbe Name (Art A). Art C gilt nur, wenn der Weg wirklich zu einer anderen Straße gehört.
9. **Bestätigung durch das Projekt zählt mehr als die Auswertung.** Was das Projekt entscheidet (zum Beispiel „Anlieger, nicht Stadt“, „Diagonale ist Stadt“), wird übernommen, die Konfidenz ist dann hoch, und die notiz nennt die Bestätigung.

10. **Gleichnamige Abzweige von L/K-Straßen.** Trägt die Hauptstraße eine Referenz (OSM `ref` L, K oder B) und der Abzweig denselben Straßennamen, darf der Abzweig nicht über den Namen der L/K-Straße zugeschlagen werden, und die L/K-Wege selbst gehören nie zu einer Zusatzzeile. Der Abzweig wird nur über Lage und Geometrie (Regel 2) zugeordnet. Für die Karte heißt das: Baulast aus der Zusatzzeile hat Vorrang vor der Namenszuordnung, und Wege mit `ref` bleiben bei der Haupteintrag-Baulast. Betroffen sind unter anderem Alte Bahnhofstraße und Reideburger Straße (L 168), Leipziger Straße und Zörbiger Straße (L 143), Delitzscher Chaussee (L 165), Stichelsdorfer Straße (L 167), Schkeuditzer Straße (K 2140), Otto-Quandt-Straße (K 2137), Merseburger Straße (K 2139).

## Prüfschritt vor jeder Zuordnung

1. Welche Wege zweigen von der durchgehenden Straße ab? Das ist das Teilnetz.
2. Gehören alle zusammenhängenden Wege des Teilnetzes dazu, auch ohne Hausnummer?
3. Ist ein Weg nur Pfad, Feldweg oder Fußweg? Dann streichen.
4. Liegt eine genannte Hausnummer nur an der durchgehenden Straße? Dann nicht zuordnen, in der notiz nennen.
5. Ist das Ergebnis ein Rondell? Dann Ring und genannter Zubringer, nicht die Mittelinsel.

## Sonderfälle aus der Session (Systematik)

| Typ | Erkennung | Behandlung | Beispiel |
|---|---|---|---|
| Stichstraße an durchgehender Straße | Zusatzhausnummern an kurzem Abzweig, durchgehender Weg daneben | nur der Stich, ganz | Am Landrain 8 A–8 E |
| Teilnetz abseits der Hauptstraße | mehrere verbundene Wege, Hausnummern verteilt | alle Wege des Netzes, auch ohne Hausnummer | Anger Dammendorf, Otto-Quandt-Straße, Zum Rittergut |
| Teilnetz mit Servicestich | unbenannter service-Weg hängt am Teilnetz | zuordnen (Konfidenz mittel) | 1425709704, 39962397, 887532620 |
| Separater Stich an der Hauptstraße | unbenannter Weg zweigt direkt von der Hauptstraße ab, gehört nicht zum Netz | nicht zuordnen | 188144140 (Alte Bahnhofstraße) |
| Gleichnamiger Abzweig einer L/K/B | Weg ohne `ref`, Name wie die Hauptstraße | über Geometrie, nie über den Namen; Wege mit `ref` raus | Alte Bahnhofstraße, Reideburger Straße, Neue Bahnhofstraße |
| Bereich westlich einer Landesstraße | Projektaussage „Stadt, Anlieger“ | alle Wege westlich bis zur L, ohne L | Alte Bahnhofstraße 42–42 D |
| Diagonale / Verbindungsweg | Projektaussage „gehört zur Stadt“ | zuordnen, Konfidenz hoch | Alte Bahnhofstraße 1–11 |
| Rondell | Zeile nennt „Rondell“ | Ring und der Zubringer, den der Auftraggeber nennt; nicht die Mittelinsel | Blumenstraße Rondell Dorfplatz (Ring + 28731058) |
| Geteilte Straße mit Zwei-Zeilen-Zuordnung | ein Weg gehört zu zwei Zeilen | Teilstücke mit von/bis, nie dieselbe Spanne doppelt | 188144125 (Zeilen 1–11 und 43 bis Bahnhof) |
| Pfad, Feldweg, Fußweg | `highway` path, track, footway, steps | nicht zuordnen, Hausnummer in der notiz | 923134922, 53512820, 224882490, 604661716 |
| Zufahrt ohne eigenen Weg | keine Straße in OSM | Art E | Berliner Straße 41/42, Niemberger Weg Zufahrt, Reinsdorf Merseburger Straße 51/52 |
| Ort-/Landmarke-Zeile | „ab Kirche“, „Zufahrt EKZ“, „bis FFW“ | Art D, Strecke zwischen den Landmarken, Teilstücke mit von/bis | Klepzig, Maschwitz, Zwebendorf |
| Abweichender Name | Weg heißt anders als die Zeile | Art C, Konfidenz niedrig/mittel | Schultze-Gallera-Weg, Hoffmannplatz |
| Tippfehler in der Zeile | „Krezuzung“ | Schlüssel unverändert übernehmen | Oppin Maschwitzer Straße |

## Ablauf des Gesamtdurchgangs

1. Alle zugeordneten Wege auf `ref`, `highway`, Name und Länge geprüft (OSM API).
2. Je Fall Kandidaten in 2 Wegschritten Entfernung gesucht (service, residential, living_street, unclassified, ohne `ref`).
3. Alle 41 Fälle mit Wegen als Karte gezeichnet (Zuordnung blau, Teilstücke rot, Kandidaten orange, Hausnummern) und 1:1 per Screenshot geprüft. Die Screenshots liegen in `docs/pruefung/runde3/`.
4. Ergebnis: 12 Wege mit L/K/B-Referenz entfernt, 3 Servicestiche ergänzt, Reinsdorf Merseburger Straße 51/52 als Art E.

## Offene Kandidaten (nicht zugeordnet, bei Bedarf prüfen)

- Queis Delitzscher Chaussee: 224871227 (176 m) und 146195288 (54 m) zweigen eigenständig ab
- Hohenthurm Alte Bahnhofstraße: 188144140, 404956842, 570393938, 1481058679, 53512821 zweigen direkt von der L 168 ab
- Zwebendorf Reideburger Straße: 142238366, 1053081240, 224877384 zweigen separat ab
- Maschwitz An der Schenke: 980229164 (kleine Schleife, 57 m)
- Hohenthurm Berliner Straße: 404555181 (104 m, nach Norden)
- Offene Entscheidungen des Projekts: Fußweg am Bach Dammendorf (923134922) und Feldweg Hausnr. 89 Hohenthurm (53512820): derzeit nicht zugeordnet
