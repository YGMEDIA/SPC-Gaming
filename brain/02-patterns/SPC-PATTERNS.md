# SPC PATTERN-KATALOG

> Wiederkehrende Bau-Muster, aus dem echten Projekt erkannt. Jede Änderung folgt einem Pattern — oder definiert hier ein neues. Ein Pattern ist erst "echt", wenn es mindestens einmal im Repo funktioniert.

## P-1 · Produktkarten-Pattern
**Wann:** Jede Darstellung eines Produkts in Grids (Hubs, /produkte/, Finder, Marken).
**Form:** `.pcard` mit data-product (slug), .pcard-brand/-name/-claim/-specs, price-row, .pcard-actions = btn-detail ("Mehr erfahren" → detail) + btn-amazon (data-asin, data-product, data-img, href="#"). Statisches HTML und JS-Renderer (hub-render.js/produkte.js/finder.js) erzeugen **byte-identisches Markup** — Hydration überschreibt 1:1 (§A2).
**Vorlage:** gen_hubs.py `card_html()` = Referenz-Implementierung.
**Gesetze:** §A1, §A2, §A3.

## P-2 · Detailseiten-Generator-Pattern
**Wann:** Produktseiten ohne redaktionelles Voll-Review.
**Form:** gen_content.py (CONTENT-Dict: verdict, 2 Absätze, pros/cons, 2 FAQs — individuell geschrieben, nie Template-Floskeln) + gen_pages.py (Kurzcheck-Layout: Breadcrumb, verdict-box, Specs mit sichtbarem Amazon-Rating, Stärken/Schwächen, FAQ, Related ×3, Sticky-CTA; Product+BreadcrumbList+FAQPage-Schema). Ehrlichkeits-Abstufung nach §A6.
**Vorlage:** /produkte/risoka-finger-sleeves/ (stark) · /produkte/marsgaming-mgpxpro/ (ehrliche Abwertung).
**Gesetze:** §A1, §A4, §A6.

## P-3 · Hub-Pre-Render-Pattern
**Wann:** Jede Seite, deren Produktliste aus products.json kommt.
**Form:** gen_hubs.py rendert Karten statisch in den Grid-Container, setzt Zähler statisch, injiziert SEO-Editorial (3 Absätze mit internen Links) + FAQ-Sektion + ItemList/BreadcrumbList/FAQPage-Schema. JS filtert/hydratisiert danach.
**Vorlage:** controller/ios/index.html.
**Gesetze:** §A2, §B1, §B4.

## P-4 · Review-Update-Loop-Pattern
**Wann:** Preis-/Daten-Aktualisierung bestehender Produkte.
**Form:** Strikt seriell: Claude nennt EINEN Amazon-Link → Yasin liefert Screenshot → Daten extrahieren → products.json + betroffene HTML-Stellen updaten (Schema = sichtbarer Text!) → nächster. Nie mehrere gleichzeitig, nie ohne Screenshot.
**Gesetze:** §A1, §A4, §A5.

## P-5 · Blog-Artikel-Pattern
**Wann:** Jeder neue oder ausgebaute Blog-Artikel.
**Form:** verdict-box (Direktantwort aufs Frage-Keyword) → H2/H3-Prosa (~800 W) → aufklappbare FAQ → Related-Box → Finder-CTA. Article+BreadcrumbList+FAQPage-Schema, OG komplett. Kontextuelle Links auf Reviews/Hubs (§B4). Byline/Layout einheitlich.
**Vorlage:** blog/cloud-gaming-smartphone/.
**Gesetze:** §B1, §B4, §B5.

## P-6 · Longtail-Datenblatt-Pattern [bewiesen 18.07.2026]
**Wann:** Alt-/Budget-Modelle aus dem Longtail-Sheet, oft nicht (mehr) bei Amazon.de kaufbar.
**Form:** gen_longtail.py + assets/data/longtail.json (getrennt von products.json, §A1): P-2-Template, aber Kaufbox → Verfügbarkeits-Box (ehrlich, kein Kauflink), Preiszeile → Status-Zeile, 2-3 kaufbare Alternativen als related-cards + "Beste Alternative"-CTA. Product-Schema NUR belegte Felder (kein Preis/Rating/Bild). Generator-Asserts: FAQ-Schema == sichtbarer Text, ≥2 kaufbare Links, Title ≤62.
**Vorlage:** /produkte/8bitdo-lite-2/ (Top-Volumen) · /produkte/mocute-050/ (ehrliche Abratung).
**Gesetze:** §A5, §A6, §B1, §B3.

## P-7 · Verify-Suite-Pattern
**Wann:** Vor jedem "fertig", nach jedem Umbau.
**Form:** scripts/verify.py — stdlib-only, Exit 0/1, prüft: JSON-LD-Validität, interne Links, Sitemap (XML + Datei-Abgleich beidseitig), No-JS-Statik (Karten-Mindestzahlen), Invarianten (CNAME, .nojekyll, kein /ratgeber/, keine \x02), products.json-Integrität (Pflichtfelder, Unikate), data-asin-Format.
**Gesetze:** Teil D.

## P-8 · Screenshot-als-Ground-Truth-Pattern
**Wann:** Jede externe Datenlage (Amazon, GSC, GA4).
**Form:** Yasin liefert Screenshot/Export → landet konzeptionell in 03-research/raw/ (Ablage der Kernzahlen als datierte Notiz) → Claude leitet Maßnahmen ab und schreibt die INTERPRETATION getrennt von den Rohzahlen. Rohdaten werden nie überschrieben.
**Gesetze:** Leitprinzip 1, §A5, Leseregel "Rohquellen unantastbar".

## P-9 · Bilder-Galerie-Pattern [bewiesen 19.07.2026]
**Wann:** Mehrbild pro Sortiments-Produkt (Block H Teil 2) auf generierten Detailseiten.
**Beschaffung:** Amazon blockt nur programmatische Zugriffe — Yasins ECHTER Chrome via Claude-in-Chrome-Extension kommt durch. Pro ASIN: /dp/ASIN öffnen, hiRes-URLs per Regex `["']hiRes["']\s*:\s*["'](https:[^"']+)["']` aus den Seiten-Scripts ziehen (dedupe, Original-Reihenfolge; browser_batch bündelt navigate+JS für ~5 Produkte pro Call). Validierung: urls[0] muss idealerweise der products.json-img entsprechen (Methoden-Beweis); jede Galerie-URL per HEAD == 200; Dedupe gegen img über die Bild-ID (Pfadteil vor `._`).
**Daten:** `gallery`-Feld in products.json = 2–3 Zusatz-URLs (ohne Hauptbild-Duplikat). products.json bleibt einzige Wahrheit (§A1).
**Bau:** gen_pages.py rendert bei vorhandenem gallery eine "Produktbilder"-Sektion (figure-Grid, lazy, onerror-remove) zwischen Specs und Stärken/Schwächen; Product-Schema `image` wird Array [img, ...gallery]. Regeneration NUR über `gen_pages.py --regen [slugs]` (Normalmodus baut nur detail-lose Produkte; --regen fasst NIE Review-Seiten an). Vor Galerie-Läufen: Drift-Test mit einem galerielosen Produkt (git diff muss leer bis kosmetisch sein).
**Alt-Texte:** Ohne Bild-Sichtung KEINE erfundenen Merkmale (§A5-Geist): "{Name}, Produktansicht N". Merkmals-Alts nach A4-Formel erst, wenn Bilder gesichtet werden (Review-Galerie-Paket).
**Vorlage:** /produkte/risoka-trigger/ · Gesetze: §A1, §A2, §A5, §C3.

---

## P-10 · Produkt-Video-Pattern [bewiesen 19.07.2026]
**Wann:** Amazon-Produktvideo auf Detail-/Review-Seiten (Block H3). Ehrlicher Rahmen: NUR wo Amazon ein Video hat (Stand 19.07.: 19/40).
**Beschaffung (produktgebunden, NIE global):** /dp/ASIN in Yasins Chrome → HTML per same-origin `fetch(location.href)` (DOM-Script-Scan unzuverlässig, Tag verschwindet nach Hydration) → ab `ImageBlockATF` den `'videos'`-Array balanced parsen, leer → Fallback ab `ImageBlockBTF`; ohne Slice-Limit. videos[0] (variant MAIN) = das Video des Produkts. Der globale DOM-Scan nach .mp4 ist VERBOTEN als Quelle (multi-brand-Widget mischt Fremdvideos ein — Beweis im Protokoll 2026-07-19-dev-galerie-groesser-video-recherche.md).
**mp4-Ableitung:** ImageBlock liefert HLS (`default.jobtemplate.hls.m3u8`, nativ unspielbar) → Sibling `default.jobtemplate.mp4.480.mp4` im selben VSE-Artefakt-Ordner (einzige mp4-Rendition). Poster = slateUrl.
**Validierung pro Treffer (Pflicht):** mp4-HEAD 200 video/mp4 · Poster-HEAD · Dauer-Match deklariert vs. mvhd-Box (±2 s) · projektweite URL-Eindeutigkeit · Poster-Kontaktbogen sichten.
**Daten:** `video`-Feld in products.json = {url, poster, duration "M:SS"}; nur belegte Treffer (§A5-Geist).
**Bau:** Sektion "Produktvideo" zwischen Galerie und Stärken/Schwächen: `<video controls preload="none" poster src title>` + Zeile "Video von der Amazon-Produktseite · Länge X:XX Min.". preload=none hält die Seite statisch (§A2), kein Consent-Thema. KEIN VideoObject-Schema (uploadDate nicht belegbar). CSS synchron style.css + gen_pages-<style>. GEN-Seiten via `gen_pages.py --regen`, Reviews per Script-Pass mit Assertions.
**Vorlage:** /produkte/risoka-trigger/ · Gesetze: §A1, §A2, §A5, §C3.

---

## P-11 · Daten-Fließtext-Pattern [bewiesen 30.09.2026]
**Wann:** Immer wenn Fließtext Zahlen aus products.json trägt (Preise, Sterne, Bewertungszahlen, Durchschnitte, Preisdifferenzen). Von Hand geschriebener Text mit Datenzahlen ist ein §A1-Verstoß auf Zeit: Der nächste preis-loop ändert die Quelle, die Prosa bleibt alt.
**Regel:** Solcher Text wird generiert, nie von Hand gepflegt. Jede Zahl geht durch einen Lookup auf products.json.
**Drei Pflicht-Mechanismen (alle rot/grün beweisen, nicht nur behaupten):**
1. **Idempotenz per Marker.** Generierter Block zwischen `<!-- X:START -->` / `<!-- X:END -->`; beim Lauf erst entfernen (inklusive nachgestelltem `\n`, sonst wächst die Datei pro Lauf um eine Leerzeile), dann neu einsetzen. Beweis: drei Läufe → identische Datei-Hashes.
2. **Drift-Gate im Generator.** Erlaubte Zahlenmenge aus der Datenquelle bilden (alle Preise, Sterne, Counts, Aggregate, Preisdifferenzen), Text dagegen prüfen, Abbruch bei ungedeckter Zahl. Vorher herausfiltern: Produktnamen mit Ziffern (Kishi V3, FunCooler 6) und Fremdgeräte-/Versionsbezeichnungen (iPhone 12, iOS 13). Beweis: erfundene Zahl einschmuggeln → Abbruch.
3. **verify-Invariante.** `verify.py` ruft den Generator mit `--check` und wird rot, sobald HTML und Datenquelle auseinanderlaufen. Beweis: Preis in products.json ändern → verify rot; zurück → grün.
**Quellenregel für Sachaussagen [Kernlehre 30.09.]:** products.json ist die Wahrheit für PRODUKTDATEN (Preise, Specs, ASINs, §A1) — NICHT für Sachaussagen über Kompatibilität, Bauform, Verbindung oder Nutzererfahrung. Die stehen in unseren eigenen Review- und Blog-Seiten. Vor jeder solchen Aussage die betroffene Produktseite lesen und zitieren; `worksOn` und `specs` allein reichen NICHT. Beleg: sechs falsche Aussagen am 30.09., alle aus products.json abgeleitet, alle von den eigenen Review-Seiten widerlegt (Kishi V3 kann iPad mini, G8 Plus ist Dual-Mode, X3 Pro hat kein iOS, 8BitDo-Verbindungsart strittig). Widersprechen sich Datenkern und Seite: NICHTS behaupten, Aussage weglassen, Befund in STATUS, Screenshots anfordern (§A5).
**Schema-Kopplung (§A4):** Wenn der Block FAQs erzeugt, das FAQPage-Schema aus dem FINALEN HTML neu rendern, nicht parallel pflegen. Assertion: Anzahl sichtbarer `<details>` == Anzahl Question-Objekte. Achtung: Jede falsche Aussage in einer FAQ steht damit doppelt, sichtbar und in den strukturierten Daten.
**Bestandstext der Zielseite gegenlesen [Kernlehre 30.09., zweiter Teil]:** Ein Generator, der in eine Seite mit vorhandenem Text einfügt, muss den Bestandstext zum selben Thema kennen und angleichen. Sonst entstehen Widersprüche INNERHALB einer Seite, und die sind schlimmer als ein einheitlicher Fehler: Das FAQPage-Schema wird aus dem sichtbaren HTML gerendert, zieht die alte Antwort also aktiv in die strukturierten Daten. Beleg: Nach der ersten Korrekturrunde sagte marken/razer im neuen Block "alle drei führen das iPad mini", in der Bestands-FAQ zwölf Zeilen tiefer "Nur der Kishi Ultra". Praktisch: Nach jedem Generatorlauf die Zielseite nach den Schlüsselbegriffen des neuen Textes durchsuchen (Tablet, Bluetooth, Plattformnamen) und jede Trefferstelle lesen.
**Korrigierte Formulierungen maschinell sperren.** Eine Korrektur an Bestandstext, den ein Generator anfasst, ist verlierbar: Am 30.09. hat ein `git checkout` auf dieselbe Datei eine Handkorrektur aus der Vorrunde überschrieben, und das fiel erst zwei Prüfrunden später auf. Widerlegte Formulierungen gehören deshalb als verbotene Strings mit Begründung in `verify.py` (dort Abschnitt 7), analog zu den CNAME- und Zombie-Invarianten.
**Unabhängiger Prüflauf ist Pflicht, nicht Kür — und er endet nicht nach einer Runde.** Das Drift-Gate prüft Zahlen, keine Sachaussagen. Am 30.09. hielt ich den Stand nach vier selbst gefundenen Fehlern für sauber; Runde 1 fand zwölf weitere, sechs nachweislich falsch. Runde 2 fand drei NEUE Fehler aus meinen eigenen Korrekturen, Runde 3 eine Regression. Erst prüfen lassen, bis der Prüfer freigibt, dann committen — nicht, bis man selbst zufrieden ist.
**Eigenkontrollen gegen den Wortlaut führen, nicht gegen die Erinnerung.** Ein grep auf "weder Bluetooth noch iOS" meldete null Treffer, im Text stand "weder Bluetooth noch iPhone".
**Neue CSS-Klassen:** gegen style.css prüfen, bevor sie live gehen — verify.py fängt ungestyltes Markup NICHT. Fehlt eine Klasse, kommt sie nach dem Muster der Vergleichsseiten in einen Seiten-`<style>`-Block (dort liegt auch `.vs-table`).
**Superlative:** nur mit explizitem Geltungsbereich im Satz ("der vier Marken mit eigenem Hub" statt "in unserem Sortiment"). Drei von vier abgefangenen Fehlern am 30.09. und der Fehler vom 29.09. waren Superlative mit unausgesprochenem Bezugsrahmen.
**Aussagen-Gate zusätzlich zum Drift-Gate [ergänzt 30.09.]:** Das Drift-Gate prüft, ob eine ZAHL belegt ist. Es fängt nicht, wenn eine VERGLEICHSAUSSAGE kippt, obwohl alle Zahlen darin korrekt sind. Genau das passierte am 30.09.: Nach dem Amazon-Abgleich stimmte "GameSir hat mehr Bewertungen als die drei anderen zusammen" nicht mehr (3.504 gegen 3.941), und zwei Produkte, die im Text über den Preis verglichen wurden, kosteten plötzlich dasselbe. Deshalb prüft der Generator jede Vergleichsrelation, die im Text behauptet wird, vor dem Rendern gegen die Daten und bricht ab, wenn eine nicht mehr trägt.
**Quellen-Wahrheit hat zwei Ebenen [30.09.]:** §A1 macht products.json zur Pflege-Wahrheit, nicht zur Wahrheitsfindung. Beim Abgleich mit Amazon lag zweimal products.json falsch, zweimal die Review-Seite, einmal beide. Bei Widerspruch entscheidet nur die Herstellerangabe, und zwar aus TITEL und FEATURE-BULLETS der Produktseite: Fremdempfehlungen und Varianten-Listings stehen im selben DOM und führen sonst zu falschen Bestätigungen.
**Gates haben eine Reichweite, und die ist kleiner als man denkt [30.09.]:** Drift- und Aussagen-Gate prüfen NUR den Bereich zwischen den Generator-Markern. Produktkarten, Bestands-FAQs, Schema-Werte und Hub-Zugehörigkeit liegen außerhalb; dort lagen elf von siebzehn Befunden. Deshalb gehört zusätzlich ein generisches §A1-Audit ins verify-Gate, das HTML repoweit gegen products.json hält (`sync_product_values.py --audit`: Karten mit allen Spec-Chips, Schema-Werte, Hub-Zugehörigkeit gegen worksOn). Eine generische Invariante schlägt jede Liste verbotener Strings, weil sie auch die Fehler fängt, die noch niemand gemacht hat.
**Karten-Scan beginnt am `<article>`, nicht am `data-product` [30.09., zweite Lehre]:** In 29 von 202 Karten sitzt `data-product` erst im Kauf-Button, also HINTER Claim und Preiszeile. Ein Scan ab dort überspringt genau die Felder, die gesynct werden sollen. Folge am 30.09.: 32 veraltete Claims und 23 falsche Preise blieben stehen, das Audit meldete trotzdem grün. Zweiter Blindfleck derselben Klasse: Karten mit einem Slug, den products.json nicht kennt (`backbone-one` statt `backbone-one-2`), wurden stumm übersprungen. Das Audit meldet verwaiste Slugs jetzt als Fehler.
**Produkte über das Feld `name` identifizieren, nie über den Slug [30.09.]:** Die Slugs sind historisch gewachsen und irreführend. `ozkak-mini-portable` heißt "L1R1 Trigger-Aufsatz" (2 Auslöser), `ozkak-trigger-l1r1` heißt "Mobile Controller 4-Trigger" (4 Auslöser). Wer beim Texten dem Slug folgt, vertauscht die Produkte, und genau das ist passiert.
**Audit-Regexes gegen echtes Markup testen:** Zwei Lücken machten das Audit zunächst stumm — ein verschachteltes `<span>` im Preisfeld und ein `data-product`, das auf einer Seite erst im Kaufbutton steht. Ein Audit, das nichts findet, ist erst dann eine gute Nachricht, wenn es an einem künstlichen Fehler bewiesen wurde.
**Vorlage:** `scripts/gen_brand_sections.py` → marken/{razer,gamesir,8bitdo,backbone}/ · Sync über `scripts/sync_product_values.py` · Gesetze: §A1, §A4, §A5, §A6.

---

## Offen / noch zu definieren
- Outreach-Vorlagen-Pattern (Block F — Blogger-Anschreiben)
- Scheduled-Loop-Pattern (Automatisierung via Claude-Desktop-Schedule — erst nach 2–3 manuellen Läufen je Loop)

*SPC Pattern-Katalog v1.3 · 2026-09-30*
