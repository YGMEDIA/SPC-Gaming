# 2026-10-05 · Content · B11: Die echte Alternative heißt Amazon und Video

## Was

Maßnahme B11 der Bücher-Synthese (Quelle: April Dunford, *Obviously Awesome*).
Positionierung fängt bei der Frage an, was der Kunde **stattdessen** täte. Für uns ist das
nicht ein anderer Controller-Blog, sondern Amazon selbst und ein Video.

**Gemessen am 05.10.2026 über alle 127 ausgelieferten Seiten:**

| Gemessen | Befund |
|---|---|
| „YouTube" im sichtbaren Text | **0 Seiten** |
| „Amazon" auf der Startseite | **3 Stellen im Seiteninhalt**, alle drei als Datenquelle („Belegte Amazon-Daten", „Preise und Bewertungen von Amazon.de", „Produktbilder aus dem Amazon-Katalog"); mit dem repoweiten Footer 4, die vierte ist der Provisionshinweis |
| „Amazon" auf /ueber-uns/ | 2 Stellen im Seiteninhalt, beide der Provisionshinweis |
| Positionierung im Text | gegen „klassische Affiliate-Seiten" und „Marketing-Blabla" |

Die Alternative, gegen die wir tatsächlich antreten, wurde also an keiner Stelle benannt.
Positioniert wurde gegen einen Gegner, den der Leser gar nicht in Betracht zieht.

**Zweiter Befund, beim Messen aufgefallen:** /ueber-uns/ und /redaktion/ sagten beide
„**Jeder** Controller wird über mehrere Wochen im echten Gaming-Alltag getestet"
(/redaktion/ sogar „mindestens 2 bis 3 Wochen"). Die Startseite sagt daneben „42 Modelle
im Sortiment und 13 davon ausführlich getestet", und gemessen tragen genau **13 der 42**
Produktseiten einen eigenen Test. Beides kann nicht stimmen, und die All-Aussage stand
auf den zwei Seiten, auf denen ein Leser die Methode prüft.

## Wie

`scripts/positionierung.py` trägt die Regel, `scripts/sync_positionierung.py` setzt zwei
Blöcke auf drei handgepflegte Seiten. Kein Generator-Zwilling: Keine dieser Seiten wird
generiert.

**Startseite**, direkt hinter dem Versprechen-Band: ein Abschnitt „Warum nicht einfach bei
Amazon schauen?" mit den drei Fragen, die sonst offen bleiben, und einem Schlusssatz zum
Video. Jede Antwort nennt eine Zahl, und jede Zahl kommt aus der Regel, die sie besitzt:

| Aussage | Zahl | Quelle |
|---|---|---|
| Kompatibilität steht im Kasten | 33 von 42, davon 13 mit Negativzeile | `kompat.py` (B1) |
| mindestens zwei Schwächen je Seite | 42 | §A6 |
| Warnung statt Empfehlung unter 3,8 | 1 von 28 | `produktdaten.A6_SCHWELLE` |
| günstigeres Modell derselben Marke besser bewertet | 6 | `guenstiger.py` (B10) |
| Lesezeit der Testseiten | 1 bis 2 Minuten | `lesezeit.py` (B5) |

**/ueber-uns/ und /redaktion/** bekommen denselben Methodik-Absatz, der die All-Aussage
ersetzt: 13 Modelle mit eigenem Test, 29 Kurzchecks, und welche Art Seite einen erwartet,
steht auf jedem Knopf („Zum Test" gegen „Zum Kurzcheck", B9). Der Missions-Absatz auf
/ueber-uns/ benennt jetzt ebenfalls die Alternative statt „klassischer Affiliate-Seiten".

## Warum so

**Die Behauptungen stehen über uns, nicht über Amazon.** Was in einer Artikelbeschreibung
steht oder fehlt, könnten wir nicht belegen. Eine Positionierung, die mit einer
unbelegbaren Aussage über den Wettbewerber anfängt, gibt genau das Argument aus der Hand,
mit dem sie wirbt. Der Abschnitt sagt deshalb, was **wir** tun, und überlässt den
Vergleich dem Leser, der die andere Seite ohnehin kennt.

**Die Zahlen werden abgeleitet, nicht eingetippt** (P-11). Eine Positionierung, die
Eigenschaften behauptet, muss sie belegen können. Wer „33 von 42" von Hand schreibt, hat
beim nächsten Produktwechsel eine Behauptung ohne Deckung, und zwar auf der Seite, die am
meisten davon abhängt, dass man ihr glaubt.

**Die All-Aussage wird nicht umformuliert, sondern gegen die Wirklichkeit gegatet.**
Solange nicht jedes Produkt einen eigenen Test hat, soll keine Methodenseite einen
All-Quantor mit einer Test-Aussage verbinden. Geprüft wird ein Sprachmuster in zwei
Satzstellungen, mit bis zu zwei Füllwörtern zwischen Quantor und Nomen, mit „Test" auch
als Substantiv und mit der Sonderform „kein X ohne Test"; ausgenommen sind Verneinung,
Frage und Sätze, die die gemessene Zahl selbst nennen. Die Schwelle hängt an der
genannten Klasse: „Jeder **Controller** wird getestet" wird an den 28 Controllern
gemessen, nicht an allen 42 Produkten, sonst blockiert das Gate irgendwann einen wahren
Satz.

**Und die Grenze dieser Prüfung steht daneben, im Code wie hier.** Meine erste Fassung
nannte sich im Kommentar „Eigenschaft statt Satz" und war es nicht: Von zehn echten
All-Aussagen fing sie **eine**. Durch rutschten Verb-zuerst („Wir testen jeden
Controller…"), ein Füllwort („Jeder **einzelne** Controller…"), „Test" als Substantiv,
„Sämtliche Controller durchlaufen unseren Testprozess" (die alte Überschrift der Seite!),
„Kein Controller kommt ohne eigenen Test" und „Jedes **Gerät**…". Gleichzeitig wurden
neun wahre Sätze rot, darunter die ehrliche Korrektur „**Nicht** jeder Controller ist von
uns getestet" — und die Meldung schnitt das „Nicht" ab und legte der Seite die
Behauptung in den Mund, die sie bestreitet. Die zweite Runde hat an derselben Zeile noch zwei
Fehler gefunden: Die Verb-zuerst-Alternative nahm auch „geprüft" und die Substantive, und
damit wurde **7 von 14** legitimen Sätzen rot, weil Methoden-Vokabular auf einer
Methodenseite der Normalfall ist („Im Test zeigte sich, dass alle Controller mit Android
laufen"). Und die Ausnahme „der Satz nennt die Zahl" galt jeder nackten 13, also auch
„einen 13-Punkte-Test im Alltag".

Jetzt: 23 Sätze einzeln gemessen, 11 müssen rot werden, 12 müssen grün bleiben, 0 falsch.
**Zwei Grenzen stehen ausdrücklich im Code**, weil sie bleiben: „Alle Modelle werden
getestet, 13 davon besonders gründlich" bleibt grün (der Unterschied zur wahren
Startseiten-Fassung liegt allein im Verb, geprüft gegen getestet, und das trennt kein
Muster), und eine Modalkonstruktion („Wir würden gern jeden Controller selbst testen,
schaffen aber nur einen Teil") wird falsch rot. Ein deutscher Satz lässt sich immer so
bauen, dass ein Muster ihn verfehlt. Das ist eine Stichprobe auf die bekannten Formen,
kein Beweis, und genau so steht es im Code.

**Eine Aussage über den eigenen Prozess entfernt, nicht ersetzt:** „Wir messen
Input-Latenz" (/redaktion/) und „Wir messen Latenz" (/ueber-uns/) standen da, und
**keine einzige der 42 Produktseiten** nennt eine Millisekunden-Zahl. Die ms-Angaben im
Repo stehen in **einem** Blog-Artikel und **einem** Hub, alle als allgemeine Spanne, keine
als eigener Messwert. Derselbe Anspruch stand ein drittes Mal in der Autorenbox auf
/redaktion/ („Verbindung und Latenz") und ist dort mit raus. Ohne Beleg fliegt die Aussage raus
statt umgeschrieben zu werden (§A5-Logik auf die eigene Arbeit angewendet). **Für Yasin:**
Wenn gemessen wird, gehört die Zahl auf die Produktseite, dann kann der Satz zurück.

## Verify

- **Dreizehn Gates, jedes exit 0** (neu: `sync_positionierung.py --check`)
- **Neues Gate §B11**, fünf Eigenschaften am ausgelieferten Stand:
  1. jede der drei Seiten trägt genau einen Block, **beide** Marker genau einmal (die
     erste Fassung zählte nur START und ließ ein verwaistes END stumm grün)
  2. jede gemessene Zahl steht im Block (mit Ziffergrenzen), **und** keine ungedeckte Zahl
     steht darin (Drift-Gate, P-11 Mechanismus 2)
  3. der Startseiten-Abschnitt benennt beide Alternativen, die Lesezeit-Spanne und die
     gemessene Mindestzahl der Schwächen (als Wort, deshalb eigene Prüfung)
  4. keine Methodenseite macht eine All-Aussage über eigene Tests, solange die Messung sie
     nicht trägt (Grenzen siehe „Warum so")
  5. der Gegentest über alle 127 Seiten: Wo der Block nicht hingehört, steht keiner
- **Neues Gate §A6**, aus dem Prüflauf erzwungen: Jede der 42 Produktseiten muss
  mindestens zwei Schwächen nennen, gezählt mit einem HTML-Parser in der `cons-box`. Das
  ist Verfassungsrecht seit dem ersten Tag und war von **nichts** geprüft. Beleg: eine
  handgepflegte Review-Seite von 4 auf 1 Schwäche gekürzt, Lauf blieb grün. Gemessene
  Verteilung heute: 16 Seiten mit 2, 16 mit 3, 9 mit 4, 1 mit 5.
- **`scripts/links_batterie.py` von 59 auf 85 Fälle** (58 rot, 27 grün), 0 falsch.
  Zweiundzwanzig B11-Formen, darunter zehn, die **nur** die Satzprüfung findet (die
  All-Aussagen in ihren verschiedenen Stellungen und die vier Gegenproben): Der
  Zeichenvergleich sieht sie nicht, weil der Block selbst unberührt bleibt.
- Die All-Aussagen-Prüfung zusätzlich an **23 Sätzen** einzeln gemessen (11 müssen rot
  werden, 12 müssen grün bleiben), 0 falsch
- Die Schwächen-Zählung an **10 Markup-Formen** gemessen: `<img>` und `<br>` ohne
  Schrägstrich im Kasten, Kasten in `<template>`, verschachtelte Liste, leerer Kasten,
  fehlendes `<main>`, Großschreibung, mehrwertige Klasse, `<section>` statt `<div>` —
  alle korrekt. Die Void-Tag-Behandlung fehlte zuerst, und ohne sie hätte ein `<img>` im
  Kasten jedes spätere `<li>` der Seite als Schwäche gezählt (Richtung: stumm grün)
- Die Teilstring-Falle hat hier eine eigene Pointe: „42" steht zweimal im Abschnitt. Wird
  eine der beiden zu „142", bleibt die Anwesenheitsprüfung grün, weil die andere stehen
  bleibt. Rot wird die Form erst über das Drift-Gate.
- Idempotent und reihenfolgeunabhängig: Entfernen und Einsetzen sind ein Paar je Richtung
  (davor/dahinter). Acht Permutationen der Sync- und Generator-Kette, darunter fünf Läufe
  des neuen Syncs hintereinander, alle zeichengleich (`4e5ed5f94f8b3e43` über alle
  HTML-Dateien), verify.py jedes Mal exit 0. `idempotenzprobe.py` zählt jetzt 16
  Schreiber, alle idempotent und baumstabil
- Die erste Fassung war NICHT idempotent: Ein Entfernen-Muster für beide Richtungen fraß
  auf einer der zwei Methodenseiten die Einrückung der Folgezeile. Aufgefallen beim
  zweiten `--check` direkt nach dem Setzen
- Browser: Abschnitt als direktes Kind von `<main>`, bei 1024 px drei Spalten zu
  314,664 px, mobil eine Spalte zu 335 von 375 px, kein Horizontal-Scroll, keine
  Konsolenfehler. **Mit gesetzter Viewport-Größe gemessen:** Bei eingeklapptem
  Browser-Fenster meldet `clientWidth` 0, und dann ist jede Scroll-Prüfung wahr. Einmal
  genau so passiert und beinahe als Layout-Fehler notiert
- Die Behauptung „mindestens zwei Schwächen" eigens nachgemessen, mit einem HTML-Parser
  statt mit einem Regex: 42 von 42 Produktseiten, 0 mit weniger als zwei Punkten
- Die vier stehenden Proben gegen den Endstand: `robustheitsprobe.py` 117 Defektformen /
  118 verify-Starts · `idempotenzprobe.py` **16** Schreiber · `besten_batterie.py` 36 ·
  `finder_batterie.py` 111 — zusammen 0 Befunde

## Gelernt

1. **Eine Positionierung ohne benannte Alternative positioniert gegen niemanden.** „Kein
   Marketing-Blabla" grenzt gegen andere Blogs ab. Der Leser vergleicht uns aber nicht mit
   anderen Blogs, er vergleicht uns mit dem Tab, den er sonst geöffnet hätte.
2. **Die Methodenseite ist der teuerste Ort für eine Übertreibung.** Dort schaut genau der
   Leser nach, der schon zweifelt. „Jeder Controller wird getestet" stand zwei Klicks neben
   „13 von 42" auf der Startseite.
3. **Eine All-Aussage ist eine Zahl ohne Zahl.** Sie behauptet Vollständigkeit und entzieht
   sich damit der Prüfung, die jede Zahl in diesem Repo hat. Das Gate macht daraus wieder
   eine prüfbare Aussage, indem es die Eigenschaft prüft statt den Satz.
4. **Auch der korrigierte Satz war zuerst zu groß.** Meine erste Fassung des
   Kompatibilitäts-Arguments sagte, auf 33 von 42 Seiten stehe, „an welche Geräte ein
   Modell passt **und an welche nicht**". Nachgemessen: Die Negativzeile liefert
   `kompat()` nur, wenn die Verbindungsart eine Ausgrenzung hergibt, und das sind **13**
   der 33. Der stärkere Teil der Aussage galt für ein Drittel der genannten Menge. Jetzt
   stehen beide Zahlen da, und die 13 ist genauso gegatet wie die 33. Eine Maßnahme gegen
   Übertreibung schützt nicht davor, selbst zu übertreiben: Jede Mengenaussage will
   nachgerechnet werden, auch die in der Korrektur.
5. **Der Satz, der die Maßnahme trägt, war selbst ungegatet.** „Jede unserer 42
   Produktseiten nennt mindestens zwei Schwächen" stimmte, aber nichts hielt ihn fest:
   §A6 steht seit dem ersten Tag in der Verfassung und wurde von keiner Prüfung berührt.
   Eine Maßnahme, die Behauptungen prüfbar machen soll, hat als erstes eine ungeprüfte
   Behauptung auf die meistgelesene Seite geschrieben. Jetzt zählt ein Parser, das
   Minimum steht im Satz, und unter zwei wird der Lauf rot.
6. **Die eigene Prüfung auf Übertreibung war selbst übertrieben.** Der Kommentar neben
   dem Muster sagte „Eigenschaft statt Satz" und meinte einen Regex, der eine von zehn
   Formen fing. Eine Grenze, die man nicht hinschreibt, wird zur nächsten unbelegten
   Behauptung, und zwar in dem Teil des Repos, der genau das verhindern soll.
7. **`EXIT=0` aus einer Pipeline ist der Exit-Code von `tail`.** Ein Batterie-Lauf meldete
   „[exited with code 0]" und darunter „17 falsch": Ich hatte ihn als
   `python3 … | tail -8` gestartet, und der Exit-Code der Pipeline ist der des letzten
   Glieds. Seitdem läuft jede Messung als `… > datei 2>&1; echo EXIT=$?`. Eine grüne
   Zahl, die aus der falschen Quelle kommt, ist schlimmer als keine.
8. **Ein Werbesatz über die eigene Arbeit braucht denselben Beleg wie eine Produktzahl.**
   §A5 verbietet erfundene Produktdaten. „Wir messen Input-Latenz" ist formal keine
   Produktdatenaussage, steht aber im selben Vertrauensverhältnis, und es gibt keinen
   Grund, die eigene Arbeit lockerer zu prüfen als die Daten eines Herstellers.
