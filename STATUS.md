# 🎮 PROJEKT: Smartphone-Controller Affiliate-Plattform
**Letzte Aktualisierung:** 2026-07-06
**Projektstatus:** Phase 5 – Tech-Build aktiv (54 HTML-Seiten fertig)
**Hauptdomain:** smartphone-controller.com
**Affiliate-Tag:** ygmedia-21
**Tech-Stack:** Statisches HTML + GitHub Pages (bewusste Entscheidung, kein Next.js)

---

## ✅ WAS BEREITS FERTIG IST

### PHASE 1: Keyword-Recherche ✅ ABGESCHLOSSEN
- 937 Keywords aus 13 Google-Keyword-Planner-CSV-Exporten verifiziert (DE, Juni 2026)
- Keyword-Master-Excel v3 mit echten Volumina, KD, CPC
- 6 neue Zubehör-Cluster ergänzt (Trigger, Finger Sleeves, Kühler, etc.)
- Budget-Longtail-Sheet: 212 iPega/Mocute-Keywords (je ~50/Mon., niedrige KD)
- Insights-Sheet mit strategischen Erkenntnissen
- **Output:** Keyword-Master_SmartphoneController_v3_VERIFIZIERT.xlsx

**Wichtigste echte Keyword-Daten (DE):**
| Keyword | Vol./Monat | Wettbewerb |
|---------|-----------|-----------|
| gamesir / gamesir controller | 5.000 | Mittel |
| handy controller | 5.000 | Hoch |
| controller für handy | 500 | Hoch |
| gaming finger sleeves | 500 | Hoch |
| controller für iphone | 500 | Hoch |
| android controller bluetooth | 500 | Hoch |
| razer kishi / backbone one | 500 | Hoch |
| handy trigger / pubg trigger | 50 | Hoch (CPC↑) |
| handy kühler gaming | unbekannt | — |

---

### PHASE 2: Produkt- & Kategorisierungsstrategie ✅ ABGESCHLOSSEN
- Dreischichtige Navigation: Produkttyp / Plattform / Marke
- 40 Produkte in 3 Tiers (A: Top-Modelle, B: Zubehör, C: Budget-Longtail)
- 16-Felder-Datenstruktur pro Produkt definiert
- 8 Vergleichsmatrizen geplant
- Affiliate-Strategie: Amazon → AWIN → CJ
- **Output:** Phase2_Produktstrategie.docx

---

### PHASE 3: Website-Architektur ✅ ABGESCHLOSSEN
- 52 URLs in 3 Silos (/controller/, /zubehoer/, /marken/)
- sitemap.xml fertig (hreflang DE/EN, priorities, changefreq)
- robots.txt fertig (KI-Crawler ausdrücklich erlaubt: GPTBot, ClaudeBot etc.)
- Interne Verlinkungsstrategie dokumentiert
- **Output:** Phase3_Architektur.docx + sitemap.xml + robots.txt

---

### PHASE 4: Content-Strategie ✅ ABGESCHLOSSEN
- Content-Kalender Q3 2026 (20 Artikel, KW 27–37)
- Review-Template (8 Abschnitte, Pros/Cons-Pflicht)
- Vergleichs-Template + Ratgeber-Template
- Schema-Markup (7 Typen + JSON-LD-Beispiel)
- 6 E-E-A-T-Pflichtseiten definiert
- Erster Pillar-Artikel fertig ("handy controller", 5.000/Monat)
- **Output:** Phase4_ContentStrategie.docx

---

### PHASE 5: Tech-Build ✅ 54 SEITEN FERTIG

**Tech-Stack-Entscheidung:** Statisches HTML + GitHub Pages
- Kostenlos, keine Build-Tools, kein Framework-Overhead
- Maximale Core Web Vitals out-of-the-box
- Direkt in Git-Repo schiebbar

**Globale Infrastruktur (fertig):**
- `/assets/css/style.css` — komplettes Design-System (Shop-Look, weiß/navy/blau)
- `/assets/js/main.js` — Header/Footer-Injection, Affiliate-Link-Automation via data-asin, GA4-Events

**Affiliate-Link-System:**
```html
<!-- So funktioniert es: -->
<a class="btn-amazon" data-asin="B0XXXXXXX" data-product="produktname" href="#">
  Preis prüfen →
</a>
<!-- main.js baut daraus automatisch: -->
<!-- amazon.de/dp/B0XXXXXXX?tag=ygmedia-21 -->
```

**Fertige Seiten (54 total):**

| Typ | Anzahl | Status |
|-----|--------|--------|
| Homepage | 1 | ✅ |
| Controller-Hub + Plattform-Hubs | 5 | ✅ |
| Zubehör-Hubs | 4 | ✅ |
| Marken-Hubs | 6 | ✅ |
| Gaming-Phones | 1 | ✅ |
| Produktreviews | 13 | ✅ |
| Vergleichsseiten | 6 | ✅ |
| Ratgeber | 8 | ✅ |
| Controller-Finder | 1 | ✅ (Platzhalter, Berater separat) |
| E-E-A-T / Legal | 6 | ✅ |
| Sonstige | 3 | ✅ |

**✅ ASINs GRÖSSTENTEILS EINGETRAGEN (Stand 06.07.2026):**
- 23 Produkte mit echten ASINs versehen (Testsieger, Zubehör, Budget)
- 26 zusätzliche Produkte aus Amazon-Links eingebaut (Trigger, Sleeves, Budget-Controller)
- Cross-Selling (Taschen/Hüllen) auf 5 Review-Seiten
- **Nur noch 3 offene ASINs:** asus-rog-phone-9, ozkak-mini-joystick, redmagic-10-pro
- ⚠️ Hinweis: Asus ROG Phone 9 Pro hatte falsche ASIN (= ROG Tessen Controller), zurückgesetzt

**⚠️ KRITISCH VOR LIVE-GANG:**
- Die 3 offenen ASINs oben ergänzen
- Impressum mit echten Kontaktdaten befüllen
- Datenschutzerklärung rechtlich prüfen lassen
- GA4 Measurement ID in main.js eintragen

---

## 🔧 NOCH OFFEN (Phase 5 + 6)

### Sofort als nächstes:
- [ ] Controller-Finder-Prototyp (controller-shop.html) in `/controller-finder/` einbinden
- [ ] Alle echten Amazon-ASINs für 40 Produkte heraussuchen und eintragen
- [ ] GA4 Property anlegen + Measurement ID in main.js eintragen
- [ ] Search Console verifizieren + Sitemap einreichen
- [ ] GitHub Pages aktivieren (Settings → Pages → main branch)
- [ ] Custom Domain smartphone-controller.com in GitHub Pages eintragen

### Phase 6: Tracking & Monetarisierung (noch offen)
- [ ] Google Tag Manager Container anlegen
- [ ] GA4 über GTM einbinden (nicht direkt)
- [ ] affiliate_click Event testen (ist schon im main.js vorbereitet)
- [ ] finder_complete Event für Controller-Finder
- [ ] Microsoft Clarity für Heatmaps
- [ ] KPI-Dashboard aufbauen

### Content-Produktion (laufend):
- [ ] Artikel 1–5 aus Content-Kalender schreiben (Pillar-Content zuerst)
- [ ] Produktbilder via Amazon PartnerNet einbinden
- [ ] Schema-Markup in alle Reviews einbauen
- [ ] FAQ-Blöcke erweitern (min. 5 FAQs pro Review)

---

## 🏗️ REPO-STRUKTUR

```
smartphone-controller.com/ (Git-Root)
├── index.html
├── sitemap.xml
├── robots.txt
├── assets/
│   ├── css/style.css
│   └── js/main.js
├── controller/
│   ├── index.html          (Controller-Hub mit Filter/Sort)
│   ├── ios/index.html
│   ├── android/index.html
│   ├── universal/index.html
│   ├── tablet/index.html
│   ├── mini-gamepad/index.html
│   └── [slug]/[slug]-review/index.html  (13 Reviews)
├── zubehoer/
│   ├── index.html
│   ├── finger-sleeves/index.html
│   ├── trigger/index.html
│   └── handy-kuehler/index.html
├── marken/
│   ├── gamesir/ razer/ backbone/ 8bitdo/ ipega/ mocute/
├── vergleich/
│   ├── index.html + 5 Vergleiche
├── ratgeber/
│   ├── index.html + 7 Ratgeber
├── controller-finder/index.html
├── gaming-phones/index.html
├── ueber-uns/ redaktion/ kontakt/
├── impressum/ datenschutz/ affiliate-hinweis/
```

---

## 🔄 LOOPS (aktiv ab Launch)

| Loop | Frequenz | Aufgabe |
|------|----------|---------|
| Content-Loop | Wöchentlich | Neue Reviews, Artikel aus Kalender |
| Preis-Loop | Monatlich | ASINs prüfen, Preise aktualisieren |
| SEO-Loop | Wöchentlich | GSC-Daten, Rankings, interne Links |
| GEO-Loop | Monatlich | KI-Zitierungen prüfen |
| ASIN-Loop | Bei Launch | Alle Platzhalter-ASINs ersetzen |

---

## 🔄 CHAT-ÜBERGABE PROTOKOLL

**So startest du einen neuen Chat:**
1. Lade diese STATUS.md in den neuen Chat hoch
2. Schreib: "Smartphone-Controller Projekt — bitte Status lesen und weitermachen"
3. Claude weiß sofort wo wir stehen

**Aktuell wichtigste nächste Aufgabe:**
→ ASINs eintragen + GitHub Pages live schalten + Controller-Finder einbinden

---

## 💡 PROJEKT-PHILOSOPHIE

> "Wir bauen keine klassische Affiliate-Seite. Wir bauen eine Autorität."

- **GEO als Differenzierer:** robots.txt erlaubt KI-Crawler ausdrücklich
- **Ehrliche Cons:** Jedes Review nennt mindestens 2 echte Schwächen
- **Struktur vor Content:** 54 Seiten Fundament steht — jetzt Content drauf
- **Affiliate-Tag:** ygmedia-21 — überall in main.js eingebaut, automatisch
