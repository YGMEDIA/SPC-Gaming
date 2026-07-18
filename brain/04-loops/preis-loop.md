# PREIS-LOOP (monatlich)

**Zweck:** Preise, Verfügbarkeit und Bewertungszahlen aller 40 Produkte aktuell halten (§A1, §A4, §A5). Letzter Voll-Abgleich: 07.–10.07.2026.
**Trigger:** Monatsanfang, oder wenn Yasin Screenshots liefert.
**Ablauf (P-4, strikt seriell):**
1. LOOP-STATE lesen; offene Produkte aus letztem Lauf zuerst.
2. Kandidatenliste erzeugen: products.json nach ältestem Preis-Stand sortiert (STATUS-Datumseinträge); Top 10 pro Lauf.
3. Pro Produkt: Amazon-Link an Yasin → Screenshot abwarten → products.json + alle sichtbaren HTML-Stellen + Schema synchron updaten → Datum in STATUS.
4. Nicht verfügbare Produkte: als Befund melden (Entfernen = Menschen-Gate).
5. Nach Batch: gen_pages.py + gen_hubs.py + verify.py → STATUS + LOOP-STATE fortschreiben.
**Fertig-Kriterium (maschinell):** verify.py grün UND kein bearbeitetes Produkt mit Preis-Diff zwischen products.json und HTML (verify prüft Stichprobe).
**Menschen-Gate:** ASIN-Wechsel, Produkt-Entfernung, >10 Dateien.
**Offene Screenshot-Queue (übernommen aus STATUS 10.07., Reihenfolge = Abarbeitung):**
Trigger: B0CNPVCJCL ozkak-6finger · B0CSSDDH52 ozkak-gamepad · B0DPQQJYL4 risoka-trigger · B0F3JF5P5J toaluea-trigger-joystick — dann Handy-Kühler: B09LVF2RYL razer-phone-cooler · B0F1FW7BYG magnet-peltier · B0GWL9QDRG black-shark-funcooler — dann Sonstige: B0DVLTX8SX trust-gxt-rgb · B07ZQ9G7ZX ozkak-mini-portable.
Hinweis: Die zugehörigen Karten/Detailseiten wurden am 08.–11.07. mit Bestandsdaten gebaut; die Queue dient der Screenshot-VERIFIZIERUNG dieser Werte (§A5), nicht dem Neubau.
**Läufe:** — (noch keiner über das Brain)
