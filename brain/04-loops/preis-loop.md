# PREIS-LOOP (monatlich)

**Zweck:** Preise, Verfügbarkeit und Bewertungszahlen aller 40 Produkte aktuell halten (§A1, §A4, §A5). Letzter Voll-Abgleich: 07.–10.07.2026.
**Trigger:** Monatsanfang, oder wenn Yasin Screenshots liefert.
**Ablauf (P-4, strikt seriell):**
1. LOOP-STATE lesen; offene Produkte aus letztem Lauf zuerst.
2. Kandidatenliste erzeugen: products.json nach ältestem Preis-Stand sortiert (STATUS-Datumseinträge); Top 10 pro Lauf.
3. Pro Produkt: Amazon-Link an Yasin → Screenshot abwarten → products.json + alle sichtbaren HTML-Stellen + Schema synchron updaten → Datum in STATUS.
   **Preis-Träger-Checkliste (Lehre 19.07. — der 18.07.-Sync fand nur Kaufboxen):** (a) Kaufbox/Specs-Tabelle der Review-Seite · (b) Product-Schema offers.price · (c) Meta-/OG-/Twitter-Description · (d) Prosa: Verdict, Fazit, Pro/Con-Items, FAQ (Schema UND sichtbar) · (e) related-cards (rc-price) + cat-cards (cat-count) in ALLEN anderen Reviews · (f) Karten-Claims mit Preisnennung (products.json claim + statische Karten auf Startseite/Hubs/Vergleichen) · (g) /vergleich/-Tabellen samt winner-Zellen und Differenz-Aussagen ("X € günstiger"). Suchmuster: pcard-Parser (pcard-name → price-row, 900er-Fenster, Alias-Map für Kurznamen) als Standard-Audit — ±120-Greps übersehen Karten-Layouts (Lehre Welle 3, 19.07.); (h) statische Karten-price-rows auf Hubs/Marken/Startseite (11.07.-Rendering driftet, gen_hubs nie nachgelaufen).
4. Nicht verfügbare Produkte: als Befund melden (Entfernen = Menschen-Gate).
5. Nach Batch: gen_pages.py + gen_hubs.py + verify.py → STATUS + LOOP-STATE fortschreiben.
**Fertig-Kriterium (maschinell):** verify.py grün UND kein bearbeitetes Produkt mit Preis-Diff zwischen products.json und HTML (verify prüft Stichprobe).
**Menschen-Gate:** ASIN-Wechsel, Produkt-Entfernung, >10 Dateien.
**Offene Screenshot-Queue (übernommen aus STATUS 10.07., Reihenfolge = Abarbeitung):**
Trigger: B0CNPVCJCL ozkak-6finger · B0CSSDDH52 ozkak-gamepad · B0DPQQJYL4 risoka-trigger · B0F3JF5P5J toaluea-trigger-joystick — dann Handy-Kühler: B09LVF2RYL razer-phone-cooler · B0F1FW7BYG magnet-peltier · B0GWL9QDRG black-shark-funcooler — dann Sonstige: B0DVLTX8SX trust-gxt-rgb · B07ZQ9G7ZX ozkak-mini-portable.
Hinweis: Die zugehörigen Karten/Detailseiten wurden am 08.–11.07. mit Bestandsdaten gebaut; die Queue dient der Screenshot-VERIFIZIERUNG dieser Werte (§A5), nicht dem Neubau.
**Läufe:** 2026-07-19 · außerplanmäßig (Fund bei content-loop Lauf 3): 42 veraltete Preis-Stellen in 27 Seiten auf products.json-Wahrheit gesynct — /vergleich/-Tabellen (inkl. 2 gekippter "günstiger"-Aussagen), related-/cat-cards aller Reviews, Meta-Descriptions, FAQ-Texte, X5-Lite-Schema-offers, Startseiten-Claims; dazu X2s-Varianten-Korrektur (Karten sagten "Type-C/USB-C/Pass-Through", Produkt ist lt. products.json + eigenem Review die Bluetooth-Variante). Kein Screenshot nötig: Sync AUF bereits belegte JSON-Werte. Details: 05-protokoll/2026-07-19-content-preis-sync-vergleiche.md · Welle 3 gleicher Tag: 27 Karten-price-rows auf Hubs/Marken/Startseite (05-protokoll/2026-07-19-content-preis-sync-welle3.md)

## Rückfluss aus der Rating-Welle (21.07.2026)
- **Preis-Welle = Rating-Welle.** Nie nur Preise prüfen: Bewertungen hängen an denselben Trägerstellen UND lösen §A6-Konsequenzen aus (Warnpflicht unter 3,8). Am 21.07. waren 42 von 42 Rating-Angaben veraltet, während die Preise dreimal gesynct worden waren.
- **Keine geschätzten Counts mehr** ("900+", "1.200+"). Sie altern schlecht und lagen durchweg zu hoch. Exakte Zahlen sind über den Chrome-Belegweg beschaffbar.
- **Beschaffung (Standard):** alle ASINs über Yasins Chrome, Preis aus `#corePrice_feature_div`, Rating aus `#acrPopover[title]`, Anzahl aus `#acrCustomerReviewText`; ASIN-Schlüssel aus der URL, nicht aus `#ASIN`. Rohdaten nach `03-research/raw/amazon/JJJJ-MM-TT-*.md`.
- **Sync-Reihenfolge:** products.json → `gen_pages.py --regen` → `sync_new_products.py --refresh` (Karten, Zähler, ItemList) → Hand-Seiten → Gegen-Audit.
- **NIE an generierten Seiten von Hand korrigieren** (Generator-Drift): Quelle ist `gen_content.py` bzw. `products.json`, sonst wirft der nächste Generator-Lauf alles zurück.
- **Immer unabhängiges Gegen-Audit** nach Massen-Syncs: Am 21.07. übersahen die Bereichs-Läufe 62 Stellen und schleppten einen neuen Fehler ein (fremder Preis in einer Karte).
- **Varianten-Listings prüfen:** Bewertungszahlen können die ganze Varianten-Familie meinen (Backbone One PS: 16.951 statt produktgenau) und Listings ohne Preis sind ein Auslistungs-Signal.
