# GSC-LOOP (wöchentlich)

**Zweck:** Datenbasierte Steuerung — was rankt, entscheidet, was gebaut wird (Leitprinzip 1, P-8).
**Input (Yasin, wöchentlich):** Screenshots/Export aus GSC: Leistung 7 Tage (Suchanfragen + Seiten) + Indexierung → Seiten (IMMER mitliefern, auf frisches "Letzte Aktualisierung"-Datum achten). Optional GA4-Wochenzahlen.
**Ablauf:**
1. Kernzahlen als datierte Notiz nach 03-research/raw/gsc/ (JJJJ-MM-TT.md: Klicks, Impressionen, Position, Top-Queries, Top-Seiten, Indexstand). Rohzahlen nie überschreiben.
2. Interpretation getrennt: Auf-/Absteiger, neue Query-Chancen (Impressionen ohne passende Seite → content-loop-Warteschlange), Indexierungs-Probleme (→ Befund).
3. Maßnahmen ableiten: max. 3 konkrete Punkte, in LOOP-STATE bzw. Warteschlangen eintragen.
**Fertig-Kriterium:** raw-Notiz existiert + Interpretation in STATUS (3 Sätze) + Warteschlangen aktualisiert.
**Erfolgskontrollen offen (Checkliste Lauf 4):**
1. **EINBRUCH-KONTROLLE (wichtigster Punkt):** Kommen Impressionen/Klicks nach dem 25.07.-Einbruch zurück? Yasin liefert SAUBERES 7-Tage-Fenster + 28-Tage-Vergleich. Falls weiter nahe 0: Positions-Analyse der Top-5-Bestandsqueries (Query-Filter), erst danach über Content-Reaktionen entscheiden.
2. Meta-Freeze einhalten bis dieser Punkt geklärt ist (keine Title/Description-Änderungen an Seiten mit Impressionen).
3. ratgeber-Stubs: 404-Klicks weg? (www…/ratgeber/… muss via Refresh auf /blog/ landen; GSC-Seitenliste auf /ratgeber/-Reste prüfen)
4. Neue Seiten per Seiten-Filter prüfen (Vergleich g8-plus-vs-kishi-v3-pro, 4 Kalender-Artikel, kishi-ultra, scuf-nomad): erste Impressionen? Die 6 Indexierungs-Anträge vom 27.07. müssen jetzt sichtbar sein.
5. verbindet-nicht: bleibt die Seite auch nach Einbruch-Erholung unsichtbar → Positions-Analyse + ggf. Title-Rückbau als Experiment (NUR nach Freeze-Ende).
6. Indexierung: FRISCHES Datum + Gründe-Tabelle zum aktuellen Stand (fehlte im 07.08.-Paket). Kontrolle: 69 indexiert (24.07.) → weiter steigend? "Gefunden, nicht indexiert" (47 Baseline) endlich fallend?
7. Finder "controller finden" (0/28): bei >30 Impr. Snippet-CTR-Analyse (nach Freeze-Ende).
Erwartet & kein Befund: robots.txt blockiert /suche/ + Parameter absichtlich (§B3) · www-Konsolidierung läuft (Technik sauber geprüft 27.07. + 07.08.).
**Läufe:** 2026-07-19 · Lauf 1 (Fenster 11.-17.07., Vorher-Baseline; 2 Maßnahmen in content-loop, 1 Beobachtungspunkt). · 2026-07-27 · Lauf 2 (Fenster 18.-26.07.: Position 16,8 → **13,6**, CTR 1,6 → 2,3 %, Klicks 7; Klick-Träger drehen von Blog auf Startseite/Zubehör-Hubs; Maßnahmen: Vergleichs-Artikel G8 Plus vs. Kishi V3 Pro gebaut, Yasin-Indexierungs-Anträge, www-Diagnose sauber). · 2026-08-07 · Lauf 3 (Mischfenster 3M/28T: **Einbruch ab 25.07. auf nahe 0**, Technik-Ausschluss bestanden, externe Aug-Volatilität dokumentiert, Haupthypothese New-Site-Boost-Ende; Meilenstein 10 Klicks/28T erreicht 04.08., Indexierung 53→69; Maßnahmen: 14 ratgeber-Stubs deployed, Meta-Freeze, Q4-Saat vorgezogen).
