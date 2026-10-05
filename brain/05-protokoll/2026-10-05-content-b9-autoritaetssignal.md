# 2026-10-05 · Content · B9: Das Autoritätssignal stand da und wurde gelöscht

## Was

Maßnahme B9 der Bücher-Synthese (Quelle: Cialdini, Autorität am Entscheidungspunkt). Die
Aufgabenbeschreibung in LOOP-STATE nannte als Ausgangslage *„bisher nur im Header: 100+
Controller getestet"* — **diese Behauptung existiert nirgends auf der Site**, weder im
Header noch sonstwo. Die Site sagt heute „42 Modelle im Sortiment, 13 davon ausführlich
getestet", und das stimmt (gemessen: 42 Produkte, 13 mit eigener Testseite).

**Gemessen am 05.10.2026 über alle 200 Produktkarten der Site:**

| Karte zeigt auf | Beschriftung | n | Bewertung |
|---|---|---|---|
| eigenen Test | „Mehr erfahren" | **66** | Signal verschenkt |
| Datenblatt | „Mehr erfahren" | **95** | nichtssagend |
| Datenblatt | **„Zum Test"** | **2** | **schlicht falsch** |
| eigener Test | „Zum Test" | 35 | richtig |
| Datenblatt | „Zum Kurzcheck" | 2 | richtig |

Und darüber hinaus: **`main.js` benannte jeden Detail-Knopf zur Laufzeit in „Mehr erfahren"
um** (Zeile 230–233, Kommentar: *„for consistency"*). Für jeden Leser **mit** JavaScript gab
es die Unterscheidung auf **2 von 200** Karten: Die Regel traf `/zum test|details/i`
und löschte 35 der 37 richtigen Beschriftungen, die zwei „Zum Kurzcheck" überlebten
sie. Ohne JavaScript war sie auf 37 von 200 da.

Das Autoritätssignal war damit nicht abwesend, sondern vorhanden und wurde aktiv gelöscht.

## Wie

**Eine Regel, in `produktdaten.detail_label()`:** Ziel unter `/produkte/` → „Zum
Kurzcheck", sonst → „Zum Test". Abgeleitet aus dem Ziel, nie getippt.

- `gen_hubs.py` und `gen_bestenliste.py` importieren sie (letzteres hatte seit B6 eine
  eigene Fassung — die ist jetzt weg).
- Die **drei JS-Renderer** (`hub-render.js`, `produkte.js`, `finder.js`) führen sie
  zwangsläufig ein zweites Mal — der Browser kann kein Python importieren. verify.py prüft
  die JS-Fassungen **gegen** die Python-Fassung, so wie bei `A6_SCHWELLE`.
- **`main.js` benennt nicht mehr um.** Die drei Zeilen sind raus.
- Die handgepflegten Seiten zieht `sync_product_values.sync_detail_label()` nach: vom
  HEAD-Stand aus, nach dem Lauf der drei Generatoren, sind das **10 Dateien mit 45
  Beschriftungen** — angefasst wird nur der Linktext, nie
  das Ziel.

**Ergebnis:** 101 Karten sagen „Zum Test", 99 „Zum Kurzcheck", **0 Abweichungen** zwischen
Beschriftung und Ziel. Im Browser nachgemessen (mit laufendem JavaScript): auf
`/controller/ios/` 10× „Zum Test", 14× „Zum Kurzcheck".

## Warum so

Die Alternative wäre ein eigenes Badge auf der Karte gewesen („Von uns getestet"). Das
hätte **fünf** Renderer gleichzeitig anfassen müssen und wäre genau die Sorte
Mehrfach-Markup, die dieses Repo laufend einfängt. Die Beschriftung des Knopfs trägt
dieselbe Information, steht schon in jeder Karte und musste nur aufhören, falsch zu sein.

Die 95 Karten, die von „Mehr erfahren" auf „Zum Kurzcheck" wechseln, sind eine sichtbare
Copy-Änderung. Sie ist gewollt: „Mehr erfahren" sagt nichts, „Zum Kurzcheck" sagt, was den
Leser erwartet — und schafft erst den Kontrast, der „Zum Test" zum Signal macht.

## Verify

- **Elf Gates, jedes exit 0**
- **Vier neue Gates:**
  1. §B9: Jeder `.btn-detail` auf ein Produkt trägt die aus dem Ziel abgeleitete
     Beschriftung (HTML-Kommentare ausgenommen)
  2. §B9: Die drei JS-Fassungen stimmen mit der Python-Regel überein — Konstanten **und**
     Ableitung aus dem Ziel, und die Funktion muss im Karten-Markup auch **benutzt**
     werden (nicht nur vorhanden sein)
  3. §B9/§A2: `main.js` darf die Beschriftung nicht zur Laufzeit überschreiben
  4. §A5: Die Prosa-Zahl „13 davon ausführlich getestet" wird gegen die Zahl der
     Testseiten gerechnet
- **`scripts/links_batterie.py` von 35 auf 44 Fälle** (28 müssen rot werden, 16 müssen grün
  bleiben), 0 falsch, 0 nicht gegriffen
- `node`-Gegenprobe: alle drei JS-Renderer liefern für dieselben Ziele dieselben Labels wie
  die Python-Regel

## Gelernt

1. **Ein Signal kann vorhanden sein und trotzdem nicht ankommen.** 37 Karten trugen die
   richtige Beschriftung im HTML — und `main.js` überschrieb sie bei jedem Seitenaufruf.
   Wer nur das ausgelieferte HTML misst, sieht das nicht; wer nur den Browser ansieht,
   sieht nicht, dass es im HTML richtig stand.
2. **„for consistency" ist eine Begründung, die man nachrechnen muss.** Der Kommentar in
   `main.js` nannte Einheitlichkeit als Grund. Einheitlich war das Ergebnis tatsächlich:
   einheitlich nichtssagend.
3. **Die Aufgabenbeschreibung war selbst veraltet.** LOOP-STATE nannte ein Zitat („100+
   Controller getestet"), das es nicht gibt. Eine Maßnahme fängt deshalb mit der Messung
   an, nicht mit ihrer eigenen Beschreibung.
4. **Ein Gate, das die Erwähnung prüft, prüft nicht die Verwendung.** Meine erste Fassung
   verlangte nur, dass `detailLabel` in der JS-Datei vorkommt. Die Funktion stehen zu
   lassen und die Beschriftung daneben fest zu verdrahten blieb still grün — also genau
   der Zustand, den B9 beseitigt hat. Gefunden hat das meine eigene Gegenprobe.

## Offen für Yasin

- **Die zwei falschen „Zum Test" standen auf `/zubehoer/handy-kuehler/`** — derselben
  Seite, deren Selbstlinks ich in B7 repariert habe. Damals habe ich die Ziele korrigiert
  und die Beschriftung stehen lassen; davor zeigte „Zum Test" auf den Hub selbst, war also
  schon falsch. Jetzt beides stimmig.
- **Eine Karte trägt weiter „Details"**: das ROG Phone 9 Pro auf `/gaming-phones/`. Es ist
  kein Produkt aus products.json und hat keine Detailseite — der Knopf zeigt auf die eigene
  Seite. Das steht seit B7 als redaktionelle Frage offen.

## Nachtrag: Prüflauf zu B9 (Runde 35), zwei Blocker

Der Bericht hat den ausgelieferten Inhalt unabhängig nachgerechnet (eigener
`html.parser`-Nachrechner, 201 `.btn-detail`-Anker, 101 „Zum Test" / 99 „Zum Kurzcheck" /
1 „Details", **0 Abweichungen** außer der bekannten ROG-Karte) und auch die Ausgangslage
Zahl für Zahl gegen HEAD bestätigt (66 / 95 / 2 / 35 / 2). Blockiert wurde an zwei
Stellen im mitgelieferten Code.

**B35-1 · Drei neue globale `const` machten die JS-Renderer gegenseitig ausschließend.**
Ich hatte den B9-Block **vor** die IIFE gesetzt, während alles andere in diesen Dateien
innerhalb von `(function(){ 'use strict'; … })()` liegt. Zwei dieser Skripte im selben
globalen Scope ergeben `SyntaxError: Identifier 'LABEL_TEST' has already been declared` —
und dann läuft das zweite Skript **gar nicht**, nicht nur seine Deklaration: Hydrierung,
Filter, Sortierung fielen still aus. Heute lädt keine Seite zwei davon, es war also keine
Live-Störung, aber eine Mine, die es vor B9 nicht gab und die kein Gate sieht. Der Block
steht jetzt in allen drei Dateien innerhalb der IIFE; mit node gegengeprüft, dass alle
drei im selben Scope ladbar sind.

**B35-2 · Das `main.js`-Gate prüfte eine Schreibweise, nicht die Eigenschafts-Klasse.**
`detailLink.textContent =` wörtlich gesucht — `innerHTML`, `innerText` und ein anderer
Variablenname blieben still grün, obwohl sie dasselbe tun. Das ist **die eigene Lehre
dieses Pakets eine Ebene tiefer** („ein Gate, das die Erwähnung prüft, prüft nicht die
Verwendung"), und `innerHTML` ist genau die Variante, die jemand beim nächsten „for
consistency" tippt. Der Variablenname wird jetzt aus dem `.btn-detail`-Query **abgeleitet**
statt geraten, und geprüft wird die Klasse
(`textContent|innerText|innerHTML|outerHTML|replaceChildren|insertAdjacentHTML|append`).
Alle vier Formen rot, der legitime Fall (`amazonLink.textContent`) grün.

**Dazu zwei blinde Flecken und zwei falsche Zahlen, alle übernommen:**

- **404.html fiel aus dem Gate.** Mein Filter übersprang jede Seite mit `noindex` im Head —
  und 404.html trägt `noindex, follow`, steht aber ausdrücklich in `pages`, mit genau der
  umgekehrten Begründung („sonst wäre sie die einzige ausgelieferte HTML-Datei ohne
  Gate"). Übersprungen wird jetzt nur noch, was eine Weiterleitung ist.
- **Dasselbe Anker-Muster stand zweimal zeichengleich** in `verify.py` und
  `sync_product_values.py` — der Anti-Pattern, den `sync_product_values.py` selbst benennt
  („Getrennte Muster sind am 30.09. zweimal auseinandergelaufen"). Es liegt jetzt als
  `BTN_DETAIL` samt `btn_ziel_text()` und `PRODUKT_PRAEFIXE` in `produktdaten.py`.
- **„Die 37, die stimmten" war falsch.** Die alte `main.js`-Regel traf `/zum test|details/i`
  und löschte damit **35** der 37 richtigen Beschriftungen; die zwei „Zum Kurzcheck"
  überlebten sie. Mit JavaScript war die Unterscheidung also auf **2 von 200** Karten da,
  nicht auf keiner.
- **„Neun Seiten, 42 Labels" war die falsche Messung.** Das war gezählt, nachdem `gen_hubs`
  schon einen Teil erledigt hatte. Die Reichweite der Sync-Funktion ist vom HEAD-Stand aus,
  nach dem Lauf der drei Generatoren: **10 Dateien, 45 Beschriftungen.**

**Batterie von 44 auf 49 Fälle** (31 rot, 18 grün).

**Lehre:** *Code, der in eine Datei eingefügt wird, erbt deren Scope-Regeln — oder bricht
sie.* Ich habe eine korrekte Funktion an die falsche Stelle gesetzt. Syntaktisch gültig,
semantisch richtig, und trotzdem eine Zeitbombe, weil die drei Dateien ihre Globals
bisher sorgfältig vermieden hatten. Wer einen Block in fremden Code einfügt, liest
zuerst, wie dieser Code seinen Scope organisiert.
