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

**Strategie:** Sichtbarkeits-Plan mit Blöcken A–H steht (Framework Teil VI). Block E (Reddit/Gutefrage) von Felgen freigegeben und bei ihm in Arbeit. Blöcke A+B als Spec formuliert, **warten auf Freigabe** (`06-specs/SPEC-sichtbarkeit-blockA-B.md`).

**Brain:** Mit diesem Commit aufgesetzt (Framework, Constitution, Patterns, Loops, Specs, verify.py, CLAUDE.md, Actions-Deploy). Ersetzt das bisherige ZIP-/STATUS-Handoff-Verfahren — Arbeit läuft ab jetzt über Claude Code im Repo.

## Todo-Landkarte (wo liegt was — ein Blick von hier reicht)
| Art des Todos | Ort | Aktuell dort |
|---|---|---|
| Entscheidungen & Handgriffe für Felgen | **hier unten: "Braucht Felgen"** | 7 Punkte (Spec-Freigabe, Deploy-Checks, Bing, GSC-Screenshot, GA4-Test, 2. Domain, Rich-Results) |
| Offene Mängel mit Gesetzes-Bezug | **hier: Befund-Tabelle** | 4 offen (reviewCounts, Rechtstexte, Domains, Tracking-Kontrolle) |
| Fernes / bewusst Geparktes | **hier: Später-Merkposten** | Clarity, ATP-Anfragen, Pinterest, Unboxings, Loop-Automatisierung |
| Freigegebene/wartende Bauvorhaben | `06-specs/` | SPEC-sichtbarkeit-blockA-B (A+B) |
| Laufende Arbeits-Warteschlangen | `04-loops/LOOP-STATE.md` + Loop-Dateien | content-loop: 8 Blog-Ausbauten · preis-loop: 9 Screenshot-ASINs + Voll-Abgleich August |
| Große Roadmap (Blöcke A–H) | `SPC-FRAMEWORK.md` Teil VI | E läuft (Felgen), A+B im Spec, C–H danach |
| Detail-Doku alles Gemachten (Was+Wie) | `05-protokoll/` (+ `marketing-log.md` für Block E/F) | Eintrag #1: Brain-Setup 18.07. |
Regel: Ein Todo steht an genau EINEM Ort; diese Tabelle verlinkt nur. Neue Todos landen zuerst hier in STATUS (Braucht Felgen / Befund / Merkposten) oder in einer Loop-Warteschlange — nie in Chat-Verläufen.

---

## Befund-Status
| Befund | Gesetz | Status |
|---|---|---|
| /ratgeber/ lag als Duplikat neben /blog/ live (8 Artikel doppelt, selbst-kanonisch) | §B2 | **behoben im Brain-Commit** (Ordner gelöscht) — Deploy ausstehend |
| marken/ipega/ + marken/mocute/ als Zombie-Seiten live (am 08.07. beschlossen gelöscht, per Upload-Deploy zurückgekehrt) | §B2 | **behoben im Brain-Commit** — von verify.py gefunden (Sitemap-Rückabgleich), Deploy ausstehend |
| .nojekyll fehlte im Repo | §B2 | **behoben** (angelegt) — Deploy ausstehend |
| Tracking-Events erreichten GA4 nie (gtag statt dataLayer.push, keine Delegation) | §A8 | behoben 11.07., deployed — **Erfolgskontrolle in GA4-Echtzeit noch offen (Felgen)** |
| 5 Reviews mit geschätzten reviewCounts (ROG Tessen, X3 Pro, Turtle Beach, Backbone One PS, Kishi V3 Pro) | §A4 | offen — bei nächsten Screenshots präzisieren |
| Rechtstexte ohne anwaltliche Abnahme | §C4 | offen (Felgen) |
| .de-Domain + eine weitere Domain nicht angebunden (Redirect empfohlen; welche zweite Domain: Felgen nennt sie noch) | — | offen (Felgen, IONOS) |

## Braucht Felgen (Entscheidungen & Handgriffe)
1. **Freigabe SPEC-sichtbarkeit-blockA-B** (oder Änderungen).
2. **Deploy dieses Brain-Stands** — dabei einmalig: GitHub → Settings → Pages → Source auf **"GitHub Actions"** stellen (sonst würde brain/ öffentlich!). Details im Deploy-Loop.
3. **Bing Webmaster Tools** einrichten (Block C, ~20 Min, GSC-Import).
4. **GSC Indexierungs-Screenshot** (Indexierung → Seiten) — die Zahl fehlt uns noch.
5. GA4-Echtzeit-Check: kommt `affiliate_click` jetzt an? (1 Testklick nach Consent genügt.)
6. Zweite anzubindende Domain benennen (neben der .de).
7. **Rich-Results-Test** nach Deploy (offen seit 11.07.): search.google.com/test/rich-results — G8-Galileo-Review + 2–3 neue /produkte/-Seiten auf Sterne-Snippets prüfen.

## Später-Merkposten
- **Microsoft Clarity** (Heatmaps) via GTM nachrüsten — kein Code-Deploy nötig, erst wenn genug Traffic für auswertbare Daten da ist.
- **3 freie AnswerThePublic-Anfragen** ungenutzt — aufheben für gezielte Keyword-Vertiefung (z. B. vor Blog-Neuartikeln).
- Pinterest-Mini-Test (Q4) · TikTok/Shorts-Unboxings · Scheduled-Loop-Automatisierung (nach 2–3 manuellen Läufen je Loop).

---

## Verlauf (chronologisch, neueste zuletzt — Kompakt; Details je Schritt in `05-protokoll/`)

1. **Kompakt-Archiv Juni–10.07.** Site-Aufbau in 5 Phasen (Keywords → Architektur → 57 Seiten → QA), Deployment auf GitHub Pages + IONOS-DNS, GTM/GA4 über Consent Mode v2 live (Lehre: Container VERÖFFENTLICHEN, nicht nur speichern), Search Console Domain-Property + Sitemap, Produkt-Review-Workflow per Screenshots (13 Reviews + Karten aktualisiert, iPega/Mocute entfernt), Shop-Umbau (/produkte/ mit Filtern, products.json 40 Produkte, Hubs dynamisch), Blog konsolidiert (13 Artikel, /ratgeber/ aufgelöst), Cookie-Banner, Finder interaktiv, SEO-Paket (OG sitewide, Product-Schema 13 Reviews, 5er-Skala-Fix).
2. **11.07. Tiefen-Optimierung (Fable 5), deployed.** GEO-Pre-Rendering der Hubs + /produkte/ (statische Karten, SEO-Editorial, FAQs, ItemList), 27 generierte Produkt-Detailseiten (alle 40 Produkte haben "Mehr erfahren"), Tracking-Fix (dataLayer.push + Delegation), products.json bereinigt (Preise, Slugs, Marken), 14 tote Buttons repariert, \x02-Korruption in 13 Reviews gefixt, BreadcrumbList auf 48 Seiten, Organization-Schema, llms.txt, Sitemap 87, Titles/Descriptions auf 21 Seiten, Startseiten-Fotostrip. Alles Playwright-verifiziert.
3. **18.07. GSC-Auswertung + Sichtbarkeits-Plan.** Erste 7 Klicks analysiert (alle via Blog), Plan A–H aufgestellt, Block E freigegeben (Felgen), Pinterest/Unboxing als Später-Merkposten, Alt-Texte + Mehrbild als Block H notiert.
4. **18.07. Brain gebaut (dieser Stand).** Zwei Live-Befunde bei der Repo-Inspektion gefunden und behoben: /ratgeber/-Duplikat (Deploy-Prozess-Fehler: Gelöschtes wurde auf GitHub nie entfernt) + fehlendes .nojekyll. verify.py fand beim Erstlauf zwei weitere Zombie-Seiten (marken/ipega, marken/mocute — gleiche Deploy-Fehlerklasse wie ratgeber, beschlossener Zustand vom 08.07. wiederhergestellt). brain/-Struktur nach USELY/YOU-Muster aufgesetzt (Framework v1.0, Constitution v1.0, Patterns v1.0, 4 Loops + LOOP-STATE, Spec Block A+B, Keyword-Destillat), Generator-Scripts nach scripts/ überführt (repo-relative Pfade), verify.py als maschinelles Gate gebaut, CLAUDE.md, GitHub-Actions-Deploy (Option A: brain/ bleibt privat). Altes Root-STATUS.md hierher migriert und entfernt.

---

## Nächster geplanter Schritt

**Felgen:** Punkte 1–3 der "Braucht Felgen"-Liste (Spec-Freigabe → Deploy mit Pages-Umstellung → Bing).
**Claude Code (nach Spec-Freigabe):** Block A (Finder-Keyword, Blog-Verstärkung, interne Links, Alt-Text-Pass) + Block B (Longtail Batch 1) nach Spec, verify.py grün, STATUS fortschreiben.
**Loops:** Erster manueller Lauf des GSC-Loops nach nächstem Screenshot-Paket; Preis-Loop fällig ab August (letzter Voll-Abgleich 07./08.07.).
