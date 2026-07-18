# 2026-07-18 · content · Block B umgesetzt (Longtail Batch 1) + Loop-Fixes

> Kategorie: content · Erster voll autonomer Arbeitslauf (Commit + Push ohne Rückfragen)

## Was

**Loop-Fixes (Warteschlange aus Block-A-Session):**
- content-loop: CoD/PUBG-FAQ in iOS- UND Android-Hub korrigiert. Vorher behaupteten beide, CoD Mobile unterstütze keine Controller; richtig ist: CoD Mobile hat offiziellen Controller-Support mit eigenem Matchmaking, PUBG Mobile nicht. Schema + sichtbarer Text + gen_hubs.py in einem Zug synchron geändert.
- preis-loop: 12 Preisdivergenzen auf products.json-Werte gesynct (G8 Galileo 80 €, X5 Lite 38 €, Kishi V3 Pro 149 €, Backbone One 65 €) in 8 Dateien; projektweite Nachkontrolle 0 Restfunde. Beleg: Voll-Abgleich 07./08.07.

**Block B — Longtail Batch 1 (P-6, damit erstmals real):**
10 Datenblatt-Seiten unter /produkte/ für Altmodelle: 8bitdo-lite-2 (Keyword ~500/Mon.!), 8bitdo-lite-se, gamesir-x2, gamesir-x3, gamesir-t4-pro, ipega-pg-9083s, ipega-pg-9023, mocute-050, razer-kishi-v1, gamesir-g4s.
- Neue Datenbasis `assets/data/longtail.json` (bewusst NICHT products.json, §A1-Abgrenzung laut Spec) + neuer Generator `scripts/gen_longtail.py` (idempotent, kompletter Overwrite).
- Jede Seite: Kurz-Einschätzung, ehrlicher Verfügbarkeits-Hinweis (Altmodell, kein Kauflink), 2 individuelle Absätze, Eckdaten-Tabelle explizit als "Herstellerangaben/Archiv, nicht selbst getestet" gekennzeichnet, 3 kaufbare Alternativen als Karten + Sticky-Box mit "Beste Alternative"-CTA und Finder-Link (Konversionspfad), 2 individuelle FAQs.
- Schema: Product NUR mit belegten Feldern (name, brand, description, url — kein Preis, kein Rating, kein Bild) + BreadcrumbList + FAQPage. Generator erzwingt per assert: FAQ-Schema == sichtbarer Text, ≥2 interne Links auf kaufbare Produkte, Title ≤62 Zeichen.
- Sitemap 87 → 97 URLs (lastmod 2026-07-18). llms.txt unverändert (Spec: keine Kern-Seiten).
- Keyword-Vergabe in `03-research/keyword-strategie.md` dokumentiert (§B1), inkl. Abgrenzung zu den Nachfolger-Reviews (keine Doppelbelegung).

## Wie
Template 1:1 an gen_pages.py (P-2) angelehnt, aber als eigener Generator: Kaufbox durch Verfügbarkeits-Box ersetzt, Preiszeile durch Status-Zeile. Inhalte individuell geschrieben (P-2-Regel: keine Template-Floskeln); Fakten konservativ gehalten und als Herstellerangaben markiert, unsichere Werte (Akku-mAh, exakte Preise, Ratings) bewusst weggelassen (§A5). Verify-Gates maschinell im Generator + verify.py.

## Warum so
- Kein Kauflink am Altmodell: ehrlicher als tote oder Drittanbieter-Links, und der Konversionspfad läuft sauber über die Alternativen-Karten zu unseren Review-/Kurzcheck-Seiten mit aktuellem Preis.
- iPega/Mocute als Datenblatt trotz Sortiments-Rauswurf: Die Suchnachfrage existiert; die Seiten erklären transparent, WARUM wir die Marken nicht mehr führen, und leiten auf Kaufbares um. Das ist §A6-Positionierung, kein Widerspruch zur Rauswurf-Entscheidung (die betraf /marken/-Hubs mit Kaufempfehlung).
- gen_hubs.py-Fix per Hand-Sync statt Regenerierung: Der Generator ist nicht idempotent (würde SEO/FAQ-Blöcke und Schemas duplizieren) — als Warnung im Protokoll, Kandidat für späteren Umbau.

## Verify
verify.py GRÜN: 98 Seiten · 204 JSON-LD-Blöcke · 40 Produkte · Sitemap 97 URLs beidseitig abgeglichen. Generator-Asserts: 10/10 Seiten mit sichtbarem FAQ-Schema-Text, ≥2 kaufbare Links, Title-Limit. Preis-Nachkontrolle projektweit 0 Altwerte.

## Gelernt
1. **gen_hubs.py ist nicht idempotent** (Insert-basiert statt Overwrite) — bei Hub-Änderungen IMMER Hand-Sync von Schema + Text + Generator, nie blind neu rendern. Umbau auf idempotentes Rendering wäre ein sinnvolles kleines Spec.
2. **P-6 ist jetzt bewiesen** (Pattern-Katalog kann den Status "geplant" verlieren): P-2-Template + Verfügbarkeits-Box + Alternativen-Karten, Datenbasis getrennt in longtail.json.
3. Title-Gate als Assert im Generator fängt Fehler vor dem Schreiben — billiger als jede nachträgliche Prüfung.
