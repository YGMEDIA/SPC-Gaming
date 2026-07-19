# 2026-07-19 · content · Kuratierung beste-budget-controller (Rahmen-Fix)

**Was:** Platz 3 der Budget-Liste (/vergleich/beste-budget-controller/) getauscht: GameSir X2s Bluetooth (53 €) raus, 8BitDo Ultimate Mobile (45 €) rein. Fund aus Preis-Sync Welle 2: Nach der Preis-Korrektur verletzte der X2s sichtbar den Seiten-Rahmen "unter 50 €".

**Wie:** Kompletter article-Block getauscht (P-1-Karten-Stil der Seite): Claim "Hall-Effect-Sticks und -Trigger für 45 €." (belegt durch products.json-claim + price), Specs Sticks/Bluetooth aus JSON, Button "Zum Kurzcheck" auf /produkte/8bitdo-ultimate-mobile/ (das Produkt hat Kurzcheck statt Review, Button-Text ehrlich angepasst), data-asin B0DK36N98Q. Kein weiterer Sync nötig: X2s kam auf der Seite nur 1x vor, Schema ist nur BreadcrumbList. Sitemap-lastmod 19.07.

**Verify:** Assertion 0 X2s-/53-€-Reste · verify.py GRÜN (99 Seiten, 221 Schemas).

**Gelernt:** Preis-Syncs können Kuratierungs-Fehler SICHTBAR machen (korrekter Preis passt nicht mehr zum Listen-Rahmen) — Kuratierungs-Check gehört ans Ende jedes Preis-Sync-Laufs (Ergänzung in der preis-loop-Checkliste sinnvoll beim nächsten Lauf).
