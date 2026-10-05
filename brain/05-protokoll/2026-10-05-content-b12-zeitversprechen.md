# 2026-10-05 · Content · B12: Jede Seite sagt, was sie kostet

## Was

Maßnahme B12 der Bücher-Synthese, die letzte (Quelle: Hormozi, Wert-Gleichung). Der Wert
eines Angebots steht im Zähler, Zeitaufwand und Mühe stehen im Nenner. Wer vor einer Seite
steht und nicht weiß, wie lange sie dauert, rechnet den Nenner nach oben.

**Gemessen am 05.10.2026 über alle 127 ausgelieferten Seiten:**

| Gemessen | Befund |
|---|---|
| Seiten, die ihre eigene Lesezeit nennen | **19 von 127** |
| davon Produktseiten | **0** |
| Lesezeit der 42 Produktseiten (gerechnet) | 1 bis 3 Minuten, Median 2 (Verteilung 10 × 1, 30 × 2, 2 × 3; nach dem Ausschluss der Byline aus der Messung derselbe Stand) |
| Zeitversprechen zum Finder | 7 Stellen, alle „60 Sekunden", **ungegatet** |
| Fragenzahl des Finders | seit 01.10. gegatet |

Die Seiten, über die der Produkt-Traffic kommt, sagten also als einzige nicht, worauf sich
der Leser einlässt. Und das einzige Zeitversprechen, das die Site macht, stand an sieben
Stellen ohne jede Absicherung: Wer eine davon auf „90 Sekunden" setzt, bekommt eine Site,
die zwei verschiedene Versprechen macht.

## Wie

**Alle 52 Produktseiten tragen jetzt ihre Lesezeit**, gerechnet mit derselben Regel, die
seit B5 die Blog-Artikel trägt (`lesezeit.py`, 200 Wörter pro Minute):

| Seitenart | Anzahl | Wer schreibt | Text |
|---|---|---|---|
| handgepflegte Reviews | 13 | `sync_lesezeit.py` | „Getestet von Yannick Gerber · 1 Min. Lesezeit · Redaktion …" |
| generierte Datenblätter | 29 | `gen_pages.py` | „Kurzcheck ohne eigenen Test · 2 Min. Lesezeit" |
| Longtail-Datenblätter | 10 | `gen_longtail.py` | „Datenblatt ohne eigenen Test · 2 Min. Lesezeit" |

Die beiden Generatoren bauen **zweistufig**: einmal bauen, um den fertigen Text zu zählen,
dann mit der echten Zahl. Dieselbe Lösung wie in `gen_preisfrage.py`, und aus demselben
Grund: Eine getippte Lesezeit auf einer Seite, die sonst jede Zahl ableitet, wäre die
erste, die nicht mehr stimmt.

**Pendeln kann das nicht, und zwar baulich:** Die beiden Läufe unterscheiden sich in genau
einem Token („1" gegen „2"), die Wortzahl ist in beiden identisch. Nachgemessen über alle
39 generierten Seiten: 0 Seiten, bei denen der zweite Lauf etwas anderes ergibt; der
Prüfer hat dasselbe für k = 1 bis 99 durchgerechnet, ebenfalls ohne Ausnahme.

*(Hier stand zuerst „die nächste Seite liegt 66 Wörter von einer Minutengrenze entfernt",
als zusätzliche Sicherheit. Die Zahl kam aus einer falschen Formel, und die Korrektur
(„1 Wort, ozkak-6finger") kam aus **derselben** falschen Formel: Gemessen wurde der
Abstand zu einem Vielfachen von 200, die Rundungsgrenze liegt aber bei 200n+100. Der Satz
ist jetzt ganz raus. Er sollte ein Argument stützen, das ohne ihn steht, und ist deshalb
zweimal unbemerkt falsch gewesen: Die Ziffern-Invarianz ist der Beweis, nicht der
Abstand.)*

**Das Zeitversprechen zum Finder hat eine Quelle.** `scripts/zeitversprechen.py` hält die
Zahl und die sieben Stellen, `sync_zeitversprechen.py` schreibt sie, verify.py vergleicht
zeichengleich und verlangt jede Stelle genau einmal. Ob 60 Sekunden stimmen, prüft das
Gate ausdrücklich nicht; der Leser misst das in 60 Sekunden selbst nach.

## Warum so

**Die Byline sagt auch, was für eine Seite das ist.** „Kurzcheck ohne eigenen Test" steht
dort nicht als Selbstkritik, sondern weil es dieselbe Unterscheidung ist, die seit B9 auf
jedem Knopf steht („Zum Test" gegen „Zum Kurzcheck") und seit B11 auf den Methodenseiten.
Drei Stellen, dieselbe Aussage, keine davon getextet.

**Die Zusage wird gepflegt, nicht erraten.** Meine erste Fassung suchte sie repoweit per
Muster und entschied am Umfeld (45 Zeichen, Stichwörter Finder, Fragen, Ergebnis,
Empfehlung, Wahl), ob eine Sekundenangabe eine Finder-Zusage ist. Der Prüfer hat beide
Richtungen zerlegt: Fünf Umformulierungen blieben grün, weil die übrigen Stellen weiter
60 sagten („in zwei Minuten", „in 90 s", „in neunzig Sekunden", Zusage entfernt, Kachel
durch „kostenlos" ersetzt), dazu eine **zusätzliche** Zusage auf der Finder-Seite, deren
Umfeld zufällig kein Stichwort enthielt. Und umgekehrt wurde ein Fehlersuche-Artikel
falsch rot: „Nach 20 Sekunden blinkt die LED, dann ist die Wahl des Modus wieder frei" —
„Wahl", „Fragen", „Ergebnis" sind Alltagswörter, und das Fenster muss über Blockgrenzen
laufen, sonst findet es die Kachel („60 Sek." und „bis zum Ergebnis" stehen in zwei divs).

Beides fällt weg, sobald die Zahl eine Quelle hat. Geblieben ist ein **enger Sweep** auf
genau den zwei Seiten, auf denen heute jede Sekundenangabe eine Finder-Zusage ist
(Startseite und Finder-Seite): Er fängt die eine Form, die eine Liste bekannter Stellen
nicht fängt, nämlich eine zusätzliche Zusage daneben. Die Büroklammer-Sekunden im
Fehlersuche-Artikel liegen außerhalb des Sweeps und sind damit kein Thema mehr.

**Der Lesezeit-Wert bleibt, was er ist, auch wenn er klein ist.** Die 13 Testseiten liegen
bei 1 bis 2 Minuten. Das ist kein Ruhmesblatt, aber es ist die Wahrheit, und es ist genau
das Argument, das B11 auf der Startseite gegen ein Video führt.

## Verify

- **Vierzehn Gates, jedes exit 0** (neu: `sync_zeitversprechen.py --check`)
- **Neue Prüfung §A1/B12 (Anwesenheit):** Die Menge der Seiten, die eine Lesezeit tragen
  müssen, wird **abgeleitet** (alle Produktseiten aus products.json, alles unter
  `/produkte/`, jeder Blog-Artikel außer der Listenseite) und jede einzeln geprüft
- **Neue Prüfung §A5/B12 (Zeitversprechen):** jede der sieben Stellen passt genau einmal
  und nennt die gepflegte Zahl; dazu der enge Sweep auf Startseite und Finder-Seite gegen
  eine zusätzliche Zusage
- **Elf Defektformen einzeln gemessen, 0 falsch:** Finder-Dauer an drei Stellen verfälscht
  (Startseite sichtbar, Meta-Description, Kachel) · Lesezeit auf Review- und auf
  generierter Seite verfälscht · Lesezeit auf Review-, generierter und Blog-Seite
  **entfernt** · Text einer Review-Seite verdoppelt, Zahl bleibt stehen (Alterungsprobe,
  P-13 Mechanismus 3) · zwei legitime Formen grün (Büroklammer-Sekunden, zusätzlicher
  Absatz neben der Byline)
- **`scripts/links_batterie.py` von 85 auf 98 Fälle** (69 rot, 29 grün), 0 falsch —
  darunter die sechs Mutationen, an denen die erste Gate-Fassung gescheitert ist, und die
  Alterungsprobe (Text verlängert, Zahl bleibt stehen)
- Die zehn Formen des Prüfers einzeln nachgefahren: acht rot (fünf Umformulierungen,
  zusätzliche Zusage, zwei verfälschte Zahlen), zwei legitime Sekundenangaben grün
- `idempotenzprobe.py` **17** Schreiber, alle idempotent und baumstabil — **das ist hier die
  eigentliche Probe**, weil zwei Generatoren jetzt zweistufig bauen und ein Pendeln
  zwischen zwei Minutenwerten genau so aussähe
- **Jede der 71 Lesezeiten mit einem eigenen Zähler nachgerechnet** (ohne `lesezeit.py`,
  eigene Regex-Fassung von Textextraktion und Rundung): 0 Abweichungen
- Die Pflichtmenge einzeln geprüft: 71 Seiten (39 unter `/produkte/`, 19 Blog-Artikel,
  13 Reviews), keine ohne Lesezeit, kein Redirect-Stub darin, und keine Seite außerhalb
  der Menge, die eine trägt
- `robustheitsprobe.py` 117 Defektformen · `besten_batterie.py` 36 · `finder_batterie.py`
  111 — alle 0 Befunde
- Browser: Byline auf beiden Seitenarten sichtbar, 13 px, `--ink-soft`, unter dem Lead;
  mobil 335 von 375 px einzeilig, kein Horizontal-Scroll; Kontrast im Browser gemessen: 5,79:1 (vorher 2,74:1, unter WCAG AA)

## Gelernt

1. **Ein Abdeckungs-Anker, der nur prüft, wo die Zahl steht, prüft nicht, dass sie steht.**
   P-13 Mechanismus 4 fordert den Anker seit Runde 15, gebaut war er nur für die Seiten,
   die die Angabe schon trugen. Meine eigene Probe hat es gefunden: Lesezeit aus der Byline
   entfernt, Lauf grün. Jetzt wird die MENGE abgeleitet, nicht das Vorkommen gezählt. Als
   Mechanismus 25 in P-13 zurückgeflossen.
2. **`Sek\.` plus `\b` findet „60 Sek." nicht.** Nach dem Punkt steht kein Wortzeichen,
   also auch keine Wortgrenze. Die erste Fassung des Musters übersah damit ausgerechnet die
   Kachel auf der Startseite, also die prominenteste der sieben Stellen. Gefunden, weil ich
   die Treffer einzeln ausgegeben und mit der Messung von vorher verglichen habe, nicht
   weil das Gate etwas gesagt hätte: Ein Muster, das zu wenig findet, meldet nichts.
3. **Eine Zusage, die man sucht statt pflegt, ist keine Zusage.** Die erste Fassung des
   Zeitversprechen-Gates suchte „N Sekunden" und entschied am Umfeld. Das ist dieselbe
   Bauart wie der All-Quantor-Regex aus B11, und sie hat dieselben zwei Fehler gemacht:
   fünf Umformulierungen durchgelassen und einen wahren Satz rot gemacht. Sobald die Zahl
   eine Quelle hat und ein Sync sie schreibt, ist beides weg. Die Heuristik war nur nötig,
   weil ich die Stellen nicht aufschreiben wollte.
4. **Die Byline hat sich selbst in die Länge gerechnet.** Sie steht im `<main>`, also
   zählte der Lesezeit-Zähler sie mit — und auf zwei Seiten kippte sie die Zahl von 1 auf
   2 Minuten. Eine Messung, deren Ergebnis in die gemessene Menge zurückfließt, ist ein
   Regelkreis; die Byline fällt jetzt wie `<nav>` aus der Messung.
5. **Ein Block zwischen zwei Blöcken verschwindet beim Ersetzen des Nachbarn.** Beim
   Umbau des Zeitversprechen-Gates habe ich die Anwesenheitspflicht gleich mitgelöscht,
   und der Lauf blieb grün: Eine gelöschte Prüfung meldet nichts. Dasselbe ist dem
   Finder-§A6-Gate zweimal passiert, die Lehre stand zwanzig Zeilen weiter unten im selben
   File. Jetzt stehen Trennmarken drum.
6. **Dieselbe falsche Formel zweimal, in der Korrektur derselben Zahl.** Die Randlage
   zur Minutengrenze stand erst mit 66 Wörtern da, dann korrigiert mit 1 Wort, und beide
   Male maß die Formel den Abstand zum falschen Punkt. Eine Zahl, die ein Argument stützen
   soll, das ohne sie trägt, wird von niemandem nachgerechnet, von mir zuerst nicht.
7. **Eine Zahl, die drei Writer schreiben, braucht eine Regel und drei Importe.** 13 Seiten
   kommen vom Sync, 29 vom einen und 10 vom anderen Generator. Alle drei rufen
   `lesezeit.minuten()`; eine eigene Formulierung derselben Regel hätte dafür gesorgt, dass
   Sync und Generator sich bei jedem Lauf gegenseitig überschreiben.
