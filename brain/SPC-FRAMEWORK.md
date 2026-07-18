# SPC FRAMEWORK — Das Systemdokument

> **Version 1.0 · Kanonisch · 2026-07-18**
> Konsolidiert aus: der echten Live-Site (88 Seiten, deployed), dem Keyword-Master v3 (937 verifizierte Keywords), allen Build-Sessions seit Juni 2026 und den ersten echten GSC-Daten.
> Konfliktregel: Bei Widerspruch zwischen Dokumenten gewinnt dieses. Bei Widerspruch zwischen Doku und Repo gewinnt das Repo — dann wird die Doku korrigiert.

---

# TEIL 0 · LEITPRINZIPIEN

1. **Datenlage vor Annahme.** Entscheidungen basieren auf GSC-Daten, Amazon-Screenshots und dem Keyword-Master — nie auf Bauchgefühl oder erinnerten Zahlen. Was nicht belegt ist, wird nicht behauptet (gilt für Content UND für Diagnosen).
2. **Eine Galaxie nach der anderen.** Erst Longtail-Rankings (50er-Keywords, niedrige Konkurrenz), dann Mittelschicht (500er), zuletzt die Volumen-Riesen (5.000er "handy controller", "gamesir") — die brauchen Domain-Autorität, die nur mit Zeit + Backlinks entsteht. Kein Frontalangriff auf umkämpfte Keywords ohne Fundament.
3. **Autorität statt Linkschleuder.** Wir bauen keine klassische Affiliate-Seite, wir bauen die deutsche Referenz für Mobile-Gaming-Hardware. Ehrliche Cons, echte Fotos, Warnungen bei schwachen Produkten — Vertrauen ist der Burggraben, den Preisvergleicher nicht kopieren.
4. **GEO ist Gleichrangig mit SEO.** KI-Antwortmaschinen (ChatGPT, Perplexity, Copilot, AI Overviews) sind ein eigener Kanal. Alles, was gebaut wird, muss ohne JavaScript vollständig lesbar sein; llms.txt, Schema und statisches HTML sind Pflicht, nicht Kür.
5. **Hybrid-Entwicklung.** Claude Code baut nach diesem Framework; Felgen entscheidet, deployt und liefert die Daten (Screenshots, GSC), die die Maschine nicht beschaffen kann. Alles wird aus dem Framework abgeleitet — kein Feature ad-hoc.

---

# TEIL I · GESCHÄFTSMODELL & MARKT

## 1.1 Was SPC Gaming ist
Deutschsprachiges Test- und Kaufberatungsportal für Smartphone-Gaming-Controller und Zubehör (Finger Sleeves, Trigger, Handy-Kühler). Monetarisierung: ausschließlich Amazon-PartnerNet-Provisionen (Tag `ygmedia-21`). Kein Shop, kein Login, keine Ads. Betreiber: YG MEDIA (Würzburg).

## 1.2 Keyword-Strategie (aus Keyword-Master v3, Juni 2026)
- **Volumen-Riesen (~5.000/Monat):** "gamesir", "handy controller" — Ziel der Hub-/Pillar-Seiten, realistisch erst mit Autorität (Monat 3–6+).
- **Mittelschicht (~500/Monat):** "controller für handy/iphone", "android controller bluetooth", "gaming finger sleeves" — Ziel der Plattform-Hubs und Kategorie-Seiten.
- **Longtail (~50/Monat, 212 Keywords):** Alt-/Budget-Modelle (iPega, Mocute, GameSir-Altmodelle; Ausreißer "8bitdo lite 2" ~500/Monat) — automatisierte Datenblatt-Seiten, schnellster Ranking-Weg für eine junge Domain.
- **Frage-Keywords:** Blog beantwortet echte Nutzerfragen (Verbindung, Kompatibilität, Cloud Gaming) — nachweislich der erste funktionierende Kanal (GSC Juli 2026: alle ersten Klicks über Blog).
- Rohdaten: `brain/03-research/raw/` · Destillat: `brain/03-research/keyword-strategie.md`.

## 1.3 Wachstumsstufen
| Stufe | Ziel | Messkriterium | Stand |
|---|---|---|---|
| 1 | Indexierung + erste Longtail-Rankings | 80+ Seiten indexiert, erste Top-20-Longtails | **läuft** (Juli 2026) |
| 2 | Blog als Traffic-Kanal + Bing/GEO-Sichtbarkeit | 100+ Klicks/Monat, Zitierungen in KI-Antworten | nächste |
| 3 | Mittelschicht-Rankings (500er) | Hub-Seiten Top 10 | braucht Backlinks |
| 4 | Volumen-Keywords + Skalierung | "handy controller" Top 10, 4-stellige Klicks/Monat | Monat 6+ |

Regel: Stufe N ist **messbar erreicht**, bevor Aufwand in N+1 fließt.

---

# TEIL II · SITE-ARCHITEKTUR

## 2.1 Grundsatz: Statisches HTML, ein Datenkern
GitHub Pages (Repo YGMEDIA/SPC-Gaming, Domain via IONOS auf `smartphone-controller.com`, non-www kanonisch). Kein Build-Framework, kein CMS — HTML/CSS/JS pur, Python-Generatoren für alles Wiederholbare.

```
products.json (40 Produkte — DIE Wahrheit)
   ├── gen_pages.py  → /produkte/<slug>/   (27 Detailseiten, Kurzcheck-Format)
   ├── gen_hubs.py   → statische Karten in Hubs + /produkte/  (GEO-Pre-Render)
   ├── hub-render.js / produkte.js / finder.js  → Hydration + Filter (identisches Markup!)
   └── main.js       → Header/Footer-Injection, Affiliate-Links aus data-asin, Consent, Tracking
```

## 2.2 Seitentypen (Silos)
`/controller/` (Hubs iOS/Android/Universal/Tablet/Mini + 13 Reviews + Pillar `/controller/beste/`) · `/zubehoer/` (Sleeves/Trigger/Kühler) · `/marken/` (GameSir, Razer, Backbone, 8BitDo) · `/produkte/` (Filter-Übersicht + 27 Detailseiten) · `/vergleich/` (6) · `/blog/` (13, einziger Ratgeber-Ort — /ratgeber/ ist tot und bleibt tot) · `/controller-finder/` (interaktiv, 3 Fragen) · E-E-A-T/Legal.

## 2.3 Tracking & Consent
GTM `GTM-PV7MKJ8P` → GA4 `G-Q1EK5X7PTC`. Consent Mode v2: default denied, GTM lädt erst nach "Alle akzeptieren" (localStorage `spc_cookie_consent`). Events: `page_view`, `affiliate_click` (product_name, destination), `finder_complete` (platform, budget, prio) — ausschließlich `dataLayer.push`, Event-Delegation auf document-Ebene.

---

# TEIL III · DATENMODELL (products.json)

Pflichtfelder je Produkt: `slug` (sprechend, einmalig) · `asin` (einmalig, B0…) · `name` · `brand` (normalisiert — genau EINE Schreibweise pro Marke) · `type` (controller|zubehoer) · `platform` · `worksOn` (Kompatibilitätsliste; USB-C ODER Bluetooth ⇒ iPhone-tauglich) · `price` ("NN €", Stand = letzter Screenshot) · `claim` · `specs` (Paare; "Bew." = "X,X (NNN)" von Amazon) · `img` (Amazon-CDN-URL oder lokal) · `detail` (Review-URL oder /produkte/<slug>/ — nie leer).

**Datengesetze:** (1) Neue Produkte: erst products.json, dann Generatoren — nie umgekehrt. (2) ASIN-Änderung/Variantenwechsel ist Menschen-Gate. (3) Preis-/Bewertungsänderung nur mit Screenshot-Beleg, Datum in STATUS. (4) Slug-Umbenennung zieht projektweiten data-product-Sync nach sich (Script, nicht Hand).

---

# TEIL IV · MODULE

**M1 Reviews (13)** — volles Testformat: Verdict, Specs, Pros/Cons (≥2 echte Cons), FAQ, Product+FAQPage+BreadcrumbList-Schema, Update-Workflow per Screenshot (P-4).
**M2 Produkt-Kurzchecks (27)** — generiert, ehrlich abgestuft, Related-Products, Sticky-CTA.
**M3 Hubs** — statisch pre-rendert + SEO-Editorial + FAQ + ItemList-Schema. Volumen-Keyword-Träger.
**M4 Blog (13)** — Frage-Keywords, verdict-box, FAQ-Schema, starke interne Verlinkung auf Geld-Seiten. Erster funktionierender Kanal → Ausbau hat Priorität (8 Kurz-Artikel auf ~800 Wörter).
**M5 Finder** — 3 Fragen → Top-3-Matches aus products.json, finder_complete-Event.
**M6 Longtail-Datenblätter** — geplant (Spec): /produkte/-Template als Generator, Traffic-Fänger mit "Alternative im Sortiment"-Box für nicht (mehr) verfügbare Modelle.
**M7 Vergleiche (6)** — Duelle + Best-of, CTAs mit echten ASINs.

---

# TEIL V · QUERSCHNITT

**Design:** Heller Shop-Look (weiß/navy/blau, Cyberport-Klasse), globales style.css (~735 Zeilen) + seitenlokale <style>-Blöcke. Bewusst KEIN Scroll-Fade-in. Emotion über echte Testfotos (products-real/), nicht über Stock.
**Schema:** Product (5er-Skala, sichtbare Werte), FAQPage, BreadcrumbList (sitewide), ItemList (Hubs/Pillar), Organization + WebSite (Home). 124+ Blöcke, verify.py validiert jeden.
**Recht:** Impressum/Datenschutz mit echten YG-MEDIA-Daten · Affiliate-Kennzeichnung sitewide · Consent vor Tracking (§C) · Bildrechte: nur Amazon-CDN-URLs (per Rechtsklick geliefert) oder eigene Fotos · Rechtstexte: anwaltliche Endabnahme offen.
**Qualität:** `scripts/verify.py` als maschinelles Gate — JSON-LD-Validierung, interner Link-Check, Sitemap-XML + Datei-Abgleich, No-JS-Statik-Check, Invarianten (CNAME, .nojekyll, kein /ratgeber/, keine Steuerzeichen), products.json-Integrität.

---

# TEIL VI · ROADMAP (Blöcke = Sichtbarkeits-Plan 18.07.)

**A** Quick Wins On-Site (Finder-Keyword, Blog-Verstärkung, interne Links, Alt-Texte) — Spec zur Freigabe.
**B** Longtail Batch 1 (10 Seiten) — Spec zur Freigabe. Bei Erfolg (Impressionen nach 3–4 Wochen) → Batches 2–5.
**C** Bing Webmaster Tools (Felgen, einmalig) — Tor zu ChatGPT/Copilot-Index.
**D** Indexierung beschleunigen (Felgen: URL-Prüfung Top-20, Sitemap-Pflege).
**E** Reddit/Gutefrage-Antworten (Felgen, laufend) — **freigegeben, aktueller Fokus.**
**F** Backlink-Fundament (ab Woche 2–3: Verzeichnisse, Blogger-Outreach, Kompatibilitäts-Asset).
**G** Blog-Ausbau (8 Kurz-Artikel → 800 Wörter, Priorität nach GSC-Impressionen).
**H** Bilder: Alt-Text-Pass + Mehrbild-Galerien pro Produkt (Bild-URLs liefert Felgen).
**Später/optional:** Pinterest-Mini-Test (Q4, Setup/Geschenk), TikTok/Shorts-Unboxings, .de-Domain-Redirect + weitere Domain.

---

# TEIL VII · ENTWICKLUNGSSYSTEM

## 7.1 Komponenten
SPC BRAIN (`brain/`, Git-versioniert, Obsidian-kompatibel): dieses Framework · Constitution · Patterns · STATUS · Loops (`04-loops/` + LOOP-STATE) · Research (`03-research/`, raw = Ground Truth) · Specs (`06-specs/`).
Werkzeuge: Claude (Planung/Specs/Review) · Claude Code (Implementierung im Repo) · GitHub (Deploy via Actions) · verify.py (Gate).

## 7.2 Rollenteilung
| Wer | Macht | Macht nicht |
|---|---|---|
| **Felgen** | Prioritäten, Freigaben, Deploy, Screenshots/GSC-Daten, Off-Site (Block C/D/E/F-Outreach) | Boilerplate |
| **Claude (Chat)** | Specs, Architektur-Review, Auswertung der GSC-Daten, Pushback | still zustimmen |
| **Claude Code** | Bau nach Spec+Constitution+Patterns, verify.py, STATUS-Pflege | deployen, Architektur eigenmächtig ändern |

## 7.3 Feature-Kette (verbindlich für jedes größere Vorhaben)
Idee → Spec (`06-specs/SPEC-<name>.md`: Ziel · Keyword-Bezug · Seiten/Änderungen · Gesetzes-Check · Verify-Gate) → Freigabe Felgen → Claude Code baut → verify.py grün + Review in frischem Kontext → Felgen deployt → **Rückfluss** (neues Pattern? Gesetz präzisieren? → Brain).
Kleine Fixes (<5 Dateien, kein Geld/Löschen) brauchen kein Spec, aber verify.py + STATUS immer.

## 7.4 Loop-Regeln (verbindlich, aus USELY 7.5 übernommen)
1 · Messbares Fertig-Kriterium (Maschine prüfbar). 2 · Macher ≠ Prüfer (Review frischer Kontext). 3 · State-Datei `04-loops/LOOP-STATE.md` — jeder Lauf liest sie zuerst, erledigte Arbeit wird nie wiederholt. 4 · Stop-Bedingung: 3 Versuche pro Item, dann blockiert loggen und weiter. 5 · Menschen-Gate: Deploy, Löschen von Seiten, Massenänderung (>10 Dateien), Geld/ASIN → stoppen, auf „braucht Felgen"-Liste. 6 · Kein Loop für einmalige/vage/nicht prüfbare Arbeit.

## 7.5 Brain-Leseregeln (Token-Ökonomie, aus USELY 7.6)
INDEX zuerst, dann Links. CLAUDE.md < 200 Zeilen — zeigt aufs Brain, enthält es nicht. Update statt Duplikat; Falsches löschen. `03-research/raw/` unantastbar (lesen ja, überschreiben nie). Git als einziges Sync-System — Obsidian öffnet den Ordner direkt, NIE iCloud-Sync parallel auf dem Repo.

---

# TEIL VIII · GOVERNANCE

1. Dieses Dokument ist kanonisch; Änderung nur per datiertem Änderungslog-Eintrag.
2. Constitution bricht Bequemlichkeit — was §A–§D verletzt, wird nicht gemergt, auch wenn es funktioniert.
3. Der Mensch hat das letzte Wort: Deploy, Seiten-Löschung, Geld, ASINs, neue Domains = Felgen.
4. **Struktur folgt Substanz:** Neue Brain-Dateien/Meta-Ebenen nur, wenn sie ein konkretes, benanntes Problem lösen. Skill-Dateien entstehen beim ersten echten Einsatz.
5. **Keys, not prompts:** Sicherheit über Zugriffsrechte, nicht über Anweisungen. Deploy liegt physisch bei Felgen (Actions-Workflow entscheidet, was öffentlich wird — brain/, scripts/, CLAUDE.md nie).

---

## Änderungslog
| Datum | Version | Änderung |
|---|---|---|
| 2026-07-18 | 1.0 | Erstfassung: konsolidiert aus Live-Site, Keyword-Master v3, Projekthistorie Juni–Juli 2026 und ersten GSC-Daten. Muster übernommen aus USELY-Framework v1.5 und YOU-Brain (Loop-Regeln, Leseregeln, Governance). |

---

*SPC FRAMEWORK v1.0 · Single Source of Truth · oberste Datei neben INDEX.md*
