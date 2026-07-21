# 2026-07-21 · preis-loop · Rating-Welle: alle 42 Produkte auf frischen Amazon-Belegstand

**Was:** Den am selben Tag gefundenen Befund (products.json vs. Review-Seiten divergieren bei Bewertungen, teils §A4-Verstöße) vollständig aufgelöst. Erstmals wurden Preise UND Ratings aller 42 Produkte in einem Zug frisch belegt und sitewide durchgezogen.

**Beschaffung:** Alle 42 ASINs über Yasins Chrome ausgelesen (Preis aus `#corePrice_feature_div`, Rating aus `#acrPopover[title]`, Anzahl aus `#acrCustomerReviewText`), ASIN-Schlüssel aus der URL statt aus `#ASIN` (Varianten-Listings melden dort die Parent-ASIN). Rohdaten als Ground Truth: `03-research/raw/amazon/2026-07-21-rating-welle.md`.

**Wie groß der Schaden war:** 16 Preise und 42 Rating-Angaben mussten korrigiert werden. Die schwersten Fälle:
- **G8 Galileo (unser Testsieger): 4,4 (1.200+) → 4,2 (688)** — die Site wies ihn deutlich besser aus, als er ist.
- **Backbone One 2. Gen: 4,4 (900+) → 4,1 (51)** — die Bewertungsbasis war um den Faktor 18 zu hoch angegeben.
- ROG Tessen 4,3 (400+) → 4,0 (125) · X3 Pro 4,2 (200+) → 3,9 (283) · Turtle Beach 4,1 (300+) → 4,0 (1.896).
- Preise: X5 Lite 38 → 45 € (verliert den Budget-King-Titel), G8 Plus 76 → 90 € (jetzt teurer als der Testsieger), HELLCOOL ab 29 → ab 50 €, M4 Snap-On 38 → 50 €; dagegen Trust 40 → 30 €, abxylute S8 46 → 39 €, VITURE 79 → 67 €, X2s 53 → 46 €.
- **Alle "Plus"-Counts (900+, 1.200+, 400+ …) waren Schätzungen und durchweg zu hoch.** Sie sind jetzt exakte Zahlen.

**Akute §A4-Verstöße, die dabei ans Licht kamen und behoben wurden:** Backbone-One-2-Schema behauptete `offers.price` 99 € bei sichtbaren 63 € · Kishi-V3-Schema 99 € bei 93 € · ROG-Tessen-Schema 4,3/400 bei sichtbarem 4,0/122 · X2s `review.reviewRating` 4 bei sichtbaren 3,8. Genau die Klasse, die Google als Preis-Mismatch abstraft.

**Ablauf:** products.json zuerst (Wahrheit, §A1) → gen_pages `--regen` → `sync_new_products.py --refresh` (neuer Modus: rendert bestehende Karten neu, statt nur fehlende einzufügen; Karten, hubCount, ItemList-Schemas) → Workflow mit 4 Bereichs-Agents (Reviews, Vergleiche/Bestenlisten, Blog, Hubs/Marken/Startseite) → unabhängiges Gegen-Audit. Ergebnis: rund 330 Ersetzungen in 90 Dateien. Das Gegen-Audit fand 62 von den Sync-Agents übersehene Stellen, darunter einen eingeschleppten Fehler (G8-**Plus**-Preis in der G8-**Galileo**-Karte auf marken/gamesir) und neun nie angefasste Longtail-Archivseiten.

**Inhaltlich gekippte Aussagen wurden neu formuliert, nicht nur umgezahlt** (Auswahl): X5 Lite "Budget-King für unschlagbare 38 €" → "Preis-Leistungs-Tipp für 45 €" (der Preis-Anker ist jetzt der 8BitDo 2C für 20 €) · G8 Plus "sehr stark für 76 €" → "liegt über dem Testsieger, Aufpreis nur für Bluetooth" · X2s war "Mittelweg zwischen X5 Lite und G8 Galileo", bei 1 € Abstand zum X5 Lite hinfällig · Razer Phone Cooler war "teuerster Kühler mit 10 € Markenaufschlag", ist jetzt gleich teuer wie der besser bewertete Black Shark · Setup-Rechnungen im Blog nachgerechnet (Einsteiger-Setup 45 → 52 €).

**§A6-Konsequenz:** Drei Produkte sind unter die 3,8-Schwelle gefallen und haben jetzt explizite Warnungen statt Kaufempfehlung: Razer Phone Cooler 3,2 (72), magnet-peltier-cooler 3,4 (128), ozkak-trigger-gamepad 3,6 (277). Kontrolle: alle fünf Produkte unter 3,8 tragen die Warnung sichtbar.

**Generator-Drift (wichtige Lehre):** Die Sync-Agents hatten auch generierte `/produkte/`-Seiten von Hand korrigiert, ohne die Quelle `gen_content.py` anzufassen. Ein `--regen` hätte alles zurückgeworfen — an drei Seiten live beobachtet, als ich für die §A6-Warnungen regenerierte. Behoben: 28 Korrekturen an der Quelle, danach alle 29 GEN-Seiten neu gebaut. **Regel für künftige Wellen: An generierten Seiten wird nie von Hand korrigiert, immer an gen_content.py bzw. products.json.**

**Verify:** verify.py GRÜN (104 Seiten, 227 Schemas, 42 Produkte) nach jeder Etappe · eigener Nachlauf: 0 ALT-Werte sitewide, 0 §A4-Probleme (jeder Schema-Wert sichtbar im Text), GEN-Seiten-Konsistenz gegen products.json fehlerfrei, alle 5 Unter-3,8-Produkte mit Warnung · 3 Commits, deployed, IndexNow je 103 URLs.

**~~Offen (braucht Yasin)~~ GELÖST am selben Abend:** **Backbone One PS (B0CT17GPNT)** wurde bewusst nicht aktualisiert. Das Listing zeigt keinen Preis, heißt "iPhone (Lightning) 1st Gen" und die 16.951 Bewertungen gehören zur gesamten Varianten-Familie, nicht zu dieser Variante. Lightning ist für iPhone 15+ obsolet. Entscheidung nötig: Produkt behalten (dann mit welchem Beleg?), auf die aktuelle Variante umstellen oder auslisten.

**Gelernt:** (1) Geschätzte "Plus"-Angaben altern schlecht und werden im Zweifel zu optimistisch geschätzt — exakte Zahlen sind Pflicht, jetzt sind sie beschaffbar. (2) Eine Preis-Welle muss immer eine Rating-Welle sein: Beide Werte hängen an denselben Trägerstellen, und Ratings tragen zusätzlich §A6-Konsequenzen. (3) Bei Massen-Syncs braucht es ein unabhängiges Gegen-Audit; die Bereichs-Agents übersahen 62 Stellen und schleppten einen neuen Fehler ein. (4) Generierte Seiten und ihre Quelle müssen im selben Arbeitsschritt gepflegt werden.

**Nachtrag: Backbone One PS Edition gelöst.** Yasin lieferte das richtige Listing: **B0BHH8DT37** (das bisher geführte B0CT17GPNT war ein Familien-Listing ohne Preis). Ausgelesen: 58,99 € → geführt als 59 €, **4,2 bei 312 produktgenauen Bewertungen** statt der Familien-Schätzung 4,3 (500+), Modellnummer BB-02-W-S, "Nur noch 1 auf Lager". Unsere Review-Seite führte das Modell schon korrekt als "Lightning, iPhone 14 & älter" — kein inhaltlicher Widerspruch. Gesynct: products.json (ASIN, Preis, Rating), Karten via `--refresh`, Review-Seite (data-asin, sichtbarer Text, Schema-ratingValue/reviewCount), Blog-Preisnennungen. Gegen-Audit: 0 Reststellen der alten ASIN und der alten Werte. Damit sind **alle 42 Produkte belegt und konsistent**.

**Neuer Merkposten daraus:** 6 der 13 Review-Seiten (die älteren) haben kein `offers` im Product-Schema, also kein Preis-Snippet in den Suchergebnissen. Kein Verstoß, aber verschenkte Sichtbarkeit — seit der Welle sind alle Preise belegt, das Nachrüsten wäre ein kleines eigenes Paket.
