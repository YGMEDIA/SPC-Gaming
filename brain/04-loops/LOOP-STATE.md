# LOOP-STATE

> Zentrale Zustandsdatei aller Loops. JEDER Lauf liest sie zuerst; erledigte Arbeit wird nie wiederholt (Loop-Regel 3). Max. 3 Versuche pro Item, dann → blockiert (Regel 4). Menschen-Gates → "braucht Yasin" (Regel 5).

**Letzte Aktualisierung:** 2026-07-19 (nach gsc-loop Lauf 1)

## Erledigt
| Datum | Loop | Item |
|---|---|---|
| 2026-07-18 | (Setup) | Brain aufgesetzt, verify.py gebaut, Zombies behoben (/ratgeber/, marken/ipega, marken/mocute) + .nojekyll |
| 2026-07-18 | (Spec Block A) | A1 Finder-Keyword · A2 drei Klick-Artikel verstärkt · A3 alle 13 Blog-Artikel ≥3 Geld-Links · A4 Alt-Pass (67 Bilder, 0 Verstöße). Details: 05-protokoll/2026-07-18-content-block-a.md |
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
| deploy-loop | Deploy Brain-Stand + Block A; dabei Pages-Source auf "GitHub Actions" umstellen. WICHTIG: nur per git push deployen — GitHub-Web-Upload ("Add files via upload") hat /ratgeber/ zum 3. Mal wiederbelebt und .nojekyll nie mitgenommen |
| gsc-loop | GSC Indexierungs-Screenshot (Indexierung → Seiten) + wöchentliches Leistungs-Paket |
| (Block C) | Bing Webmaster Tools einrichten |
| (Tracking) | GA4-Echtzeit-Check affiliate_click nach Deploy |
