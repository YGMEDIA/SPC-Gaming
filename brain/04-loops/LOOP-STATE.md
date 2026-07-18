# LOOP-STATE

> Zentrale Zustandsdatei aller Loops. JEDER Lauf liest sie zuerst; erledigte Arbeit wird nie wiederholt (Loop-Regel 3). Max. 3 Versuche pro Item, dann → blockiert (Regel 4). Menschen-Gates → "braucht Yasin" (Regel 5).

**Letzte Aktualisierung:** 2026-07-18 (nach Block A)

## Erledigt
| Datum | Loop | Item |
|---|---|---|
| 2026-07-18 | (Setup) | Brain aufgesetzt, verify.py gebaut, Zombies behoben (/ratgeber/, marken/ipega, marken/mocute) + .nojekyll |
| 2026-07-18 | (Spec Block A) | A1 Finder-Keyword · A2 drei Klick-Artikel verstärkt · A3 alle 13 Blog-Artikel ≥3 Geld-Links · A4 Alt-Pass (67 Bilder, 0 Verstöße). Details: 05-protokoll/2026-07-18-content-block-a.md |
| 2026-07-18 | (Wiederholungs-Fix) | /ratgeber/-Zombie (3. Rückkehr, via Commit 418b937 "1.1") erneut gelöscht + .nojekyll erneut angelegt (war nie im Git — Web-Upload nimmt keine Dotfiles) |

## Blockiert
| Loop | Item | Grund | Versuche |
|---|---|---|---|
| preis-loop | Screenshot-Verifizierung 9 offene ASINs (Queue im preis-loop) | wartet auf Amazon-Screenshots (Yasin) | 0 |
| preis-loop | Voll-Abgleich August | fällig ab 01.08. | 0 |
| preis-loop | 12 Preisdivergenzen HTML vs. products.json syncen (Scan 18.07.): vergleich/backbone-one-vs-gamesir-g8 (G8 79→80), vergleich/backbone-pro-vs-kishi-v3-pro (Kishi V3 Pro 147→149), blog/mobile-gaming-setup (X5 32→38, G8 79→80), controller/universal/gamesir-x2s-review + razer-kishi-v3-pro-review (G8 79→80), controller/beste (X5 32→38, G8 79→80, Backbone One 99→65), marken/gamesir (X5 32→38, G8 79→80) | mechanischer Sync, nächster preis-loop-Lauf (Geld-Seiten, nicht Block-A-Scope) | 0 |
| content-loop | iOS-Hub-FAQ behauptet, CoD Mobile unterstütze keine Controller — Widerspruch zu blog/welche-spiele-controller (CoD ist offiziell controller-kompatibel, PUBG nicht). Hub-FAQ korrigieren (Schema + sichtbarer Text) | nächster content-loop-Lauf | 0 |

## Braucht Yasin
| Loop/Quelle | Item |
|---|---|
| deploy-loop | Deploy Brain-Stand + Block A; dabei Pages-Source auf "GitHub Actions" umstellen. WICHTIG: nur per git push deployen — GitHub-Web-Upload ("Add files via upload") hat /ratgeber/ zum 3. Mal wiederbelebt und .nojekyll nie mitgenommen |
| gsc-loop | GSC Indexierungs-Screenshot (Indexierung → Seiten) + wöchentliches Leistungs-Paket |
| (Block C) | Bing Webmaster Tools einrichten |
| (Tracking) | GA4-Echtzeit-Check affiliate_click nach Deploy |
