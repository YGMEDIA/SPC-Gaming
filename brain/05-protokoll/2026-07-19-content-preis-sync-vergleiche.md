# 2026-07-19 · content/preis · Preis-Sync Welle 2: /vergleich/ + Querverweise (42 Stellen, 27 Seiten)

**Was:** Beim Vorbereiten des Marken-Vergleichs (content-loop) zeigte der bestehende Modell-Vergleich backbone-one-vs-gamesir-g8 veraltete Preise MIT gekippter Kernaussage: "G8 20 € günstiger als Backbone One" — laut products.json ist der G8 15 € TEURER (80 vs. 65 €). Projektweiter Audit fand 42 Stellen derselben Klasse in 27 Dateien. Alle auf products.json-Wahrheit gesynct (§A1); kein Screenshot nötig, da Sync AUF bereits belegte Werte (Voll-Abgleich 07.–10.07.).

**Betroffene Klassen (alle vom 18.07.-Sync übersehen, der nur Kaufboxen prüfte):**
1. /vergleich/-Duell-Tabellen inkl. winner-Zellen: 2 gekippte bzw. falsche "günstiger"-Aussagen korrigiert (backbone-one-vs-gamesir-g8: Preis-Gewinner ist jetzt der Backbone, Testsieger-Begründung des G8 ehrlich auf "Zwar 15 € teurer, dafür …" umgestellt; g8-galileo-vs-kishi-v3: "20 €" → "14 € günstiger", Label "Preis (UVP)" → "Preis").
2. Best-of-Karten (beste-android/-budget/-iphone): price-rows auf Wahrheit + irreführendes "UVP"-Label durch das ehrliche "ca."-Format ersetzt (Format existierte dort bereits).
3. related-cards (rc-price) und cat-cards (cat-count) in ALLEN Review-Seiten: G8 79→80, Kishi V3 99→94, Backbone One 99→65, X5 Lite 32→38, Ultimate 2C 42→20, Backbone Pro 169→189.
4. Prosa/FAQ/Meta: backbone-one-2-FAQ "Beide kosten ca. 99 €" (doppelt falsch) → getrennte echte Preise; Kishi-v3-Metas; G8-Verdict; Kishi-Con-Item; Backbone-Pro-Verdict+Con; Startseiten-Claims (Kishi 99→94, X5 39→38); Haupt-Hub controller/ (X5 32→38).
5. X5-Lite-Review komplett (9 Stellen inkl. Product-Schema offers.price "32"→"38" — Schema widersprach der eigenen Kaufbox, §A4) + products.json-Claim "Hall-Effect für 32 €" → 38 mit Hand-Sync in 7 statische Karten-Renderings (gen_hubs NICHT benutzt, nicht idempotent).
6. X2s-Varianten-Korrektur: Karten in controller/beste/ + vergleich/beste-budget/ nannten "X2s Type-C, USB-C, Pass-Through, 45 €" — das verkaufte Produkt (ASIN B0D5GTM2PL) ist lt. products.json und eigenem Review die Bluetooth-Variante für 53 €. Name/Spec/Claim korrigiert.
7. Zwei site-intern widerlegbare Superlative im X5-Review präzisiert ("gibt es nirgendwo sonst" → "im Teleskop-Format sonst kaum"; Ultimate 2C hat Hall-Effect für 20 €, ist aber Standalone).

**Wie:** Zwei deterministische Python-Pässe mit exakten Mustern + erwarteter Trefferzahl je Muster (Abbruch ohne Schreiben bei Abweichung; Karten-Muster mit Produktnamen-Anker, weil z. B. 79 € beim VITURE-Modell korrekt ist). Danach Gegen-Audit: 0 Verdachtsstellen. Sitemap-lastmod für alle 27 Seiten auf 19.07.

**Warum so:** Halber Fix (nur /vergleich/) hätte drei divergierende Preisstände pro Produkt hinterlassen; der neue Marken-Artikel braucht die saubere Basis, da er genau diese Produkte bepreist und auf die Vergleiche verlinkt.

**Verify:** Skript-Assertions (33 + 32 Ersetzungen exakt wie erwartet) · Gegen-Audit 0 Reststellen · products.json weiterhin valide · `scripts/verify.py` GRÜN (98 Seiten, 218 Schemas).

**Gelernt (Rückfluss in preis-loop.md, Schritt 3):** Preise leben in 7 Träger-Klassen, nicht nur in Kaufboxen — Checkliste jetzt im Loop verankert. Die LOOP-STATE-Aussage vom 18.07. "Nachkontrolle projektweit sauber" war falsch, weil die Nachkontrolle nur die Kaufbox-Klasse prüfte.

**Offen geblieben (bewusst, → content-loop):** beste-budget-controller rahmt "unter 50 €", listet aber den X2s Bluetooth mit 53 € auf Platz 3 — Kuratierungs-Entscheidung (Kandidat als Ersatz: 8BitDo Ultimate Mobile, 45 €), kein mechanischer Fix.
