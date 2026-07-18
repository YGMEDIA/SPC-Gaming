# SPC STATUS

> Lebendiges Session-Gedächtnis. Hält fest, was zuletzt passiert ist, was läuft und was als Nächstes kommt.
> Regel: Nach jedem abgeschlossenen Schritt aktualisiert. Bei Widerspruch gewinnt das Repo, dann wird diese Datei korrigiert.
> Lesereihenfolge für neue Sessions: INDEX.md → diese Datei → gezielt weiter.
> Historie vor dem Brain (Juni bis 11.07.2026) ist unten als Kompakt-Archiv erhalten; Details liegen in den Chat-Verläufen.

**Letzte Aktualisierung:** 2026-07-18

---

## Wo wir stehen

**Site:** LIVE, 88 Seiten (Stand-Korrektur nach Brain-Commit: 87 indexierbare + Suche), Sitemap 87 URLs, Analytics/GTM aktiv (Events seit 11.07.-Fix korrekt), Search Console + Bing offen.

**Erste echte Marktdaten (GSC, 18.07., 3-Monats-Sicht = real ~10 Tage Index):**
7 Klicks · 348 Impressionen (Verzehnfachung in einer Woche) · Ø Position 18,3 (von 23 kommend) · CTR 2 %.
**Kern-Erkenntnis:** ALLE Klicks kommen über Blog-Artikel ("Welche Spiele unterstützen Controller" 2×, iPhone-USB-C, Hall-Effect) → Blog-first-Vererbung ist bewiesen (§B4), Blog-Ausbau hat Priorität. Top-Impressions-Begriff ohne optimierte Zielseite: "controller finden" (9) → Block A.

**Strategie:** Sichtbarkeits-Plan mit Blöcken A–H steht (Framework Teil VI). Block E (Reddit/Gutefrage) von Yasin freigegeben und bei ihm in Arbeit. Spec A+B am 18.07. freigegeben; **Block A und Block B umgesetzt + deployed (18.07.)** — Spec #1 damit komplett abgearbeitet (`06-specs/SPEC-sichtbarkeit-blockA-B.md`).

**Brain:** Am 18.07. aufgesetzt (Framework, Constitution, Patterns, Loops, Specs, verify.py, CLAUDE.md). Ersetzt das ZIP-/STATUS-Handoff-Verfahren. Stand-Korrektur (Repo gewinnt): Der im Brain-Setup dokumentierte Actions-Deploy war NIE im Repo (.github/ fehlte komplett) — nachgeholt am 18.07. abends samt Pages-Umstellung.

**Arbeitsmodell (seit 18.07. abends, Yasins Entscheidung):** VOLLAUTONOMIE. Claude Code committet und pusht selbst; Push auf main deployt automatisch via GitHub Actions. Hartes Maschinen-Gate: verify.py grün vor jedem Commit, nie einen roten Stand pushen. Menschen-Gates nur noch: Geld-/ASIN-Änderungen ohne Screenshot-Beleg · .github/workflows · .claude/settings.json. Yasin: Live-Stichproben + Rollback via git revert. Nachtrag (18.07. spät): Permission-Prompts komplett abgeschafft (settings.json: bypassPermissions, deny nur rm -rf/sudo) + Kontext-Schnitt-Regel etabliert (Constitution v1.2): Sessions enden nur an sauberen Schnitten — Teilstück fertig, verify grün, gepusht, Folgeschritt in STATUS.

## Todo-Landkarte (wo liegt was — ein Blick von hier reicht)
| Art des Todos | Ort | Aktuell dort |
|---|---|---|
| Entscheidungen & Handgriffe für Yasin | **hier unten: "Braucht Yasin"** | 6 Punkte (Live-Stichprobe, Bing, GSC-Screenshot, GA4-Test, 2. Domain, Rich-Results) |
| Offene Mängel mit Gesetzes-Bezug | **hier: Befund-Tabelle** | 6 offen (reviewCounts, Rechtstexte, Domains, Tracking-Kontrolle, Preisdivergenzen, CoD-FAQ); Brain-Leak 18.07. behoben |
| Fernes / bewusst Geparktes | **hier: Später-Merkposten** | Clarity, ATP-Anfragen, Pinterest, Unboxings, Loop-Automatisierung |
| Freigegebene/wartende Bauvorhaben | `06-specs/` | SPEC-sichtbarkeit-blockA-B: A+B umgesetzt 18.07. (komplett), nächstes Spec offen |
| Laufende Arbeits-Warteschlangen | `04-loops/LOOP-STATE.md` + Loop-Dateien | content-loop: Blog-Ausbauten KOMPLETT (18.07.), nächstes: neue Artikel/Batches nach GSC-Signal · preis-loop: 9 Screenshot-ASINs + Voll-Abgleich August |
| Große Roadmap (Blöcke A–H) | `SPC-FRAMEWORK.md` Teil VI | E läuft (Yasin), A+B umgesetzt, C–H danach |
| Detail-Doku alles Gemachten (Was+Wie) | `05-protokoll/` (+ `marketing-log.md` für Block E/F) | #1 Brain-Setup · #2 Block A · #3 Vollautonomie (alle 18.07.) |
Regel: Ein Todo steht an genau EINEM Ort; diese Tabelle verlinkt nur. Neue Todos landen zuerst hier in STATUS (Braucht Yasin / Befund / Merkposten) oder in einer Loop-Warteschlange — nie in Chat-Verläufen.

---

## Befund-Status
| Befund | Gesetz | Status |
|---|---|---|
| **brain/ + Root-STATUS.md + SPC-Gaming-Visuals/ waren LIVE öffentlich** (Pages im Legacy-Modus deployte den ganzen Branch; /brain/STATUS.md lieferte HTTP 200; der dokumentierte Actions-Workflow existierte nie) | §B2 / Governance 5 | **behoben 18.07. abends:** deploy.yml erstellt (Option A), Pages auf GitHub Actions umgestellt, Root-STATUS-Zombie gelöscht, Push + Live-Check /brain/ → 404 |
| /ratgeber/ lag als Duplikat neben /blog/ live; kehrte per Bulk-Upload (Commit "1.1") ein DRITTES Mal zurück | §B2 | **behoben + deployed 18.07. abends, live 404-verifiziert** — Ursache war Deploy per GitHub-Web-Upload; künftig NUR git push |
| marken/ipega/ + marken/mocute/ als Zombie-Seiten live (am 08.07. beschlossen gelöscht, per Upload-Deploy zurückgekehrt) | §B2 | **behoben im Brain-Commit, deployed 18.07. abends** — von verify.py gefunden (Sitemap-Rückabgleich) |
| .nojekyll war laut Git-Historie NIE committet (Web-Upload nimmt keine Dotfiles) | §B2 | **erneut angelegt + deployed 18.07.** (unter Actions-Deploy ohnehin obsolet, bleibt als Belt-and-Braces) |
| 12 Preisdivergenzen HTML vs. products.json auf Geld-Seiten (u. a. controller/beste: Backbone One 99 statt 65 €) | §A1 | offen — Warteschlange preis-loop (Liste in LOOP-STATE); in den 3 Block-A-Artikeln bereits gesynct |
| iOS-Hub-FAQ behauptet, CoD Mobile unterstütze keine Controller — Widerspruch zu blog/welche-spiele-controller (Blog ist korrekt) | §A6 | offen — Warteschlange content-loop (Schema + sichtbarer Text zusammen ändern) |
| Tracking-Events erreichten GA4 nie (gtag statt dataLayer.push, keine Delegation) | §A8 | behoben 11.07., deployed — **Erfolgskontrolle in GA4-Echtzeit noch offen (Yasin)** |
| 5 Reviews mit geschätzten reviewCounts (ROG Tessen, X3 Pro, Turtle Beach, Backbone One PS, Kishi V3 Pro) | §A4 | offen — bei nächsten Screenshots präzisieren |
| Rechtstexte ohne anwaltliche Abnahme | §C4 | offen (Yasin) |
| .de-Domain + eine weitere Domain nicht angebunden (Redirect empfohlen; welche zweite Domain: Yasin nennt sie noch) | — | offen (Yasin, IONOS) |

## Braucht Yasin (Entscheidungen & Handgriffe)
1. **Live-Stichprobe nach dem ersten autonomen Deploy** (Prüfliste im Protokoll content-block-a): kurz gegenchecken, ob live alles wie erwartet aussieht. Ab jetzt gilt: Deploys laufen autonom, nie mehr "Add files via upload".
2. **Bing Webmaster Tools** einrichten (Block C, ~20 Min, GSC-Import).
3. **GSC Indexierungs-Screenshot** (Indexierung → Seiten) — die Zahl fehlt uns noch.
4. GA4-Echtzeit-Check: kommt `affiliate_click` jetzt an? (1 Testklick nach Consent genügt.)
5. Zweite anzubindende Domain benennen (neben der .de).
6. **Bild-URLs für Mehrbild-Galerien (Block H Teil 2):** Pro Sortiments-Produkt 2-3 zusätzliche Amazon-Bild-URLs (Rechtsklick auf Produktbild → Grafikadresse kopieren, §C3). Sobald die da sind, baue ich Galerien + Schema autonom.
7. **Rich-Results-Test** nach Deploy (offen seit 11.07.): search.google.com/test/rich-results — G8-Galileo-Review + 2–3 neue /produkte/-Seiten auf Sterne-Snippets prüfen; NEU dazu: /controller-finder/ (frisches FAQPage-Schema).

## Später-Merkposten
- **Microsoft Clarity** (Heatmaps) via GTM nachrüsten — kein Code-Deploy nötig, erst wenn genug Traffic für auswertbare Daten da ist.
- **3 freie AnswerThePublic-Anfragen** ungenutzt — aufheben für gezielte Keyword-Vertiefung (z. B. vor Blog-Neuartikeln).
- Pinterest-Mini-Test (Q4) · TikTok/Shorts-Unboxings · Scheduled-Loop-Automatisierung (nach 2–3 manuellen Läufen je Loop).

---

## Verlauf (chronologisch, neueste zuletzt — Kompakt; Details je Schritt in `05-protokoll/`)

1. **Kompakt-Archiv Juni–10.07.** Site-Aufbau in 5 Phasen (Keywords → Architektur → 57 Seiten → QA), Deployment auf GitHub Pages + IONOS-DNS, GTM/GA4 über Consent Mode v2 live (Lehre: Container VERÖFFENTLICHEN, nicht nur speichern), Search Console Domain-Property + Sitemap, Produkt-Review-Workflow per Screenshots (13 Reviews + Karten aktualisiert, iPega/Mocute entfernt), Shop-Umbau (/produkte/ mit Filtern, products.json 40 Produkte, Hubs dynamisch), Blog konsolidiert (13 Artikel, /ratgeber/ aufgelöst), Cookie-Banner, Finder interaktiv, SEO-Paket (OG sitewide, Product-Schema 13 Reviews, 5er-Skala-Fix).
2. **11.07. Tiefen-Optimierung (Fable 5), deployed.** GEO-Pre-Rendering der Hubs + /produkte/ (statische Karten, SEO-Editorial, FAQs, ItemList), 27 generierte Produkt-Detailseiten (alle 40 Produkte haben "Mehr erfahren"), Tracking-Fix (dataLayer.push + Delegation), products.json bereinigt (Preise, Slugs, Marken), 14 tote Buttons repariert, \x02-Korruption in 13 Reviews gefixt, BreadcrumbList auf 48 Seiten, Organization-Schema, llms.txt, Sitemap 87, Titles/Descriptions auf 21 Seiten, Startseiten-Fotostrip. Alles Playwright-verifiziert.
3. **18.07. GSC-Auswertung + Sichtbarkeits-Plan.** Erste 7 Klicks analysiert (alle via Blog), Plan A–H aufgestellt, Block E freigegeben (Yasin), Pinterest/Unboxing als Später-Merkposten, Alt-Texte + Mehrbild als Block H notiert.
4. **18.07. Brain gebaut.** Zwei Live-Befunde bei der Repo-Inspektion gefunden und behoben: /ratgeber/-Duplikat (Deploy-Prozess-Fehler: Gelöschtes wurde auf GitHub nie entfernt) + fehlendes .nojekyll. verify.py fand beim Erstlauf zwei weitere Zombie-Seiten (marken/ipega, marken/mocute — gleiche Deploy-Fehlerklasse wie ratgeber, beschlossener Zustand vom 08.07. wiederhergestellt). brain/-Struktur nach USELY/YOU-Muster aufgesetzt (Framework v1.0, Constitution v1.0, Patterns v1.0, 4 Loops + LOOP-STATE, Spec Block A+B, Keyword-Destillat), Generator-Scripts nach scripts/ überführt (repo-relative Pfade), verify.py als maschinelles Gate gebaut, CLAUDE.md, GitHub-Actions-Deploy (Option A: brain/ bleibt privat). Altes Root-STATUS.md hierher migriert und entfernt.

5. **18.07. Block A umgesetzt (diese Session, Deploy ausstehend).** Spec A+B von Yasin freigegeben (nur A in dieser Session). Baseline-Reparatur vorweg: /ratgeber/-Zombie (3. Rückkehr via Bulk-Upload-Commit "1.1") gelöscht + nie committetes .nojekyll angelegt → verify GRÜN. Dann: A1 Finder-Seite auf "controller finden" (Title/H1/Description, statischer SEO-Block mit 5 internen Links, 3 FAQs mit FAQPage-Schema, 7 CTA-Anker sitewide umgestellt) · A2 die drei klickenden Artikel verstärkt (Titles ≤62 Zeichen, je +3 FAQs, PUBG-Faktenfehler korrigiert, hall-effect auf P-5-Standard gehoben inkl. Article-Schema) · A3 alle 13 Blog-Artikel auf ≥3 kontextuelle Geld-Links gebracht (7 nachgerüstet, Finder-CTAs vereinheitlicht) · A4 Alt-Text-Pass (67 Bilder: 45 Produktbild-Alts auf Formel Name+Merkmal+Kontext, Formel auch in gen_pages.py verankert; End-Audit 0 Verstöße). Nebenbefunde in Befund-Tabelle + LOOP-STATE (12 Preisdivergenzen → preis-loop, CoD-FAQ-Widerspruch → content-loop). verify.py GRÜN. Details: `05-protokoll/2026-07-18-content-block-a.md`.

6. **18.07. abends: Vollautonomie + Namenskorrektur + Leak-Fix (diese Session).** Yasins Entscheidung: Claude Code committet/pusht künftig selbst, verify.py ersetzt als hartes Gate das Deploy-Menschen-Gate (CLAUDE.md, Constitution v1.1 Teil D, Framework v1.1, deploy-loop, settings.json umgestellt). Namenskorrektur projektweit: Projektinhaber heißt Yasin (bisheriger Name war Transkriptionsfehler). Dabei KRITISCHEN Befund gefunden und behoben: brain/ war live öffentlich (Pages Legacy-Modus, Actions-Workflow existierte entgegen Doku nie) — deploy.yml erstellt, Pages per API auf "GitHub Actions" umgestellt, Root-STATUS-Zombie gelöscht, erster autonomer Push. Details: `05-protokoll/2026-07-18-system-vollautonomie.md`.

7. **18.07. spät: Erster voll autonomer Arbeitslauf — Loop-Fixes + Block B (deployed).** Ohne Rückfragen umgesetzt und gepusht: (a) CoD/PUBG-FAQ in iOS- und Android-Hub faktisch korrigiert (Schema + Text + gen_hubs.py synchron; gen_hubs ist NICHT idempotent, deshalb Hand-Sync). (b) 12 Preisdivergenzen auf products.json-Werte gesynct. (c) Block B komplett: 10 Longtail-Datenblätter (P-6) via neuem gen_longtail.py aus longtail.json — ehrliche Verfügbarkeits-Hinweise, Specs als Herstellerangaben gekennzeichnet, KEINE erfundenen Preise/Ratings, je 3 kaufbare Alternativen als Konversionspfad, Sitemap 97 URLs, Keyword-Vergabe dokumentiert. verify GRÜN (98 Seiten, 204 Schemas). Details: `05-protokoll/2026-07-18-content-block-b.md`.

8. **18.07. spät: content-loop Lauf 1 — alle 8 Kurz-Artikel auf P-5 (deployed).** Autonomer Batch auf Yasins Anweisung: usb-c-vs-bluetooth, mobile-gaming-setup, trigger-erlaubt-pubg, was-ist-ein-smartphone-controller, finger-sleeves-sinnvoll, handy-kuehler-sinnvoll, huellen-kompatibilitaet je komplett ausgebaut (Article+FAQPage-Schema, Byline, 4-5 Prosa-Sektionen, 4 FAQs, Related, Finder-CTA), hall-effect nur Prosa-Ergänzung (rankt bereits, A2-Ausbau blieb unangetastet). Dabei 2 weitere Faktenkorrekturen (CoD-Behauptung in usb-c-vs-bluetooth, veraltete Zubehör-Preise in mobile-gaming-setup auf JSON-Werte). Maschinelles Gate: 13/13 Artikel ≥700 W netto, ≥3 Geld-Links, Schema-Spiegel. Sitemap-lastmod aktualisiert. Details: `05-protokoll/2026-07-18-content-blog-ausbau.md`.

---

## Nächster geplanter Schritt

**Yasin:** Die 6 Punkte der "Braucht Yasin"-Liste, v. a. Live-Stichprobe, Bing, GSC-Screenshot + Amazon-Screenshots für den preis-loop (9 ASINs + 5 reviewCounts).
**Claude Code (nächste Session, sobald Yasins Input da ist):** preis-loop-Lauf mit den Screenshots · gsc-loop-Erstlauf mit dem GSC-Paket · danach content-loop (8 Blog-Ausbauten). Ohne Yasin-Input möglich: content-loop-Start.
**Claude Code (nächste Session):** Block B (Longtail Batch 1, 10 Datenblatt-Seiten nach P-6) nach Spec; danach Erfolgskontrolle Block A im gsc-loop (3–4 Wochen).
**Loops:** Erster manueller Lauf des GSC-Loops nach nächstem Screenshot-Paket; Preis-Loop fällig ab August (letzter Voll-Abgleich 07./08.07.) — Warteschlange enthält jetzt zusätzlich 12 dokumentierte Preisdivergenzen.
