# SPC CONSTITUTION

> Die Gesetze von smartphone-controller.com. Aus dem echten Live-Projekt extrahiert (Juni–Juli 2026).
> Wenn neuer Code/Content gegen ein Gesetz verstößt, ist entweder die Arbeit falsch oder das Gesetz veraltet. Beides wird hier entschieden, nicht im Vorbeigehen.
> Marker: **[bewiesen]** = das Repo erfüllt es heute nachweislich · **[Soll, verletzt]** = offener Befund und direkter Arbeitspunkt.

---

## TEIL A · Site-Gesetze

### §A1 · products.json ist die einzige Produkt-Wahrheit [bewiesen]
42 Produkte (gemessen 02.10.2026; hier stand bis dahin 40, waehrend §A6 in derselben Datei schon 42 nannte), alle Preise/Specs/ASINs/Detail-Links leben dort. HTML wird generiert (gen_pages.py, gen_hubs.py) oder per Script gesynct. Divergenz zwischen JSON und HTML ist ein Befund (Historie: 7 fehlende Preise, 6 Preis-Abweichungen — behoben 11.07.).

### §A2 · Statik zuerst — GEO-Gesetz [bewiesen]
Jede Seite zeigt ihren vollen Inhalt ohne JavaScript (KI-Crawler führen kein JS aus). JS hydratisiert identisches Markup, überschreibt nie mit anderem. Bewiesen per No-JS-Playwright-Test (11.07.): Hubs 26/25/25 Karten, /produkte/ 40. verify.py wacht darüber.

### §A3 · Affiliate-Link-Automation [bewiesen]
Links entstehen ausschließlich in main.js aus `data-asin` → `amazon.de/dp/[ASIN]?tag=ygmedia-21`, mit `rel="nofollow sponsored noopener"`. Buttons im HTML tragen nie harte Amazon-URLs. Tag-Änderung = eine Stelle.

### §A4 · Schema = sichtbare Wahrheit [bewiesen]
aggregateRating immer `bestRating: "5"`, `reviewCount` > 1, jeder Schema-Wert (Preis, Rating, Count) steht sichtbar im Seitentext. Keine 10er-Skalen, keine erfundenen Counts (Historie: 4 Seiten mit 10er-Skala + count 1 — behoben 10.07.). Geschätzte Counts sind als Befund zu führen (aktuell: 5 Seiten Gruppe A mit gerundeten Werten — offen, valide aber zu präzisieren).
**Zusatz [bewiesen 20.07.]:** Ein Product-Schema trägt IMMER mindestens eins von `offers`, `review`, `aggregateRating` — sonst meldet Google einen kritischen Produkt-Snippets-Fehler (GSC-Mail WNC-10030322: 10 Longtail-Datenblätter mit "ehrlichem" Minimal-Product). Gibt es dafür keine belegbaren Daten (§A5), dann KEIN Product-Schema (Breadcrumb + FAQ genügen). Maschinell erzwungen in verify.py.

### §A5 · Produktdaten nur mit Beleg [bewiesen]
Amazon blockt jeden programmatischen Zugriff (web_fetch 403, CDN-curl 403). Quelle für Preise/Ratings/Verfügbarkeit sind ausschließlich Yasins Screenshots; Bild-URLs kommen per Rechtsklick → Grafikadresse. Jede Datenänderung trägt ihr Screenshot-Datum in STATUS. Nie verfügbare Produkte werden entfernt, nicht schöngeredet (Historie: iPega, Mocute, RedMagic).

### §A6 · Ehrlichkeit ist der Burggraben [bewiesen]
Jedes Review ≥2 echte Cons. Produkte unter ~3,8 Sternen bekommen explizite Warnung oder "keine Kaufempfehlung" (Stand 02.10.2026, nachgerechnet: 6 Produkte liegen darunter — turtle-beach-atom 3,5 als einziger Controller, dazu razer-phone-cooler 3,3, rxkfigx-sleeves 3,6, magnet-peltier-cooler 3,6, ozkak-trigger-gamepad 3,6, ozkak-6finger 3,7. Die vorige Fassung nannte "RXKFIGX 3,5 · MGPXPRO 3,3"; der MGPXPRO liegt inzwischen bei 4,3, und die RXKFIGX-Zahl war veraltet. Wer diese Beispiele liest, prueft sie gegen products.json — eine getippte Bewertung in der Constitution altert wie jede andere). Wir listen sie transparent und empfehlen die Alternative — das ist Positionierung, kein Bug.
**Superlativ-Regel [ergänzt 30.09.2026]:** Jeder Superlativ und jede Vergleichsaussage ("bestbewertet", "günstigster", "die meisten", "teuerste") nennt ihren Geltungsbereich im Satz selbst und wird vor dem Commit gegen products.json nachgerechnet — über den Bereich, den die Formulierung behauptet. "In unserem Sortiment" heißt alle 42 Produkte, nicht die gerade betrachtete Teilmenge. Belegt durch vier abgefangene Fehler am 30.09. und einen am 29.09., alle vom selben Typ: richtige Zahl, falscher Bezugsrahmen.

### §A7 · Design-Konstanz [bewiesen]
Heller Shop-Look (weiß/navy/blau). Globale Styles in style.css, seitenlokale in <style>-Blöcken. Kein Dark-Theme, kein Scroll-Fade-in (bewusste Entscheidung 08.07.). Emotion über echte Testfotos.

### §A8 · Tracking-Gesetz [bewiesen]
Custom Events nur als `dataLayer.push({event: ...})` mit exakt den GTM-DLV-Namen. Event-Listener als document-Delegation (dynamische Karten!). NIE `gtag('event', ...)` — das erreicht GTM-Trigger nicht (Historie: affiliate_click kam monatelang nie an — behoben 11.07.). Consent Mode v2: GTM lädt erst nach Zustimmung.

---

## TEIL B · SEO/GEO-Gesetze

### §B1 · Ein Keyword-Ziel pro Seite [bewiesen]
Jede kommerzielle Seite hat ihr Keyword aus dem Keyword-Master (Title ≤62 Zeichen, Description 70–165). Keine zwei Seiten auf dasselbe Keyword.

### §B2 · Kanonische Ordnung [Soll, verletzt]
non-www ist kanonisch, jede Seite trägt genau einen Canonical auf sich selbst, gelöschte Pfade verschwinden physisch aus dem Deploy. **Verletzt entdeckt 18.07.:** /ratgeber/ lag als Duplikat-Zombie neben /blog/ live (8 Artikel doppelt, beide selbst-kanonisch), marken/ipega + marken/mocute ebenso (beschlossene Löschung 08.07. war live nie vollzogen), .nojekyll fehlte im Repo. Behoben im Brain-Commit; Option-A-Workflow verhindert die Fehlerklasse (Deploy = exakter Repo-Stand).

### §B3 · Sitemap & llms.txt wachsen mit [bewiesen]
Jede neue indexierbare Seite → sitemap.xml (+ lastmod) und ggf. llms.txt. /suche/ bleibt noindex + disallowed. Nach Deploy mit neuen Seiten: Sitemap in GSC neu einreichen (Yasin).

### §B4 · Blog-first-Vererbung [bewiesen]
Die ersten Rankings/Klicks kommen über Info-Content (GSC-Beleg 18.07.). Jeder Blog-Artikel verlinkt kontextuell auf passende Geld-Seiten (Review/Hub, nicht generisch). Interne Links sind Pflichtteil jedes Content-Piece.

### §B5 · Interne Links brechen nie [bewiesen]
Jeder href="/..." zeigt auf eine existierende Seite. verify.py prüft projektweit (Historie: 14 tote Details-Buttons — behoben 11.07.).

---

## TEIL C · Rechts-Gesetze

### §C1 · Consent vor Tracking [bewiesen]
Kein GTM/GA4-Load vor expliziter Zustimmung. Consent Mode v2 default denied. Ablehnen lädt nichts.

### §C2 · Affiliate-Transparenz [bewiesen]
Kennzeichnung sitewide (Footer + Affiliate-Hinweis-Seite + cta-note an Kaufboxen). Keine irreführenden Shop-Signale (Zahlungsarten-Icons wurden entfernt — wir sind kein Shop).

### §C3 · Bildrechte [bewiesen]
Nur offizielle Amazon-CDN-URLs (SiteStripe/Rechtsklick) oder eigene Fotos. Keine Pressebilder, keine fremden Reviews-Fotos. PA-API nicht verfügbar (Konto ohne qualifizierte Verkäufe).

### §C4 · Anwaltliche Endabnahme [Soll, offen]
Impressum/Datenschutz sind fachlich solide aufgebaut, die juristische Prüfung steht aus. Vor größeren Marketing-Pushes erledigen. (Kein Blocker für Content-Arbeit.)

---

## TEIL D · Betriebsregeln für Claude Code

- **Verify-Gate:** `python3 scripts/verify.py` muss grün sein, bevor irgendetwas als fertig gilt. Nie "sieht gut aus".
- **STATUS-Pflicht:** Nach jedem abgeschlossenen Schritt `brain/STATUS.md` aktualisieren. Bei Widerspruch gewinnt das Repo.
- **Diagnose vor Fix:** Ursache faktisch beweisen (Grep, Test, Datenlage), nie auf Verdacht bauen. Historisches Vorbild: GTM-Debugging 10.07. (Container geladen aber leer → Ursache "nicht veröffentlicht" bewiesen, nicht geraten).
- **Autonomes Deploy (seit 18.07.2026):** Claude Code committet und pusht selbstständig; Push auf main löst den Live-Deploy aus (GitHub Actions). Hartes Maschinen-Gate: verify.py MUSS grün sein vor jedem Commit — ein roter Stand wird niemals gepusht. Eine aussagekräftige Commit-Message pro abgeschlossenem Arbeitspaket. Yasin hat jederzeit Rollback-Recht via `git revert`.
- **Verbleibende Menschen-Gates:** Geld-/ASIN-Änderungen ohne Screenshot-Beleg · Änderungen an `.github/workflows/` · Änderungen an `.claude/settings.json`. Stoppen, auf "braucht Yasin"-Liste (LOOP-STATE), fragen. (Deploy, Seiten-Löschung und >10-Dateien-Gate sind seit 18.07.2026 durch das verify-Gate ersetzt.)
- **Macher ≠ Prüfer:** Reviews größerer Umbauten in frischem Kontext.
- **Keine Permission-Prompts (seit 18.07.2026):** settings.json genehmigt alle Werkzeuge autonom (bypassPermissions); harte technische Ausnahmen bleiben `rm -rf` und `sudo` (deny). Die inhaltlichen Menschen-Gates aus dieser Constitution gelten unabhängig davon auf Verhaltensebene weiter.
- **Kontext-Schnitt (seit 18.07.2026):** Claude Code überwacht sein Kontextfenster selbst. Bei absehbarer Erschöpfung wird KEINE neue Baustelle mehr geöffnet: das laufende Teilstück wird fertiggestellt (verify grün, Commit + Push, STATUS/Protokoll/LOOP-STATE aktuell), der Folgeschritt präzise in STATUS hinterlegt, dann sauberer Session-Schnitt. Kein halbfertiges Feature, kein uncommitteter Stand über Session-Grenzen.
- **str_replace mit vollem Kontext**, mehrzeilige HTML-Blöcke nie per sed. Sitemap-Änderungen immer mit XML-Validierung.
- **Komplett-Läufe der Generatoren** nach products.json-Änderungen (gen_pages → gen_hubs → verify), nie Teilstände committen.
- **Rückfluss:** Neues Muster oder neue Lehre → Patterns/Constitution ergänzen, im Änderungslog datieren.

---

## Offene Befunde
| Befund | Gesetz | Status |
|---|---|---|
| /ratgeber/-Duplikat live + .nojekyll fehlte im Repo | §B2 | im Brain-Commit behoben — **Deploy ausstehend** |
| 5 Reviews mit geschätzten reviewCounts (Gruppe A) | §A4 | offen, bei nächsten Screenshots präzisieren |
| Rechtstexte ohne anwaltliche Abnahme | §C4 | offen (Yasin) |
| Alt-Texte generisch, nur 1 Bild pro Produkt | §A6/Block H | geplant (Spec folgt) |

## Änderungslog
| Datum | Änderung |
|---|---|
| 2026-07-18 | v1.0 — Constitution aus Projekthistorie extrahiert; alle A/B/C-Gesetze durch Sessions bewiesen oder als Befund markiert. |
| 2026-07-18 | v1.2 — Zwei Betriebsregeln ergänzt (Yasins Anweisung): Keine Permission-Prompts mehr (settings.json bypassPermissions, deny nur rm -rf/sudo) + Kontext-Schnitt-Regel (Session endet nur an sauberen Schnitten: Teilstück fertig, grün, gepusht, Folgeschritt in STATUS). |
| 2026-07-18 | v1.1 — Teil D auf Vollautonomie umgestellt (Yasins Entscheidung): verify.py als hartes Maschinen-Gate ersetzt das Deploy-Menschen-Gate; Claude Code committet/pusht selbst; Rollback-Recht Yasin via git revert. Namenskorrektur: Projektinhaber heißt Yasin; der bisher im Brain verwendete Rufname war ein Transkriptionsfehler und wurde projektweit ersetzt. |
