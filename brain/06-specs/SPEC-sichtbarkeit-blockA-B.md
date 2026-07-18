# SPEC · Sichtbarkeit Block A (Quick Wins) + Block B (Longtail Batch 1)

> Feature-Spec #1 des SPC Brain · Status: **ZUR FREIGABE (Felgen)** · geschrieben gegen das echte Repo, Stand 2026-07-18
> Gelesen zusammen mit: SPC-CONSTITUTION (§A, §B), SPC-PATTERNS (P-2, P-3, P-5, P-6), CLAUDE.md.

## 1 · Ziel & Datenbasis
GSC 18.07.: 7 Klicks, alle über Blog; "controller finden" = Top-Impressions-Query (9) ohne optimierte Zielseite; Position 18,3 steigend. Ziel dieses Specs: die nachweislich funktionierenden Assets verstärken (A) und die schnellste Ranking-Fläche für eine junge Domain aufbauen (B). Erfolgskontrolle nach 3–4 Wochen im gsc-loop.

## 2 · Block A — Quick Wins On-Site
**A1 Finder-Seite auf "controller finden":** Title "Controller finden — Welcher Controller passt zu mir? | smartphone-controller.com", H1/Description angleichen, statischer SEO-Textblock (~2 Absätze) unter dem Tool + 3 FAQs mit FAQPage-Schema (No-JS-konform, §A2). Interne Links von Startseite/Hubs auf den Finder prüfen ("Controller-Finder" → Ankertext "Controller finden").
**A2 Klickende Blog-Artikel verstärken (P-5):** welche-spiele-controller, controller-iphone-15-16-usb-c, hall-effect-erklaert — je: 2–3 zusätzliche FAQ aus verwandten Suchfragen, interne Links auf konkrete Reviews/Hubs schärfen, Title-CTR prüfen (≤62 Zeichen). Kein Umschreiben rankender Passagen (Rankings nicht gefährden).
**A3 Interne Verlinkung Blog → Geld-Seiten:** Alle 13 Artikel: ≥3 kontextuelle Links auf Reviews/Hubs, Audit + Nachrüstung.
**A4 Alt-Text-Pass (Block H, Teil 1):** Projektweit generische Alts durch beschreibende, keyword-relevante ersetzen (Produktname + Merkmal + Kontext). Kein Bild ohne Alt.

## 3 · Block B — Longtail Batch 1 (P-6, neu zu beweisen)
10 Datenblatt-Seiten unter /produkte/ nach P-2-Template + "Alternative im Sortiment"-Box. Auswahl (aus Longtail-Sheet, Volumen × Konkurrenz): 8bitdo lite 2 (~500!), 8bitdo lite se, gamesir x2 (Vorgänger), gamesir x3 (Vorgänger), gamesir t4 pro, ipega 9083s, ipega 9023, mocute 050, razer kishi v1, gamesir g4s. Nicht kaufbare Modelle: ehrlicher Verfügbarkeits-Hinweis + 2–3 kaufbare Alternativen als Karten (Konversionspfad). Sitemap +10, llms.txt unverändert (keine Kern-Seiten).
**Abgrenzung:** KEINE erfundenen Preise/Ratings für Altmodelle — nur belegbare Fakten (Specs aus Herstellerangaben, als solche gekennzeichnet) oder neutrale Beschreibung. §A5 gilt.

## 4 · Gesetzes-Check
§A1 (Batch-Produkte optional in eigener longtail.json, NICHT in products.json — sie sind keine Sortiments-Produkte; Entscheidung: eigene Datei) · §A2 statisch · §A4 kein aggregateRating ohne belegte Werte · §A5 ✓ · §B1 ein Keyword/Seite, Vergabe in keyword-strategie.md dokumentieren · §B3 Sitemap · §B5 verify.

## 5 · Verify-Gate (maschinell)
verify.py grün · 10 neue Seiten mit validem Schema (Product ohne Rating bzw. nur belegte Felder, BreadcrumbList) · jede Batch-Seite hat ≥2 interne Links auf kaufbare Produkte · Finder-Seite zeigt SEO-Block ohne JS · Alt-Audit: 0 Bilder ohne Alt, 0 Alts == Dateiname.

## 6 · Explizit NICHT in diesem Spec
Batches 2–5 (erst Erfolgskontrolle) · Mehrbild-Galerien (Block H Teil 2, braucht Bild-URLs von Felgen) · Blog-Ausbau der 8 Kurz-Artikel (content-loop) · Backlinks (Block F).

## 7 · Freigabe
[ ] Felgen: freigegeben am ______ / Änderungen: ______
