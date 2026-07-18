# 2026-07-18 · content · Block A umgesetzt (SPEC-sichtbarkeit-blockA-B)

> Kategorie: content · Spec freigegeben 18.07. (nur Block A; Block B in eigener Session)

## Was

**A0 (ungeplant): Baseline-Reparatur.** verify.py war beim Start ROT: /ratgeber/ als Zombie zurück (3. Rückkehr, eingeschleppt durch Commit 418b937 "1.1" = Bulk-Upload vom lokalen Ordner) und .nojekyll fehlte (war laut Git-Historie NIE committet — GitHub-Web-Upload nimmt keine Dotfiles mit). Beides wiederhergestellt (beschlossener Zustand vom 08.07., keine neue Lösch-Entscheidung), danach GRÜN.

**A1 Finder-Seite auf "controller finden":** Title exakt nach Spec, H1 "Controller finden", Description/OG/Twitter/Breadcrumb angeglichen. Statischer SEO-Block (2 Absätze, 5 interne Links: G8-Review, iOS-/Android-Hub, /produkte/, Budget-Bestenliste) + 3 FAQs mit FAQPage-Schema, Markup 1:1 vom Hub-Pattern (hub-seo/hub-faq) übernommen. 7 CTA-Anker auf Startseite, /controller/, /controller/beste/ und 3 Vergleichsseiten von "Controller-Finder starten" auf "(Jetzt) Controller finden" umgestellt.

**A2 Drei Klick-Artikel verstärkt (P-5), rankende Passagen unangetastet:**
- welche-spiele-controller: Title 66→61 Zeichen, exakt auf GSC-Query "welche spiele unterstützen controller". +3 FAQs (Fortnite, PUBG offiziell, Cloud Gaming) → 7 im Schema. Faktenfehler korrigiert: PUBG war als controller-kompatibel gelistet (Widerspruch zum eigenen Trigger-Artikel) → ehrlicher Sonderfall-Hinweis + Link. +2 Review-Links (Kishi V3, Backbone One).
- controller-iphone-15-16-usb-c: Title 65→57 Zeichen. +3 FAQs (Pass-Through, iPad, Preis mit products.json-exakten Werten). +Cloud-Gaming-Link.
- hall-effect-erklaert: Article-Schema ergänzt (datePublished 2026-07-07 aus Git belegt), og:type→article, Byline, Related-Box + Finder-CTA (P-5-Angleichung). FAQ-Schema 2→7 (2 sichtbare fehlten im Schema, 3 neue inkl. Nachteile-Frage). §A1-Preissync: 79→80, 32→38, 42→20, 99→94 €.

**A3 Interne Links Blog → Geld-Seiten:** Audit-Script (Geld-Links = Reviews/Hubs/produkte/vergleich/zubehoer/gaming-phones, uniq, ohne Finder). 7 Artikel lagen unter 3 (2 davon bei 0) → kontextuell nachgerüstet, u. a. Hüllen-Tabelle: alle 5 Modellnamen → Reviews; Kurz-Artikel Sleeves/Kühler: je 1 Produktlink mit JSON-exaktem Preis. Ergebnis: 13/13 Artikel ≥3. Alle Blog-Finder-CTAs auf "Jetzt Controller finden →" vereinheitlicht.

**A4 Alt-Text-Pass projektweit:** Audit über 88 Seiten / 67 img. Kein Bild ohne/mit leerem/Dateinamen-Alt, aber 45 Produktbilder mit nacktem Produktnamen. Einheitliche Formel (Produktname + Merkmal + Kontext) in scripts/gen_pages.py als `alt_text()` verankert UND per Script auf Bestand angewendet (Startseite, 13 Review-Seiten, 27 produkte/-Seiten, 1 Blog-Hero). Blog-Index-Thumbnails behalten Artikel-Titel als Alt (verlinktes Bild → Alt beschreibt Linkziel, korrekte a11y-Praxis). End-Audit: 0 Verstöße.

## Wie
Diagnose vor Fix (Git-Historie für Zombie-Ursache), Audit-Scripts vor jeder Änderung (Link-Zählung, Alt-Klassifikation, Preis-Scan), Edits per Python mit assert-Guards (kein stilles Fehlschlagen), FAQ-Schema und sichtbarer Text immer aus derselben Quelle generiert und maschinell auf Gleichheit geprüft. Generator-Idempotenz vor gen_pages.py-Änderung per git diff bewiesen (0 Diffs).

## Warum so
- Preise/Fakten nur aus products.json bzw. Git (§A1/§A5) — nichts erfunden, neue FAQ-Preise als Spannen bzw. JSON-exakt.
- PUBG-Korrektur trotz "rankende Passagen nicht anfassen": Faktenfehler mit Selbst-Widerspruch schadet Vertrauen + GEO mehr als eine Listen-Zeile dem Ranking (§A6-Geist). Query-relevante Passagen (H1, Prosa) blieben unberührt.
- 12 weitere Preisdivergenzen auf Geld-Seiten NICHT gefixt: preis-loop-Scope + Geld-Änderungs-Gate → als Warteschlangen-Item in LOOP-STATE dokumentiert.

## Verify
`python3 scripts/verify.py` GRÜN (88 Seiten, 174 JSON-LD, 40 Produkte). Spec-Gate Abschnitt 5: Finder-SEO-Block statisch ohne JS im HTML (maschinell geprüft, FAQ-Schema = sichtbarer Text) ✓ · Alt-Audit 67 Bilder, 0 Verstöße ✓ · 13/13 Blog-Artikel ≥3 Geld-Links ✓.

## Gelernt
1. **Deploy-Prozess ist die eigentliche Fehlerquelle:** "Add files via upload" hat /ratgeber/ zum 3. Mal wiederbelebt und kann keine Dotfiles (.nojekyll). Konsequenz: Deploy nur per git push / Actions — als Warnung in LOOP-STATE (braucht Yasin).
2. **FAQ-Schema driftet vom sichtbaren Text** (hall-effect: 2 von 4 FAQs fehlten im Schema). Kandidat für verify.py-Erweiterung: FAQPage-mainEntity ⊆ sichtbarer Text UND sichtbare .faq-item ⊆ Schema.
3. **Preisdivergenzen entstehen schleichend** (11.07. products.json bereinigt, HTML-Nebenstellen nicht). Kandidat für verify.py oder preis-loop-Script: Muster "Name (XX €)" gegen products.json prüfen.
