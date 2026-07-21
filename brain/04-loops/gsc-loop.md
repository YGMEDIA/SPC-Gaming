# GSC-LOOP (wöchentlich)

**Zweck:** Datenbasierte Steuerung — was rankt, entscheidet, was gebaut wird (Leitprinzip 1, P-8).
**Input (Yasin, wöchentlich):** Screenshots/Export aus GSC: Leistung 7 Tage (Suchanfragen + Seiten) + Indexierung → Seiten (IMMER mitliefern, auf frisches "Letzte Aktualisierung"-Datum achten). Optional GA4-Wochenzahlen.
**Ablauf:**
1. Kernzahlen als datierte Notiz nach 03-research/raw/gsc/ (JJJJ-MM-TT.md: Klicks, Impressionen, Position, Top-Queries, Top-Seiten, Indexstand). Rohzahlen nie überschreiben.
2. Interpretation getrennt: Auf-/Absteiger, neue Query-Chancen (Impressionen ohne passende Seite → content-loop-Warteschlange), Indexierungs-Probleme (→ Befund).
3. Maßnahmen ableiten: max. 3 konkrete Punkte, in LOOP-STATE bzw. Warteschlangen eintragen.
**Fertig-Kriterium:** raw-Notiz existiert + Interpretation in STATUS (3 Sätze) + Warteschlangen aktualisiert.
**Erfolgskontrollen offen (Checkliste nächster Lauf):**
1. Longtail-Batch 1: erste Impressionen auf 8bitdo-lite-2/ipega/mocute-Datenblätter? (Baseline 0; ipega-Nachfrage existiert nachweislich)
2. Finder-Seite "controller finden": Klicks/Position vs. Baseline 0/9.
3. FRISCHER Indexierungs-Stand (Baseline 10.07.: 53 indexiert / 65 nicht): sinken "Gefunden, nicht indexiert" (47) und "Gecrawlt, nicht indexiert" (11) nach Blog-Ausbau? Wandern die gelöschten Zombies in Weiterleitung/404-Gründe?
4. Falls "Gecrawlt, nicht indexiert" stagniert: Yasin exportiert die URL-Liste des Grunds → gezielte interne Stärkung der Seiten (To-do Claude Code).
5. Falls "Zugriffsverbot 403" (1 Seite) erneut auftaucht: Yasin klickt den Grund an, schickt die URL → Diagnose.
6. CTR-Rettung controller-verbindet-nicht: Wirkung nach Title-Schärfung (Baseline 0/47).
7. Neuer Marken-Vergleich /blog/gamesir-oder-backbone/: erste Impressionen auf das Query-Cluster "gamesir vs/oder backbone" (Baseline: 5+ Varianten je 0 Klicks, auch die ENGLISCHEN Varianten beobachten).
8. ~~GSC-Validierung "Produkt-Snippets"~~ **BESTANDEN 20.07. am selben Tag** (Bestätigungs-Mail WNC-10030335: "Probleme wurden behoben") — kein Prüfpunkt mehr, nur noch Vollständigkeits-Blick: taucht der Fehlertyp im frischen Bericht wirklich nicht mehr auf?
Erwartet & kein Befund: robots.txt blockiert /suche/ + Parameter-URLs absichtlich (§B3); "Alternative Seite mit Canonical" = www-Kanonisierung arbeitet korrekt.
**Läufe:** 2026-07-19 · Lauf 1 (Fenster 11.-17.07., Vorher-Baseline; 2 Maßnahmen in content-loop, 1 Beobachtungspunkt).
