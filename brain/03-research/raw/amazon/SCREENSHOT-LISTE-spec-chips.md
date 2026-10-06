# Screenshot-Liste · die letzten ungedeckten Spec-Chips

> Stand 06.10.2026. Gemessen über alle Produktkarten der Site: Chip-Werte, die in
> `products.json` unter keinem Schlüssel stehen. Was hier abgearbeitet ist, verschwindet
> aus dieser Liste, sobald der Wert im Datenkern steht.

**Acht Angaben über sieben Produkte.** Pro Produkt reicht EIN Screenshot der
Amazon-Produktseite, auf dem die genannte Angabe lesbar ist (Titel, Bullet Points oder
Tabelle „Technische Details"). Wenn eine Angabe dort **nicht** steht, ist das auch ein
Ergebnis: Dann fliegt der Chip raus statt in den Datenkern.

| # | Produkt | Angabe, die belegt werden muss | ASIN | Amazon-Link |
|---|---|---|---|---|
| 1 | GameSir X5 Lite | **Gewicht 135 g** | B0DXPMVCWC | https://amazon.de/dp/B0DXPMVCWC |
| 2 | GameSir G8 Galileo | **Gewicht ~230 g** | B0CXHVCTW9 | https://amazon.de/dp/B0CXHVCTW9 |
| 3 | Backbone Pro | **Akkulaufzeit ~40 h** | B0DQM23MLZ | https://amazon.de/dp/B0DQM23MLZ |
| 4 | Razer Kishi V3 | **4 Rücktasten** | B0F2JFWSJ5 | https://amazon.de/dp/B0F2JFWSJ5 |
| 5 | Razer Kishi V3 Pro | **4 Rücktasten** | B0F2JGV9NK | https://amazon.de/dp/B0F2JGV9NK |
| 6 | Razer Kishi V3 Pro | **TMR-Sticks + haptisches Feedback** | B0F2JGV9NK | (derselbe Screenshot wie 5) |
| 7 | 8BitDo Ultimate 2C | **läuft an Switch und PC** | B0D72WYT8Z | https://amazon.de/dp/B0D72WYT8Z |
| 8 | GameSir G8 Plus | **läuft an Switch und PC** | B0FYQ1SHHS | https://amazon.de/dp/B0FYQ1SHHS |

Das sind **sieben Seiten**, weil 5 und 6 derselbe Screenshot sind.

## Was mit den Screenshots passiert

1. Wert aus dem Screenshot in `products.json` eintragen (`specs`), mit Datum und ASIN im
   Beleg-Protokoll unter `03-research/raw/amazon/`.
2. Die Karten-Chips auf den Datenkern ziehen, damit `sync_product_values` sie ab dann
   vergleicht. Danach sind sie gegatet und können nicht mehr auseinanderlaufen.
3. Steht eine Angabe nicht auf der Amazon-Seite: Chip entfernen. Eine Produktaussage ohne
   Beleg gehört weder auf die Karte noch in den Datenkern (§A5).

## Bereits erledigt, ohne Screenshot (06.10.)

Von den ursprünglich 14 gemeldeten Chips brauchten fünf keinen Beleg:

| Chip | Warum kein Screenshot |
|---|---|
| `backbone-one-2` „Gewicht 138 g" | steht als `Gew. 138 g` im Datenkern, nur andere Schreibweise des Schlüssels — angeglichen |
| `ozkak-trigger-l1r1` „Typ: Vergold. Kontakte" | steht als `Kontakte: vergoldet` im Datenkern — angeglichen |
| `ozkak-trigger-gamepad` „Für: Tablet/iPad <10mm" | steht so im Datenkern; die erste Messung hat `&lt;` gegen `<` verglichen und es deshalb als offen gezählt |
| `gamesir-g8-galileo` „Plattform: iOS+Android" (2×) | aus `worksOn` ableitbar und wahr — jetzt mit einem eigenen §A5-Gate gegen `worksOn` geprüft statt ungeprüft gelassen |
