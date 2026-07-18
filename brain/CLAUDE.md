# CLAUDE.md — SPC Gaming

Du arbeitest am SPC-Gaming-Repo: **smartphone-controller.com** — deutsche Amazon-Affiliate-Plattform
für Smartphone-Gaming-Controller & Zubehör (YG MEDIA). **LIVE** auf GitHub Pages.
Stack: Statisches HTML/CSS/JS · products.json als Datenkern · Python-Generatoren · GTM/GA4 · Amazon PartnerNet (`ygmedia-21`).

## Wissensquellen (in dieser Reihenfolge, nie alles auf einmal lesen)
1. `brain/SPC-FRAMEWORK.md` — kanonische Referenz: Geschäftsmodell, Keyword-Strategie, Architektur, Roadmap. Gewinnt bei Konflikten.
2. `brain/01-constitution/SPC-CONSTITUTION.md` — Gesetze §A (Site) · §B (SEO/GEO) · §C (Recht) · §D (Betrieb). Was sie verletzt, wird nicht gemergt.
3. `brain/02-patterns/SPC-PATTERNS.md` — Bau-Muster P-1…P-8. Jede Änderung folgt einem Pattern oder definiert ein neues.
4. `brain/STATUS.md` — lebendiges Session-Gedächtnis. Direkt nach dem INDEX lesen.
5. `brain/06-specs/` — größere Vorhaben nur nach freigegebenem Spec.
Lies gezielt (INDEX → relevante Seite → Links), nie den ganzen Vault (Framework 7.6).

## Harte Regeln
- **products.json ist die einzige Produkt-Wahrheit** (§A1). Preise/Specs/ASINs werden dort gepflegt; HTML wird generiert oder per Script gesynct — nie divergent von Hand.
- **Statik zuerst (GEO, §A2):** Jede Seite zeigt ihren vollen Inhalt ohne JavaScript. JS hydratisiert nur. Nach Umbauten: No-JS-Check via `scripts/verify.py`.
- **Produktdaten NUR aus Felgens Amazon-Screenshots** (§A5). Amazon blockt jeden programmatischen Zugriff (403) — web_fetch auf Amazon ist zwecklos. Nie Preise/Bewertungen erfinden oder "aktualisieren" ohne Beleg.
- **Schema-Gesetz (§A4):** aggregateRating immer 5er-Skala (`bestRating: "5"`), `reviewCount` > 1, jeder Schema-Wert steht sichtbar im Seitentext. Verstoß = Rich-Results-Risiko + manuelle Maßnahme.
- **Tracking (§A8):** Custom Events NUR als `dataLayer.push({event: '...'})` mit den GTM-DLV-Namen (product_name, destination, platform, budget, prio). NIE `gtag('event', ...)`.
- **Affiliate-Links** entstehen ausschließlich in main.js aus `data-asin` → `amazon.de/dp/[ASIN]?tag=ygmedia-21`. Buttons tragen `href="#"` + data-asin, nie harte Amazon-URLs.
- **Ehrliche Reviews (§A6):** Jedes Review nennt ≥2 echte Schwächen. Schwache Produkte (Rating < 3,8) bekommen explizite Warnung statt Kaufempfehlung.
- **Deploy ist Menschen-Gate:** Du pushst/deployst NIE selbst. Arbeit endet mit grünem `python3 scripts/verify.py` + aktualisiertem `brain/STATUS.md`. Felgen deployt.
- **Löschen von Seiten, Massenänderungen (>10 Dateien), Geld-/ASIN-Änderungen:** stoppen, in STATUS unter „braucht Felgen" eintragen, fragen.
- **Keine Em-Dashes** in Copy. Deutsch für Content, Englisch für Code. Helles Shop-Design (weiß/navy/blau), CSS nur in style.css bzw. Seiten-<style>.

## Arbeitsweise
Senior-Haltung: Ursache faktisch beweisen (Diagnose vor Fix), klare Anweisung statt Optionsliste, Einwände ernst nehmen. „ok/weiter/passt" = sofort nächster Schritt. Felgen kommuniziert knapp, oft per Sprachnachricht-Transkript.
Verify-Gate pro Aufgabe: maschinell prüfbar, nie „sieht gut aus". Macher ≠ Prüfer: Review-Läufe in frischem Kontext.
Nach JEDEM abgeschlossenen Schritt: `brain/STATUS.md` aktualisieren (kompakt; bei Widerspruch gewinnt das Repo) UND einen Protokoll-Eintrag in `brain/05-protokoll/` schreiben (JJJJ-MM-TT-kategorie-thema.md: Was · Wie · Warum so · Verify · Gelernt). Gelerntes → Constitution/Patterns (Rückfluss).
Loops in `brain/04-loops/` laufen über `LOOP-STATE.md` (erledigt/blockiert/braucht Felgen) — zuerst lesen, erledigte Arbeit nie wiederholen, max. 3 Versuche pro Item.

## Werkzeuge
- `python3 scripts/verify.py` — Pflicht-Gate vor jedem „fertig" (Schemas, Links, Sitemap, No-JS-Statik, Invarianten CNAME/.nojekyll, products.json-Integrität).
- `scripts/gen_pages.py` (+ gen_content.py) — Produkt-Detailseiten aus products.json. `scripts/gen_hubs.py` — statisches Pre-Rendering der Hubs + /produkte/.
- Lokal testen: `python3 -m http.server` (file:// lädt kein CSS/JS — absolute Pfade). Playwright verfügbar für tiefere Checks.

## Aktueller Stand & nächster Schritt
Steht IMMER in `brain/STATUS.md` — dort weiterlesen. Kurzfassung bei Brain-Erstellung (2026-07-18): 88 Seiten live, GSC zeigt ersten Traffic über Blog-Artikel (7 Klicks, Position 18,3 steigend), Sichtbarkeits-Plan liegt als Spec zur Freigabe, Loops frisch aufgesetzt.
