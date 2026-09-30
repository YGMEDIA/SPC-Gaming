# 2026-09-30 · Daten · Amazon-Abgleich klärt den Datenkern-Konflikt

## Was

Die drei Widersprüche zwischen products.json und unseren eigenen Review-Seiten, die der
Faktencheck der Marken-Keyword-Offensive aufgedeckt hatte, sind geklärt. Yasin:
"öffne selbst in chrome amazon und schau selber nach."

Fünf Produkte in seinem Chrome geöffnet, Titel, Feature-Bullets, Preis und Bewertung aus
der Seite gelesen. Ergebnis: products.json korrigiert, ~30 Seiten gesynct, zwei
Hub-Zugehörigkeiten bereinigt, fünf Review-Seiten und der Tablet-Blog nachgezogen.

## Ergebnis je Produkt

| Produkt | Wer hatte recht | Korrektur |
|---|---|---|
| 8BitDo Ultimate 2C | **Review-Seite** | Amazon: "Ultimate 2C **Wired** Controller for **Windows PC and Android**", "Kabelgebundene Verbindung (abnehmbar)". products.json hatte Bluetooth, iOS und Switch. Alles falsch, korrigiert |
| GameSir X3 Pro | **Review-Seite** | Amazon-Titel: "**Android Controller**". `worksOn` hat `ios` verloren |
| Razer Kishi V3 | **products.json** | Amazon: "für iPhone und Android **Smartphones**", kein iPad. Unsere Review-Seite behauptete "iPad Mini" in der Datentabelle |
| Razer Kishi V3 Pro | **beide daneben** | Amazon: "und **Tablets 8\"**", "Für **iPads** & Android-Tablets bis zu 8 Zoll". `worksOn` hat `tablet` bekommen |
| GameSir X5 Lite | **products.json** | Maschinell geprüft: iPad/Tablet kommt im eigenen Titel und in den Features nicht vor. Review-Seite nannte "iPad Mini 6/7" |

Die Lehre daraus ist unbequemer als ein einfaches "die eine Quelle war schuld": Zweimal
lag products.json falsch, zweimal die Review-Seite, einmal beide. Es gibt keine Quelle im
Repo, der man ohne Abgleich trauen kann.

**Warum die iPad-Treffer täuschten:** Auf jeder Amazon-Produktseite stehen unter dem
eigenen Text Fremdempfehlungen und Varianten-Listings. Beim Kishi V3 kamen alle
iPad-Treffer aus Empfehlungen für GameSir G8 Plus und abxylute S9. Die Prüfung musste
deshalb Titel und Feature-Bullets isolieren, statt den Seitentext zu durchsuchen.

## Nebenbefund, gravierender als der Anlass

Bei **5 von 5** geprüften Produkten wich mindestens ein Wert ab:

| Produkt | Preis | Bewertung |
|---|---|---|
| 8BitDo Ultimate 2C | 20 → **30 €** | 4,5 (854) → **4,6 (2.188)** |
| GameSir X3 Pro | 90 → **45 €** | 3,9 (283) → **4,0 (306)** |
| Razer Kishi V3 | 93 → **88 €** | 4,4 (126) → **4,4 (153)** |
| Razer Kishi V3 Pro | 149 → **152 €** | 4,4 (125) → **4,2 (151)** |
| GameSir X5 Lite | 45 → **45 €** | 4,2 (1.655) → **4,2 (1.953)** |

Der Belegstand der übrigen 37 Produkte ist der 21.07.2026. Wenn 5 von 5 Stichproben
abweichen, ist der preis-loop-Vollabgleich überfällig, nicht optional. Steht als eigener
Befund in STATUS.

## Wie

**Beschaffung:** Amazon-Produktseiten in Yasins Chrome, Werte per DOM-Abfrage aus
`#productTitle`, `#feature-bullets`, `.a-price`, `#acrPopover` und `#acrCustomerReviewText`.
Der etablierte P-8/P-9-Weg. Belege liegen in
`03-research/raw/amazon/2026-09-30-datenkern-klaerung.md`.

**Sync:** Neues Werkzeug `scripts/sync_product_values.py`, das HTML-Karten und
Bewertungs-Strings im gesamten Repo gegen products.json zieht. Es ergänzt
`sync_new_products.py` (das nur die drei Plattform-Hubs und /produkte/ abdeckt) um
Marken-, Geschenk- und Themenseiten sowie Prosa und Schemas. Ergebnis dieses Laufs:
9 Karten und 27 Namens- und Claim-Stellen über 15 Dateien, dazu 40 Stellen auf fünf
Review-Seiten per Einzelpass.

**Hub-Bereinigung:** Zwei Karten aus dem iOS-Hub (2C und X3 Pro können kein iOS) und eine
aus dem Mini-Hub (der Hub verspricht Bluetooth-Gamepads, der 2C ist kabelgebunden),
jeweils inklusive ItemList-Schema und Zähler.

## Zwei Aussagen sind durch die neuen Zahlen gekippt

Das ist der interessanteste Teil. Beide Aussagen enthielten **nur belegte Zahlen**, das
Drift-Gate schlug also nicht an. Gekippt ist die Aussage, nicht die Zahl:

1. "GameSir hat mehr Bewertungen als Razer, Backbone und 8BitDo zusammen" trägt nicht
   mehr: 3.504 gegen 3.941, weil der 2C von 854 auf 2.188 Bewertungen gesprungen ist.
2. "Der X3 Pro kostet 90 Euro, der X5 Lite die Hälfte und liegt darüber" trägt nicht mehr,
   beide kosten jetzt 45 Euro.

Dazu wurde meine eigene, am selben Tag freigegebene Razer-Formulierung falsch: "alle drei
führen das iPad mini" gilt nicht mehr, der V3 kann es nicht.

**Konsequenz: ein Aussagen-Gate.** `gen_brand_sections.py` prüft jetzt vor dem Rendern
sieben Vergleichsaussagen gegen die Daten und bricht ab, wenn eine kippt (wer die meisten
Bewertungen hat, wer die bestbewertete Marke ist, wer die kleinste Basis hat, welches
Gerät das teuerste ist, ob der G8 Plus teurer als der X5 Lite ist und schlechter bewertet,
ob der Kishi V3 mindestens gleichauf mit dem V3 Pro liegt). Rot/grün bewiesen durch
Nachstellen genau dieser Kippung.

## Die eigentliche Konsequenz: ein §A1-Vollaudit

Der Prüflauf nach dem Abgleich fand siebzehn offene Stellen und traf mit seiner Analyse
den Kern: **Elf davon lagen außerhalb der Generator-Marker.** Drift-Gate und Aussagen-Gate
prüfen nur den Bereich zwischen `BRAND-EXT:START` und `:END`. Alles andere, also
Produktkarten auf 125 Seiten, Bestands-FAQs, Schema-Werte und Hub-Zugehörigkeit, war
ungeprüft. Seine Empfehlung, statt weiterer Einzelstrings eine generische Invariante zu
bauen, war richtig.

**`scripts/sync_product_values.py --audit`**, aufgerufen von verify.py, prüft jetzt
repoweit:

| Was | Wogegen |
|---|---|
| jede Produktkarte | Preis und **alle** Spec-Chips gegen products.json |
| jeder Product-Schema-Block | `offers/price`, `ratingValue`, `reviewCount` |
| reviewCount separat | Tausenderpunkt, der von Google als Kommazahl gelesen wird |
| jeder Plattform-Hub | Kartenbestand gegen `worksOn`, in beide Richtungen |

Beim ersten Lauf: 15 Abweichungen, vier mehr als der Prüfer gemeldet hatte, darunter ein
Doppel-Escaping (`Tablet/iPad &amp;lt;10mm`) und drei Tablet-Hub-Fehler. Der Tablet-Hub
führte den Ultimate 2C als "Tablet-Empfehlung" mit dem Claim "Bluetooth-Controller ideal
für Tablets, Hall-Effect, Switch und PC kompatibel", was nach dem Abgleich dreifach falsch
war, und es fehlte der Kishi V3 Pro, der neu `tablet` bekommen hatte.

**Zwei eigene Regex-Lücken** musste ich dabei schließen, beide hätten das Audit stumm
gemacht: Der Preis-Regex brach an verschachtelten Spans
(`<span class="price">93 €<span class="price-approx">UVP</span>`), und die
Hub-Kartenerkennung griff nicht, weil der Tablet-Hub `data-product` erst im Kaufbutton
trägt statt am `<article>`. Erst danach deckten sich meine Funde mit denen des Prüfers.

Rot/grün bewiesen für beide Fehlerklassen: ein verfälschter Kartenpreis und ein Produkt im
falschen Hub werden je mit Datei, Produkt, Ist- und Sollwert gemeldet.

## Die Kaskade: 83 Stellen im Fließtext

Der letzte Prüflauf stellte die entscheidende Frage: Gibt es Träger von Produktwerten, die
weder Karte noch Schema sind? Die Antwort ist ja, und sie ist umfangreich. Nach dem
Herausschneiden von Karten und JSON-LD blieben **83 Stellen** mit veralteten Werten der
fünf Produkte: Cross-Sell-Kacheln auf Review-Seiten, Vergleichstabellen, Blog-Fließtext,
die Black-Friday-Referenzpreise, das Startseiten-Ranking und `llms.txt`.

Behandelt in drei Stufen:

1. **Mechanisch eindeutige Muster automatisiert** (Produktname unmittelbar gefolgt von
   seinem Preis in einer Kachel oder in Klammern): 46 Ersetzungen über 20 Dateien.
2. **Gezielt von Hand**, wo der Kontext zählt: Black-Friday-Schwellen (mit den
   Zielpreisen), die drei Vergleichsseiten inklusive der Urteilssätze
   ("mit 4,4 zu 4,1 Sternen" wurde zu "mit 4,2 zu 4,1 Sternen der knapp besser
   bewertete"), die Mini-Gamepad-Empfehlung und vier Blog-Stellen.
3. **Als Warnung im Audit belassen**, was sich nicht sauber automatisieren lässt. Die
   Fließtext-Prüfung meldet Treffer, blockiert aber nicht: Im Umfeld eines Produktnamens
   stehen auch Nachbarpreise, ein hartes Gate wäre unbrauchbar. Aufruf mit
   `sync_product_values.py --audit --text`.

**Bewusst NICHT erledigt:** Der Fließtext nennt auch Werte der übrigen 37 Produkte, und
die sind seit dem 21.07. nicht abgeglichen. Beispiele aus der Warnliste: G8 Galileo mit
63 statt 80 Euro in einem Blog, MGPXPRO mit 4,0 statt 3,6 Sternen. Diese Stellen jetzt zu
korrigieren hieße, sie nach dem Vollabgleich ein zweites Mal anzufassen. Sie bleiben
offen und sind über die Warnliste jederzeit auffindbar.

## Verify

- `python3 scripts/verify.py` grün: 125 Seiten, 247 JSON-LD-Blöcke, 42 Produkte
- Aussagen-Gate rot/grün bewiesen (Bewertungszahl künstlich erhöht → Abbruch mit
  "GameSir hat nicht mehr die meisten Bewertungen der vier Marken")
- Restkontrolle: 0 Treffer für alle neun alten Werte ("Standalone-Bluetooth",
  "Ultimate 2C Wireless", die fünf alten Bewertungs-Strings, "iPad Mini, Win 11",
  "iPad Mini 6/7")
- `gen_brand_sections.py --check` meldet keine Abweichung
- Hub-Zugehörigkeit gegen `worksOn` geprüft: iOS 26, Android 26, Mini 2, keine Abweichung
- Unabhängiger Prüflauf in frischem Kontext

## Gelernt

1. **Keine Quelle im Repo ist ohne Abgleich vertrauenswürdig.** Zweimal lag products.json
   falsch, zweimal die Review-Seite, einmal beide. Die Regel "products.json gewinnt" (§A1)
   gilt für die Pflege, nicht für die Wahrheitsfindung.

2. **Ein Drift-Gate über Zahlen fängt keine gekippten Aussagen.** Beide gekippten Sätze
   bestanden ausschließlich aus belegten Zahlen. Wer Vergleiche schreibt, muss die
   Vergleichsrelation selbst prüfen, nicht nur ihre Bestandteile. Daher das Aussagen-Gate.

3. **Auf Amazon-Produktseiten muss man den eigenen Text isolieren.** Fremdempfehlungen und
   Varianten-Listings stehen im selben DOM und haben hier fast zu einer falschen
   Bestätigung geführt. Titel und Feature-Bullets prüfen, nicht `body.innerText`.

4. **Ein Sync-Regex, der Whitespace verändert, meldet falsche Treffer.** Der erste Entwurf
   von `sync_product_values.py` hätte 128 korrekte Karten angefasst, nur um ein doppeltes
   Leerzeichen einzufügen. Gefunden, weil ich den Diff vor dem Schreiben angesehen habe,
   statt der Trefferzahl zu glauben.
