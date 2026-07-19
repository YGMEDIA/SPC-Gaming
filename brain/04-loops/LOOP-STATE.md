# LOOP-STATE

> Zentrale Zustandsdatei aller Loops. JEDER Lauf liest sie zuerst; erledigte Arbeit wird nie wiederholt (Loop-Regel 3). Max. 3 Versuche pro Item, dann → blockiert (Regel 4). Menschen-Gates → "braucht Yasin" (Regel 5).

**Letzte Aktualisierung:** 2026-07-19 (nach Galerie-Batch 1, Block H2)

## Erledigt
| Datum | Loop | Item |
|---|---|---|
| 2026-07-19 | (Block H2) | Galerie-Batch 2: 16 restliche GEN-Produkte gezogen + regeneriert (48 URLs validiert); 26/27 GEN-Seiten mit Galerie. magnet-peltier-cooler ohne (Amazon: nur 1 hiRes). Warteschlange: Batch 3 + Review-Einbau |
| 2026-07-19 | (Block H2) | Galerie-Batch 1: 11 Produkte × 3 Bilder autonom via Chrome-Extension gezogen (P-9 neu), gallery-Feld in products.json, gen_pages-Galerie + --regen gebaut, 10 Seiten live. Details: 05-protokoll/2026-07-19-dev-galerie-block-h2.md |
| 2026-07-19 | content-loop | Lauf 3: Marken-Vergleich "GameSir oder Backbone?" neu gebaut (/blog/gamesir-oder-backbone/, P-5, Blog-Index Pos. 1, Sitemap 98, llms.txt, Keyword-Vergabe). Erfolgskontrolle: gsc-loop Punkt 7. Details: 05-protokoll/2026-07-19-content-gamesir-oder-backbone.md |
| 2026-07-19 | preis-loop | Außerplanmäßig: Preis-Sync Welle 2 — 42 veraltete Stellen in 27 Seiten (Vergleiche, related-/cat-cards, Metas, FAQ, X5-Schema, X2s-Variantenfehler) auf products.json gesynct; Träger-Checkliste in preis-loop verankert. Details: 05-protokoll/2026-07-19-content-preis-sync-vergleiche.md |
| 2026-07-19 | content-loop | Lauf 2: CTR-Rettung controller-verbindet-nicht — Title ("Meist in 2 Min. gelöst", 60 Z.) + Description ("kein Defekt", 4 Meta-Stellen synchron) neu, Prosa unangetastet, Sitemap-lastmod 19.07. Erfolgskontrolle: gsc-loop Punkt 6 (Baseline 0/47). Details: 05-protokoll/2026-07-19-content-ctr-verbindet-nicht.md |
| 2026-07-18 | (Setup) | Brain aufgesetzt, verify.py gebaut, Zombies behoben (/ratgeber/, marken/ipega, marken/mocute) + .nojekyll |
| 2026-07-18 | (Spec Block A) | A1 Finder-Keyword · A2 drei Klick-Artikel verstärkt · A3 alle 13 Blog-Artikel ≥3 Geld-Links · A4 Alt-Pass (67 Bilder, 0 Verstöße). Details: 05-protokoll/2026-07-18-content-block-a.md |
| 2026-07-19 | gsc-loop | Nachtrag: Indexierungs-Baseline archiviert (Stand 10.07.: 53/65, Gründe dokumentiert), robots-Blockierungen als gewollt verifiziert, 6-Punkte-Checkliste für nächsten Lauf in gsc-loop.md |
| 2026-07-19 | gsc-loop | Lauf 1 komplett: Rohdaten raw/gsc/2026-07-19.md (Fenster 11.-17.07. = Vorher-Baseline), Interpretation in STATUS, 2 neue content-loop-Items (CTR-Rettung verbindet-nicht, Marken-Vergleich GameSir/Backbone). Indexierungs-Screenshot steht noch aus |
| 2026-07-19 | (Block C) | Bing Webmaster Tools verifiziert (Yasin, GSC-Import) + IndexNow live (Key + Ping-Script, Erst-Ping 97 URLs HTTP 202) |
| 2026-07-18 | content-loop | Alle 8 Kurz-Artikel auf P-5 ausgebaut (je ≥700 W netto, Article+FAQPage-Schema, Byline, Related, Finder-CTA, Sitemap-lastmod). 13/13 Blog-Artikel jetzt auf Vollstandard. Warteschlange Punkt 1 komplett |
| 2026-07-18 | (Spec Block B) | Longtail Batch 1: 10 Datenblatt-Seiten (P-6, gen_longtail.py + longtail.json), Sitemap 97 URLs, Keywords dokumentiert. Erfolgskontrolle ab ~08/2026 im gsc-loop |
| 2026-07-18 | preis-loop | 12 Preisdivergenzen auf products.json-Werte gesynct (Beleg: Voll-Abgleich 07./08.07.); Nachkontrolle projektweit sauber |
| 2026-07-18 | content-loop | CoD/PUBG-FAQ in iOS- und Android-Hub korrigiert (CoD unterstützt Controller offiziell, PUBG nicht) — Schema + sichtbarer Text + gen_hubs.py synchron |
| 2026-07-18 | (Wiederholungs-Fix) | /ratgeber/-Zombie (3. Rückkehr, via Commit 418b937 "1.1") erneut gelöscht + .nojekyll erneut angelegt (war nie im Git — Web-Upload nimmt keine Dotfiles) |

## Blockiert
| Loop | Item | Grund | Versuche |
|---|---|---|---|
| preis-loop | Screenshot-Verifizierung 9 offene ASINs (Queue im preis-loop) | wartet auf Amazon-Screenshots (Yasin) | 0 |
| preis-loop | Voll-Abgleich August | fällig ab 01.08. | 0 |

## Braucht Yasin
| Loop/Quelle | Item |
|---|---|
| gsc-loop | Wöchentliches GSC-Paket ~26.07. (Leistung 7 Tage + FRISCHE Indexierung; Checkliste mit 6 Punkten in gsc-loop.md) |
| preis-loop | Amazon-Screenshots: 9 offene ASINs + 5 geschätzte reviewCounts |
(Erledigt und ausgetragen 19.07.: Actions-Deploy + Pages-Umstellung 18.07. · Bing/IndexNow live · GA4 end-to-end bewiesen · GSC-Paket 1 inkl. Indexierungs-Baseline geliefert — Details in STATUS-Verlauf 6, 11 und Befund-Tabelle.)
