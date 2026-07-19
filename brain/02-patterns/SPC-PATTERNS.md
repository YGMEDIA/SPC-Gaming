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
**Form:** Strikt seriell: Claude nennt EINEN Amazon-Link → Yasin liefert Screenshot → Daten extrahieren → products.json + betroffene HTML-Stellen updaten (Schema = sichtbarer Text!) → nächster. Nie mehrere gleichzeitig, nie ohne Screenshot.
**Gesetze:** §A1, §A4, §A5.

## P-5 · Blog-Artikel-Pattern
**Wann:** Jeder neue oder ausgebaute Blog-Artikel.
**Form:** verdict-box (Direktantwort aufs Frage-Keyword) → H2/H3-Prosa (~800 W) → aufklappbare FAQ → Related-Box → Finder-CTA. Article+BreadcrumbList+FAQPage-Schema, OG komplett. Kontextuelle Links auf Reviews/Hubs (§B4). Byline/Layout einheitlich.
**Vorlage:** blog/cloud-gaming-smartphone/.
**Gesetze:** §B1, §B4, §B5.

## P-6 · Longtail-Datenblatt-Pattern [bewiesen 18.07.2026]
**Wann:** Alt-/Budget-Modelle aus dem Longtail-Sheet, oft nicht (mehr) bei Amazon.de kaufbar.
**Form:** gen_longtail.py + assets/data/longtail.json (getrennt von products.json, §A1): P-2-Template, aber Kaufbox → Verfügbarkeits-Box (ehrlich, kein Kauflink), Preiszeile → Status-Zeile, 2-3 kaufbare Alternativen als related-cards + "Beste Alternative"-CTA. Product-Schema NUR belegte Felder (kein Preis/Rating/Bild). Generator-Asserts: FAQ-Schema == sichtbarer Text, ≥2 kaufbare Links, Title ≤62.
**Vorlage:** /produkte/8bitdo-lite-2/ (Top-Volumen) · /produkte/mocute-050/ (ehrliche Abratung).
**Gesetze:** §A5, §A6, §B1, §B3.

## P-7 · Verify-Suite-Pattern
**Wann:** Vor jedem "fertig", nach jedem Umbau.
**Form:** scripts/verify.py — stdlib-only, Exit 0/1, prüft: JSON-LD-Validität, interne Links, Sitemap (XML + Datei-Abgleich beidseitig), No-JS-Statik (Karten-Mindestzahlen), Invarianten (CNAME, .nojekyll, kein /ratgeber/, keine \x02), products.json-Integrität (Pflichtfelder, Unikate), data-asin-Format.
**Gesetze:** Teil D.

## P-8 · Screenshot-als-Ground-Truth-Pattern
**Wann:** Jede externe Datenlage (Amazon, GSC, GA4).
**Form:** Yasin liefert Screenshot/Export → landet konzeptionell in 03-research/raw/ (Ablage der Kernzahlen als datierte Notiz) → Claude leitet Maßnahmen ab und schreibt die INTERPRETATION getrennt von den Rohzahlen. Rohdaten werden nie überschrieben.
**Gesetze:** Leitprinzip 1, §A5, Leseregel "Rohquellen unantastbar".

## P-9 · Bilder-Galerie-Pattern [bewiesen 19.07.2026]
**Wann:** Mehrbild pro Sortiments-Produkt (Block H Teil 2) auf generierten Detailseiten.
**Beschaffung:** Amazon blockt nur programmatische Zugriffe — Yasins ECHTER Chrome via Claude-in-Chrome-Extension kommt durch. Pro ASIN: /dp/ASIN öffnen, hiRes-URLs per Regex `["']hiRes["']\s*:\s*["'](https:[^"']+)["']` aus den Seiten-Scripts ziehen (dedupe, Original-Reihenfolge; browser_batch bündelt navigate+JS für ~5 Produkte pro Call). Validierung: urls[0] muss idealerweise der products.json-img entsprechen (Methoden-Beweis); jede Galerie-URL per HEAD == 200; Dedupe gegen img über die Bild-ID (Pfadteil vor `._`).
**Daten:** `gallery`-Feld in products.json = 2–3 Zusatz-URLs (ohne Hauptbild-Duplikat). products.json bleibt einzige Wahrheit (§A1).
**Bau:** gen_pages.py rendert bei vorhandenem gallery eine "Produktbilder"-Sektion (figure-Grid, lazy, onerror-remove) zwischen Specs und Stärken/Schwächen; Product-Schema `image` wird Array [img, ...gallery]. Regeneration NUR über `gen_pages.py --regen [slugs]` (Normalmodus baut nur detail-lose Produkte; --regen fasst NIE Review-Seiten an). Vor Galerie-Läufen: Drift-Test mit einem galerielosen Produkt (git diff muss leer bis kosmetisch sein).
**Alt-Texte:** Ohne Bild-Sichtung KEINE erfundenen Merkmale (§A5-Geist): "{Name}, Produktansicht N". Merkmals-Alts nach A4-Formel erst, wenn Bilder gesichtet werden (Review-Galerie-Paket).
**Vorlage:** /produkte/risoka-trigger/ · Gesetze: §A1, §A2, §A5, §C3.

---

## Offen / noch zu definieren
- Outreach-Vorlagen-Pattern (Block F — Blogger-Anschreiben)
- Scheduled-Loop-Pattern (Automatisierung via Claude-Desktop-Schedule — erst nach 2–3 manuellen Läufen je Loop)

*SPC Pattern-Katalog v1.1 · 2026-07-19*
