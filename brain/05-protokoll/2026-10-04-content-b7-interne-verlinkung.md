# 2026-10-04 · Content · B7: Interne Verlinkung, systematisch statt punktuell

## Was

Maßnahme B7 der Bücher-Synthese (Quelle: Brem, On-Page-SEO). Gemessen wurde zuerst, nicht
gebaut: der **Inhaltslink-Graph**, also Links innerhalb von `<main>` ohne Breadcrumb,
Navigation und Footer. Die stehen auf jeder Seite gleich und tragen deshalb kein
thematisches Signal; wer sie mitzählt, misst, dass jede Seite mit jeder verbunden ist.

**Der Befund war nicht "zu wenig Links", sondern "nur in eine Richtung".** 777
Inhaltslinks über 109 Inhaltsseiten:

| | gemessen |
|---|---|
| Marken-Hubs → ihre Produkte | **4 von 4 Hubs lückenlos**, 0 fehlen |
| Produkte → ihr Marken-Hub | **0 von 14.** Alle 14 Produkte der vier Marken verlinkten nicht zurück |
| Die fünf Plattform-Hubs → ihre Controller | lückenlos, 0 fehlen |
| Controller → irgendein Plattform-Hub | **13 von 28: keiner** |
| Blog-Artikel, eingehend | Median **3**, Minimum 1 (Reviews: Median 18) |
| Longtail-Datenblätter | 7 hingen an **genau einem** Link, **3 an gar keinem** |

Die drei Waisen (`ipega-pg-9023`, `ipega-pg-9083s`, `mocute-050`) hatten je **eine**
Quelle, und die war in beiden Fällen eine **noindex-Weiterleitung** (`/marken/ipega/`,
`/marken/mocute/`). Entstanden ist das beim Zurückbauen dieser zwei Marken-Hubs zu Stubs:
Die Seiten verloren ihren einzigen echten Link. Das Waisen-Gate hat nichts gemerkt, weil
es Links von Stub-Seiten mitzählte — **ein Link von einer Seite, die "indexiere mich
nicht, geh woanders hin" sagt, trägt kein Crawl-Signal.**

## Wie

Drei Stücke, alle abgeleitet:

1. **`scripts/hublinks.py`** — die Regel: *Jede Produktseite verlinkt zurück auf jede
   Taxonomie-Seite, die sie listet.* Die Zuordnung wird **nicht gepflegt**, sondern aus dem
   bestehenden Linkgraph gelesen: Wer ein Produkt in seinen **Produktkarten** führt (nicht:
   wer es irgendwo im Fließtext erwähnt), ist für dieses Produkt eine Übersicht. Damit gibt es keine zweite Wahrheit, die veralten könnte. Auch
   die Beschriftung ist abgeleitet — aus der `<h1>` der Zielseite.
   Taxonomie heißt: die fünf Plattform-Hubs, `/marken/*/` und `/zubehoer/*/`. **Nicht**
   dazu gehören Bestenlisten, die Geschenke-Seite und die Startseite: Das ist redaktionelle
   Auswahl, nicht die Kategorie, in der ein Produkt lebt. Mit ihnen hätte jede Produktseite
   acht Rückverweise und keiner sagte mehr etwas.
2. **Zwei Wege, eine Quelle**, wie bei B1: `gen_pages.py` rendert den Block für die 29
   generierten `/produkte/`-Seiten, `scripts/sync_hublinks.py` setzt ihn in die 13
   handgepflegten Reviews. Beide rufen dieselbe Funktion.
3. **Die 10 Longtail-Datenblätter** bekommen einen abgeleiteten Abschnitt auf `/produkte/`
   ("Ältere und Nischenmodelle", aus `longtail.json`). `/produkte/` ist die vollständige
   Sortimentsübersicht und damit der Ort, an den Altmodelle gehören.

## Warum so

Die Regel erfindet keine Zuordnung, sie **liest die vorhandene**. Eine neue Marke, ein
neuer Plattform-Hub oder ein umsortiertes Produkt wirken beim nächsten Lauf von allein —
es gibt keine Tabelle, die man vergessen kann. Das war die Lehre aus B6: Jede getippte
Liste ist die nächste, die veraltet.

Und sie ist **leise**: ein Satz am Ende des Inhalts, keine Überschrift, kein zweiter
Kaufaufruf. Das ist Navigation, nicht Inhalt, und B3 (ein Handlungsaufruf pro Seite) gilt
weiter.

## Verify

- **Elf Gates, jedes exit 0** (neu: `sync_hublinks.py --check` als elftes)
- **Neues Gate §B7 am ausgelieferten Stand:** Jede Produktseite muss auf jede Übersicht
  zurückverlinken, die sie führt. Geprüft wird die EIGENSCHAFT, nicht der Lauf eines
  Generators — den Block setzen zwei verschiedene Wege, und ein Gate, das nur einen kennt,
  deckt die Hälfte nicht ab.
- **Waisen-Gate korrigiert:** Links von noindex-Seiten und Weiterleitungen zählen nicht
  mehr als eingehende Links. Beim Einbau sofort rot auf den drei Waisen.
- **`scripts/links_batterie.py`: 14 Fälle (9 müssen rot werden, 5 müssen grün bleiben),
  0 falsch, 0 nicht gegriffen.**
- Browser: Block in der Inhaltsspalte (676 bzw. 652 von 1024 px), mobil 335 von 375 px,
  kein Horizontal-Scroll; Longtail-Liste mit 10 Einträgen
- Wirkung, gemessen gegen HEAD: Inhaltslinks **777 → 869**, Seiten ohne eingehenden
  Inhaltslink **9 → 6** (die sechs übrigen sind Rechts- und Index-Seiten aus der
  Navigation), `/produkte/`-Seiten ohne eingehenden Link **3 → 0**, Produkte ohne Rückweg
  zum Marken-Hub **14 → 0** (Produkte der vier Marken MIT eigenem Hub), Controller ohne Plattform-Hub-Link **13 → 0** von 28

## Gelernt

1. **Ein Link von einer noindex-Weiterleitung ist kein Link.** Das Waisen-Gate zählte
   jede Quelle gleich und hat deshalb drei faktisch verwaiste Seiten durchgewunken. Wer
   eingehende Links zählt, muss die QUELLE ansehen, nicht nur die Kante.
2. **Nav und Footer gehören nicht in die Messung.** Sie stehen auf jeder Seite; wer sie
   mitzählt, bekommt einen Graph, in dem alles mit allem verbunden ist, und sieht die
   Einseitigkeit nicht, um die es geht.
3. **Eine Zuordnung, die man ableiten kann, pflegt man nicht.** Welcher Hub welches
   Produkt führt, steht schon im HTML. Eine zweite Liste daneben wäre die nächste, die
   veraltet.
4. **HTML korrekt heißt nicht Layout korrekt.** Meine erste Fassung setzte den Block
   direkt vor `<aside` — und damit als dritte Zelle in ein zweispaltiges CSS-Grid. Im
   Browser stand er oben rechts in der Seitenleiste neben dem Kurz-Urteil. **Alle Gates
   waren grün**, Linkziele und Markup die ganze Zeit korrekt; gefunden hat es nur der
   Blick in den Browser. Jetzt wird der Einfügepunkt gezählt (rückwärts über Leerraum und
   HTML-Kommentare bis zum `</div>`, das die Inhaltsspalte schließt), nicht geraten.
5. **Nicht jede Datenänderung ist ein Refactoring.** Mein Batterie-Fall "Produkt wechselt
   die Plattform-Zugehörigkeit" sollte grün bleiben und wurde rot — an der handgepflegten
   Kachelzahl der Startseite (§A5 rechnet sie gegen `worksOn`) und an den Marken-Hub-Texten.
   Nach dem Lauf **aller zwölf Generatoren** blieb der Stand rot, und zwar zu Recht: In
   diesem Repo ist ein `worksOn`-Wechsel nie eine reine Umsortierung, sondern immer auch
   eine Textaufgabe. Der Fall ist deshalb aus der Batterie heraus und steht als Befund in
   ihrem Docstring — ein grüner Fall, der an einem unbeteiligten Nachbarn rot wird, prüft
   nicht das, wofür er geschrieben ist.

## Offen

- **Blog-Artikel bleiben der am schwächsten verlinkte Seitentyp** (Median 3 eingehend
  gegen 18 bei Reviews), und das sind laut STATUS die Seiten, über die der GSC-Traffic
  kommt. B7 hat die Taxonomie-Richtung geschlossen, nicht die thematische: Welcher Artikel
  welchen anderen sinnvoll verlinkt, ist eine redaktionelle Frage und keine ableitbare.
  Gehört in einen eigenen Durchgang.
- Sechs Seiten haben weiter null eingehende Inhaltslinks: `/datenschutz/`, `/impressum/`,
  `/ueber-uns/`, `/marken/`, `/vergleich/`, `/zubehoer/`. Die ersten drei sind
  Rechtsseiten, die letzten drei Index-Seiten; alle sechs hängen in der globalen
  Navigation. Kein Handlungsbedarf, aber nachgemessen und benannt.

## Nachtrag: Prüflauf zu B7 (Runde 33), sechs Blocker

Der Bericht hat die Regel unabhängig nachgerechnet (eigener `html.parser`-Graph, 0
Befunde über alle 42 Produkte), Layout und Idempotenz bestätigt, alle Zahlen bis auf eine
reproduziert — und trotzdem sechs Blocker gefunden. Der schwerste hat vier falsche Sätze
live stehen gehabt.

**B33-1 · Die Regel im Code war nicht die Regel in der Doku, und das hat vier falsche
Aussagen ausgeliefert.** Mein Docstring sagte *"wer ein Produkt in seinen KARTEN führt"*,
der Code las **jeden** Link in `<main>` — also auch redaktionelle Vergleichssätze. Live
stand damit unter anderem auf der Black-Shark-**Kühler**-Seite: *"Dieses Modell steht auch
in dieser Übersicht: Razer Controller 2026"*, und das war ihr **einziger** Hub-Link.
Quelle: ein Satz auf dem Razer-Hub, der den Black Shark als Alternative zum Razer-Kühler
empfiehlt. Dazu ein Backbone-Produkt im 8BitDo-Hub, ein GameSir-Produkt im Razer-Hub und
ein Teleskop-Controller im Mini-Gamepad-Hub. Das ist das Gegenteil des B7-Ziels: ein
falsches thematisches Signal mit falschem Ankertext.

**Und die zu weite Regel hat einen echten Defekt verdeckt.** Auf
`/zubehoer/handy-kuehler/` zeigten **zwei von drei** Produktkarten mit "Mehr erfahren" auf
den Hub selbst statt auf die Produktseite. Die beiden Kühler hingen damit an keinem
Kategorie-Hub — meine Messung meldete trotzdem "jedes der 42 Produkte hängt an mindestens
einer Übersicht", weil sie den Prosa-Link mitzählte. **Eine zu großzügige Zuordnung findet
keine Lücken, sie füllt sie mit Falschem.** Die zwei Karten zeigen jetzt auf ihre
Produktseiten, und ein neues Gate macht jeden solchen Selbstlink rot (nur für Karten mit
`data-product`; eine Karte ohne, wie das ROG Phone 9 Pro auf `/gaming-phones/`, hat kein
bekanntes Ziel und bleibt ein redaktioneller Befund).

**B33-2 · "29 → 0" war für keine Population nachrechenbar.** Die 29 galt für *alle 42
Produkte gegen nur drei* der fünf Plattform-Hubs, die 0 nur für *Controller*. Zubehör kann
per Konstruktion keinen Plattform-Hub haben. Richtig und unter einer Methode gemessen:
**13 der 28 Controller → 0**. Dazu sagte mein eigener Docstring "die drei Plattform-Hubs",
während `PLATTFORM_HUBS` zwei Zeilen tiefer fünf führt.

**B33-3 · `ist_stub()` war ein Substring über die ganze Datei.** `'noindex' in text` — ein
Hub, dessen Prosa das Wort erwähnt, galt als Weiterleitung, und alle seine Produkte
verloren ihre Übersicht. Der vom Gate vorgeschlagene Fix hätte es **schlimmer** gemacht:
Der Rückweg-Block wäre auf sieben Produktseiten gelöscht worden und der Lauf wäre rot
geblieben. Ein Gate, aus dem es keinen Ausweg gibt außer dem Zurücknehmen eines korrekten
Satzes, hat die falsche Regel. Jetzt wird das Meta-Tag im `<head>` geprüft. Und die
zweite Kopie derselben Regel in `verify.py` ist weg — sie importiert jetzt, wie P-15
Mechanismus 1 es verlangt.

**B33-4 · `einfuegepunkt()` zählte `<aside` im Rohtext**, also auch in Kommentaren — und
der Kommentar zwei Zeilen darüber erklärt, dass rückwärts ÜBER Kommentare gelaufen wird.
Ein Kommentar, der das Wort erwähnt, machte die Prüfung rot, mit einer Meldung, die in die
falsche Richtung zeigte. Jetzt wird auf kommentarfreiem Text und auf Element-Starts
gezählt, und die Meldung nennt die echte Ursache.

**B33-5 · Doppeltes Escaping, still grün.** Ohne `html.unescape()` vor dem Escapen wäre
aus `&amp;` im `<h1>` ein sichtbares `&amp;amp;` geworden — auf fünf Seiten, bei grünem
Lauf. Dass es heute gut aussah, war Zufall: Die Tablet-Seite schreibt ein nacktes `&`.

**B33-6 · Hub ohne `<h1>`, still grün.** Die Beschriftung wich auf die URL aus, und dann
stand `<a href="/zubehoer/trigger/">/zubehoer/trigger/</a>` als Satzbaustein auf sieben
Produktseiten. Jetzt ist eine fehlende h1 auf einer Taxonomie-Seite ein harter Befund.

Dazu übernommen: Query-Strings machten einen Link unsichtbar (`href="/x/?from=hub"` fiel
aus der Zuordnung, das Produkt verlor die Übersicht) · die Mess-Vorschrift nennt jetzt
die Entduplizierung (je Quelle-Ziel-Paar einmal) · `gen_brand_sections.py --check` lief
ganz **ohne** Timeout und drei weitere Gate-Aufrufe ohne `try` (ein Hänger hätte verify.py
unbegrenzt blockiert bzw. mit Traceback beendet) · die Proben kopierten pro Fall 593 MB
`SPC-Gaming-Visuals/` mit, jetzt ausgeschlossen.

**Batterie von 14 auf 20 Fälle** (11 rot, 9 grün). Drei meiner sechs neuen Fälle waren
beim ersten Versuch selbst falsch gebaut: einer mutierte einen generatorbesessenen Hub und
wurde am falschen Gate rot, einer traf die Attributreihenfolge im Markup nicht, und einer
prüfte die Beschriftung auf einer Seite, die den betreffenden Hub gar nicht führt.

**Lehre:** *Wenn der Code großzügiger ist als die Doku, ist nicht die Doku ungenau.* Mein
Docstring beschrieb die richtige Regel, der Code eine weitere — und die Differenz war
nicht Toleranz, sondern vier falsche Sätze plus ein verdeckter Defekt.
