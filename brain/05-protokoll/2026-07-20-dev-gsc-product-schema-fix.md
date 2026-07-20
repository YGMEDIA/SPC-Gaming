# 2026-07-20 · dev · GSC-Kritikmeldung Produkt-Snippets: 10 Longtail-Product-Schemas entfernt

**Was:** Yasin bekam die GSC-Mail "Probleme vom Typ Produkt-Snippets" (WNC-10030322, kritisch): "Entweder offers, review oder aggregateRating müssen angegeben werden." Repo-Scan über alle 103 Seiten (JSON-LD rekursiv geparst): Betroffen sind exakt die **10 Longtail-Datenblätter** aus Block B (gamesir-x2/x3/t4-pro/g4s, ipega-9083s/9023, mocute-050, razer-kishi-v1, 8bitdo-lite-2/lite-se). Deren Product-Schema war bewusst minimal (nur name/description/brand/url, "nur belegte Felder") — genau dieses ehrlich gemeinte Minimal-Product ist für Google ein kritischer Fehler.

**Warum so gelöst (Product-Schema ersatzlos raus statt Felder ergänzen):** Die drei von Google akzeptierten Felder sind ohne Beleg nicht ehrlich zu füllen — Preise der Altgeräte schwanken/fehlen (teils delisted), Ratings ohne Screenshot-Beleg verbietet §A5. Ein Product ohne Rich-Result-Anspruch bringt auf diesen Seiten nichts, der Longtail-Traffic kommt über Text + FAQ. Also: BreadcrumbList + FAQPage bleiben, Product entfällt. Die 4 heutigen Rich-Results-Tests waren grün, weil keine Longtail-Seite dabei war.

**Wie:** gen_longtail.py: schema_prod entfernt (Kommentar dokumentiert den Grund samt WNC-Nummer) → alle 10 Seiten regeneriert (Diff je Seite: exakt der 13-Zeilen-Product-Block). **Rückfluss doppelt:** (1) verify.py-Invariante neu — jedes Product-Schema muss offers/review/aggregateRating tragen, rekursiv über alle JSON-LD-Blöcke; (2) Constitution §A4-Zusatz. Beweis in beide Richtungen: verify VOR der Regeneration ROT mit exakt 10 Treffern, NACH ihr GRÜN.

**Verify:** Scan 103 Seiten → 10 Treffer = 10 Longtail-Blätter (kein anderer Seitentyp betroffen) · verify rot→grün wie oben · Diff-Kontrolle gamesir-x2 (nur Schema-Block entfernt) · Sitemap-lastmod 10/10 auf 2026-07-20 · Commit + Deploy + IndexNow.

**Yasin (optional, 1 Klick):** In der GSC-Mail auf "Probleme beheben" → "Validierung starten" klicken beschleunigt die Grün-Meldung; ohne Klick löst der nächste reguläre Crawl es auch.

**Gelernt:** "Nur belegte Felder" reicht bei Schema.org nicht als Regel — Google definiert PFLICHT-Kombinationen je Typ. Vor dem Einsatz eines Schema-Typs die Google-Pflichtfelder gegen unsere belegbaren Daten prüfen; wenn sie nicht ehrlich füllbar sind, den Typ weglassen. Die verify-Invariante macht diese Klasse (Product) jetzt unmöglich; weitere Typen bei Bedarf ergänzen.

**Nachtrag:** Yasin hat die GSC-Validierung am 20.07. gestartet ("Prüfung läuft"). Erfolgskontrolle als Punkt 8 in der gsc-loop-Checkliste verankert; Google meldet den Abschluss per Mail (typisch wenige Tage bis ~2 Wochen).
