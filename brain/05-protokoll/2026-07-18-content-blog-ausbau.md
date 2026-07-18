# 2026-07-18 · content · Blog-Ausbau: alle 8 Kurz-Artikel auf P-5

> Kategorie: content · content-loop Lauf 1, als Batch auf Yasins Anweisung (statt 1 Artikel/Lauf)

## Was
Die 8 Kurz-Artikel (108 bis 427 Wörter) auf vollen P-5-Standard gebracht: usb-c-vs-bluetooth, mobile-gaming-setup, trigger-erlaubt-pubg, was-ist-ein-smartphone-controller, finger-sleeves-sinnvoll, handy-kuehler-sinnvoll, huellen-kompatibilitaet, hall-effect-erklaert. Je Artikel: Article-Schema (datePublished 2026-07-07 aus Git), FAQPage-Schema mit 4 neuen, sichtbaren FAQs, Byline, 4-5 neue Prosa-Sektionen, Related-Box, Finder-CTA, kontextuelle Geld-Links mit products.json-exakten Preisen. hall-effect-erklaert (rankt bereits) bekam NUR Prosa-Ergänzungen hinter den bestehenden Passagen, A2-Stand unangetastet. Bestehende Inhalte und A3-Links blieben überall erhalten (nur Ergänzung, kein Umschreiben).

Nebenkorrekturen (§A1/§A6): usb-c-vs-bluetooth behauptete, CoD Mobile sperre Bluetooth im Ranked (dritter Fundort desselben CoD-Fehlers, korrigiert) + Tippfehler "stabielste". mobile-gaming-setup nannte veraltete Zubehör-Preise (Sleeves 9, Trigger 12, Kühler 35 €) — auf JSON-Werte gesynct (7/9/17 €).

## Wie
Wiederverwendbarer Helper (Scratchpad blogx.py) mit harten Asserts: Article-Schema-Dedup, FAQ-Schema == sichtbarer Text, ≥700 Wörter netto nach Einbau. Abschluss-Gate über alle 13 Artikel: Wortzahl, ≥3 einzigartige Geld-Links, Schema-Tripel Article+BreadcrumbList+FAQPage, FAQ-Spiegel — 13/13 bestanden. Sitemap-lastmod der 8 URLs auf 2026-07-18.

## Warum so
- Ergänzen statt umschreiben: Auch die Kurz-Artikel können erste Impressionen gesammelt haben; bestehende Passagen blieben wortgleich stehen, neue Sektionen hängen dahinter.
- FAQs auf echte Suchfragen ausgerichtet (Bann-Risiko Trigger, Latenz-Zahlen, Hüllen-Abbrüche, Kühler-FPS), das ist die §B4-Blog-first-Fläche für neue Longtail-Queries.
- Batch statt Einzelläufe: explizite Anweisung Yasins; die Loop-Regel "1 Artikel pro Lauf" bleibt für den Normalbetrieb bestehen (in content-loop.md als Abweichung dokumentiert).

## Verify
verify.py GRÜN (98 Seiten, 218 JSON-LD-Blöcke). Abschluss-Gate 13/13 OK (Wortzahlen 700 bis 1032). Live-Check nach Deploy: Stichproben-Artikel 200 + neue FAQ sichtbar.

## Gelernt
1. Der CoD-Mobile-Faktenfehler existierte an DREI Stellen (iOS-Hub, Android-Hub, usb-c-Artikel) — Faktenfehler wandern durch Copy-Paste. Bei künftigen Korrekturen immer projektweit greppen, nicht nur die gemeldete Stelle fixen.
2. Wortzahl-Schätzung beim Schreiben liegt systematisch ~10 % zu hoch — das Assert-Gate im Helper hat jeden Unterlauf sofort gefangen. Muster beibehalten: Gates in den Werkzeugen, nicht als Nachkontrolle.
