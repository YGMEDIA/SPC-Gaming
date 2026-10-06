# 2026-10-06 · Daten · Vollabgleich über alle 42 Produkte, selbst bei Amazon gelesen

## Was

Yasin: „mach den vollabgleich für alle 42." Alle 42 Produkte auf amazon.de selbst
abgelesen (Preis, Sterne, Bewertungszahl, Verfügbarkeitstext, `#ASIN` und `canonical`),
Beleg mit jeder Einzelangabe:
`03-research/raw/amazon/2026-10-06-vollabgleich-42.md`.

**12 Preise geändert · 29 Bewertungen geändert · 6 Produkte nicht neu kaufbar · 1 Preis
gestiegen.** Datenstand von September 2026 (30.09.) auf **Oktober 2026 (06.10.)** gezogen.

Damit läuft der preis-loop nach zweieinhalb Monaten wieder. Der Grund für den Stillstand
ist in diesem Lauf sichtbar geworden und beseitigt: Die Datenpflege war billig, das
Nachziehen der Prosa war Handarbeit in dreistelliger Zahl.

## Wie

**1 · Lesen.** 42 Produktseiten über `amazon.de/dp/[ASIN]`, je ein kleines
Seitenkontext-Snippet für Preis, Sterne, Anzahl und Verfügbarkeit. `#ASIN` und
`canonical` mitgelesen, weil genau daran am Morgen die vertauschte Backbone-Pro-ASIN
aufgefallen war. Fünf widersprüchliche Fälle (Preis vorhanden, aber „nicht verfügbar")
ein zweites Mal geöffnet und über `#add-to-cart-button` und die Buybox entschieden.

**2 · Datenkern.** `price` und die `Bew.`-Spec gesetzt, dazu ein neues Feld **`stock`**
mit vier Werten (`ja` · `nein` · `gebraucht` · `drittanbieter`). Die Werte sind
absichtlich grob: Amazons „Nur noch 2 auf Lager" ist morgen falsch und gehört nicht in
einen Datenkern mit Monats-Datenstand.

**3 · Verfügbarkeit aus dem Datenkern.** „Verfügbar" stand **197 Mal** als Literal im
Markup und kam aus nichts. Jetzt liest es `STOCK_LABEL`/`STOCK_KLASSE` in
`produktdaten.py`; die fünf Renderer (`gen_hubs`, `gen_bestenliste`, `finder.js`,
`produkte.js`, `hub-render.js`) und `offers.availability` im Product-Schema hängen daran,
und `formfehler()` macht ein fehlendes oder unbekanntes `stock` rot. Ein fehlendes Feld
ergibt **kein** „Verfügbar" — genau diese Behauptung ohne Beleg stand vorher da.

**4 · Datenstand auf eine Zeile.** Das Gate in verify.py behauptete seit dem 30.09.:
„Bei jedem Preis-Sync wird hier EINE Zeile geändert." Das war nicht wahr: Der Wert stand
in **fünf Zeilen in vier Dateien**. Nach dem Umstellen in verify.py haben drei
Generatoren den alten Monat in 35 Seiten ZURÜCKgeschrieben. Jetzt gibt es
`scripts/datenstand.py` mit `MONAT`, `TAG` und `ISO`; verify.py, gen_pages, gen_longtail,
gen_preisfrage und md_to_pdf importieren es.

**5 · `scripts/preiswelle.py` (neu).** Zieht geänderte Werte in den Fließtext nach. Die
Tabelle wird nicht gepflegt, sondern aus `git show HEAD:products.json` gegen den
Arbeitsbaum abgeleitet — nach dem Commit ist sie leer und das Skript ein No-Op.
Jede Fundstelle wird ZUGEORDNET, bevor sie geschrieben wird, mit derselben Regel, die
`audit_prosa.py` zum Prüfen benutzt (importiert, nicht nachgebaut):

- `naechstes_produkt()` — der Produktname davor (bis 140 Zeichen)
- `_produkt_danach()` — Spiegelbild für „ab 45 € (GameSir X5 Lite)", 70 Zeichen
- `_seiten_eigner()` — der Ort, wenn in der Nähe gar kein Name steht: die eigene
  Produktseite, oder in `gen_content.py` der zuletzt geöffnete Slug-Block

Ohne Zuordnung wird **nicht** geschrieben, sondern berichtet. Gemessen: 10 der 30
geänderten Werte sind heute der Wert eines ANDEREN Produkts (der alte Preis des
Ultimate 2C ist der heutige des MGP-BT2), und ein globales „50 €" hätte „Controller
unter 50 €" mitgerissen.

**6 · Zwei Schreiber dort ergänzt, wo das Audit längst prüfte.**
`sync_product_values.py` meldete seit dem 30.09. Schema-Preis, -Bewertung und
`data-price` — geschrieben hat sie niemand. Jetzt tun es `sync_schemas()` (15 Werte) und
`sync_maschinenwerte()` (6 Werte). Beide benutzen `produkt_der_seite()`, dieselbe
Auflösung wie das Audit.

**7 · Redaktion.** 47 Stellen von Hand: Preisspannen, deren Reihenfolge kippte
(„von 45 € … bis 80 €" — der G8 Plus ist jetzt teurer als der G8 Galileo), 22
Differenzsätze („8 € günstiger" → 10 €), die Meta-Descriptions der Vergleichsseiten und
der Scuf Nomad.

## Warum so

**Warum `stock` vier Werte hat und nicht Amazons Text.** „Nur noch 2 auf Lager" ist eine
Momentaufnahme, unser Datenstand ein Monat. Eine Zahl, die täglich verfällt, in einen
Datenkern zu schreiben, der monatlich gepflegt wird, erzeugt garantiert falsche Seiten.
`ja` heißt deshalb „neu bei Amazon kaufbar, Knappheitshinweis eingeschlossen".

**Warum die sechs nicht kaufbaren Produkte im Sortiment bleiben.** Das ist eine
Sortimentsentscheidung und gehört Yasin. Was mir gehört, ist dass die Seite die Wahrheit
sagt — und das tut sie jetzt: Badge, Schema und Datenkern nennen die Lage.

**Warum die Prosa ein Werkzeug braucht und kein Suchen-und-Ersetzen.** Siehe Punkt 5. Das
Repo hat diese Lehre zweimal bezahlt (CHIP_REST in `sync_product_values.py`, „Multi:
Switch/PC" am Morgen desselben Tages): Ein Massen-Replace über zwei Produkte ist eine
Behauptung über beide.

## Verify

- **Vierzehn Gates exit 0.** `verify.py`: 127 Seiten · 254 JSON-LD-Blöcke · 42 Produkte,
  0 Fehler. `audit_prosa.py`: **0** Fließtext-Abweichungen (Start: 418)
- `sync_product_values.py --audit`: 0 harte Abweichungen; die weichen Hinweise sind von
  **54 auf 53** gefallen, also durch diesen Lauf nicht gewachsen
- **Neues Gate: Black-Friday-Schwellen-Matrix**, 12 Fälle gemessen (9 rot, 3 grün),
  0 falsch. Es liest die Deal-Regel aus der Seite selbst und prüft die ANZAHL der
  lesbaren Zeilen gegen die Tabelle
- **Verneinungs-Ausnahme im Hall-Effect-Gate**, 11 Fälle gemessen (5 rot, 6 grün),
  0 falsch
- **Fünf stehende Messreihen gegen den Endstand**, alle 0 Befunde:
  `robustheitsprobe.py` **124 Defektformen** (16 Felder x 7 falsche Typen + 12
  Sonderformen, 125 verify-Starts; vorher 117, weil `stock` fehlte) ·
  `finder_batterie.py` 111 Fälle · `idempotenzprobe.py` 17 Schreiber (idempotent UND
  baumstabil) · `besten_batterie.py` 36 Fälle (24 rot / 12 grün) ·
  `links_batterie.py` **130 Fälle (94 rot / 36 grün)**, um 19 Fälle für die
  Verfügbarkeit und die BF-Matrix gewachsen
- **Verfügbarkeits-Gate: 10 Fälle gemessen** (Badge-Text · Badge-Klasse · Text ohne
  Badge-Klasse · Schema-availability · JS-Label · JS-Klasse · JS-Tabelle ganz weg ·
  `stock` fehlt · `stock` ungültig · unverändert), 0 falsch. Die neun Defektfälle liegen
  als Dauerfälle in `links_batterie.py`

### Prosa-Nachzug in Zahlen

| | |
|---|---|
| Start (audit_prosa) | 418 Abweichungen |
| nach preiswelle, Lauf 1 (Namensregel) | 121 |
| nach preiswelle, Lauf 2 (Ortsregel) | 47 |
| nach Redaktion von Hand | **0** |

`preiswelle.py` hat in zwei Läufen **356 Stellen** geschrieben (264 mit der Namensregel,
92 nach der Ortsregel). Im Endstand hat es nichts mehr zu schreiben und lehnt **170
Fundstellen korrekt ab** (der Wert gehört dem Produkt, das danebensteht) — diese 170
wären bei einem globalen Suchen-und-Ersetzen zerstört worden.

## Drei Nachbefunde, die erst beim Messen aufgefallen sind

**1 · `preiswelle.py` hat in Python-KOMMENTARE geschrieben und damit Geschichte
zerstört.** In `gen_brand_sections.py` stand „Er war als G8 Plus (76 €) verdrahtet,
teuerster ist der G8 Galileo (80 €)" — nach dem Lauf „(72 €) … (68 €)", und damit das
Gegenteil der eigenen Aussage, weil der G8 Plus mit 72 € heute der teuerste ist. In
`gen_bestenliste.py` wurde das ZITAT einer alten Fehlermeldung korrigiert („459 statt 153
Bewertungen" → 157); ein korrigiertes Zitat ist kein Zitat. Ursache war nicht der
Schreiber allein: **`audit_prosa.py` hat die Änderung verlangt**, weil es Kommentare als
Prosa liest. Die Maskierung steht deshalb jetzt in `audit_prosa.py` (`tokenize`, nicht
Regex — ein `#` in einem String ist kein Kommentar) und wird vom Schreiber importiert.
Gemessen in beiden Richtungen: Wert im String-Literal → rot, derselbe Wert im Kommentar →
grün.

**2 · Das neue Verfügbarkeits-Gate hat sofort sechs echte Fälle gefunden**, alle auf
handgepflegten Seiten (`controller/`, `geschenke/`, `marken/backbone`, `marken/gamesir`,
`zubehoer/trigger`): „Verfügbar" neben Backbone Pro, X3 Pro und Toaluea. Die Generatoren
lasen `stock` schon, die Handseiten nicht. Deshalb schreibt `sync_cards()` das Badge jetzt
mit — ein Gate ohne Schreiber wäre Handarbeit bei jeder Welle, siehe Lehre 2.

**3 · Vier stehende Messreihen führten ihre Werte als Literale** und haben nach der Welle
stillschweigend weniger geprüft: `besten_batterie.py` meldete **6 Fälle „Mutation hat
nicht gegriffen"** (die Literale „4,2 (706)", „80 €", „aus 706 Bewertungen" existierten
nicht mehr) und `links_batterie.py` **2** („kostet 88 € und kommt"), dazu
`finder_batterie.py` **1** („30 und 190" als Preisspanne) und nach den Hall-Specs noch
einmal `links_batterie.py` **3** („Fünf der 28 Controller"). Die Schlusszeilen sagten
jeweils unverändert „36 Fälle", „111 Fälle", „130 Fälle". Dieselbe Klasse wie
`robustheitsprobe.py`, die ihre Feldliste selbst führte und mein neues `stock` deshalb
nicht geprüft hat, während sie „117 Defektformen, keine bricht ab" meldete. Zusammen
**12 Fälle ohne Beweiswert**. Alle lesen ihre Werte jetzt aus der Quelle: `_dk()` aus
products.json, `_b10_preis()`, `_preisspanne()` und `_hall_satz()` aus der Seite, die
Feldlisten aus `produktdaten.py`.

## Prüflauf in frischem Kontext: 14 Blocker, zwei davon aus meinem eigenen Bau

Der Prüfer hat den Stand nicht gebaut und bekam den Auftrag, Fehler zu finden. Ergebnis:
**FREIGABE NEIN** in der ersten Runde. Der Datenabgleich selbst war sauber (alle 42
Produkte, Preis, Bewertung, ASIN und `stock` in beide Richtungen gegen den Beleg
geprüft, 0 Abweichungen; „September 2026" und „30.09.2026" repoweit 0 Treffer). Falsch
war, was daneben lag.

### Die zwei schwersten Blocker waren meine eigenen Korrekturen

**1 · Die Kommentar-Maskierung hat vier Generatoren aus dem Prüfumfang geworfen.**
`maskiere_kommentare()` lief NACH `maskiere_tags()`. Das zerstört Python-String-Literale
(in einem Generator steht reichlich HTML in Strings), `tokenize` scheitert, und mein
Except-Zweig hat die GANZE Datei geblankt. Betroffen: `gen_pages.py`, `gen_hubs.py`,
`gen_bestenliste.py`, `gen_brand_sections.py`, zusammen 124 kB. Der Prüfer hat es mit
einem eingeschleusten Preis in `gen_hubs.py` bewiesen: HEAD meldete ihn, meine Fassung
sagte „0 Abweichungen". **Ein Blindfleck, entstanden beim Schließen eines anderen, und
größer als der, den er schließen sollte.** Behoben: Maskierung zuerst, auf dem Rohtext;
nicht parsebares Python wird jetzt als `NichtLesbar` GEMELDET statt still geblankt.
Nachgemessen gegen HEAD: Deckung bei allen sieben Generatoren innerhalb von zwei Prozent,
Differenz ist genau der Kommentartext.

**2 · `md_to_pdf.py` war durch meine eigene Korrektur kaputt.** Ich hatte den Datenstand
per Regex aus dem QUELLTEXT von verify.py gelesen, mit der Begründung „verify.py ist ein
flaches Skript und würde beim Import alle Gates ausführen". Das stimmte, war aber schon
beim Schreiben falsch: Im selben Schritt war `scripts/datenstand.py` entstanden, ein
Modul ohne Nebenwirkungen, und verify.py führt den Namen seitdem nur noch als Import.
Die Regex hatte danach keinen Treffer, das Skript wäre beim nächsten Aufruf mit
SystemExit gestorben. Gemerkt hätte es niemand: `md_to_pdf.py` braucht `reportlab`, läuft
in keinem Gate und wird nur von Hand aufgerufen. **Wer eine Quelle schafft, liest aus
ihr, nicht aus ihrem ersten Benutzer.**

### Zwölf inhaltliche Blocker: die Prosa war nur teilweise nachgezogen

| Was | Wo | Warum es durchkam |
|---|---|---|
| „für 88 €" dreimal in Meta-Description, og und twitter | Kishi V3 | `preiswelle` kann Attributwerte nicht schreiben, und das Audit erlaubt dort Summen und Differenzen der Seitenprodukte: 124 − 36 = 88 |
| „Günstigster echter Razer-Controller" | Kishi V3 | Superlativ ohne Nachrechnung; der Kishi Ultra kostet 63 € |
| `30 €` im Startseiten-Widget | index.html | Kein Generator schreibt `hv-item`, und „Ult. 2C" steht in keiner Alias-Tabelle |
| sechs falsche Summen, zwei davon im FAQPage-Schema | mobile-gaming-setup | abgeleitete Zahlen, gehören zu keinem Produkt |
| „38 € Aufschlag" (richtig 40) | razer-phone-cooler | dito |
| „8 € günstiger" / „17 € teurer" (richtig 10 / 5) | zwei Vergleiche | dito |
| „über 140 €", „von 30 € bis 190 €", „Zwischen 75 und 90 €" | drei Seiten | Spannen und Untergrenzen |
| „Hall-Effect ab 30 €" auf fünf Seiten | günstigster Hall ist 28 € | das Hall-Gate prüft nur Werte UNTER der Schwelle |
| „80-Euro-Testsieger" an vier Stellen | G8 Galileo kostet 68 € | Wortzusammensetzung, keine Preisform |
| `claim` sagt „Vier Rücktasten", Chip sagt „2 Rücktasten" | products.json | der Datenkern widersprach sich selbst, 26 Prosa-Stellen folgten dem Claim |
| drei CTA-Kästen „✓ Auf Amazon verfügbar" bei `OutOfStock` | hellcool, toaluea, shanwan-metallic | mein neues §A5-Gate las nur Karten, nicht die Kaufleiste |
| drei Sätze, deren Zahl gezogen und deren Wortlaut geblieben ist | X5 Lite „von 38 auf 36 € gestiegen", zwei Schwellen-Sätze | `preiswelle` ersetzt Zahlen, keine Aussagen |

Alle zwölf behoben, dazu acht Befunde zweiter Ordnung (falsche Faktoren, ein „Teurer
als" bei einem günstigeren Produkt, ein Verfügbarkeits-Badge für ein Gerät ohne
Datenquelle, der Kishi Ultra mit 63 € unter „Ab 100 Euro: Premium").

### Sechs neue Gates aus dem Prüflauf

| Gate | Was es verhindert | Proben |
|---|---|---|
| Kaufleiste gegen `stock` | die 33-fache Ausnahme vom Badge-Gate; prüft Text, Klasse UND Anwesenheit | 7 (4 rot, 3 grün) |
| Preis in Attributwerten | „für 88 €" in der Description; Summen und Differenzen zählen dort NICHT | in denselben 7 |
| Badge nur an Karten mit bekanntem `data-product` | ein „Verfügbar" außerhalb jeder Produktkarte | 3 |
| Datenstand-Sweep über ALLE `scripts/*.py`, Kommentare ausgenommen | genau den `md_to_pdf.py`-Fall | 5 |
| BF-Matrix über ALLE `bf-table` | eine zweite, widersprechende Tabelle daneben | 3 |
| Preisband-Überschriften | der Kishi Ultra unter „Ab 100 Euro" | 4 |

Dazu: Die Schema-Verfügbarkeit meldet jetzt auch eine Seite, die sich **keinem** Produkt
zuordnen lässt. Heute führt keine Vergleichsseite ein Product-Schema (gemessen: 0
Knoten), die Lücke war latent.

## Prüflauf Runde 2: acht Blocker, fünf davon aus den Korrekturen von Runde 1

Zweiter Prüfer, frischer Kontext, auf dem korrigierten Stand. Wieder **FREIGABE NEIN**.
Der Befund ist unbequem und lehrreich: **fünf der acht Blocker sind erst durch meine
Korrekturen aus Runde 1 entstanden.**

| Blocker | Wie er entstand |
|---|---|
| „= komplettes Setup für rund 87 €" bei 68 + 7 | Mein Korrektur-Skript brach an einem `assert` ab, NACHDEM es die erste Ersetzung im Speicher angewandt hatte, und schrieb die Datei nie. Die Ersetzung ging lautlos verloren. |
| „X3 Pro kostet inzwischen dasselbe wie der X5 Lite" | Der Satz steht im Generator, nicht in der Seite; mein Edit am HTML wurde beim nächsten Lauf überschrieben. Jetzt rechnet `L.abstand()` den Preisabstand. |
| Scuf Nomad „schwächster Wert im Sortiment" | Meine Umformulierung hat den Geltungsbereich „unter den iPhone-Controllern" gestrichen. 3,9 ist im Sortiment der sechstschwächste Wert, nicht der schwächste. |
| Kishi-Ultra-Karte außerhalb des Grids | Mein Verschieben hat die Karte zwischen `</section>` und die nächste `<h2>` gelegt: 984 px breit statt 316, sichtbar in keinem Band. |
| „Klasse ab 80 €, wie sie unser Testsieger bietet" | Der Testsieger kostet seit dem Abgleich 68 €. Bei der Sammelkorrektur „80 → 68" übersehen. |

Dazu zwei übersehene Stellen (Title/og/twitter auf „ab 30 €", während H1 und headline
„ab 28 €" sagten; eine achte „ab 30 €"-Stelle in `hall-effect-erklaert`) und ein
Gate-Befund, der schwerer wiegt als alle inhaltlichen zusammen:

**Das Fließtext-Gate konnte lautlos ausfallen.** verify ruft `audit_prosa.py` als
Unterprozess und iterierte **nur über stdout**. Bei einem Traceback ist stdout leer, der
Fehler steht auf stderr, und `err()` wurde null Mal aufgerufen: verify meldete 20 andere
Fehler und kein Wort darüber, dass die größte Einzelprüfung nicht stattgefunden hat.
Gemessen mit einem Nicht-String-Slug. Jetzt wird ein leerer stdout bei Exit ≠ 0 selbst
zum Fehler, mit der letzten stderr-Zeile in der Meldung.

### Sieben weitere Gates und ein bewusst NICHT gebautes

| Gate | Was es verhindert | Proben |
|---|---|---|
| Titel-Fassungen nennen dieselben Euro-Beträge | `<title>` sagt 30 €, `<h1>` sagt 28 € | 4 |
| Attributpreise über ALLE Seiten (vorher nur Produktseiten), mit Statistik-Ausnahme | genau den Title-Fall | 5 |
| Kaufleiste: ALLE Instanzen, nicht nur die erste | eine zweite, widersprechende Zeile | in den 6 unten |
| BF-Matrix: `class="bf-table deal"` zählt mit | zweite Tabelle mit Zusatzklasse | 6 |
| Datenstand: Kleinschreibung, ausgeschriebener Tag, auch `.js` | „Preisstand 30.09.2026" | 6 |
| Preisbänder: auch Prosa-Links, nicht nur Karten | Bänder auf der Blog-Geschenkseite | 3 |

**Nicht gebaut: ein Gate für Verfügbarkeitsaussagen im Fließtext.** Dieselben Wörter
stehen harmlos in „PS Remote Play ist nur auf iOS verfügbar" und „prüfe, ob ein
System-Update verfügbar ist"; ein Muster darauf wäre ein Fehlalarm-Generator, und ein
Gate, das wahre Sätze rot macht, wird umgangen. Stattdessen gemessen: über alle 127
Seiten gibt es **0** positive Verfügbarkeitsaussagen über eines der 6 nicht kaufbaren
Produkte. Die Grenze steht als Kommentar im Gate, damit niemand den Fließtext für
gedeckt hält.

### Ein Nebenbefund wurde zur Datenfrage: Hall-Effect

Der Prüfer fand, dass `blog/hall-effect-erklaert` „Fünf der 28 Controller" mit
Hall-Effect nennt, während **zehn Claims** damit werben. Das ist eine §A5-Frage, also am
Listing geklärt: Sechs der sieben strittigen Produkte nennen Hall ausdrücklich im Titel
oder in den Bullets (8BitDo Ultimate Mobile „Hall Effect Joysticks and Hall Triggers",
abxylute S8 „Hall-Sensor Joystick", EasySMX M15 „HALL EFFEKT JOYSTICK & TRIGGER",
GameSir X2s „Gen 2 - Hall-Effekt", HELLCOOL „Präzise Joysticks mit Hall-Effekt",
Mars Gaming MGPXPRO „HALL EFFECT"). Der siebte, der ASUS ROG Tessen, nennt kein Hall und
sein Claim sagt ausdrücklich „Ohne Hall-Sticks" — mein Filter hatte die Verneinung
mitgezählt. Die sechs Specs stehen jetzt im Datenkern, und **das S1-Gate hat die Folge
sofort gemeldet**: „Fünf der 28 Controller" ist jetzt elf, die Preisfrage-Seite rechnet
„11 Modelle" von allein. Der günstigste Hall-Controller bleibt der Ultimate 2C mit 28 €,
also stimmen alle „ab 28 €"-Aussagen weiter.

## Gelernt

1. **Eine Behauptung über die Bauweise ist kein Zustand.** Das Datenstand-Gate sagte seit
   einer Woche „hier wird EINE Zeile geändert", und die Zeile war fünffach. Gemerkt habe
   ich es daran, dass drei Generatoren meine Änderung zurückgeschrieben haben — das Gate
   hat den Rückfall korrekt gemeldet, es prüft auch `scripts/gen_*.py`. Die Lehre ist
   nicht, dass eine Prüfung fehlte, sondern dass ein Kommentar eine Absicht beschrieb und
   als Zustand gelesen wurde.

2. **„Audit vorhanden" ist nicht „gepflegt".** Drei Wertklassen wurden seit dem 30.09.
   geprüft und nie geschrieben: Schema-Preis, Schema-Bewertung und `data-price`. Beim
   Vollabgleich waren 15 bzw. 6 Werte falsch. Ein Audit ohne Schreiber verlagert die
   Arbeit nur, und bei dreistelligen Stückzahlen bleibt sie liegen — genau das hat den
   preis-loop zweieinhalb Monate angehalten. Wer ein Audit baut, baut den Schreiber mit.

3. **Ein Gate, das wahre Sätze rot macht, wird umgangen.** Das Hall-Effect-Gate hat
   „Potentiometer-Sticks (kein Hall-Effect) und eine Haptik, die man für 23 € erwarten
   darf" als „verspricht Hall-Effect ab 23 EUR" gemeldet. Ausgelöst hat es eine
   Preisänderung, aber der Fehlalarm lag vorher im Muster: Es kannte keine Verneinung.
   Fehlalarme sind nicht die harmlose Richtung — sie kosten das Vertrauen ins Gate.

4. **Abgeleitete Zahlen sind die unsichtbarste Preisfolge.** 22 Differenzsätze und eine
   siebenzeilige Deal-Matrix hingen an Preisen, standen aber in keinem Produkt und
   wurden daher von keiner Wertprüfung erfasst. Die Black-Friday-Matrix behauptete
   4 Prozent Rabatt, wo sie 20 versprach, und das stand auf einer Seite, deren erster
   Absatz Transparenz zusichert. Nach jeder Preiswelle gehören Differenzen und Prozente
   nachgerechnet, und zwar maschinell.

5. **Eine Rot/Grün-Probe muss auch den Teil-Ausfall prüfen.** Meine eigene Probe für das
   neue BF-Gate hat gezeigt, dass es bei zerstörtem Markup **eine** lesbare Zeile
   fand, die stimmte, und schwieg. Nicht „findet es den Fehler", sondern „weiß es, wie
   viel es nicht geprüft hat" ist die Frage — dieselbe Klasse wie `unerfasst()` in
   `sync_lesezeit.py` und `spec_paare()` in `produktdaten.py`.

6. **Eine Probe, die ihre Werte selbst führt, prüft nach der nächsten Welle weniger und
   sagt es nicht.** Vier stehende Messreihen waren betroffen (`robustheitsprobe.py` mit
   ihrer Feldliste, `besten_batterie.py`, `links_batterie.py` und `finder_batterie.py`
   mit getippten Preisen, Bewertungen und Spannen), zusammen **12 Fälle ohne Beweiswert**
   — bei unveränderter Schlusszeile, und zweimal am selben Tag (einmal nach der
   Preiswelle, einmal nach den Hall-Specs).
   Das ist dieselbe Klasse, die diese Proben prüfen sollen, einen Stock höher: eine
   zweite, handgepflegte Kopie von Werten, die woanders gepflegt werden. Eine Probe muss
   ihre Erwartung ABLEITEN, und wenn der Anker fehlt, muss sie laut werden statt zu zählen.

7. **Ein Werkzeug, das Prosa nachzieht, darf Kommentare nicht anfassen** — und der Prüfer
   darf sie nicht verlangen. Ein Kommentar beschreibt Vergangenheit; ein nachgezogener
   historischer Wert macht ihn nicht aktuell, sondern falsch. Dass beide Seiten dieselbe
   Maskierung brauchen, ist der dritte Riss dieser Art in diesem Repo (CHIP_REST, das
   Chip-Muster, jetzt der Kommentar): Wo Prüfer und Schreiber verschiedene Sicht auf
   denselben Text haben, korrigiert der eine, was der andere fordert.

8. **Wer einen Blindfleck schließt, baut leicht einen größeren.** Meine
   Kommentar-Maskierung sollte zwei zerstörte historische Kommentare verhindern und hat
   stattdessen vier Generatoren aus dem Prüfumfang geworfen — 124 kB, lautlos, mit
   grünem Audit. Der Auslöser war eine Reihenfolge (Maskieren nach statt vor dem
   Tag-Entfernen) und ein Except-Zweig, der „kann ich nicht lesen" als „ist in Ordnung"
   behandelt hat. **Ein Prüfer, der eine Quelle nicht lesen kann, muss das sagen.**
   Und: Eine Änderung am Prüfer gehört in beide Richtungen gemessen, nicht nur daran, ob
   der eine gemeinte Fall jetzt schweigt.

9. **Wer eine Quelle schafft, liest aus ihr.** Im selben Schritt, in dem
   `scripts/datenstand.py` entstand, habe ich `md_to_pdf.py` den Wert per Regex aus
   verify.py greppen lassen — aus dem ersten Benutzer der neuen Quelle statt aus der
   Quelle. Zwei Zeilen später war verify.py selbst nur noch Importeur, die Regex traf
   nichts mehr, und das Skript war kaputt. Niemand hätte es gemerkt: Es läuft in keinem
   Gate. Dafür gibt es jetzt den Sweep über alle `scripts/*.py`.

10. **Ein Gate, das nur die naheliegende Stelle liest, erzeugt eine Ausnahme in der
    Größe des Bestands.** Mein Verfügbarkeits-Gate las Produktkarten und hat die
    Kaufleiste nicht gesehen: 33 Seiten, drei davon falsch. Beim Schreiben hatte ich
    „alle fünf Renderer" im Kopf und die sechste Stelle nicht gesucht. Die Frage beim
    Bauen eines Gates ist nicht „fängt es den Fall, den ich gerade behebe", sondern
    „wie viele Stellen behaupten dasselbe, und erreiche ich alle".

11. **Der Prüflauf ist kein Ritual.** Er hat 14 Blocker gefunden, zwölf im Inhalt und
    zwei in meinem eigenen Werkzeugbau, und für jeden eine Messung mitgeliefert. Die
    zwei Werkzeug-Blocker hätte kein Gate gefunden, weil beide das Prüfen selbst
    betrafen. Macher ≠ Prüfer ist genau dafür da.

12. **Ein Import verwandelt gemeldete Fehler in Abbrüche.** `audit_prosa.py` lief seit
    jeher als UNTERPROZESS: Ein Traceback darin war ein gemeldeter Fehler mit Exit 1.
    Als verify.py es für die neuen Gates IMPORTIERTE, wurden dieselben Schwachstellen zu
    verify-Abbrüchen — die Robustheitsprobe zeigte **10 Abbrüche** statt 0, an drei
    Stellen in `audit_prosa.py`, die alle älter sind als dieser Lauf (`bySlug[p['slug']]`,
    `preis()` ohne `str()`, `bySlug[s]` ohne Mitgliedschaftstest). Gefunden hat es die
    stehende Messreihe, nicht ich und nicht der Prüfer. **Wer eine Abhängigkeit vom
    Unterprozess in den Prozess holt, erbt ihre Zerbrechlichkeit** — und zwar für alles,
    was hinter der Abbruchstelle steht. Behoben an der Quelle (drei Lesestellen gehärtet)
    UND mit einem Gürtel um den neuen Gate-Block, der einen künftigen Abbruch als Fehler
    meldet statt den Lauf mitzureißen.

13. **Eine Korrektur ist eine Änderung und braucht dieselbe Sorgfalt wie der Bau.**
    Fünf der acht Blocker aus Runde 2 sind erst durch meine Korrekturen aus Runde 1
    entstanden: eine verlorene Ersetzung (Skript brach am `assert` ab und schrieb die
    Datei nie), ein Edit am Generator-Output statt an der Quelle, ein gestrichener
    Geltungsbereich, eine Karte außerhalb ihres Grids, eine Sammelkorrektur mit einer
    übersehenen Stelle. **Unter Zeitdruck korrigiert man schneller, als man misst** —
    und genau dann entstehen die Fehler, die der erste Prüfer nicht mehr sehen kann.
    Konkret: Jede Ersetzung einzeln schreiben (nicht mehrere in einem Skript mit
    `assert` dazwischen), und nach jeder Korrektur fragen, ob die Stelle generiert ist.

14. **Ein Unterprozess, der abstürzt, sagt nichts auf stdout.** verify las nur stdout
    von `audit_prosa.py`. Ein Traceback landet auf stderr, stdout bleibt leer, und die
    Schleife über stdout lief null Mal: Das größte Einzelgate fiel aus, und der Lauf
    meldete es nicht. Das ist dieselbe Klasse wie der Except-Zweig, der eine Datei
    blankt — nur eine Ebene höher. **Ein Gate muss seinen eigenen Ausfall melden
    können, und zwar auf dem Kanal, den der Aufrufer liest.**

15. **Eine Zählung aus `specs` und eine Werbung aus `claim` sind zwei verschiedene
    Aussagen.** „Fünf der 28 Controller führen Hall-Effect" stimmte gegen die Specs und
    stand gegen zehn Claims, die damit werben. Am Listing geprüft: sechs davon sind
    belegt, einer sagt im eigenen Claim „Ohne Hall-Sticks" (meine Filterung hat die
    Verneinung mitgezählt — dieselbe Klasse wie der Fehlalarm im Hall-Gate). Wo zwei
    Felder desselben Datenkerns dasselbe behaupten könnten, gehört geprüft, ob sie es
    tun.

16. **Ein Preis, der steigt, kippt mehr als eine Zahl.** Beim Scuf Nomad (40 € → 75 €)
   waren drei Aussagen betroffen, die bei 40 € stimmten, darunter ein PRO-Punkt
   („günstiger als die meisten iPhone-Controller"), der jetzt das Gegenteil der Wahrheit
   war: 18 von 23 anderen sind günstiger. Bei fallenden Preisen ist eine veraltete Zahl
   peinlich; bei steigenden ist sie eine falsche Kaufempfehlung.
