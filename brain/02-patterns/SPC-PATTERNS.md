# SPC PATTERN-KATALOG

> Wiederkehrende Bau-Muster, aus dem echten Projekt erkannt. Jede Änderung folgt einem Pattern — oder definiert hier ein neues. Ein Pattern ist erst "echt", wenn es mindestens einmal im Repo funktioniert.

## P-1 · Produktkarten-Pattern
**Wann:** Jede Darstellung eines Produkts in Grids (Hubs, /produkte/, Finder, Marken).
**Form:** `.pcard` mit data-product (slug), .pcard-brand/-name/-claim/-specs, price-row, .pcard-actions = btn-detail ("Mehr erfahren" → detail) + btn-amazon (data-asin, data-product, data-img, href="#"). Statisches HTML und JS-Renderer (hub-render.js/produkte.js/finder.js) erzeugen **byte-identisches Markup** — Hydration überschreibt 1:1 (§A2).
**Vorlage:** gen_hubs.py `card_html()` = Referenz-Implementierung.
**Gesetze:** §A1, §A2, §A3.

## P-2 · Detailseiten-Generator-Pattern
**Wann:** Produktseiten ohne redaktionelles Voll-Review.
**Form:** gen_content.py (CONTENT-Dict: verdict, 2 Absätze, pros/cons, 2 FAQs — individuell geschrieben, nie Template-Floskeln) + gen_pages.py (Kurzcheck-Layout: Breadcrumb, verdict-box, Specs mit sichtbarem Amazon-Rating, Stärken/Schwächen, FAQ, Related ×3, Sticky-CTA; Product+BreadcrumbList+FAQPage-Schema). Ehrlichkeits-Abstufung nach §A6.
**Vorlage:** /produkte/risoka-finger-sleeves/ (stark) · /produkte/marsgaming-mgpxpro/ (ehrliche Abwertung).
**Gesetze:** §A1, §A4, §A6.

## P-3 · Hub-Pre-Render-Pattern
**Wann:** Jede Seite, deren Produktliste aus products.json kommt.
**Form:** gen_hubs.py rendert Karten statisch in den Grid-Container, setzt Zähler statisch, injiziert SEO-Editorial (3 Absätze mit internen Links) + FAQ-Sektion + ItemList/BreadcrumbList/FAQPage-Schema. JS filtert/hydratisiert danach.
**Vorlage:** controller/ios/index.html.
**Gesetze:** §A2, §B1, §B4.

## P-4 · Review-Update-Loop-Pattern
**Wann:** Preis-/Daten-Aktualisierung bestehender Produkte.
**Form:** Strikt seriell: Claude nennt EINEN Amazon-Link → Felgen liefert Screenshot → Daten extrahieren → products.json + betroffene HTML-Stellen updaten (Schema = sichtbarer Text!) → nächster. Nie mehrere gleichzeitig, nie ohne Screenshot.
**Gesetze:** §A1, §A4, §A5.

## P-5 · Blog-Artikel-Pattern
**Wann:** Jeder neue oder ausgebaute Blog-Artikel.
**Form:** verdict-box (Direktantwort aufs Frage-Keyword) → H2/H3-Prosa (~800 W) → aufklappbare FAQ → Related-Box → Finder-CTA. Article+BreadcrumbList+FAQPage-Schema, OG komplett. Kontextuelle Links auf Reviews/Hubs (§B4). Byline/Layout einheitlich.
**Vorlage:** blog/cloud-gaming-smartphone/.
**Gesetze:** §B1, §B4, §B5.

## P-6 · Longtail-Datenblatt-Pattern (geplant — Spec ausstehend)
**Wann:** Alt-/Budget-Modelle aus dem Longtail-Sheet, oft nicht (mehr) bei Amazon.de kaufbar.
**Form:** P-2-Template + "Nachfolger/Alternative im Sortiment"-Box (2–3 Karten auf kaufbare Produkte) statt/neben CTA. Ehrlicher Verfügbarkeits-Hinweis. Ziel: Traffic-Fänger → Weiterleitung auf Geld-Seiten.
**Status:** wird mit SPEC-longtail-batch1 real.

## P-7 · Verify-Suite-Pattern
**Wann:** Vor jedem "fertig", nach jedem Umbau.
**Form:** scripts/verify.py — stdlib-only, Exit 0/1, prüft: JSON-LD-Validität, interne Links, Sitemap (XML + Datei-Abgleich beidseitig), No-JS-Statik (Karten-Mindestzahlen), Invarianten (CNAME, .nojekyll, kein /ratgeber/, keine \x02), products.json-Integrität (Pflichtfelder, Unikate), data-asin-Format.
**Gesetze:** Teil D.

## P-8 · Screenshot-als-Ground-Truth-Pattern
**Wann:** Jede externe Datenlage (Amazon, GSC, GA4).
**Form:** Felgen liefert Screenshot/Export → landet konzeptionell in 03-research/raw/ (Ablage der Kernzahlen als datierte Notiz) → Claude leitet Maßnahmen ab und schreibt die INTERPRETATION getrennt von den Rohzahlen. Rohdaten werden nie überschrieben.
**Gesetze:** Leitprinzip 1, §A5, Leseregel "Rohquellen unantastbar".

---

## Offen / noch zu definieren
- Bilder-Galerie-Pattern (Block H — Mehrbild pro Produkt, Alt-Text-Systematik)
- Outreach-Vorlagen-Pattern (Block F — Blogger-Anschreiben)
- Scheduled-Loop-Pattern (Automatisierung via Claude-Desktop-Schedule — erst nach 2–3 manuellen Läufen je Loop)

*SPC Pattern-Katalog v1.0 · 2026-07-18*
