# 2026-09-29 · gsc-loop · Lauf 7: Trendwende bestätigt, Thin-Page-Muster auf allen Marken-Seiten

**Was:** Lauf 7 ausgewertet (erstes vollständiges Paket: 7T + 28T + Gründe-Tabelle) und das in Lauf 6 erkannte Muster konsequent zu Ende geführt. Rohdaten: `03-research/raw/gsc/2026-09-29.md`.

**Die Trendwende ist bestätigt:** Position **55,9 → 43,5 → 41,8** über drei Läufe, und die Impressionen steigen erstmals seit dem Einbruch wieder (19 → 31, plus 63 %). Die Durststrecke seit dem 25.07. hat ihren Boden gefunden und dreht.

**Indexierungs-Frage abschließend geklärt (Gründe-Tabelle nach viermaliger Bitte geliefert):** Der Rückgang der indexierten Seiten (71 → 66) ist vollständig strukturell erklärbar. Die Rechnung geht exakt auf: +4 "Seite mit Weiterleitung", +3 "durch noindex ausgeschlossen" (neue Kategorie), +1 robots, +1 gecrawlt, -1 kanonisch = +8 nicht indexierte Seiten. **72 der 129 nicht indexierten Seiten sind unsere eigenen, absichtlichen Ausschlüsse** (ratgeber- und marken-Redirect-Stubs, www-Duplikate, robots-Regeln). Der echte Engpass "Gefunden, zurzeit nicht indexiert" liegt stabil bei 35, nach 47 in Lauf 3. Kein Handlungsbedarf.

**Das Muster aus Lauf 6 wiederholt sich, diesmal vierfach.** In Lauf 6 war der Mini-Gamepad-Hub die Thin Page unter der stärksten Query. Die Prüfung der Marken-Seiten zeigt dasselbe Bild: **marken/razer 120 Wörter, marken/gamesir 138, marken/backbone 88, marken/8bitdo 59** (Referenz: iOS-Hub 1181, ausgebauter Mini-Hub 499). Und marken/razer ist mit **11 Impressionen in 28 Tagen die viertstärkste Seite überhaupt**, getragen von den Queries "razer controller" (4), "gaming controller razer" und "razer controller android".

**Maßnahme: alle vier Marken-Seiten auf Standard gebracht.**
| Seite | vorher | nachher | Karten |
|---|---|---|---|
| marken/razer | 120 W | 470 W | 3 → **4** |
| marken/gamesir | 138 W | 443 W | 3 → **5** |
| marken/backbone | 88 W | 351 W | 2 → **3** |
| marken/8bitdo | 59 W | 331 W | 1 → **2** |
Je Seite: markenspezifische Überblicks-Sektion (2-3 Absätze), 3 FAQs, ItemList- und FAQPage-Schema, alle Karten driftfrei über `gen_hubs.card_html` neu gerendert. **Vollständigkeits-Fund nebenbei:** Die Seiten zeigten nicht einmal alle Produkte der eigenen Marke (8BitDo 1 von 2, Backbone 2 von 3, GameSir 3 von 5, Razer 3 von 4). Jetzt sind alle belegten Produkte gelistet.

**§A6 umgesetzt statt umgangen:** Der Razer Phone Cooler (3,2 von 5 aus 72 Bewertungen) fehlte auf der Marken-Seite komplett. Er steht jetzt drin, aber mit expliziter Warnung im Fließtext ("empfehlen wir ausdrücklich nicht") und dem Verweis auf den gleich teuren, mit 4,2 Sternen deutlich besser bewerteten Black Shark FunCooler. Transparent listen und die Alternative nennen ist unsere Linie, nicht verschweigen.

**Ein echter Fehler, von der Faktenkontrolle abgefangen:** Im ersten Entwurf stand, der GameSir X5 Lite sei "mit 1.655 Bewertungen das meistbewertete Gerät unseres gesamten Sortiments". Falsch, gleich doppelt: Die RISOKA Finger Sleeves haben 2.835, der Turtle Beach Atom 1.896. Korrigiert auf die belegbare Aussage "der meistbewertete GameSir in unserem Sortiment" (maschinell gegen products.json verifiziert). Genau die Fehlerklasse, die am 21.07. schon einmal zugeschlagen hat: ein plausibel klingender, produktbegünstigender Superlativ.

**Verify:** verify.py GRÜN nach jedem Schritt (123 Seiten) · Superlativ-Prüfung maschinell gegen products.json (bestbewertet = 8BitDo 2C als einziges 4,5-Produkt, teuerstes = Backbone Pro, meistbewerteter GameSir = X5 Lite) · alle 18 Preis- und Rating-Angaben exakt gegen products.json abgeglichen · §A6-Warnung vorhanden · keine Em-Dashes im neuen Text · Browser-DOM-Prüfung marken/razer (4 Karten mit korrekten Preisen, 3 Schemas, 3 FAQs, Warnung sichtbar) · Meta-Freeze eingehalten (kein Title/Description angefasst) · Sitemap-lastmod 4/4.

**Gelernt:** (1) **Ein einmal erkanntes Strukturmuster lohnt die systematische Suche.** Der Thin-Page-Fund aus Lauf 6 war kein Einzelfall, sondern galt für jede Marken-Seite. Nach so einem Fund immer die verwandten Seitentypen durchzählen. (2) Kartenbestände gegen products.json rückwärts prüfen deckt nicht nur falsche Slugs auf (Lauf 6), sondern auch fehlende Produkte: Vier Marken-Seiten zeigten zusammen 9 von 14 Produkten. (3) Superlative gehören maschinell geprüft, nicht plausibilisiert. "Das meistbewertete Gerät" klang richtig und war zweifach falsch.
