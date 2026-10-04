# 2026-10-04 · Content · B6: Bestenlisten als Seitentyp, mit nachrechenbarer Reihenfolge

## Was

Maßnahme B6 der Bücher-Synthese (Quelle: Sheridan, *They Ask You Answer*). Die vier
Bestenlisten der Site kommen ab jetzt aus einem Generator.

**Der Befund, der den Umbau erzwungen hat.** Gemessen am 04.10.2026 an
`/controller/beste/` und den drei `/vergleich/beste-*/`:

| Was | Gemessen |
|---|---|
| Sortier-Regel | Genau eine Seite nannte eine, und die lautete "Preis, Sticks, **Ergonomie** und Kompatibilität". **"Ergonomie" kommt in products.json unter keinem Spec-Schlüssel vor, bei keinem der 42 Produkte.** Die drei `/vergleich/`-Seiten nannten gar keine Regel. |
| Sichtbare Bewertungen | **0** auf allen vier Seiten. Seiten, deren Zweck eine Rangfolge ist, zeigten die Zahl nicht, an der man sie misst. |
| ItemList-Schema | Drei der vier Seiten hatten keins, obwohl ihre Titel "Top 5" und "Top-Auswahl" versprechen. Die vierte führte 3 von 10 Positionen. |
| Spec-Chips ohne Datengrundlage | **14** (siehe unten) |
| Herkunft | Alle vier handgeschrieben. Damit waren sie die **siebte Renderstelle für Produktdaten und die einzige ungegatete**; sechs andere sind am 30.09. geschlossen worden. |

Das Gegenbeispiel stand auf der Seite selbst: Platz 5 der Gesamtliste war mit
**4,6 Sternen aus 2.188 Bewertungen zu 30 €** in jeder messbaren Hinsicht besser als
Platz 1 (4,2 aus 706, 80 €) — und der Leser konnte das nirgends sehen.

## Wie

`scripts/gen_bestenliste.py` besitzt den Ranking-Abschnitt aller vier Seiten
(Marker-Block, zwei ausdrückliche Fälle statt remove-then-insert, weil der Block sein
eigenes Gitter enthält). Redaktioneller Input je Position sind **zwei Angaben**:
Reihenfolge und Badge. Alles andere kommt aus products.json: Name, Claim, Preis,
Bewertung, Specs, Bild, Detail-Link.

Neu auf den Seiten:

- **Eine Regel, deren Begriffe es gibt.** "Sortiert nach Plattform-Reichweite,
  Stick-Technik, Verbindung und Preis, nicht nach der Sternzahl." Die Begründung rechnet
  sich selbst aus: "Von den 27 Modellen, aus denen diese Liste gewählt ist, liegen alle
  zwischen 3,8 und 4,6 Sternen, allein 7 davon teilen sich 4,2." (Grundmenge sind die
  WÄHLBAREN, also die über der §A6-Schwelle — die erste Fassung rechnete über alle 28
  und nannte damit ein 3,5-Modell, das die eigene Schwelle nie zulässt.)
- **Eine Faktenzeile je Platz:** Bewertung mit Anzahl, Plattformen, Stick-Technik,
  kabelgebunden. Damit ist die Reihenfolge überhaupt erst widerlegbar.
- **Der Abschnitt, der gegen die eigene Liste spricht**, vollständig abgeleitet: wer in
  der Grundmenge die beste Bewertung hat, wo er steht, was er kostet, und was in seinen
  DATEN gegen Platz 1 spricht. Erfunden wird nichts: "kabelgebunden" steht wörtlich in
  `Verb.`, die fehlende Plattform in `worksOn`.
- **ItemList vollständig und in der sichtbaren Reihenfolge**, auf allen vier Seiten.

Dazu `bewertung()`, `sterne_text()` und `anzahl_text()` in `produktdaten.py`: Dasselbe
`Bew.`-Muster stand an drei Stellen einzeln.

## Warum so

**Die Reihenfolge wurde NICHT umgerechnet, und das ist eine Entscheidung mit Begründung.**
Nach Sternen allein lässt sich diese Liste nicht ordnen: 27 der 28 Controller liegen
zwischen 3,8 und 4,6, allein sieben teilen sich 4,2. Eine Rangfolge aus Zehntelsternen
wäre Scheingenauigkeit. Zusätzlich gemessen: Der heutige Spitzenplatz der Gesamtliste
liegt nach geglätteter Bewertung auf **Platz 12 von 28**, und sieben Controller, die auf
keiner Liste stehen, liegen nach Sternen über mindestens drei gelisteten.

Daraus folgt nicht "umranken". Es folgt: **Die Reihenfolge ist ein redaktionelles Urteil,
und dann muss sie als solches erkennbar sein.** Das Urteil hat gute Gründe (der 4,6er ist
kabelgebunden und läuft nicht am iPhone), sie standen nur nirgends. Ob tatsächlich
umgerankt wird, ist eine redaktionelle und kommerzielle Entscheidung und steht als Punkt
für Yasin in STATUS, nicht im Generator.

**Die 14 ungedeckten Spec-Chips wandern NICHT nach products.json.** Jeder von ihnen steht
auch auf der Review-Seite des Produkts, mehrere zusätzlich im `claim` desselben Produkts
(backbone-pro: "hält 40 Stunden durch"; x2s und ultimate-mobile: "Driftfreie
Hall-Sticks"). Die Behauptungen sind seitenweit konsistent, nur fehlen sie im Datenkern.
Sie dort einzutragen hieße, eine unbelegte Produktaussage in die Quelle der Wahrheit zu
waschen, und §A5 verbietet genau das. Der Generator rendert deshalb nur Belegtes; die
Chips fallen weg, und die Liste steht als Punkt für Yasin.

## Verify

- **Zehn Gates, jedes exit 0:** verify.py · audit_prosa.py · sync_product_values --audit ·
  sync_footer --check · sync_lesezeit --check · sync_kompat --check · css_kaskade ·
  gen_preisfrage --check · gen_brand_sections --check · **gen_bestenliste --check** (neu)
- **`scripts/besten_batterie.py`: 36 Fälle, 24 müssen rot werden, 12 müssen grün bleiben,
  0 falsch, 0 nicht gegriffen.** Jeder Fall bekommt eine frische Kopie. Die legitimen
  Fälle sind die wichtigeren: eine redaktionell getauschte Reihenfolge, ein umbenanntes
  Badge und eine entfernte Position MIT nachgezogener Top-N-Zusage müssen nach einem
  Generatorlauf grün sein, sonst verteidigt das Gate den Stand gegen Korrektur. (Hier
  stand "eine entfernte Position" ohne den Zusatz — und genau dieser Fall war der Defekt,
  den die Batterie zertifiziert hat, siehe B31-7.)
- Generator idempotent und baumstabil (Lauf 2 und 3 ändern nichts; `--check` exit 0)
- Browser (Sichtprüfung, kein Gate): Desktop und 375 px; kein Horizontal-Scroll
  maschinell über `document.documentElement.scrollWidth` geprüft, der Rest ist Augenschein
- Em-Dash-Delta der vier Seiten: **−1** (keine neue)
- Umfang am SICHTBAREN `<main>`-Text (ohne JSON-LD, ohne `<script>`): **1.196 → 1.947 Wörter**.
  Die drei `/vergleich/`-Seiten waren mit 123 bis 190 Wörtern Thin Pages und liegen
  jetzt bei 299 bis 373. Meine erste Fassung nannte 1.783 → 2.821 und 242–308: Das war
  die ganze Datei inklusive JSON-LD mit naivem `split()`, also rund 45 Prozent zu hoch,
  und ein Teil des Wachstums wäre das neue ItemList-Schema gewesen. `verify.py`
  streicht `<script>`-Inhalt in `_klartext()` aus genau diesem Grund.

## Gelernt

**P-14 · Begründete-Rangfolge-Pattern**, acht Pflicht-Mechanismen (sechs beim Bau, zwei aus den Prüfläufen). Dazu drei Lehren aus
dem Bau selbst, alle drei von den eigenen Gates gefunden:

1. **Ein Block, der seinen eigenen Anker enthält, ist beim zweiten Lauf nicht mehr
   auffindbar.** Meine erste Fassung folgte dem Haus-Muster "erst entfernen, dann
   einsetzen" (`sync_kompat.py`) — aber dort steht der Anker AUSSERHALB des Blocks. Hier
   enthält der Block das Karten-Gitter, das der Anker ist. Zwei ausdrückliche Fälle
   (erster Lauf ersetzt die Handfassung, jeder weitere den eigenen Block) statt eines
   Musters, das anderswo passt.
2. **Was zwischen Anker und Block steht, darf nicht mitgelöscht werden, nur weil es
   strukturell aussieht.** Um den "Ergonomie"-Satz mit zu übernehmen, rutschte der
   Blockanfang über alles, was aus Leerraum und `div`-Tags besteht — und verschluckte das
   `</div>`, das `sec-head` schließt. Gefunden von der HTML-Prüfung in verify.py ("lässt 1
   `<div>` offen").
3. **Eine Probe, die das Falsche trifft, sieht aus wie eine bestandene Probe.** Mein
   Batterie-Fall "ItemList-Positionen nicht aufsteigend" ersetzte das erste
   `"position": 2` der Datei und traf damit die BreadcrumbList, nicht die ItemList — und
   blieb grün. Die Lücke war nicht der Fall, sondern das fehlende Gate: Die
   Positionsfolge war nur INNERHALB des BESTEN-Blocks geprüft, also auf vier von 127
   Seiten. Jetzt prüft verify.py jede ItemList und jede BreadcrumbList jeder Seite
   (gemessen beim Einbau: 124 Listen-Schemas, 0 kaputt). Der Fall steht jetzt zweimal da,
   einmal je Schema-Art.

Dazu eine vierte, kleinere: **ein Etikett ist auch dann eine Behauptung, wenn JavaScript
es überschreibt.** Meine erste Fassung schrieb pauschal "Zum Test" auf jeden
Detail-Button; genau ein Produkt der 23 Positionen hat aber ein `/produkte/`-Datenblatt
statt eines Tests, und die Handfassung hatte dort richtig "Zum Kurzcheck". Dass `main.js`
jeden Button zur Laufzeit in "Mehr erfahren" umbenennt, ändert daran nichts: Ohne JS ist
das Etikett die ausgelieferte Wahrheit, und §A2 ist genau der Fall, der ohne JS gilt.

## Offen für Yasin

1. **14 Spec-Chips ohne Beleg im Datenkern** (braucht Screenshots, §A5). Sie standen auf
   den Bestenlisten und stehen weiterhin auf den jeweiligen Review-Seiten:
   `Gew. 135 g` (x5-lite) · `Extra 4 Rücktasten` (kishi-v3) · `Sticks TMR+Haptik` und
   `Extra Haptik` (kishi-v3-pro) · `Sticks Hall-Effect` (x2s) · `Sticks Hall-Effect`
   (ultimate-mobile) · `Fokus Shooter` (rog-tessen) · `Akku 40 h` (backbone-pro).
   Mehrere davon bestätigt products.json im `claim`-Feld desselben Produkts, führt sie
   aber nicht in `specs` — der Datenkern widerspricht sich also selbst.
2. **Soll umgerankt werden?** Der sitewide "Testsieger" (GameSir G8 Galileo) ist nach
   geglätteter Bewertung Platz 12 von 28. Die Entscheidung ist redaktionell und
   kommerziell, der Generator macht sie in einer Zeile mit.
3. **Sieben der 17 nicht gelisteten Controller liegen nach Sternen über mindestens
   drei der 11 gelisteten.** Die Schwelle gehört dazu, sonst bedeutet die Zahl nichts:
   über mindestens zwei sind es 14, über mindestens vier noch 3. Es sind abxylute-s8 (4,3/273), abxylute-m4-snapon (4,3/417), marsgaming-mgpxpro (4,3/16), trust-gxt-rgb (4,2/355), shanwan-teleskop-black und shanwan-metallic (je 4,2/826) und marsgaming-mgp-bt2 (4,2/40).
   (Hier stand erst "fünf" — mit einem Produkt, das laut eigenem Klammerzusatz auf der
   Budget-Liste steht — dann "vier", beide ohne Schwelle und damit nicht nachrechenbar.)

## Nachtrag: Prüflauf zu B6 (Runde 31), acht Blocker

Der Prüfbericht in frischem Kontext hat jede Zahl auf den vier Seiten bestätigt (23
Positionen, eigene Parser, 0 Befunde an Preis, Sterne, Anzahl, Plattformen, Specs,
Links) und trotzdem acht Blocker gebracht. Sieben davon in meinem eigenen Bau.

**B31-1 · Ein Superlativ, den die eigene Seite zwei Karten höher widerlegt.** Auf der
iPhone-Liste teilen sich Razer Kishi V3 (4,4 aus 153) und Backbone Pro (4,4 aus 459) die
beste Bewertung. Mein `ehrlichtext()` brach den Gleichstand still über die
Bewertungsanzahl (`max(..., key=(sterne, anzahl))`) und schrieb "hat nicht Platz 1,
sondern Backbone Pro mit 4,4" — während Kishi V3 auf derselben Seite als #3 mit sichtbaren
"4,4 Sterne aus 153 Bewertungen" steht. Genau die Klasse, für die die Superlativ-Regel in
§A6 geschrieben wurde. Jetzt wird die Spitzenmenge gebildet und bei Gleichstand anders
formuliert. **Mein erster Fix war wieder falsch**: Er sammelte die Namen vorn und die
Bewertungszahlen hinten ("A und B kommen beide auf 4,4 (459, 153)"), und der
§A1-Fließtext-Gate meldete sofort "Razer Kishi V3: 459 statt 153 Bewertungen". Die
Meldung war richtig. Jetzt steht jede Zahl bei ihrem Produkt.

**B31-2 · Zwei Schreiber für dieselbe Stelle, und kein Zustand, in dem beide grün sind.**
Ich rendere den Preis als `{preis_zahl(p)} €`, `sync_product_values.py` setzt dort den
Rohstring aus products.json. Bei einem Preis mit "ca." (7 der 42) machte jeder Lauf den
jeweils anderen rot. Heute steht kein solcher Preis auf einer Liste, der Patt war latent
— und erreichbar über genau den Schritt, den mein eigener Text unter "Offen für Yasin"
vorschlägt (ein Mars-Gaming-Modell aufnehmen). Jetzt Rohstring, ein Schreiber.

**B31-3 · `None €` auf der Seite, alle vier B6-Gates grün.** Dieselbe Zeile: Ein Preis,
den `preis_zahl()` nicht lesen kann, wurde zu "None €", und `--check` blieb grün, weil der
Generator mit seinem eigenen Fehler konsistent war. **Ein Generator, der seine Ausgabe
gegen sich selbst prüft, adelt seinen Müll zur Soll-Vorgabe.**

**B31-4 · Traceback statt Meldung, mitten im Schreiben.** `Bew.` als "4.2 (706)" (Punkt
statt Komma) macht `bewertung()` zu `(None, None)`, und `sterne_text(None)` stirbt mit
TypeError — nachdem zwei der vier Seiten schon neu geschrieben waren. Jetzt wird geprüft,
und bei Befunden für eine Datei wird sie gar nicht geschrieben.

**B31-5 · Der Pflicht-Mechanismus, um den das Paket gebaut ist, war nicht gegatet.** Eine
Position ohne lesbare `Bew.` rutschte still durch: Die Faktenzeile ließ die Sterne weg,
P-14 Mechanismus 3 ("Jede Position zeigt ihre Zahlen") war verletzt, kein B6-Gate sagte
etwas.

**B31-6 · Überschriften-Sprung h1 → h3, von mir eingeführt.** Ich hatte `<h3>` fest
verdrahtet; in HEAD trugen die drei `/vergleich/`-Seiten `<h2>` und haben keine andere h2.
Jetzt steht die Ebene je Liste in `LISTEN` — und weil das seitenweit gilt und nirgends
geprüft war, prüft verify.py die Hierarchie jetzt auf allen Seiten (gemessen: 127 Seiten,
0 Sprünge).

**B31-7 · Die eigene Batterie hat einen Defekt zertifiziert.** Fall `'LEGITIM eine
Position entfernt, neu generiert'` mit Erwartung GRÜN: Danach standen viermal "Top 10"
über neun Karten, alle Gates grün. Die Batterie bewies das Loch nicht nur nicht, sie hat
es abgesegnet. Der Fall steht jetzt auf ROT, und "Top N" wird gegen die Kartenzahl
geprüft — dieselbe Gate-Klasse gibt es für den Finder längst.

**B31-8 · Drei falsche Zahlen in meiner eigenen Doku:** "21 Positionen" (es sind 23,
und dieselben Dateien sagen an anderer Stelle 23) · "Fünf Produkte stehen auf keiner
Bestenliste", wobei der eigene Klammerzusatz beim ersten sagt, dass es auf der
Budget-Liste steht (es sind vier) · "das Repo hat neun Gates", während dieselbe Datei zwei
Absätze höher "zehn" sagt.

Dazu übernommen: `.besten-ehrlich` hatte keine CSS-Regel · `A6_SCHWELLE` wäre die vierte
Kopie geworden (liegt jetzt in `produktdaten.py`, verify.py und der Generator importieren,
finder.js wird dagegen geprüft) · der Regelsatz nannte eine Grundmenge inklusive des
3,5-Modells, das die eigene Schwelle nie zulässt (jetzt 27 Modelle, 3,8 bis 4,6) · zwei
Fehlalarm-Risiken in meinen neuen Gates (nackte Zeichenkette "Sortiert nach"; eine
`ItemListUnordered` ohne `position` wäre rot geworden) · ein Batterie-Fall, der nur das
öffnende `<article>`-Tag entfernte statt der Karte · die Wortzahlen (siehe oben) · eine
Docstring-Begründung für ein `str()`, das im Code nicht steht.

**Als benannte Grenze stehen geblieben** (im Modul-Docstring, mit gemessener Zahl):
Badge-Text ist freier redaktioneller Text und ungegatet · `menge` und `menge_dativ` sind
nicht aneinander gebunden · das Positions-Gate erfasst keine tief verschachtelten
ItemLists (gemessen: 124 Schemas, 0 verschachtelt).

**Zwei Lehren, beide über Proben statt über Code:**

1. **Ein Fall, der aus dem falschen Grund rot wird, beweist nichts.** Drei meiner neuen
   Batterie-Fälle mutieren products.json — und dort wird `gen_brand_sections --check`
   zuerst rot. Der Lauf sah bestanden aus, über meine neuen B6-Gates sagte er nichts. Es
   gibt jetzt die Erwartung `ROT_B6`: Der B6-Generator muss den Befund SELBST nennen.
   Dieselbe Klasse für `ROT_NACH_GENERATOR` beim Überschriften-Sprung: erst regenerieren,
   dann muss verify rot sein, sonst prüft man nur die Abweichung von der Generator-Ausgabe.
2. **Ein Generator, der gegen seine eigene Ausgabe prüft, prüft nichts.** `--check`
   vergleicht Datei und Neubau. Jeder Fehler, der in beiden steckt, ist unsichtbar
   ("None €"). Deshalb braucht jeder Generator Befunde über die DATEN, nicht nur den
   Vergleich mit sich selbst.

## Nachtrag: Nachprüfung der Nachbesserungen (Runde 32), vier Blocker

Fünf der acht Nachbesserungen hat der zweite Prüflauf als geschlossen bestätigt (Preis als
Rohstring inklusive "ca."-Produkt in beiden Lauf-Reihenfolgen · Befunde statt "None €" ·
Abbruchschutz über 22 Datenmutationen ohne einen Traceback · Überschriften-Gate in beide
Richtungen · `A6_SCHWELLE` an einer Stelle). Vier waren offen, und drei davon lagen in
Code, der schon beim ersten Versuch falsch war.

**B32-1 · Der Gleichstands-Fix war für genau zwei geschrieben, verzweigt aber für mehr
als einen.** `len(spitze) > 1`, und im Text standen "teilen sich zwei", "beide", "der
beiden" als Literale. Bei drei gleichauf ergab das "A und B und C kommen beide auf 4,4" —
bei grünem Gate-Set, erreichbar durch ein einziges Screenshot-Update. Die Zahlwörter, das
Verb und das Pronomen werden jetzt aus `len(spitze)` gerechnet, die Aufzählung nach
PLATZ sortiert statt nach Bewertungsanzahl. Nachgemessen mit einem erzeugten
Dreier-Gleichstand: "Die beste Bewertung teilen sich drei: … kommen alle drei auf 4,4".

**B32-2 · Mein Top-N-Gate hätte den nächsten geplanten Schritt blockiert.** Es las jedes
"Top N" der ganzen Datei als Zusage — also auch einen Querverweis auf die Schwesterseite,
deren echter Titel "Beste Android Controller Top 5" lautet. Der nächste content-loop-Punkt
ist B7, *interne Verlinkung systematisch*. Ein Gate, das die nächste Korrektur rot macht,
hat die falsche Regel (P-13 Mechanismus 6). Gescannt werden jetzt nur `<title>`,
`og:title`, `twitter:title` und Überschriftentext mit gestrippten `<a>`.

**Und die Batterie behauptete eine Probe, die es nicht gab.** Mein Kommentar sagte, der
grüne Gegenfall zum Top-N-Gate stehe "zwei Fälle weiter unten" — dort standen zwei
ROT-Fälle. Es gab keinen einzigen grünen Fall für das jüngste Gate, die
Zwei-Richtungs-Regel war für genau dieses Gate nicht erfüllt. **Eine Probe, die in einem
Kommentar existiert, ist keine Probe.**

**B32-3 · Das "Sortiert nach"-Gate hatte Loch UND Fehlalarm aus derselben Zeile, zum
zweiten Mal.** Ich hatte am Wort "und" verankert. Der alte Handsatz mit Komma-Aufzählung
derselben vier Kriterien ("Preis, Sticks, Ergonomie, Kompatibilität.") kam damit durch —
also genau der Befund, der B6 erzwungen hat — und ein beliebiger Satz mit "und" wurde
wieder rot. Verankert ist jetzt das KRITERIEN-Vokabular.

**B32-4 · Sieben weitere Zahlen in der Doku falsch**, überwiegend weil die Batterie von 24
auf 29 und dann auf 36 Fälle gewachsen ist und die Zahl an drei Stellen stand. Dazu zwei
inhaltliche: Der Protokolltext zitierte den Regelsatz noch in der Fassung "28 Modelle, 3,5
bis 4,6", die zwei Abschnitte weiter als korrigiert beschrieben ist; und die Aussage "vier
Produkte stehen auf keiner Bestenliste, liegen aber über mehreren" war **auch als Vier
nicht ableitbar**. Gemessen über die 28 Controller und die 11 gelisteten: über mindestens
zwei liegen 14, über mindestens drei sieben, über mindestens vier drei. Eine Zahl ohne
Schwelle bedeutet hier nichts, und meine Liste ließ bei gleicher Sternzahl Produkte mit
mehr Bewertungen weg. Jetzt steht die Schwelle im Satz.

**Lehre:** *Eine Zahl, die aus einer Rangfolge abgeleitet wird, braucht ihre Schwelle im
Satz.* "Liegt über mehreren" ist kein Kriterium. Das ist die §A6-Superlativ-Regel
("jeder Superlativ nennt seinen Geltungsbereich") einen Schritt weiter: Auch ein
Vergleich ohne Superlativ braucht seinen Bezugsrahmen, sobald er zählt.

**Als benannte Grenze stehen geblieben** (Hinweise des Prüfers, gemessen und nicht
geschlossen): Das Top-N-Gate greift auf drei der vier Seiten, weil
`/vergleich/beste-budget-controller/` an keiner Zusagestelle eine Zahl nennt — dort trägt
allein der `topn`-Befund im Generator · das Überschriften-Gate meldet je Seite nur den
ERSTEN Sprung und sieht eine Seite nicht, die ohne h1 beginnt · `ordnung` und `menge` sind
nicht aneinander gebunden (nimmt man einem gelisteten Produkt die Plattform, bleibt es auf
der Liste; verify.py wird rot, aber über andere Gates).
