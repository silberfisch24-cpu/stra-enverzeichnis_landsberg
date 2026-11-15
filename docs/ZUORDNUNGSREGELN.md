# Zuordnungsregeln für Zusatzzeilen (aus den Korrekturen des Projekts abgeleitet)

Stand 15.11.2026. Diese Regeln gelten für `daten/abschnitte.csv` und für alle künftigen Zuordnungen. Sie sind aus den Beispielen des Projekts verallgemeinert.

## Grundsätze

1. **Die durchgehende Straße bleibt beim Haupteintrag.** Eine Zusatzzeile gilt für das, was von der übergeordneten Straße abzweigt (Stichstraße, Nebenstraße, Zufahrt), nicht für die durchgehende Straße selbst, auch wenn eine genannte Hausnummer näher an ihr liegt. (Beispiele: Am Landrain 8 A bis 8 E; Schkeuditzer Straße; Otto-Quandt-Straße; Hauptstraße Reußen.) Als durchgehend gelten Wege mit `ref` L oder K, `secondary`, `tertiary`, `primary` und die lange Hauptachse eines Ortes.
2. **Eine Zusatzzeile meint ein zusammenhängendes Teilnetz, nicht einzelne Wege.** Die Hausnummern zeigen nur, welches Teilnetz gemeint ist. Zugeordnet wird dann das gesamte Netz, das abseits der durchgehenden Straße liegt, bis zu ihr, mit allen Verbindungsstücken und Wegen ohne Hausnummer. (Beispiele: Dammendorf Anger: gesamter Abschnitt östlich der Nord-Süd-Straße; Zöberitzer Weg: ganzer Teil bis zum Feldweg; Alte Bahnhofstraße 42: gesamter Bereich westlich der L 168.)
3. **Lücken in der Nummernfolge gehören dazu.** Liegen Hausnummern zwischen zwei Zusatzbereichen (zum Beispiel 12 und 13 zwischen „1 - 11“ und „14 - 17“) an Wegen, die das Teilnetz verbinden, gehört dieser Weg zur Zusatzzeile, wenn das Projekt ihn als Stadt/Anlieger bestätigt. (Beispiel: Diagonale der Alten Bahnhofstraße in Hohenthurm.)
4. **Nur Straßen, keine Pfade.** Wege mit `highway` path, footway, track, steps, cycleway oder bridleway (Fußweg, Grasweg, Feldweg) werden nicht zugeordnet. Hausnummern an solchen Wegen stehen nur in der notiz. (Beispiele: 224882490, 604661716, 923134922, 53512820.) Zugeordnet werden service, residential, living_street, unclassified.
5. **Teilstücke nur ausnahmsweise.** Ein Teilstück einer Straße wird nur vergeben, wenn die Zusatzzeile erkennbar ein Stück derselben Straße meint (Hausnummern an der Straße selbst, keine Stichstraße). Ein Stichweg wird immer ganz zugeordnet, nicht nur sein Anfang.
6. **Inseln und Plätze.** Bei einem Rondell oder einer Insel (Grund der Ausnahme: zum Beispiel die Bushaltestelle) wird die Fläche selbst zugeordnet. Der Ring und die kleinen Zubringer bleiben in übergeordneter Verantwortung. Die Fläche wird als Fläche gezeichnet.
7. **Kein Stichweg in OSM: Art E.** Wenn eine Zufahrt in OSM nicht als Weg erfasst ist, wird nicht die durchgehende Straße gefärbt, sondern Art E vergeben. Die Hausnummern stehen in der notiz.
8. **Der Straßenname ist nachrangig.** Abweichende Schreibweisen (Anger / Am Anger) zählen als derselbe Name (Art A). Art C gilt nur, wenn der Weg wirklich zu einer anderen Straße gehört.
9. **Bestätigung durch das Projekt zählt mehr als die Auswertung.** Was das Projekt entscheidet (zum Beispiel „Anlieger, nicht Stadt“, „Diagonale ist Stadt“), wird übernommen, die Konfidenz ist dann hoch, und die notiz nennt die Bestätigung.

10. **Gleichnamige Abzweige von L/K-Straßen.** Trägt die Hauptstraße eine Referenz (OSM `ref` L, K oder B) und der Abzweig denselben Straßennamen, darf der Abzweig nicht über den Namen der L/K-Straße zugeschlagen werden, und die L/K-Wege selbst gehören nie zu einer Zusatzzeile. Der Abzweig wird nur über Lage und Geometrie (Regel 2) zugeordnet. Für die Karte heißt das: Baulast aus der Zusatzzeile hat Vorrang vor der Namenszuordnung, und Wege mit `ref` bleiben bei der Haupteintrag-Baulast. Betroffen sind unter anderem Alte Bahnhofstraße und Reideburger Straße (L 168), Leipziger Straße und Zörbiger Straße (L 143), Delitzscher Chaussee (L 165), Stichelsdorfer Straße (L 167), Schkeuditzer Straße (K 2140), Otto-Quandt-Straße (K 2137), Merseburger Straße (K 2139).

## Prüfschritt vor jeder Zuordnung

1. Welche Wege zweigen von der durchgehenden Straße ab? Das ist das Teilnetz.
2. Gehören alle zusammenhängenden Wege des Teilnetzes dazu, auch ohne Hausnummer?
3. Ist ein Weg nur Pfad, Feldweg oder Fußweg? Dann streichen.
4. Liegt eine genannte Hausnummer nur an der durchgehenden Straße? Dann nicht zuordnen, in der notiz nennen.
5. Ist das Ergebnis eine Fläche oder Insel? Dann Fläche.

## Offene Kandidaten für Regel 2 (noch nicht umgesetzt)

Bei der Auswertung des Wegenetzes fielen unbenannte Servicewege an Teilnetzen auf, die nach Regel 2 zur Zusatzzeile gehören könnten. Sie sind nicht zugeordnet und müssen mit der Karte geprüft werden:

- Hohenthurm Alte Bahnhofstraße 14 - 17 und 43 bis Bahnhof: 188144140 (71 m), 404956842 (85 m), 570393938 (69 m), 1481058679 (90 m), 53512821 (110 m)
- Hohenthurm Alte Bahnhofstraße 42 - 42 D: 104384352 (157 m), 104384329 (179 m)
- Gütz Otto-Quandt-Straße: 1425709704 (47 m)
- Landsberg Leipziger Straße 36 A - 36 D: 39962397 (152 m)
- Queis Delitzscher Chaussee 13, 15: 224871227 (176 m)
- Reinsdorf Friedensplatz und Merseburger Straße: 424590033 (175 m)
- Reußen Hauptstraße: 887532620 (74 m)
- Zwebendorf Reideburger Straße: 142238366 (64 m), 1053081240 (25 m), 224877384 (39 m)
- Braschwitz Zöberitzer Weg 17 - 18 und 2 A bis 2 E: 33046422 (40 m)
