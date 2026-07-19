# 2026-07-19 · dev · Block H2 gestartet: Galerie-Beschaffung via Chrome + gen_pages-Galerie (P-9 neu)

**Was:** Yasins Delegation aus dem Chat ("die Links für die Bilder kannst du über die Claude-Chrome-Extension öffnen und ziehen") umgesetzt: Amazon-Galerie-URLs erstmals AUTONOM beschafft statt per Hand-Kopie durch Yasin. Batch 1: 11 Produkte (10 mit generierten Detailseiten + G8 Galileo als Methoden-Pilot), je 3 validierte Zusatzbilder als neues `gallery`-Feld in products.json. Galerie-Feature in gen_pages.py gebaut und 10 Seiten live regeneriert. Pattern P-9 dokumentiert (Katalog v1.1).

**Die entscheidende Erkenntnis:** §A5 sagt "Amazon blockt jeden programmatischen Zugriff" — das gilt weiterhin für curl/web_fetch auf SHOP-Seiten. Yasins echter Chrome (Claude-in-Chrome) kommt aber durch, und das Bilder-CDN m.media-amazon.com blockt gar nicht (HEAD 200 auch via curl). Beschaffungsweg: /dp/ASIN im echten Chrome öffnen, hiRes-URLs per Regex aus den Seiten-Scripts, browser_batch bündelt ~5 Produkte pro Call. Methoden-Beweis: Beim G8 und 8 weiteren war urls[0] exakt das bestehende products.json-Hauptbild.

**Bau:** `gallery` in products.json (2–3 URLs, Bild-ID-Dedupe gegen img, alle 33 HEAD-validiert) · gen_pages.py: Produktbilder-Sektion (figure-Grid, lazy, onerror-remove) zwischen Specs und Stärken/Schwächen, Product-Schema image als Array [img + gallery] · NEU: `--regen [slugs]`-Modus (der Normalmodus überspringt alle Produkte mit detail-Feld — ein Lauf hätte sonst NICHTS regeneriert; --regen fasst ausschließlich /produkte/-Seiten an, nie Reviews). Drift-Test vorab: galerieloses Produkt regeneriert → Diff nur neue CSS-Regeln + Leerzeile, Template stabil.

**Alt-Texte bewusst neutral** ("{Name}, Produktansicht N"): Ich habe die Bildinhalte nicht gesichtet, erfundene Merkmals-Alts wären §A5-widrig. Merkmals-Alts nach A4-Formel folgen beim Review-Galerie-Paket (Bilder werden dort gesichtet).

**Batch 1 (je 3 Bilder):** 8bitdo-ultimate-mobile · risoka-finger-sleeves · razer-phone-cooler · black-shark-funcooler · risoka-trigger · ozkak-6finger · easysmx-m15 · viture-8bitdo · shanwan-teleskop-black · marsgaming-mgpxpro · (gamesir-g8-galileo: nur Daten, Review-Seite folgt im Hand-Paket). Priorisierung: GSC-Cluster Trigger/Kühler (Impressionen vorhanden) + Budget-Kandidat Ultimate Mobile.

**Verify:** 33/33 URLs HEAD 200 · Schema-Check (image-Array mit 4 Einträgen) · verify.py GRÜN (99 Seiten, 221 Schemas) · Browser-Sichtung /produkte/risoka-trigger/ (3 Kacheln rendern; Lazy-Load-Leerstand im Test war Artefakt des Debug-DOM-Umbaus) · Sitemap-lastmod 11 Seiten.

**Offen (Warteschlange content-loop):** Batch 2 = restliche 17 GEN-Produkte ziehen + regenerieren · Batch 3 = 12 Review-Produkte ziehen · Review-Galerie-Paket = Hand-Einbau in die 13 Review-Seiten inkl. gesichteter Merkmals-Alts. Voraussetzung je Lauf: Yasins Chrome läuft und die Extension ist verbunden.

**Gelernt:** (1) gen_pages.py war bis heute ein Einmal-Generator (detail-Skip) — für jede Template-Änderung ist --regen jetzt der Weg. (2) browser_batch macht die Beschaffung skalierbar (~14 Aktionen/Call stabil). (3) In der Browser-Pane erzwingen versteckte Vorgänger-Sektionen kein Lazy-Reload — für Sichtprüfungen Bilder per src-Reset laden.

**Nachtrag gleiche Session — Batch 2 komplett:** Die 17 restlichen GEN-Produkte in 3 browser_batch-Läufen gezogen; 16 mit je 3 validierten Bildern (48 HEAD-200) regeneriert und deployed. Ausnahme: magnet-peltier-cooler (B0F1FW7BYG) liefert nur 1 hiRes-Bild auf der Amazon-Seite → keine Galerie möglich, kein Fehler (Seite bleibt ohne Galerie-Sektion). Damit haben 26/27 generierte Detailseiten Mehrbild-Galerien. Verbleibende Warteschlange: Batch 3 (12 Review-Produkte ziehen) + Review-Hand-Einbau (13 Seiten, gesichtete Merkmals-Alts).
