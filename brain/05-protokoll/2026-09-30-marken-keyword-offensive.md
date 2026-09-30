# 2026-09-30 · Content · Marken-Keyword-Offensive (vier Marken-Hubs)

## Was

Die vier Marken-Hubs (`marken/razer`, `marken/gamesir`, `marken/8bitdo`, `marken/backbone`)
um zwei Sektionen erweitert, die bisher auf keiner Seite bedient wurden:

1. **"Wie gut sind [Marke]-Controller wirklich?"** — Erfahrungs-Intent. Aggregierte,
   belegte Bewertungslage der Marke, ehrliche Einordnung, Vergleichstabelle der vier Marken.
2. **"[Marke] an Android-Handy, iPhone und Tablet"** — Plattform-Intent. Welches Modell
   an welchem Gerät, mit den echten Stolperfallen.

Dazu je zwei zusätzliche FAQs (3 → 5 pro Seite). Umfang: 331–470 → 747–866 Wörter.

Neu im Repo: `scripts/gen_brand_sections.py` (Generator), eine verify-Invariante,
Seiten-CSS für Tabelle und Häkchenliste.

## Warum so

Auslöser ist der Wolf-of-SEO-Befund vom selben Tag
(`03-research/2026-09-30-wolf-of-seo-framework.md`). Dessen "Ziel 3: Brand Ownership"
ist aus Shop-Sicht geschrieben und benennt dabei wörtlich die offenen Flanken, durch
die eine Vergleichsseite wie unsere in Marken-Suchanfragen kommt: erfahrungsbezogene
Keywords ("Vergleichsseiten, die stattdessen andere Produkte empfehlen") und
Angebots-Keywords ("Kauf bei Amazon, auf anderen Plattformen oder Affiliate-Seiten").

Die zugehörige Nachfrage ist in unseren eigenen GSC-Rohdaten belegt, nicht angenommen:
`razer controller` (4 Impr., stärkste Marken-Query), `razer controller android`,
`backbone android`, `backbone pro controller`, `gamesir vs backbone` /
`backbone vs gamesir` / `is gamesir better than backbone?` (dieselbe Frage dreimal),
`8bitdo controller`, `gamesir controller`. Dazu trägt `/marken/razer/` mit 11 Impr./28T
die viertstärkste Seite der Domain.

Bewusst **keine** neuen Seiten gebaut, sondern die bestehenden verbreitert. Grund ist
das Cluster-Prinzip aus derselben Quelle (eine Seite rankt für 200–500 Keywords) und
§B1: Für "gamesir vs backbone" existiert bereits `blog/gamesir-oder-backbone`, eine
zweite Seite auf dasselbe Keyword hätte kannibalisiert. Stattdessen verlinken beide
betroffenen Marken-Hubs jetzt dorthin und stärken den Cluster.

Zur Reihenfolge: Ich hatte empfohlen, erst Lauf 8 abzuwarten, damit der Ausbau vom
29.09. sauber messbar bleibt. Yasin hat anders entschieden. Das Argument trägt hier
ohnehin weniger, als ich zunächst annahm: Der 29.09.-Stand ist einen Tag alt und von
Google noch nicht bewertet, die beiden Ausbauten wirken also faktisch als eine
Intervention statt als zwei vermischte Messungen.

## Wie

**Generator statt Handarbeit (§A1).** Die Sektionen tragen Preise, Sterne und
Bewertungszahlen im Fließtext. Von Hand geschrieben wäre das genau die Divergenz, die
§A1 verbietet: Der nächste preis-loop ändert products.json, der Fließtext bliebe alt.
Deshalb kommt jede Zahl über ein `Lookup`-Objekt aus products.json.

**Drei Schutzmechanismen**, alle rot/grün bewiesen:

1. **Idempotenz.** Der erzeugte Block steht zwischen Markern (`BRAND-EXT`, `BRAND-FAQ`,
   `BRAND-CSS`) und wird bei jedem Lauf ersetzt. Erster Entwurf hängte pro Lauf eine
   Leerzeile an (gefunden per Hash-Vergleich über mehrere Läufe), behoben; drei
   aufeinanderfolgende Läufe liefern jetzt byteidentische Dateien.
2. **Drift-Gate im Generator.** Jeder Euro-Betrag, Sternewert und jede Bewertungszahl
   im erzeugten Text muss aus products.json ableitbar sein, sonst bricht das Skript ab.
   Produktnamen mit Ziffern (Kishi V3, FunCooler 6) und Gerätebezeichnungen
   (iPhone 12, iOS 13) werden vorher herausgefiltert. Rot-Test: eine erfundene
   Prozentzahl in den Text geschmuggelt → Abbruch mit Nennung der Zahl.
3. **verify-Invariante (§A1).** `verify.py` ruft `gen_brand_sections.py --check` auf
   und wird rot, sobald die Hubs nicht mehr deckungsgleich mit products.json sind.
   Rot-Test: einen Preis in products.json geändert → verify rot mit Fix-Hinweis;
   nach Rückbau grün. Damit kann der nächste preis-loop die Hubs nicht stillschweigend
   veralten lassen.

**Was die Faktenkontrolle abgefangen hat.** Vier Behauptungen in meinen eigenen
Entwürfen hielten der Prüfung gegen products.json nicht stand:

| Behauptung im Entwurf | Realität | Korrektur |
|---|---|---|
| Razer hat "die kleinste Bewertungsbasis in unserem Sortiment" | HELLCOOL (100), ASUS (125), Scuf (157), VITURE (241), Trust (322) liegen unter Razer (361) | Geltungsbereich präzisiert: "der vier Marken, die wir mit eigenem Hub führen" |
| GameSir hat "die größte Spannweite aller vier Hersteller" | GameSir 0,4 = Razer 0,4, Gleichstand | Superlativ gestrichen, Werte genannt |
| "Für ältere iPhones gibt es von Razer kein passendes Modell" | Aussage über Razers Gesamtsortiment, die wir nicht belegen können | "führen wir kein Razer-Modell" |
| Backbone ist "die teuerste Marke bei uns" | Backbone hat das teuerste Gerät (190 €), aber Razer den höheren Einstieg (93 € vs 59 €) | Beides sauber getrennt benannt |

Zusätzlich fiel beim Parsen auf, dass ein Regex ohne Tausenderpunkt den X5 Lite
(1.655 Bewertungen) verschluckte und GameSirs Markenschnitt dadurch falsch war.
Behoben vor dem ersten Schreibvorgang.

**§A6 eingehalten.** Jede Marke bekommt ihre echte Schwäche: Razer die dünne
Bewertungsbasis und den Phone Cooler (3,2 Sterne, ausdrückliche Gegenempfehlung),
GameSir die Streuung zwischen 3,8 und 4,2 sowie die belegten Schwächen von X2s und
X3 Pro, 8BitDo die fehlende Halterung und die schmale Zwei-Produkt-Basis, Backbone das
Abo-Modell und die 51-Bewertungen-Zahl, die für ein Urteil zu klein ist.

**Meta-Freeze eingehalten**, maschinell belegt: 0 geänderte Zeilen mit title,
description, og/twitter oder canonical auf allen vier Seiten; die Meta-Blöcke von
`marken/8bitdo` und `marken/gamesir` (beide Impressions-Träger) sind byteidentisch zu HEAD.

## Der zweite Durchgang: was der unabhängige Faktencheck gefunden hat

Der Prüflauf in frischem Kontext hat **zwölf** Befunde geliefert, sechs davon
nachweislich falsch. Ich habe jeden einzeln gegen die Quellen nachvollzogen, alle
trafen zu. Das ist der eigentliche Ertrag dieses Arbeitspakets, deshalb steht es hier
vollständig.

| # | Was ich behauptet hatte | Was unsere eigenen Seiten sagen |
|---|---|---|
| 1 | "Tablet: nur der Kishi Ultra" | V3- und V3-Pro-Review führen iPad Mini in der Kompatibilitätsliste, `blog/controller-fuer-tablet` sagt es ebenfalls, dort sogar im Schema |
| 2 | "Beide 8BitDo-Modelle sind Bluetooth-Gamepads", "iPhone: beide, unabhängig vom Baujahr" | Die Ultimate-2C-Review: "Wired", "kabelgebunden (1000 Hz Polling)", "Kein iOS-Support". Ultimate-Mobile-Seite: "kein iPhone-Fokus" |
| 3 | "Der Ultimate Mobile bringt eine Handyklemme mit" | Unbelegt, und im selben Absatz stand das Gegenteil ("fehlende Halterung") |
| 4 | Backbone hat "die ungleichmäßigste Verteilung" | Backbone hat die kleinste Sterne-Spanne der vier (0,3) und die kleinste Standardabweichung (0,125) |
| 5 | G8 Plus unter "USB-C direkt am Handy", X2s als einziges Bluetooth-Modell | products.json: G8 Plus ist `BT+USB-C`, die Seite selbst wirbt mit Switch- und Kabellos-Betrieb |
| 6 | "Der X2s verbindet sich nicht mit jedem Handy zuverlässig" | Frei erfunden. Unsere Review nennt Verarbeitung und Griffgröße, nicht die Verbindung. §A5-Verstoß |

Dazu sechs Ungenauigkeiten: X3 Pro fehlte in der GameSir-Plattformliste komplett
(obwohl er das einzige Modell ohne iOS ist), X5 Lite kann laut eigener Review ebenfalls
iPad mini, der Backbone Pro läuft auch kabellos, die Android-14-Mindestversion des
Kishi V3 fehlte, und die Kausalität "USB-C gut, Bluetooth schlecht" trug nicht, weil
der zweitschwächste GameSir gar kein Bluetooth hat.

**Die Ursache, und sie ist wichtiger als die einzelnen Fehler:** Ich habe products.json
als Quelle für Sachaussagen benutzt. §A1 macht sie aber nur zur Wahrheit für
Produktdaten, also Preise, Specs und ASINs. Für Kompatibilität, Bauform und
Nutzererfahrung steht die Wahrheit in unseren eigenen Review-Seiten, und die hatte ich
nicht gelesen. Das Drift-Gate half hier nicht: Es prüft Zahlen, keine Sachaussagen.

**Nicht behebbar ohne Beleg:** Bei drei Produkten widersprechen sich products.json und
die Review-Seiten (Details in der Befund-Tabelle in STATUS.md, neu aufgenommen). Der
gravierendste Fall ist der 8BitDo Ultimate 2C: dieselbe ASIN B0D72WYT8Z, aber
products.json nennt ihn "Wireless" mit Bluetooth und iOS, die Review-Seite "Wired" ohne
iOS, und die Review-Seite widerspricht sich zusätzlich selbst, weil ihr Schema und ihre
Alt-Texte wieder "Wireless" sagen. Nach §A5 darf ich das nicht raten. Die betroffenen
Sektionen behaupten zu diesen Punkten deshalb bewusst nichts und verweisen auf die
Produktseiten. Yasins Screenshots klären es.

**Zwei Bestandsfehler mitgenommen**, beide vom Prüfer außerhalb des Auftrags gefunden:
Die Razer-Bestands-FAQ sprach vom "doppelt so teuren V3 Pro" (tatsächlich 93 zu 149 Euro,
also 60 Prozent), und `produkte/8bitdo-ultimate-mobile` stand auf 4,3 Sternen bei 506
Bewertungen, während products.json 4,4 bei 517 sagt. Beides lief auch in die
strukturierten Daten. Neun Stellen nachgezogen.

## Der dritte Durchgang: warum die Korrektur selbst zum Problem wurde

Die Nachprüfung des korrigierten Stands fiel durch: **nicht deploybar**. Acht der zwölf
Befunde waren behoben, aber meine Korrekturen hatten drei neue Fehler und drei
Widersprüche **innerhalb einzelner Seiten** erzeugt, die es vorher nicht gab.

| | Was passiert war |
|---|---|
| Razer | Der EXT-Block sagte jetzt "alle drei führen das iPad mini", die Bestands-FAQ zwölf Zeilen darunter weiter "Nur der Kishi Ultra ... V3 und V3 Pro sind für Smartphones ausgelegt" |
| Razer | Der EXT-Block nannte Android 14 als Mindestversion, die neue FAQ sagte weiter "praktisch jedes Android-Handy" |
| 8BitDo | Die Plattform-Sektion hatte "Bluetooth" zurückgezogen, Erfahrungstext und beide FAQs behaupteten es weiter |
| N1 | "G8 Plus ist das einzige Modell, das sich auch kabellos nutzen lässt" — der X2s ist ebenfalls kabellos, und das stand zwei Listenpunkte tiefer auf derselben Seite |
| N2 | Neu eingeführt: "PC, Switch und Fernseher" für 8BitDo, obwohl unsere Ultimate-2C-Review "nicht Switch" sagt |
| N3 | "X3 Pro hat weder Bluetooth noch iOS" — korrekt laut Review, aber der iPhone-Hub führt ihn wegen `worksOn: ios` als iPhone-Controller |

**Der eigentliche Fehler dahinter:** Ich hatte nur meine eigenen Marker-Blöcke korrigiert
und den Bestandstext derselben Seite nicht gegengelesen. Weil der Generator das
FAQPage-Schema aus dem sichtbaren HTML rendert, zog er die falschen Bestandsantworten
aktiv in die strukturierten Daten. Der Prüfer hat das präzise benannt: schlechter als
der Ausgangszustand, wo die Aussage wenigstens einheitlich falsch war.

Behoben in acht Schritten, davon zwei am Bestandstext außerhalb der Marker (Razer-FAQ
Tablet an zwei Stellen inklusive Schema, 8BitDo "klassische Bluetooth-Gamepads"). Die
iOS-Frage beim X3 Pro wird jetzt wie beim Ultimate 2C behandelt: nicht kategorisch
beantwortet, sondern an die Produktseite verwiesen, solange der Datenkern strittig ist.

## Der vierte Durchgang: eine Regression, die die Lehre bestätigt hat

Auch Runde 3 fiel durch, mit sechs Punkten. Fünf waren Feinheiten, einer war eine
**Regression**: Der Fix "doppelt so teure V3 Pro" aus Runde 2 war wieder verschwunden.

Ursache: Um die Razer-Tablet-FAQ sauber neu zu setzen, hatte ich
`git checkout marken/razer/index.html` gemacht und damit die vorherige Handkorrektur an
derselben Datei überschrieben. Der Prüfer hatte in Runde 2 genau davor gewarnt, dass
Handkorrekturen an Bestands-FAQ verlierbar sind, weil der Generator sie zwar ins Schema
rendert, aber nicht selbst erzeugt. Die Warnung hat sich in derselben Sitzung realisiert.

Weitere Funde dieser Runde:

- Meine Eigenkontrolle hatte auf "weder Bluetooth noch iOS" gegrept, im Text stand aber
  die Variante mit "iPhone". Ein Suchmuster, das die eigene Formulierung nicht trifft,
  beweist nichts.
- Zwei 8BitDo-Bestands-FAQ behaupteten weiter, was der Block bewusst zurückgezogen hatte
  ("Beide Modelle koppeln per Bluetooth, das iPhone erkennt sie als MFi-fähige Gamepads"
  und "läuft an Android, PC und Switch", letzteres von unserer eigenen 2C-Review mit
  "nicht Switch" widerlegt).
- "der einzige GameSir mit aktivem Lüfter": Unsere X3-Pro-Review nennt siebenmal Peltier
  und kein einziges Mal einen Lüfter. products.json unterscheidet die Techniken sogar
  ausdrücklich ("Peltier + Lüfter" bei anderen Produkten). Korrigiert auf
  "eingebaute Peltier-Kühlung".

**Konsequenz, und das ist der bleibende Teil:** Der Prüfer hat vorgeschlagen, die
korrigierten Formulierungen maschinell abzusichern, statt sich auf Handarbeit zu
verlassen. Umgesetzt als **Abschnitt 7 in verify.py**: sieben widerlegte Formulierungen,
je Datei geprüft, jede mit ihrer Begründung im Fehlertext. Rot/grün bewiesen durch
Nachstellen genau dieser Regression. Keine dieser Aussagen kann mehr unbemerkt
zurückkehren, auch nicht durch ein `git checkout`.

## Der fünfte Durchgang: Freigabe

Runde 4 hat freigegeben. Die sechs Punkte aus Runde 3 sind bestätigt behoben, keine
neuen Fehler, ein verbleibender Widerspruch, der kein Blocker ist: Die 8BitDo-Produktkarte
trägt aus dem products.json-`claim` weiterhin "für Android, PC & Switch", während die
korrigierte FAQ 61 Zeilen tiefer "Android und Windows-PC" sagt. Das ist die sichtbare
Kante desselben Datenkern-Konflikts. Vor der Korrektur war die Seite in sich stimmig und
gegen die eigene Review falsch, jetzt folgt die FAQ der belastbareren Quelle. Der
Switch-Text steht nicht im Schema, also kein Rich-Results-Risiko. Switch ist als dritter
Aspekt in den Ultimate-2C-Befund aufgenommen.

**Vier Nachschärfungen an der neuen Invariante**, alle vor dem Commit umgesetzt, weil
eine Sperre, die legitime Arbeit blockiert, irgendwann entnervt entfernt wird:

| Problem | Lösung |
|---|---|
| `"Nur der Kishi Ultra"` hätte die wahre Aussage "Nur der Kishi Ultra bietet Passthrough-Laden" blockiert | enger gefasst auf `"V3 und V3 Pro sind für Smartphones ausgelegt"` |
| `"Bluetooth-Gamepads"` hätte die legitime Tablet-Empfehlung blockiert, die auf `controller/tablet/` zweimal zu Recht steht | enger gefasst auf `"Modelle sind Bluetooth-Gamepads"` plus die Bestandsvariante |
| `"4,3 Sterne"` fixierte gegen eine bewegliche Wahrheit: Fällt der Wert bei Amazon und der preis-loop zieht korrekt nach, wäre der richtige Stand rot | ersetzt durch einen Vergleich HTML gegen den aktuellen products.json-Wert |
| Nur `"weder Bluetooth noch iPhone"` war gesperrt, nicht die iOS-Variante — genau das Paar, das in Runde 3 eine halbe Korrektur durchrutschen ließ | beide aufgenommen |

Drei Belege danach: Rating-Drift wird datengetrieben rot, die iOS-Variante wird rot
(sogar doppelt, über Abschnitt 6 und 7), und die legitime "Bluetooth-Gamepads"-Empfehlung
auf `controller/tablet/` löst keinen Fehlalarm aus.

## Verify

- `python3 scripts/verify.py` grün: 125 Seiten, 247 JSON-LD-Blöcke, 42 Produkte, 0 Fehler
- Idempotenz: drei Läufe → identische Hashes, `--check` meldet "keine"
- Drift-Gate rot/grün bewiesen (erfundene Zahl → Abbruch)
- verify-Invariante rot/grün bewiesen (Preisänderung in products.json → rot)
- FAQ/Schema-Gleichstand per Assertion: 5 sichtbare `<details>` = 5 Question-Objekte
- Optisch geprüft im lokalen Server (Desktop + 375px): Tabelle korrekt gestylt, aktuelle
  Marke hervorgehoben, Häkchenliste, Absatzabstände. Mobil kein horizontales Seiten-
  Scrollen (`scrollWidth == clientWidth == 375`), die 508px breite Tabelle scrollt
  innerhalb ihres Wrappers.
- Unabhängiger Faktencheck in frischem Kontext (Macher ≠ Prüfer)
- sitemap.xml: lastmod der vier Seiten auf 2026-09-30

## Gelernt

1. **products.json ist die Wahrheit für Produktdaten, nicht für Sachaussagen.**
   Das ist die teuerste Lehre dieses Pakets: Sechs falsche Aussagen entstanden, weil ich
   Kompatibilität und Bauform aus `worksOn` und `specs` abgeleitet habe, statt die
   eigenen Review-Seiten zu lesen. Wer über ein Produkt schreibt, liest vorher, was wir
   selbst schon darüber geschrieben haben. Neue Pflicht in P-11.

2. **Ein Generator, der Fließtext mit Datenzahlen erzeugt, braucht ein Drift-Gate.**
   Sonst ist er nur eine schnellere Art, §A1 zu verletzen. Das Muster (erlaubte
   Zahlenmenge aus der Datenquelle bilden, Text dagegen prüfen, Namen und
   Gerätebezeichnungen vorher filtern) ist auf jeden künftigen Textgenerator übertragbar.
   Grenze des Gates: Es prüft Zahlen, keine Sachaussagen. Für die bleibt der
   unabhängige Prüflauf unverzichtbar.

3. **Der Prüflauf in frischem Kontext hat sich bezahlt gemacht.** Ich hatte vor der
   Prüfung vier eigene Fehler gefunden und den Stand für sauber gehalten. Der Prüfer fand
   zwölf weitere, sechs davon nachweislich falsch, zwei davon in strukturierten Daten.
   Ohne ihn wäre das live gegangen. "Macher ≠ Prüfer" ist keine Formalie.

4. **Superlative sind die fehleranfälligste Satzform.** Drei der vier selbst gefundenen
   und zwei der geprüften Fehler waren Superlative oder Vergleiche, und am 29.09. war es
   derselbe Fehlertyp. Die Fehlerquelle ist nicht die Zahl, sondern der unausgesprochene
   Geltungsbereich: "in unserem Sortiment" kann vier Marken oder 42 Produkte meinen.
   Jeder Superlativ braucht seinen Geltungsbereich im Satz.

5. **Ein Widerspruch im Datenkern wird nicht durch Raten gelöst.** Beim 8BitDo
   Ultimate 2C wäre jede Formulierung eine Behauptung ohne Beleg gewesen. Die Aussage
   wegzulassen und den Befund zu dokumentieren kostet ein paar Sätze Substanz und ist
   die einzige Variante, die §A5 standhält. Wichtig dabei: Die Zurückhaltung muss auf
   ALLEN Stellen einer Seite dieselbe sein, sonst entsteht genau der Widerspruch, den
   man vermeiden wollte.

6. **Eine Korrektur, die nur im Text steht, ist nicht gesichert.** Die "doppelt so
   teure"-Regression entstand durch ein `git checkout` auf eine Datei, in der eine
   Handkorrektur lag. Korrekturen an Bestandstext, den ein Generator anfasst, gehören
   in ein maschinelles Gate, nicht in die Erinnerung. Umgesetzt als Abschnitt 7 in
   verify.py.

7. **Eine Eigenkontrolle, die das eigene Suchmuster nicht trifft, beweist nichts.**
   Ich hatte auf "weder Bluetooth noch iOS" gegrept und für sauber erklärt, im Text
   stand "weder Bluetooth noch iPhone". Suchmuster gegen den tatsächlichen Wortlaut
   prüfen, nicht gegen die Erinnerung daran.

3. **Idempotenz muss man testen, nicht annehmen.** Der Marker-Ansatz sah korrekt aus
   und hängte trotzdem pro Lauf eine Leerzeile an. Nur der Hash-Vergleich über mehrere
   Läufe hat das gezeigt.

4. **Neue CSS-Klassen im generierten HTML müssen gegen style.css geprüft werden.**
   `cmp-table`, `table-wrap` und `check-list` existierten nicht und wären als
   ungestyltes HTML live gegangen. verify.py fängt das nicht. Die Vergleichsseiten
   lösen es über einen Seiten-`<style>`-Block, dieses Muster ist jetzt übernommen.

## Rückfluss

- Neues Muster für `02-patterns/`: **P-11 Daten-Fließtext-Pattern** (Generator + Drift-Gate
  + verify-Invariante für jeden Text, der Zahlen aus products.json in Prosa trägt).
- Constitution §A6 ergänzen: Superlative nur mit explizitem Geltungsbereich im Satz.
