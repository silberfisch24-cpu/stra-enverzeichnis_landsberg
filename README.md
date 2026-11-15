# Straßenverzeichnis Landsberg – Baulastkarte

Färbt die Straßen der Stadt Landsberg (Saalekreis) nach Baulast ein (Stadt blau, Kreis orange, Privat rot, Land grün)
auf OpenStreetMap. Quelle: Straßenverzeichnis (OR 288/2026, Stand 06.11.2026).

1. `skripte/01_extrahieren.py` – PDF → `daten/verzeichnis.csv`
2. `skripte/02_osm_holen.py` – Straßen und Ortsteil-Punkte aus OSM (Overpass, braucht Netz)
3. `skripte/03_karte_bauen.py` – Zuordnung per Ortsteil + Name → `docs/strassen.geojson`; Lücken in `daten/nicht_zugeordnet.csv`
4. `docs/index.html` – Leaflet-Karte (GitHub Pages, Ordner `docs/`)

Abweichende Schreibweisen trägt man in `daten/namensanpassungen.csv` ein (ortsteil, strasse_verzeichnis, strasse_osm).
Einträge mit Zusatz (Hausnr., „ab … bis …“) lassen sich nicht auf Wegstücke aufteilen; es gilt der Eintrag ohne Zusatz.
Neues Verzeichnis: PDF als `daten/strassenverzeichnis_<Datum>.pdf` ablegen, Workflow „Karte bauen“ starten.
