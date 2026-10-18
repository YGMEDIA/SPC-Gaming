# 2026-10-06 · Content · Maßnahme 9: Vergleichsseiten ausbauen

## Was

Yasin: „mach die vergleichsseiten." Maßnahme 9 der Bücher-Synthese (Sheridan), die
letzte der drei, die kein B bekommen hatte und weder GSC-Daten noch das Ende des
Meta-Freeze braucht.

**Fünf Duelle generiert statt handgeschrieben, zwei neue gebaut, ein Gate dazu.**

## Die Prämisse hat sich geändert, und das gehört gesagt

Die Synthese begründete Maßnahme 9 mit „die GSC-Daten zeigen Nachfrage nach mehr".
Nachgemessen über alle sieben GSC-Läufe:

- **Duell-Queries gab es genau einmal**, in Lauf 6 (26.08.): „razer kishi v3 pro vs
  gamesir g8 plus" und „razer kishi ultra vs gamesir g8 plus", **je eine Impression**.
  Für beide existiert längst eine Seite.
- In Lauf 7 (29.09.) taucht **keine Vergleichsseite** mehr in der Seitenliste auf, und
  keine Duell-Query in der Query-Liste.
- Die einzige Vergleichsseite, die je rankte, ist die **älteste** (3 Impressionen in
  Lauf 6). Die am 27.07. gebaute hatte einen Monat später noch nichts.

Das ist dieselbe Lage wie bei B5: Die Maßnahme ist richtig, ihre damalige Begründung
trägt nicht mehr. Umgesetzt auf dem eigenen Wert, nicht auf der alten Prämisse — und
die Reihenfolge daraus abgeleitet: **erst die fünf bestehenden gut machen, dann zwei
neue.** Mehr thin Vergleichsseiten zu bauen hätte den Fehler wiederholt, den die
Messung gerade zeigt.

## Der Befund: die achte Renderstelle

Gemessen vor dem Bau:

| Seite | Wörter |
|---|---|
| backbone-one-vs-gamesir-g8 | **103** |
| backbone-pro-vs-kishi-v3-pro | **110** |
| g8-galileo-vs-kishi-v3 | 206 |
| g8-plus-vs-kishi-v3-pro | 275 |
| kishi-ultra-vs-g8-plus | 428 |

Drei davon sind Thin Pages nach demselben Maßstab, den B6 an die Bestenlisten angelegt
hat (die lagen bei 123–190). Dazu dieselben Befunde wie dort, eine Ebene weiter:

- **Die Zeilen-Labels liefen auseinander.** Über alle fünf Tabellen standen 18
  verschiedene Labels; nur „Preis" und „Sticks" standen auf allen fünf
  („Pass-Through" gegen „Pass-Through-Charging", „Plattform" gegen „Plattformen",
  „Rücktasten" gegen „Zusatztasten").
- **Die Amazon-Bewertung stand auf zwei von fünf Seiten.** Auf einer Seite, deren
  einziger Zweck eine Kaufentscheidung ist, fehlte das Signal, das Cialdini als das
  stärkste benennt und das B8 überall sonst nach vorn geholt hat.
- **Verfügbarkeit stand auf keiner** — obwohl der Backbone Pro in einem der Duelle
  steht und seit dem Vollabgleich nicht kaufbar ist.
- Kein Duell trug mehr als ein BreadcrumbList-Schema.
- Zwei Seiten hatten **gar keinen** redaktionellen Abschnitt nach der Tabelle, zwei
  einen, eine zwei.

## Wie

**`scripts/gen_vergleich.py`** (neu). Redaktionell bleiben **Paarung, Sieger und
Urteil** — das sind Entscheidungen, keine Rechnungen. Alles andere kommt aus
products.json und wird bei jedem Lauf neu gerechnet:

- Preis mit Abstand in Euro
- Amazon-Bewertung mit Anzahl
- **Verfügbarkeit, aber nur wenn sie etwas zu sagen hat** — zwei kaufbare Geräte
  brauchen keine Zeile „Verfügbar / Verfügbar"; sobald eines nicht kaufbar ist, ist es
  die wichtigste Zeile der Tabelle
- Sticks, Verbindung, Plattformen
- die Häkchen, und zwar **nur an einem gemessenen Vorteil**
- die Kauf-Knöpfe mit aktuellem Preis und ASIN

**Die Gegenrede ist Pflicht (P-14).** Was in den DATEN gegen den gewählten Sieger
spricht, steht auf der Seite. Ergebnis: **In vier von sieben Duellen ist der gewählte
Sieger der schwächer bewertete.** Das stand vorher nirgends.

Dazu die fehlenden redaktionellen Abschnitte geschrieben: zwei Duelle hatten keinen,
zwei nur einen. Jetzt hat jedes zwei („Der Unterschied, der das Duell entscheidet" und
eine ehrliche Begründung für den Verlierer) plus Links auf beide Produktseiten.

## Die zwei neuen Duelle

Beide sind **markenintern** — die Frage, die jemand stellt, nachdem er sich für eine
Marke entschieden hat. Und beide tragen eine **Bewertungs-Umkehr**, also genau den Fall,
auf den B10 die Site positioniert hat:

| Duell | Lage |
|---|---|
| **Kishi V3 vs. Kishi V3 Pro** | 78 € gegen 124 €, und der günstigere steht bei 4,4 gegen 4,2 — bei fast identischer Datenbasis (157 gegen 152 Bewertungen) |
| **G8 Galileo vs. G8 Plus** | vier Euro Unterschied, 4,2 gegen 4,1; die Entscheidung fällt über Pass-Through gegen Bluetooth und Switch |

Keine Paarung ist geraten: 145 Paare erfüllen die Datenkriterien (Plattform-Überschneidung,
unter 40 % Preisabstand, beide kaufbar). Die Auswahl ist redaktionell und als solche
benannt — Razer ist dabei die Marke mit messbarem Interesse (marken/razer 11 Impressionen
in Lauf 7, „razer controller" 4).

**Neue Duelle entstehen ab jetzt als Definition, nicht als kopierte HTML-Datei.** Der
Generator legt die ganze Seite an, Header und Footer holt er aus `sync_header` und
`sync_footer`. Die fünf vorhandenen Seiten sind durch Kopieren entstanden, und genau
daran sind die Labels auseinandergelaufen.

## Ein §A5-Befund fiel dabei an

Beim Schreiben wollte ich „der G8 Galileo wiegt 230 Gramm" übernehmen — eine Angabe, die
ich am Morgen desselben Tages selbst als **unbelegt** protokolliert hatte (die
Amazon-Seite nennt kein Produktgewicht). Der Chip war aus products.json entfernt, die
Zahl stand weiter in sechs Prosa-Stellen.

Nachgemessen: **Sieben Gewichtsangaben stehen in der Prosa und in keinem Feld des
Datenkerns** — 230 g (G8 Galileo), 195 g (Kishi V3), 250 g (X3 Pro), 181 g (Turtle
Beach), 160 g (Backbone Pro), 245 g (G8 Plus), 140 g. Belegt sind nur 135 g (X5 Lite)
und 138 g (Backbone One) als `Gew.`-Spec sowie 56 g und 256 g aus zwei Claims.

Auf den Vergleichsseiten sind sie raus (drei Stellen). **Die übrigen vier stehen in
Pro/Contra-Listen von Review-Seiten und sind ein eigenes Arbeitspaket** — sie gehören
entweder am Listing belegt oder gelöscht, und das ist derselbe Pass wie die Spec-Chips
vom Morgen.

Zweiter Fund derselben Art: „vier frei belegbare Zusatztasten **statt zwei**" auf
g8-plus-vs-kishi-v3-pro. Der G8 Plus führt im Datenkern gar keine Zusatztasten.

## Der Prüfdurchgang hat blockiert, und er hatte recht

Der erste Prüflauf gab **FREIGABE: NEIN** mit vier Blockern. Zwei davon waren
Widersprüche zwischen einer neuen Vergleichsseite und einer eigenen Testseite, also
genau der Schaden, den eine Vergleichsseite anrichten kann: Sie stellt zwei Produkte
nebeneinander und widerspricht dabei dem, was die Site über dieselben Produkte schon
behauptet.

**B1 · Pass-Through beim G8 Plus.** Die neue Seite schrieb „Pass-Through-Charging: ✗
Nein" und darauf aufbauend „Der G8 Plus hat beides nicht". Die eigene Testseite sagte
„✓ Pass-Through-Charging". Ich bin selbst auf das Listing gegangen: **B0FYQ1SHHS sagt
„unterstützt das Durchladen"**. Die Testseite hatte recht, meine neue Seite lag falsch,
und der ganze zweite Absatz stand auf der falschen Prämisse. Zeile korrigiert auf „✓ Ja"
für beide, die Prosa neu geschrieben.

**B1b · die Klinke, für die es in keiner Richtung einen Beleg gibt.** Dieselbe
Testseite behauptete im Urteilskasten „3,5-mm-Audio" und drei Zeilen weiter unten
„✗ Kein 3,5-mm-Anschluss" — ein sichtbarer Selbstwiderspruch auf einer Kaufseite. Das
Listing nennt weder das eine noch das andere. Also ist **beides** weg, nicht eines von
beiden, und die Tabellenzeile sagt für den G8 Plus „keine Angabe". Dasselbe im
Kishi-Ultra-Duell, wo ein „✗ Nein" eine Abwesenheit behauptete, die nie belegt war.

**B2 · die 230 Gramm, ein zweites Mal.** Meine Vergleichsseite sagte korrekt „GameSir
nennt für den G8 Galileo gar kein Gewicht" (B0CXHVCTW9 nennt nur einen
Versandgewicht-Platzhalter von 520 g), während die Testseite „✗ Mit ~230 g etwas
schwerer" behauptete. Der Fehler saß in der Testseite. Dazu der Nachbarfund: Die
G8-Plus-Testseite verglich „Etwas schwerer als G8 Galileo (245 g)" gegen ein Gewicht,
das es nicht gibt. Beide Zeilen durch belegte Schwächen ersetzt (Bewertung, Preis,
fehlender Tablet-Betrieb), damit keine Review unter zwei Nachteile fällt (§A6). Und
weil dieselbe Zahl zwei Stellen weiter im Blog stand, ist sie auch dort raus: Einen
Widerspruch an einer Stelle zu beheben und an der nächsten stehen zu lassen, verschiebt
ihn nur.

**B3 · die Kauf-Knöpfe ohne Styling.** `.cta-pair` stand im Markup **aller sieben**
Seiten, die CSS-Regel aber nur im `<style>` von zwei. Auf fünf Seiten klebten die
beiden Affiliate-Knöpfe aneinander, direkt auf dem Geldweg. Die Regel steht jetzt
**einmal** in `style.css`, die zwei Dubletten sind raus.

**B4 · eine messbar falsche Exklusivaussage.** „Der Backbone Pro ist der einzige
Controller in unserem Sortiment, der sich auch kabellos koppeln lässt" — nachgemessen
tragen **17 von 42** Produkten Bluetooth. Satz raus. Im selben Satz stand „und dabei
40 Stunden durchhält", eine Angabe, die am Morgen als unbelegt protokolliert worden
war; auch raus, samt der Stelle im `claim` des Datenkerns.

Dazu aus dem Bericht nachgezogen: Der **`claim` des G8 Plus** behauptete „der einzige
der Marke mit Switch-Betrieb" — am Listing nicht auffindbar, also weg (die andere
Hälfte, „der einzige GameSir, der kabelgebunden und kabellos kann", ist nachgemessen
richtig: fünf GameSir im Sortiment, einer mit BT). Die Tabellenzeile `Switch-Betrieb`
ist auf beiden Duellen gestrichen. **„Zusatztasten: 0"** behauptete auf drei Seiten eine
Abwesenheit aus einer Lücke im Datenkern und heißt jetzt „keine Angabe".

## Fünf Fehler im Generator, die kein Gate gesehen hätte

Der Prüfbericht hat auch im Code gefunden, was die Gates grün durchließen:

1. **Die Kopfzeile hatte ihre `<th>` verloren.** Mein Umbau schrieb `<td>` — drei Seiten
   verloren dabei ihre Header-Zellen, die Regel `.vs-table th{background:var(--navy)}`
   lief ins Leere, und eine Vergleichstabelle ohne Header-Zellen ist auch für
   Screenreader keine Tabelle. Jetzt `<th scope="col">`, dreimal pro Seite geprüft.
2. **Ein zweites Markerpaar wäre unbemerkt stehen geblieben.** `h.find(START)` nimmt nur
   das erste Paar; ein durch Kopieren entstandener Zweitblock hätte dauerhaft alte
   Preise gezeigt, ohne dass je ein Gate rot wird. Jetzt Befund bei ≠ einem Paar.
3. **`if befunde:` prüfte die globale Liste.** Nach dem ersten Fund wurden alle weiteren
   Duelle übersprungen: Ein zweiter Defekt weiter hinten wäre erst nach dem Fix des
   ersten aufgetaucht. Jetzt pro Duell.
4. **`len(la) > len(lb)` verglich Zeichen, nicht Plattformen.** „keine Angabe" (12
   Zeichen) hätte gegen „Android" (7) gewonnen. Jetzt die Zahl der Plattformen.
5. **Die Prosa konnte von der Definition abdriften.** Die redaktionellen Abschnitte
   stehen außerhalb des Markerblocks; der Generator schreibt sie einmal beim Anlegen.
   Beim Korrigieren von B1 ist mir genau das passiert: Seite richtig, Definition noch
   falsch. Wer die Datei löscht, hätte die falsche Fassung zurückbekommen. Jetzt meldet
   das Gate die Abweichung.

Dazu Kleinkram aus demselben Bericht: Em-Dash in generierter Copy (`63 €, 5 €
günstiger` statt `—`), „Backbone One (2. Gen) (63 €) kaufen" (doppelte Klammer, jetzt
„für 63 € kaufen"), schweizerische Schreibung („ausserdem", „heisst").

## Runde 4: der Generator hatte die Rechenfehler geschlossen, nicht die Behauptungsfehler

Zweites NEIN, und der Satz, der es zusammenfasst, stammt aus dem Prüfbericht: **„fünf der
sechs Blocker liegen in Bereichen, die kein Gate abdeckt (freie Prosa, `merkmale`-Zellen)."**
Alle Gates waren grün. Das war der Punkt.

**Lehre 7 aus diesem Protokoll habe ich selbst verletzt, auf derselben Seite, auf der ich
sie aufgeschrieben hatte.** Ich hatte „Switch-Betrieb" beim G8 Plus aus products.json
entfernt, weil das Listing ihn nicht nennt, und dann an **zehn weiteren Stellen** stehen
gelassen: im `kurzurteil` und `urteil` der Definition, auf zwei Vergleichsseiten, dreimal
im Marken-Hub (eine davon im FAQPage-Schema), in der Product-Schema-`description` der
Testseite, im Tablet-Blog und auf der Scuf-Nomad-Seite. Dasselbe bei den **„40 Stunden"**
des Backbone Pro: aus dem Claim entfernt, auf drei weiteren Seiten weiter behauptet, eine
davon wieder in einem FAQPage-Schema. Eine Aussage aus dem Datenkern zu löschen ist der
Anfang der Arbeit, nicht das Ende.

**Zweite falsche Exklusivaussage, diesmal von mir selbst gebaut.** Ich schrieb „der
einzige GameSir im Sortiment, der auch kabellos kann" — der X2s Bluetooth kann es auch.
Richtig ist nur die Fassung des Datenkerns: der einzige, der **kabelgebunden und**
kabellos kann. Meine eigene Gegenmessung hatte das nicht gefunden, weil ich auf `BT` in
`Verb.` geprüft habe und beim X2s dort `Bluetooth` steht. **Ein Messfehler in der
Gegenprobe ist schlimmer als keine Gegenprobe**, weil er Sicherheit vortäuscht.

**Die Prosa behauptete weiter, was die Tabelle als „keine Angabe" führte.** Drei Stellen:
„Der G8 Plus hat davon nichts", „Zusatztasten, die der G8 Plus gar nicht hat", „der
Kishi V3 hat beides nicht". Genau das Muster von B1, nur eine Zeile tiefer.

### Das Loch, durch das B1 kam, ist jetzt zu

`merkmale` waren als redaktionelle Zeilen gedacht, die der Generator ungeprüft übernimmt
(„ein Premium-Look ist keine Messung"). Nur: **Ein „✗" ist keine Einschätzung, sondern
eine Tatsachenaussage.** Von 17 `✗`-Zellen hielt die Prüfung genau sieben.

Neue Regel, als Gate: **Jede Zelle, die mit „✗" beginnt, braucht einen Eintrag in
`belege`: {Label: (Datei, Suchtext)}. Das Gate liest die Datei und verlangt den Text.**
Findet sich keiner, heißt die Zelle „keine Angabe".

| Zelle | Ergebnis |
|---|---|
| Pass-Through, Abo (Backbone One) | belegt in der eigenen Contra-Liste |
| Abo (Backbone Pro) | belegt im `claim` |
| Pass-Through (Kishi V3) | belegt: „✗ Kein Pass-Through-Charging" |
| Hall nur bei den Triggern (Kishi Ultra) | belegt auf der Produktseite |
| Haptik, Mecha-Buttons (Kishi V3) | belegt: die eigene FAQ nennt beide als Grund für den Aufpreis zum Pro |
| 3,5-mm-Klinke (Backbone One, Kishi V3) | **kein Beleg → „keine Angabe"** |
| Haptik (Backbone Pro, G8 Plus) | **kein Beleg → „keine Angabe"** |
| RGB (G8 Plus), Chroma (Kishi V3) | **kein Beleg → „keine Angabe"** |
| Kabellos (4 Zeilen) | **gestrichen** — die abgeleitete Zeile „Verbindung" sagt es aus products.json, ohne eine Abwesenheit von Hand zu behaupten |

**Beim Nachmessen der Belege habe ich mich einmal selbst getäuscht** und es fast in den
Bericht geschrieben: Mein Greptreffer „HD-Haptik" auf der Kishi-V3-Seite schien die
Zelle `Haptik ✗ Nein` zu widerlegen. Er stammte aus einer Tabelle **über das Pro-Modell**
auf derselben Seite. Der Prüfer hatte recht, meine schnelle Messung nicht. Wer über eine
Produktseite grept, greift auch das Nachbarprodukt ab.

### Drei weitere Gate-Löcher aus demselben Bericht

1. **Vertippter Slug bei einer neuen Seite blieb stumm.** Der `--check`-Pfad meldete
   „wuerde NEU angelegt" und sprang ab, **bevor** die Slugs gegen products.json geprüft
   wurden. Reihenfolge gedreht: erst die Daten, dann die Datei.
2. **Die Drift-Prüfung deckte 2 von 7 Seiten ab** und davon nur `abschnitte`. `lead` und
   `kurzurteil` werden genauso einmal beim Anlegen geschrieben — und genau dort stand
   einer der Switch-Sätze. Jetzt mitgeprüft.
3. **Zwei Auskünfte über dasselbe Bauteil in einer Tabelle.** Auf kishi-ultra-vs-g8-plus
   sagte die abgeleitete Zeile „Sticks: keine Angabe" (der Datenkern führt für den Ultra
   nur einen Trigger-Wert), zwei Zeilen tiefer „Hall bei den Sticks: nur bei den
   Triggern". Eine abgeleitete Zeile fällt jetzt weg, wenn eine redaktionelle Zeile
   dieselbe Komponente behandelt.

**Und das Gate fing beim Aufräumen zwei meiner eigenen Handkorrekturen:** Der Satz im
Marken-Hub gehört `gen_brand_sections.py`, der auf der Scuf-Nomad-Seite gehört
`gen_content.py`. Ein Generatorlauf hätte beide zurückgedreht. Das ist §A1, zum zweiten
Mal nach dem 30.09. aufgefallen, und beide Male von der Maschine, nicht von mir.

## Runde 5: das Gate prüfte nur das Kreuz, nicht den Haken

Drittes NEIN, fünf Blocker, und der Bericht nennt den gemeinsamen Nenner: **„Die fünf
Blocker liegen samt und sonders außerhalb dessen, was die Gates prüfen: Meta-Tags,
Prosa gegen Tabelle und `✓`-Behauptungen ohne Beleg."**

**Die Beleg-Pflicht hatte eine Hälfte vergessen.** Sie griff bei `wa.startswith('✗')`.
Zwei falsche **positive** Behauptungen liefen deshalb ungehindert durch:

- **`Chroma-RGB: ✓ Ja`** für den Kishi V3 Pro. Im ganzen Repo ist Chroma für
  Razer-Controller **nur beim Kishi Ultra** belegt; die Testseite des V3 Pro nennt es
  nicht, products.json führt es nicht, der einzige Chroma-Eintrag im Datenkern ist der
  *Phone Cooler Chroma*. Die neue Seite war die einzige Stelle, die dem V3 Pro das
  Merkmal gab, und das Urteil und ein Prosa-Absatz bauten darauf.
- **`App: GameSir Nexus`** gegen `Razer Nexus`. „GameSir Nexus" hat genau einen Treffer
  im Repo, nämlich diese Zelle. Die Testseite des Galileo sagt das Gegenteil: „✓ Keine
  App-Pflicht, kein Abo". Meine Zeile las sich als Parität und hat eine **belegte**
  Aussage ersetzt.

Ein Haken ist genauso eine Tatsachenaussage wie ein Kreuz. **Jetzt braucht jede der 23
`merkmale`-Zeilen einen Beleg**, nicht nur die mit `✗`. Ein Beleg ist `(Datei, Suchtext)`
oder eine Liste davon, weil eine Zeile meist auf beiden Seiten etwas behauptet.
**Diese Form ist in Runde 8 durch die seitengebundene ersetzt worden** (`{'a': …, 'b': …}`,
siehe unten) — wer sie hier abschreibt, macht das Gate rot. Für echte
Einschätzungen steht `'EINSCHAETZUNG'` — und die darf dann **kein Häkchen tragen**, denn
ein Haken behauptet einen gemessenen Vorteil. „Design: ✓ Premium-Look" ist deshalb zu
„Design: Premium-Look" geworden.

**Drei weitere Blocker derselben Familie wie die vorigen:**

- **„40 Stunden" lebte in den Meta-Tags derselben Datei weiter**, aus der ich die Angabe
  aus Lead und Vorteilsliste entfernt hatte. Drei Tags (description, og, twitter), eine
  Datei, die ich angefasst hatte. Repoweit waren es die letzten drei Treffer.
- **Nach dem Pass-Through-Fix trugen zwei von drei Urteilen die alte Prämisse weiter.**
  Wenn beide G8 durchladen, kann „Laden während des Spielens entscheidet" nicht stehen
  bleiben. Ich hatte den Absatz umgeschrieben und `kurzurteil` und `urteil` übersehen.
  Jetzt entscheiden Klinke, vier Euro und die bessere Bewertung, also das, was die
  Tabelle hergibt.
- **„Zwei Dinge, die der Backbone nicht hat"** auf der ältesten Vergleichsseite: Das
  Pass-Through ist belegt, die Klinke nicht (die Backbone-Testseite nennt sie nirgends,
  auch nicht in ihrer Nachteilsliste, die drei andere Fehlstellen ausdrücklich aufführt).

**Dazu ein Informationsverlust in die andere Richtung:** Die abgeleitete Zeile zeigte für
den Backbone Pro „Sticks: keine Angabe", während seine eigene Testseite „✗ Keine
Hall-Effect-Sticks" sagt. Die Seite wusste mehr als die Tabelle. Jetzt steht es als
belegte Zeile drin.

Und ein Fund in meinem eigenen Fix: Die Unterdrückung doppelter Bauteilzeilen prüfte
`w in z[:60]` auf dem gerenderten HTML und griff damit in den ersten Wert hinein. Ein
Spec-Text wie „TMR-Sticks + Hall-Effect-Trigger" hätte eine fremde Zeile **still**
gelöscht. Jetzt wird nur das Label verglichen.

## Runde 6: das Häkchen stand auf einer Schwäche, und der Beleg war genau diese Schwäche

Viertes NEIN, sechs Blocker. Der Bericht fasst die Diagnose in einem Satz zusammen:
**„`verify.py`, `gen_vergleich.py --check` und `idempotenzprobe.py` sind gleichzeitig
grün, während sechs Blocker live gehen würden."** Fünf davon saßen in Feldern, die der
Generator **genau einmal** schreibt und danach nie wieder vergleicht.

**Der schwerste Fund war mein eigener Beleg.** Die Zeile `RGB: ✓ Chroma` für den Kishi
Ultra habe ich mit `('produkte/razer-kishi-ultra/index.html', 'Chroma-RGB')` belegt. Diese
Zeichenfolge kommt auf der Seite **genau einmal** vor, nämlich im Block
`<h3>Schwächen</h3>`: „✗ Chroma-RGB ist Geschmackssache und für das Spielgefühl ohne
Nutzen". Ich habe ein Häkchen auf ein Merkmal gesetzt, das die eigene Produktseite als
nutzlos führt, und als Beweis die Zeile angegeben, die das sagt. Die Teilstring-Prüfung
war zufrieden. **Die Zeile ist weg**, samt der Stelle im Kurz-Urteil, die RGB als Plus
nannte.

Daraus die Gate-Erweiterung: **Ein Beleg, der in einer Nachteils-Umgebung steht, zählt
nicht für ein Häkchen.** Geprüft wird der Kontext vor dem Treffer auf `✗`, `con-item` und
`<h3>Schwächen`, und nur dann, wenn die Zeile gar keine `✗`-Seite hat (die erste Fassung
hat drei korrekte Zeilen gemeldet, weil dort der negative Beleg zur `✗`-Seite gehört).

**Vier weitere Umgehungen, die der Bericht einzeln vorgeführt hat** (jede mit `CHECK=True`
nachgemessen, alle waren exit 0): eine **leere Beleg-Liste** ließ die Schleife null mal
laufen · ein **leerer Suchtext** prüfte `'' in text`, immer wahr · ein **verwaister
Beleg** ohne zugehörige Zeile verrottete unbemerkt (genau das Risiko, das beim Entfernen
der Chroma-Zeile entsteht) · ein **falsch getypter** Eintrag wurde still auseinandergenommen.
Alle vier werden jetzt rot.

**Und die Lücke, die Blocker 1 möglich gemacht hat:** Der Em-Dash im generierten Titel war
im Code behoben und stand weiter in **sechs Meta-Tags** der zwei neuen Seiten, weil der
Generator bei bestehenden Dateien nur den Markerblock pflegt. „baumstabil=True" der
Idempotenzprobe beweist genau das und nicht mehr. Jetzt prüft das Gate `<title>`,
`og:title` und `twitter:title` gegen das `titel`-Feld der Definition.

**Drei Urteile widersprachen der eigenen Seite:**

| Seite | Urteil sagte | Die Seite sagt |
|---|---|---|
| backbone-one-vs-gamesir-g8 | „Klinke … überlegene Wahl" | Tabelle: „keine Angabe" für den Backbone One |
| g8-galileo-vs-g8-plus | „Die Klinkenbuchse, **vier Euro weniger** … entscheiden" | Lead: „Die Entscheidung fällt woanders"; Absatz: „wir behaupten es in keine Richtung" |
| g8-plus-vs-kishi-v3-pro | „deckt **mehr Einsatzfälle** ab" | Plattformen-Zeile identisch, und der Gegner läuft zusätzlich an Windows 11 |

Das zweite ist besonders unangenehm: **Ich habe es in Runde 5 selbst eingebaut**, beim
Beheben des vorigen Widerspruchs. Ein Urteil umzuschreiben, ohne Lead und Absatz derselben
Seite danebenzulegen, erzeugt den nächsten.

**Ein Blocker war eine Korrektur, die ich zu weit getrieben hatte.** Ich hatte
„✓ 2 Rücktasten + 2 Bumper" auf „✓ 2 Rücktasten" verkürzt, weil der Datenkern nur
`Extra: 2 Rücktasten` führt. Der Bericht hat den Beleg gefunden, den ich übersehen habe:
`razer-kishi-v3-review` sagt in zwei FAQ-Stellen **„zwei Rücktasten plus zwei Bumper"**,
und 14 Seiten im Repo sprechen von vier. Meine Zelle halbierte damit eine belegte Zahl und
widersprach der Prosa derselben Seiten. Zurückgenommen, jetzt mit dieser FAQ-Stelle als
zweitem Beleg. **Vorsicht ist nicht automatisch richtig: Eine Zahl zu streichen, deren
Beleg man nicht gefunden hat, ist derselbe Fehler wie eine zu erfinden, nur in die andere
Richtung.**

Dazu zwei Scheinbelege aus demselben Bericht: `'Gewicht'` war mit dem **Feldnamen**
`"Gew."` belegt und hätte auch bei „999 g" gehalten (jetzt `'138 g'`), und der Abo-Beleg
für den Backbone Pro nannte weder „Backbone+" noch den Monatstakt (jetzt die Testseite).
Und eine Dopplung, die meine eigene Unterdrückungsregel nicht erfasste: „Sticks" und
„Hall-Trigger" standen als zwei Zeilen über dasselbe Bauteil, weil das Label nur
`Trigger` einbrachte. Die redaktionelle Zeile ist entfallen, die abgeleitete sagt
Hall-Effect gegen TMR.

### Der Nachlauf derselben Runde: zweimal halb gemacht

Derselbe Prüfer hat nach den Fixes erneut gemessen und sechs seiner Blocker geschlossen
gefunden. **Zwei blieben, und beide hatten dieselbe Form: im generierten Feld behoben, in
der ungegateten Prosa derselben Seite stehen gelassen.**

- `g8-plus-vs-kishi-v3-pro`: Das `urteil` sagte korrekt „52 Euro weniger, und kabellos
  spielen kann von den beiden nur er" — eine Zeile darüber stand weiter „ist der
  flexiblere Controller … läuft auch am Tablet", und drei Absätze tiefer „Reichweite über
  mehr Geräte". Die Begründung, warum das falsch ist, hatte ich selbst als Kommentar in
  den Generator geschrieben, direkt über das neue Urteil.
- `kishi-ultra-vs-g8-plus`: Tabellenzeile und Kurz-Urteil waren von Chroma bereinigt, ein
  Absatz machte es weiter zum „zweiten von zwei guten Gründen".

**Und zwei Gate-Löcher, die der Prüfer einzeln nachgemessen hat:**

1. **Ein Beleg durfte von einem fremden Produkt kommen.** Probe: „V3 Pro ✓ Chroma", belegt
   auf der Seite des Kishi **Ultra** — exit 0. Jetzt muss die Beleg-Datei zu `a` oder `b`
   des Duells gehören oder products.json sein. Die Regel hat beim Einbau sofort zwei echte
   Fälle gefunden: Mein „zwei Rücktasten plus zwei Bumper"-Beleg von der **V3**-Seite
   stand in zwei Duellen, an denen der V3 nicht teilnimmt.
2. **Die Zahl in der Zelle hing an nichts.** Probe: Zelle auf „999 g", Beleg weiter
   „138 g" — exit 0. Jetzt muss jede Zahl aus der Zelle in mindestens einem Belegtext
   derselben Zeile vorkommen.

Aus (1) folgte die bessere Fassung der Zusatztasten-Zeile: **„✓ 4 frei belegbare"**,
belegt auf der eigenen Produktseite jedes beteiligten Geräts, wo wörtlich „4 frei
belegbare Zusatztasten" steht. Damit sagen Tabelle, Prosa, Testseiten und die 14 anderen
Seiten im Repo dasselbe. Offen bleibt, dass products.json als Chip `Extra: 2 Rücktasten`
führt — das ist eine Abkürzung, kein Widerspruch (zwei Rücktasten plus zwei Bumper), aber
es gehört beim nächsten Listing-Abgleich geklärt.

### Ein Prozessfehler, der mir gehört

**Ich habe zweimal in den Arbeitsbaum geschrieben, während ein Prüfer darin gelesen hat.**
In Runde 4 waren dadurch zwei Befunde beim Nachmessen schon weg; in Runde 6 hat der Prüfer
seinen Bericht gegen einen Stand von 16:30 geschrieben, der um 16:35 nicht mehr existierte,
und dabei um 16:33 ein **rotes** `verify.py` gesehen (meine eigene Fließtext-Zeile,
sekunden später behoben). Vier Fälle seiner Links-Batterie wurden dadurch falsch rot.
Beides hat den Bericht nicht entwertet, aber es hat ihn teurer gemacht und einmal fast zu
einer falschen Schlussfolgerung geführt. **Macher ≠ Prüfer heißt auch: Während der Prüfer
liest, wird nicht geschrieben.** Die Batterien, die mutieren und zurückstellen, machen es
noch gefährlicher — sie hätten meine Edits überschreiben können.

## Runde 7: die Regel von Runde 6 war durch einen Slug-Präfix umgehbar

Fünftes NEIN, fünf Blocker. **Diesmal stand der Arbeitsbaum nachweislich still** (Hash und
Inhaltshash identisch am Anfang und am Ende der Prüfung) — der Prozessfix hat gehalten.

**Der wichtigste Fund trifft die Regel, die ich eine Runde vorher gebaut hatte.** „Ein
Beleg muss zu `a` oder `b` des Duells gehören" prüfte `v['a'] in quelle`. Und
`'razer-kishi-v3'` steckt in `'razer-kishi-v3-pro-review'`. **Die Regel war durch einen
Slug-Präfix umgehbar, und sie wurde in genau diesem Stand umgangen:** Die
Zusatztasten-Zeile von `g8-galileo-vs-kishi-v3` behauptete etwas über den Kishi **V3** und
war auf der Seite des Kishi **V3 Pro** belegt. Das Gate war grün. Jetzt wird der
Ordnername exakt verglichen (`<slug>` oder `<slug>-review`), und die reparierte Regel hat
den Fall beim ersten Lauf selbst gemeldet.

**Zwei weitere Umgehungen derselben Bauart:**

- **`'38' in '138 g'`.** Eine halbierte Zahl hielt als Teilstring der belegten — genau der
  Fehler aus Runde 6, nur eine Ebene tiefer. Jetzt mit `\b`-Grenzen.
- **`'EINSCHAETZUNG'` befreite jede Zahl von der Belegpflicht**, weil der Zweig vor der
  Zahlenprüfung `continue`t. Probe des Prüfers: Zelle „12 g" gegen „4000 g", null Befunde.
  Eine Einschätzung darf jetzt auch keine Zahl tragen.

**Und noch ein „Sensa".** Nachdem Chroma vom Kishi V3 Pro genommen war, schrieb ich dem
Kishi **Ultra** „Sensa HD Haptik" zu. Im ganzen Repo gehören alle 14 „Sensa"-Treffer dem
V3 Pro; die Ultra-Seite sagt nur allgemein „Haptik" und nennt das Wort nie. **Dieselbe
Fehlerklasse, in Spiegelrichtung, auf genau der Seite, die dafür schon zweimal
nachgebessert worden war.**

**Ein Kaufgrund ohne Tabellenzeile wurde zur Tabellenzeile.** „Windows-11-Betrieb am PC"
stand als Argument in der Prosa, während die Plattformen-Zeile Gleichstand zeigte —
`worksOn` kennt keinen Windows-Schlüssel, die gerechnete Zeile *kann* es nicht zeigen.
Statt den Satz zu löschen ist daraus eine belegte redaktionelle Zeile geworden
(`Windows-Betrieb | keine Angabe | ✓ Windows 11`, Beleg auf der Testseite des V3 Pro).
Das ist der Zweck von `merkmale`: Was wahr und belegt ist, aber nicht im Datenkern steht,
gehört mit Beleg in die Tabelle, nicht nur in die Prosa.

### Die Heuristik, die still gelöscht hätte

Der Prüfer hat vorgeführt, dass meine Unterdrückung doppelter Bauteilzeilen auf
Teilstrings im Label arbeitete: Ein redaktionelles Label **„Preis-Leistung" hätte die
gerechnete Preiszeile still entfernt**, ohne Befund. Jetzt sagt die Definition
ausdrücklich, welche abgeleitete Zeile ersetzt wird (`'ersetzt': {'Hall bei den Sticks':
['Sticks']}`), und ein Eintrag für eine Zeile oder ein Ziel, das es nicht gibt, ist ein
Befund.

**Die Umstellung hat sofort eine verdeckte Dopplung aufgedeckt:** Auf
`backbone-pro-vs-kishi-v3-pro` standen danach „Sticks | keine Angabe" **und**
„Stick-Technik | ✗ Keine Hall-Effect-Sticks" — zwei Zeilen über dasselbe Bauteil, die die
Heuristik zufällig verdeckt hatte. Eine Heuristik, die das Richtige tut, ohne dass man
weiß warum, verbirgt genauso viel wie sie löst.

### Drei eigene Gates abgeschossen, beim Schließen eines vierten Lochs

`gen_hubs.py` und `gen_longtail.py` nahmen `--check` schweigend an und liefen im
**Schreibmodus** — der Prüfer hat damit beim Prüfen in den Arbeitsbaum geschrieben (ohne
Schaden, weil sie idempotent sind, aber das war Glück). Sie lehnen das Flag jetzt ab. Meine
erste Fassung der Wache stand auf Modulebene, und damit griff sie **beim Import**: Drei
echte Gates (`sync_guenstiger`, `sync_positionierung`, `sync_hublinks`) importieren
`gen_hubs` und laufen selbst mit `--check` im `sys.argv`. `verify.py` war sofort rot mit
fünf Fehlern. Die Wache gehört in `__main__`, nicht daneben.

### Was meine eigene Dokumentation falsch sagte

Der Prüfer hat sie gegen das Repo gemessen, und drei Zahlen stimmten nicht: „alle 23
Zeilen" bei damals 22, eine kaputte Mechanismus-Nummerierung in P-18 (1, 2, 3, **5, 6,
4**), und **drei verschiedene Gate-Zahlen in zwei Dateien** („Achtzehn", „Neunzehn",
„Zwanzig"). Die Zeilenzahl ist durch die Windows-Zeile inzwischen tatsächlich 23, was es
nicht besser macht: Eine Zahl, die zufällig richtig wird, war nie gemessen. Deshalb nennt
die Dokumentation jetzt die **Liste** der Gates statt einer Zahl und bindet die Zeilenzahl
ans Wort „derzeit".

## Runde 8: der Beleg prüfte die Datei, nie das Produkt darin

Sechstes NEIN, drei Blocker und ein Befund, der schwerer wiegt als sie: **Die
Beleg-Regel prüfte, aus welcher DATEI ein Beleg kommt, nie über WELCHES PRODUKT darin er
etwas sagt.** Und `products.json` war unbedingt freigegeben, also war eine Datei mit allen
42 Produkten ein Freifahrtschein für jede Zeichenfolge. Der Prüfer hat sieben Umgehungen
vorgeführt, alle exit 0:

| Behauptung | Beleg | lief durch |
|---|---|---|
| Kishi V3 Pro `✓ Chroma 12 LEDs` | products.json (gehört dem *Phone Cooler Chroma*) | ja |
| Kishi V3 Pro `138 g` | products.json (gehört dem *Backbone One*) | ja |
| G8 Plus `✓ Windows 11` | Testseite des **V3 Pro** | ja |
| Kishi V3 `✓ Sensa HD` | products.json (gehört dem **Pro**) | ja |
| G8 Plus `✗ TPSiV-Sticks` | Seite des Kishi **Ultra** | ja |

**Genau so sind Chroma und Sensa entstanden.** Die Regel ist jetzt **seitengebunden**:
`{'a': (Datei, Suchtext), 'b': (...)}`. Jede Seite, die etwas behauptet, braucht ihren
eigenen Beleg; der Ordnername muss zu **ihrem** Produkt passen; und in products.json wird
nur das Objekt dieses Produkts durchsucht, nicht die Datei. Dazu: Ein Beleg für eine Seite,
die „keine Angabe" sagt, ist jetzt ein Befund (überflüssiger Beleg). Alle fünf Proben des
Berichts werden rot.

**Die Entwicklung dieser einen Prüfung über sechs Runden steht als Kommentar im Code**,
weil jede Stufe von einem echten Fehler erzwungen wurde: keine Prüfung → Pflicht nur bei
`✗` → Teilstring-Beleg → Datei-Herkunft per `in` → Datei-Herkunft exakt → seitengebunden.

**Und das Urteil ist nicht mehr ungegatet.** Probe des Prüfers: ein `urteil` mit „9000 mAh
Akku, Chroma-RGB und wiegt 12 g" ergab null Befunde — für die Zeile, die den Kauf trägt.
Jetzt muss jeder **Messwert** (Zahl plus Einheit) in `lead`, `kurzurteil` und `urteil` in
der eigenen Tabelle oder im Datenkern der beiden Produkte stehen. Bewusst nur messende
Zahlen: Eine Prüfung auf jede Ziffer schlägt auf Modellnamen an („G8", „V3") und auf die
Jahreszahl; nachgemessen hätte sie sieben Fehlalarme erzeugt, die enge Fassung null.

**Dazu eine Prüfung, die beide Namensfehler dieses Pakets gefangen hätte:** Markennamen
gehören ihrem Gerät. `Sensa` → V3 Pro, `Chroma` → Kishi Ultra und Phone Cooler, `TPSiV` →
Kishi Ultra, `Backbone+` → die zwei Backbones. Steht einer auf einer Vergleichsseite, an
der das Gerät nicht teilnimmt, wird es rot.

**Die drei Blocker selbst:**

- `kishi-ultra-vs-g8-plus` nannte **vier Kaufgründe ohne Tabellenzeile**. Drei stehen
  wörtlich in der Stärken-Liste der eigenen Produktseite (mecha-taktiles Steuerkreuz,
  Nexus-App ohne Abo, PC Remote Play) und sind jetzt belegte Zeilen. Der vierte
  („haptisches Feedback") steht dort **nicht**, nur in einer FAQ-Antwort, und ist aus dem
  Kaufgrund-Absatz raus.
- **Das Backbone+-Abo ist für den Backbone One keine Pflicht.** Die eigene FAQ sagt „du
  kannst den Controller problemlos ohne Abo nutzen", die Vorteilsliste „App kostenlos", und
  products.json führt `App: kostenlos`, als Chip auf zehn Seiten. Meine Zelle und mein neuer
  Satz machten daraus eine Pflicht für den „vollen Funktionsumfang". Korrigiert auf das,
  was die Quelle sagt: Cloud-Gaming kostet extra.
- „was ein Konsolen-Controller kann und **ein Handy-Aufsatz sonst nicht**: haptisches
  Feedback" — vom eigenen Repo widerlegt, der Kishi Ultra ist ein Handy-Aufsatz mit Haptik,
  und eine Seite **dieses Pakets** verkauft sie. Dieselbe Klasse wie der entfernte Satz
  „die polierteste App am Markt".

**Vier falsche Zahlen in meiner eigenen Dokumentation**, alle vom Prüfer gemessen: „elf
von 42 tragen Bluetooth" (es sind **17**; die Elf entstand durch genau den Messfehler, den
dieselbe Datei zwei Absätze weiter als Lehre notiert — Suche nach `BT`, `Bluetooth`
übersehen), „18 verschiedene Zeilen-Labels" (**18**, 19 nur mit der Kopfzelle), eine
kaputte Mechanismus-Nummerierung, und `verify.py` sprach von „fünf Direktvergleichen" bei
sieben. Dazu ein Rendering-Fehler am Element, das Runde 7 neu eingebaut hat: Der Rückweg
stand auf drei von sieben Seiten **außerhalb** des `.container` und damit randlos über die
volle Seitenbreite.

**Offen und benannt:** Der Chip `Sticks: "TMR + Sensa-HD-Haptik"` im Datenkern vermischt
zwei Eigenschaften, weshalb auf zwei Seiten „Sticks" und „Haptik" dasselbe Wort tragen.
Das gehört in den nächsten Listing-Abgleich, nicht in eine Textkorrektur.

## Runde 9: der Qualifier, der in der Zelle fehlte

Siebtes NEIN, vier Blocker. Einer davon ist **mein Fix aus Runde 8** — zum dritten Mal in
diesem Paket habe ich beim Beheben eines Widerspruchs den nächsten erzeugt:

> „das der Backbone Pro **laut seiner eigenen Testseite nicht hat**: haptisches Feedback"

Die Testseite des Backbone Pro nennt Haptik an **null** Stellen. Sie sagt also nichts und
kann keine Abwesenheit dokumentieren. Das ist wörtlich der §A5-Punkt, den dieses Paket
neu in die Constitution geschrieben hat, und die Tabelle derselben Seite sagt es richtig
(„keine Angabe").

**Zwei Blocker auf einer Zeile, die neun Runden niemand gelesen hat.** `Abo nötig? | ✗
Backbone+ (€/Mon.)` behauptete eine Pflicht. Dagegen stehen: die eigene FAQ („du kannst
den Controller problemlos ohne Abo nutzen"), der Spec `App: kostenlos`, drei weitere
Repo-Stellen („Für die Grundfunktion nicht") — und **der eigene Beleg**, der den Qualifier
trägt, den die Zelle weggelassen hat („Backbone+-Abo **für Cloud-Gaming** nötig"). Das Gate
prüfte, dass der Belegtext existiert, nicht dass die Zelle seinen Geltungsbereich
wiedergibt. Jetzt heißen die Zellen „Backbone+ nur für Cloud-Gaming" (One) und
„✗ Backbone+ für volle Funktionen" (Pro, so steht es dort), und „kein Abo" ist aus dem
Sieger-Urteil raus.

**Und einmal die Gegenrichtung:** `Sticks | keine Angabe` für den Backbone One, während
die Site „✗ Keine Hall-Effect-Sticks" an vier Stellen dokumentiert — auf der Zeile, die
die Seite selbst zur Entscheidungszeile erklärt. Denselben Fall hatte ich ein Duell weiter
schon gelöst, mit demselben Mechanismus, und hier stehen gelassen. Jetzt
`Stick-Technik | ✗ Keine Hall-Effect-Sticks | ✓ Hall-Effect` plus `ersetzt`.

### Vier Gate-Löcher, alle vom Prüfer vorgeführt

1. **Die Umgebungsprüfung lief nur für `✓`.** Ein `✗` ließ sich mit einer Zeile aus der
   **Vorteile**-Liste belegen. Jetzt beide Richtungen: Ein Häkchen darf keine
   Nachteils-Umgebung haben, ein Kreuz braucht eine — **oder** eine Einschränkung im
   Belegtext selbst. Die erste Fassung verlangte eine Nachteilsliste und meldete prompt
   drei korrekte Zeilen, deren Beleg in einem Prosa-Absatz steht („Nur die Trigger
   arbeiten mit Hall") oder in einer FAQ.
2. **`_MESSZAHL` kannte „€", aber nicht „Euro".** Ein `urteil` mit „999 Euro weniger" war
   grün. Dazu fehlte `abschnitte` in der Prüfliste.
3. **Abgeleitete Zahlen mussten rechenbar werden, sonst ist die Prüfung auf Prosa
   unbrauchbar.** „46 Euro oder 59 Prozent" steht nirgends als Literal: 46 ist 124 minus
   78, und 59 ist 46 von 78 in Prozent. Das Gate rechnet jetzt Differenzen und Prozente
   nach, statt sie zu verbieten — P-13 verlangt genau das.
4. **Das Codebeispiel in P-18 zeigte noch die alte Beleg-Form** (Liste von Tupeln), die
   das Gate inzwischen zurückweist. Wer der Dokumentation gefolgt wäre, hätte es rot
   gemacht. Dazu zwei weitere falsche Zahlen und eine Regelbeschreibung, die enger war als
   die Implementierung.

**Was weiter kein Gate hat, und das bleibt so:** Die Sachprüfung der Urteilsfelder gegen
die Tabelle. Der Prüfer hat es vorgeführt: ein `urteil` mit „OLED-Display und kabelloses
Laden" ergibt null Befunde, und „Nur der G8 Galileo lädt beim Spielen" ebenfalls, obwohl
die Tabelle für beide „✓ Ja" sagt. Alle vier Blocker dieser Runde waren nur durch Lesen
findbar. Das ist die ehrliche Grenze dieses Pattern-Typs.

## Runde 10: das Gate, das 96 Prozent aller Zahlen erlaubte

Achtes NEIN, drei Blocker. Einer davon ist der schwerste Befund des ganzen Pakets, und er
betrifft die Prüfung, die ich in Runde 9 gebaut hatte.

**Die Messwert-Prüfung war ein Freibrief.** `_abgeleitet()` nahm als Basis alle
Ziffernfolgen aus der Tabelle **und** dem JSON-Dump beider Produkte (also auch ASINs,
Bild-URLs wie `_SL1500_`, Video-Hashes), bildete darauf alle Differenzen und dann alle
Prozentverhältnisse dieser Differenzen. Nachgemessen vom Prüfer und von mir bestätigt:

| Seite | zulässige Werte | Abdeckung der Zahlen 1…2000 |
|---|---|---|
| g8-galileo-vs-kishi-v3 | 13.709 | **100,0 %** |
| backbone-one-vs-gamesir-g8 | 9.333 | **99,9 %** |
| kishi-v3-vs-kishi-v3-pro | 6.509 | **99,8 %** |

„9000 mAh", „999 Euro", „230 g", „40 Stunden", „195 g" liefen durch — **genau die Zahlen,
deren Entfernung dieses Paket mehrere Runden gekostet hat.** Sie wären ungehindert
zurückgekommen.

**Und meine eigene Rot/Grün-Probe hatte sie als wirksam ausgewiesen.** Der Grund ist
Lehre 8 dieses Protokolls, angewendet auf mein eigenes Gate: Ich habe den **Exitcode**
gelesen. In `--check` ist der aber schon 1, sobald sich der generierte Block ändert — und
das tut er bei jeder Änderung eines Urteilsfelds. Das korrekte „59 Prozent" und das
erfundene „999 Euro" gaben beide exit 1 bei 0 Befunden. Wer den Exitcode als Rot-Signal
liest, bestätigt jede Prüfung, auch eine abgeschaltete.

**Der Umbau in fünf gemessenen Stufen**, jede durch die nächste Messung verworfen:

| Stufe | Abdeckung | was noch durchkam |
|---|---|---|
| 1 Basis = Tabelle + JSON-Dump, zwei Ableitungsstufen | 96–100 % | alles |
| 2 Basis nur Tabelle | 7–14 % | 93 Prozent, 40 Stunden |
| 3 Prozente ans Paar gebunden | 3–6 % | 93 Prozent, 40 Stunden |
| 4 Prozente nur aus dem Preispaar | 1,6–2,8 % | 40 Stunden, 1 Stunde, 2 g |
| 5 Differenzen nur aus dem Preispaar, Token statt Teilstring, URLs raus, Einheiten mit Singular | **0,5 %** | — |

Endstand, nach der Messvorschrift des Prüfers (jede Erfindung auf **jeder** der sieben Seiten, nicht auf einer): **13 Erfindungen x 7 Seiten = 91 Fälle, 0 Lücken.** Gefangen werden 9000 mAh, 999 Euro, 93 Prozent, 230 g, 40 Stunden, 195 g, 160 g, 20 Stunden, 245 g, 1 Stunde, 30 Minuten, 1500 g und 3,5 Sterne; vier korrekte Aussagen bleiben grün. **Meine eigene Fassung hatte nur eine Seite geprüft und „zwölf" gezählt, wo dreizehn standen** — zwei der dreizehn liefen auf einzelnen Seiten durch: „3,5 Sterne" wurde von „3,5-mm-Klinke" gedeckt (Bindestrich fehlte in der Ausschlussmenge) und „30 Minuten" von `"duration": "0:30"`, einer Video-Laufzeit im Datenkern.

Drei Einzelfunde auf dem Weg dorthin, alle derselben Familie:
- **„40" galt durch `a40cb261`** in einer Video-URL als gedeckt, **„1" durch
  `eu-west-1-prod`** — `zahl in text` ist Teilstring, nicht Deckung. URLs sind jetzt aus
  dem Deckungsraum entfernt.
- **`\b` allein reichte nicht:** „1" hat in „4,1" eine Wortgrenze. Gebraucht wird ein
  eigenständiges Token (weder Wortzeichen noch Dezimalnachbarn), und dieselbe Regel muss
  auch beim Aufbau der Basis gelten — sonst zerlegt `\d+` die „4,1" in 4 und 1.
- **„1 Stunde" kam durch, weil die Einheitenliste nur „Stunden" kannte.** Nicht die Deckung
  war zu weit, die **Erkennung** war zu eng. Jetzt mit optionalem Plural.

**Dazu derselbe Doku-Befund wie in Runde 9, zum zweiten Mal halb behoben:** Das
**erste** Codebeispiel in P-18 zeigte noch die alte Beleg-Form (Liste von Tupeln), die das
Gate inzwischen zurückweist. Ich hatte nur den zweiten Block nachgezogen. Jetzt beide, und
die Runde-5-Passage im Protokoll trägt einen Vorwärtsverweis statt einer Rückdatierung.

**Und dritter Blocker: drei Sätze behaupteten, ein HERSTELLER schweige** („gibt Backbone
nicht an", „sagt Razer nichts", „Für beide nennt der Hersteller kein Gewicht"), belegt ist
nur, dass **das Repo** schweigt. Für den G8 Galileo IST das Listing nachgelesen und
protokolliert — dort darf der Satz so stehen, und er tut es. Für die anderen heißt es
jetzt „ist nicht dokumentiert".

Fünf Nebenbefunde mitgenommen: Auf drei von sieben Seiten verlinkte **nur der Verlierer**
seinen Test (jetzt beide, mit Gate) · die Überschrift `<h2>Specs-Vergleich</h2>` stand
handgeschrieben auf fünf Seiten und fehlte auf zwei (jetzt im Generator, also überall
genau einmal) · „Beide laufen an Handy, Tablet und iPhone" (ein iPhone ist ein Handy) ·
und eine unbelegte Haptik-Angabe für den Kishi Ultra auf seiner eigenen Produktseite — die
das Gate sofort als §A1-Verstoß gemeldet hat, weil ich sie im HTML statt in
`gen_content.py` korrigiert hatte.

## Runde 11: die Seiten sind sauber, die Dokumentation war es nicht

Neuntes NEIN — und zum ersten Mal mit einer anderen Lage: **Der Prüfer hat auf den sieben
Seiten selbst nichts Falsches gefunden.** Jede Zahl, jeder Beleg, jede Abwesenheits-,
Exklusivitäts- und Quellenaussage und jeder Kaufgrund gegen die Tabelle derselben Seite
gemessen, Ergebnis: sauber. Die drei Blocker liegen in einer Gate-Prüfung und in meiner
Dokumentation.

**Blocker 1 ist der bitterste des Pakets: Meine Zellzahl-Prüfung benutzte `\b` allein — und
genau das verbietet §A5 v1.6, die ich in diesem Paket geschrieben habe**, 130 Zeilen weiter
unten im selben File richtig umgesetzt. Folge, vom Prüfer vorgeführt: Der Belegtext
„Redaktions-Score · bei Amazon 4,4 von 5 aus 157 Bewertungen" deckte eine erfundene Zelle
`✓ 4 Hall-Trigger` (die 4 aus 4,4), `✓ 157 Stunden` und `✓ 5 Zoll`. Je 0 Befunde.

Der Fix brauchte zwei Stufen, und die zweite ist die interessantere:
1. Token statt Wortgrenze — fängt die „4" aus „4,4".
2. **Die Einheit muss mitstimmen.** „157" steht wirklich im Belegtext, nur als
   „157 Bewertungen" und nicht als „157 Stunden". Eine Zahl ohne ihre Einheit ist kein
   Beleg. Jetzt mit `_EINHEIT` für physikalische Einheiten (€, g, mAh, mm, Zoll, Stunden,
   Minuten, Prozent); Sterne und Bewertungszahlen bleiben ausgenommen, weil die Quellen
   sie anders formulieren („4,4 von 5" statt „4,4 Sterne").
   **7 Proben, 0 falsch.**

**Blocker 2: Meine Dokumentation behauptete Gate-Schutz, den es nicht gab.** „Jede dieser
fünf Stellen hat jetzt einen Befund im Gate" — nachgezählt waren es zwei. Die fehlende
Kopfzeile, der `len()`-Vergleich und die duellweise Befundprüfung hatten **keinen** Befund;
sie wurden nur als Blockdrift rot. Für die Kopfzeile ist jetzt ein echtes Gate da (drei
`<th scope="col">` je Seite, rot/grün bewiesen), die anderen zwei stehen als
Logikkorrekturen ohne Gate da. **Eine Dokumentation, die mehr verspricht als die Maschine
hält, ist schlimmer als keine** — das ist derselbe Fehler wie die zwei P-18-Codebeispiele
aus Runde 9 und 10, nur eine Abstraktionsebene höher.

**Blocker 3: „Umfang 305 bis 383 Wörter" war nicht reproduzierbar.** Gemessen 321 bis 391.
Drei Prüfrunden haben an dieser Zahl Zeit verloren, weil keine Messvorschrift dabeistand.
Jetzt steht sie dabei: Text in `<main>`, `<script>`/`<style>` entfernt, Tags durch
Leerzeichen ersetzt, Tokens über einem Zeichen gezählt.

**Drei weitere Gate-Lücken geschlossen**, alle vom Prüfer mit Befundzahl belegt:
`'EINSCHAETZUNG'` befreite eine Tatsachenbehauptung (Probe: `('Wasserdicht','Ja','Nein')`,
0 Befunde — jetzt verboten) · die Polaritätsprüfung griff nur bei `✓`/`✗` am Zellenanfang,
jetzt auch bei „Kein/Keine/ohne/nicht" · `ersetzt` konnte still eine **fremde** Zeile
löschen (Probe: `{'Haptik': ['Amazon-Bewertung']}` entfernte die Bewertungszeile), jetzt
braucht Label und Ziel einen gemeinsamen Wortstamm.

**Und eine Grenze, die bleibt:** Trägt der Belegtext irgendeine Negation, akzeptiert das
Gate ihn für jede Abwesenheitsbehauptung — „Keine App-Pflicht" würde ein „Kein Bluetooth"
decken. Dass die Negation sich auf eine andere Sache bezieht, kann eine Textprüfung nicht
sehen. Was sie kann, ist belegt: Ein „Kein X" mit rein positivem Beleg wird rot.

## Runde 12: dieselbe CSS-Lücke ein zweites Mal, auf der Schwesterklasse

Zehntes NEIN, drei Blocker — und der erste ist der lehrreichste des ganzen Pakets, weil er
**mein eigener Fix von B3 war, nur eine Klasse daneben.**

**`.cta-row` hatte nach meiner Arbeit drei Zustände über sieben Seiten:**

| Zustand | Seiten | Wirkung |
|---|---|---|
| Regel lokal + Markup | 3 | Grid mit 16px Gap |
| **Markup ohne jede Regel** | 2 | zwei `inline-flex`-Knöpfe direkt aneinander |
| **Regel ohne Markup** | 2 | tote Regel, zwei nackte `<a>` ohne Wrapper |

Bei B3 hatte ich `.cta-pair` global gelegt und die zwei lokalen Dubletten entfernt — und
`.cta-row`, die daneben im selben `<style>` stand und dasselbe Problem hatte, **nicht
angesehen.** Der Prüfer nennt den Grund dafür präzise: `css_kaskade.py` prüft nur die 39
hinterlegten Selektorfälle, also hatte Blocker 1 kein Gate, und deshalb konnte er ein
zweites Mal entstehen.

Jetzt: eine Regel in `style.css`, keine lokale, dasselbe Markup auf allen sieben Seiten —
und **ein Gate für alle drei Zustände**, rot/grün bewiesen (Markup ohne Regel · lokale
Dublette · Regel ohne Markup). Der Lauf hat sofort 113 Asset-Version-Fehler gemeldet, weil
`style.css` sich geändert hat; das ist das Gate, das tut was es soll.

**Blocker 2: P-18 schrieb „Zahlen mit `\b`-Grenzen" vor — was §A5 v1.6 im selben Commit
verbietet und der Code nicht tut.** Alle fünf Zahlenprüfungen arbeiten mit eigenständigen
Tokens. Wer P-18 folgt, baut den Fehler neu, der eine Prüfrunde gekostet hat. Dritte
Dokumentationsstelle dieser Art in diesem Paket (nach zwei Codebeispielen in Runde 9 und 10).

**Blocker 3: Meine Trefferquote war falsch gezählt — und falsch gemessen.** Ich schrieb
„Zwölf Erfindungen werden gefangen" und listete **dreizehn**. Schlimmer: Ich hatte jede
Erfindung nur auf **einer** Seite geprüft. Der Prüfer hat sie auf allen sieben getestet und
zwei Lücken gefunden:
- **„3,5 Sterne" wurde von „3,5-mm-Klinke" gedeckt** — der Bindestrich fehlte in der
  Ausschlussmenge, also galt „3,5" als freistehendes Token. Auf genau den vier Seiten mit
  einer Klinke-Zeile.
- **„30 Minuten" wurde von `"duration": "0:30"` gedeckt**, einer Video-Laufzeit im
  Datenkern. Dritter Fund derselben Art nach den Bild-URLs und `eu-west-1-prod`.

Endstand nach seiner Messvorschrift: **13 Erfindungen x 7 Seiten = 91 Fälle, 0 Lücken.**

**Die Lehre ist die Messvorschrift selbst.** Ich hatte 16 Proben auf einer Seite gemacht und
daraus eine Quote abgeleitet. Eine Prüfung, die auf einer Seite greift, kann auf sechs
anderen offen sein — weil der Deckungsraum je Seite aus deren Tabelle und deren Datenkern
entsteht. **Eine Trefferquote gilt nur für die Menge, auf der sie gemessen wurde.**

## Runde 13: der Pfad, der eine neue Seite anlegt, lief im Alltag nie

Elftes NEIN, zwei Blocker, beide ein Einzeiler — und beide im Pfad, der eine **neue** Seite
anlegt. Zum dritten Mal in Folge waren die sieben Seiten selbst sauber.

**Der Prüfer hat eine Methode erfunden, die ich hätte haben müssen:** Seite im Spiegel
löschen, Generator laufen lassen, das Ergebnis gegen den Repo-Stand diffen. Drei
Unterschiede, zwei davon Defekte:

- **Die Überschrift „Specs-Vergleich" kam doppelt.** Ich hatte sie in Runde 10 in `block()`
  verlegt und aus den fünf Seiten entfernt — aber nicht aus dem Rahmen in `neue_seite()`.
  Eine neu angelegte Seite trug sie zweimal, und kein Gate zählte sie.
- **`.cta-row` lag weiter als lokale Dublette in `SEITEN_STIL`** — also erzeugte der
  Generator genau den Zustand, den sein eigenes Gate seit Runde 12 verbietet. Schreiblauf:
  3 Befunde, danach dauerhaft 1.

Zusammen heißt das: **Die zwei neuen Seiten waren nach der Generierung von Hand korrigiert
und ließen sich aus dem Generator nicht reproduzieren.** Das ist die §A1-Divergenz, die
dieses Paket beseitigen sollte, und P-18s Satz „Der Generator legt die ganze Seite an" hielt
nur mit zwei Handgriffen hinterher.

**Der Grund, warum das elf Runden überlebt hat:** Der Pfad läuft im Alltag nie. Die sieben
Seiten existieren, also nimmt `gen_vergleich.py` immer den Markerblock-Zweig. Ein Zweig, der
nur beim ersten Mal läuft, wird nur beim ersten Mal geprüft — danach nie wieder.

**Deshalb ist die Methode jetzt ein Skript:** `scripts/rundreise.py`, sechste stehende
Batterie. Sie löscht jede Seite mit Rahmenfeldern, erzeugt sie neu und verlangt
Zeichengleichheit (bis auf die Asset-Version) plus 0 Befunde im Schreib- und im Nachlauf.
Endstand: **2 Seiten, 0 falsch.**

**Dabei fiel ein Reihenfolgefehler in meinem eigenen Gate auf.** Die Prüfungen auf
CSS-Klassen, Header-Zellen und Markennamen lasen die Datei **vor** dem Blockeinbau. Auf einer
frisch angelegten Seite ist der Markerblock leer, also schlugen sie dort falsch an — und der
Markennamen-Check griff ohnehin erst im Folgelauf (Befund B-3 des Prüfers). Alle drei lesen
jetzt die Endfassung.

**Fünf weitere Befunde aus demselben Bericht, alle echt:** P-18 zitierte die Token-Regex um
ein Zeichen zu schwach (Bindestrich fehlte im Lookbehind) · ein Kommentar im Gate behauptete
„jede Klasse" und prüfte zwei · die Vorher-Wortspanne „103 bis 428" war unter meiner eigenen
Messvorschrift nicht reproduzierbar (gemessen **100 bis 384**; der Schluss hält, drei Seiten
lagen unter der B6-Marke von 190) · und **zwei Listing-Lesungen standen nur als Prosa in
STATUS und Protokoll, nicht in einer Beleg-Datei** — obwohl auf ihnen live stehende Sätze
ruhen. Nachgetragen in `03-research/raw/amazon/2026-10-06-spec-chips-selbst-geprueft.md`,
mit der protokollierten Suche als Beleg für den Negativbefund: **Eine Aussage über das, was
ein Hersteller nicht sagt, ist genauso belegpflichtig wie eine über das, was er sagt** — nur
belegt sie kein Zitat, sondern die Suche selbst.

## Verify

- **`verify.py` ist das Pflicht-Gate und startet acht Prüfungen selbst** (`gen_bestenliste`, `gen_brand_sections`, `gen_preisfrage`, `gen_vergleich`, `sync_guenstiger`, `sync_hublinks`, `sync_positionierung`, `sync_zeitversprechen`). Von Hand laufen davor `audit_prosa`, `sync_product_values --audit`, `sync_footer`, `sync_lesezeit`, `sync_kompat`, `css_kaskade`, `gen_pages`, `sync_header` und `preiswelle`. Alle exit 0. **Gezählt statt geschätzt: 17 Skripte haben ein wirksames `--check`/`--audit`**, zwei (`gen_hubs`, `gen_longtail`) lehnen das Flag jetzt ausdrücklich ab, statt es zu ignorieren und zu schreiben.
- **Rot/Grün-Probe: 11 Fälle, 0 falsch** — Preis im Datenkern geändert · Bewertungszeile
  von Hand verfälscht · Verfügbarkeits-Zeile entfernt · „Nicht verfügbar" auf
  „Verfügbar" gedreht · Häkchen auf die falsche Seite · Gegenrede gelöscht · Sieger ist
  keiner der beiden · Produkt existiert nicht · plus drei Grün-Fälle
- **Zehn Proben-Durchgänge, 55 Fälle, 0 falsch.** Die letzten vier, jeder von einem Befund des jeweiligen Prüflaufs erzwungen: **Runde 9** (4 Fälle) ein `✗` mit Beleg aus der Vorteile-Liste · ein erfundener Euro-Betrag im `urteil` · ein erfundener Messwert in den Abschnitten. **Runde 8** (6 + 4 Fälle) die fünf Umgehungen des Berichts (products.json belegt kein fremdes Produkt mehr, Beleg der Gegenseite trägt keine Aussage über die eigene, Beleg von einer dritten Produktseite) sowie der erfundene Messwert im `urteil` und die drei Markennamen am falschen Gerät.
- **Siebte Rot/Grün-Probe (Umgehungen der Beleg-Regel): 6 Fälle, 0 falsch** — ein Slug-Präfix zählt nicht mehr als Treffer · eine halbierte Zahl als Teilstring wird rot · eine Einschätzung mit Zahl wird rot · ein `ersetzt`-Eintrag ohne Zeile wird rot · ein `ersetzt` auf eine unbekannte abgeleitete Zeile wird rot · Ausgangsstand grün
- **Sechste Rot/Grün-Probe (Beleg-Herkunft und Zahlenbindung): 3 Fälle, 0 falsch** — ein Beleg von einem dritten Produkt wird rot · eine Zahl in der Zelle ohne Deckung im Belegtext wird rot · Ausgangsstand grün
- **Fünfte Rot/Grün-Probe (Gate-Umgehungen): 6 Fälle, 0 falsch** — leere Beleg-Liste ·
  leerer Suchtext · verwaister Beleg ohne Zeile · Häkchen mit Beleg aus der
  Nachteils-Umgebung · driftender `<title>` · Ausgangsstand grün
- **Vierte Rot/Grün-Probe (Beleg-Pflicht für alle Zeilen): 5 Fälle, 0 falsch** — eine
  `✓`-Zeile ohne Beleg wird rot · eine als Einschätzung geführte Zeile mit Häkchen wird
  rot · ein Beleg aus einer **Liste** bricht weg und wird rot · eine driftende `<h2>` in
  den Abschnitten wird rot · Ausgangsstand grün
- **Repoweite Gegenprobe über alle Blocker-Klassen:** „Switch" beim G8 Plus **0**,
  „40 Stunden/40 h" **0**, 230/245/195 g **0**, Chroma beim V3 Pro **0**, „GameSir
  Nexus" **0** (die verbleibenden Treffer sind meine eigenen Code-Kommentare, die
  festhalten, warum die Aussage weg ist). **Alle sieben „einzige"-Aussagen im Repo
  einzeln gegen products.json nachgezählt und korrekt** (G8 Plus ist unter fünf GameSir
  der einzige mit BT+USB-C; der X3 Pro der einzige GameSir mit Peltier-Kühlung; der
  Backbone One im Duell das einzige Gerät mit Gewichts-Spec).
- **Dritte Rot/Grün-Probe (Beleg-Gate): 4 Fälle, 0 falsch** — ein `✗` ohne Beleg wird rot ·
  ein Beleg, der auf eine fehlende Datei zeigt, wird rot · ein Belegtext, der nicht mehr
  in der Quelle steht, wird rot (die Quelle kann sich ändern, ohne dass die Behauptung
  mitwandert) · ein vertippter Slug bei einer neuen Seite wird rot statt „wuerde NEU
  angelegt"
- **Zweite Rot/Grün-Probe nach den Blockern: 6 Fälle, 0 falsch** — zweites Markerpaar ·
  Prosa-Drift zwischen Definition und Seite · zwei gleichzeitig defekte Duelle (beide
  gemeldet, nicht nur das erste) · drei `<th scope="col">` pro Seite · Plattform-Zahl
  statt Zeichenlänge. Stand nach der Probe wieder grün.
- **Idempotent**: drei Läufe, identische Hashes
- Umfang **100 bis 384 → 321 bis 391 Wörter**, beide Spannen nach derselben Vorschrift (Text in `<main>`, `<script>`/`<style>` entfernt, Tags durch Leerzeichen, Tokens über einem Zeichen). Die erste Fassung nannte „103 bis 428" aus einer Messung ohne angegebene Vorschrift — und ein Prüfer konnte sie deshalb nicht reproduzieren. Drei der fünf Seiten lagen mit 100, 111 und 186 Wörtern unter der B6-Marke von 190, es waren also drei Thin Pages**, jede Seite mit drei Abschnitten, drei
  Header-Zellen und mindestens drei internen Links
- **Die zwei neuen Duelle sind jetzt von den vier Testseiten aus erreichbar**, die sie
  betreffen. Vorher verlinkten sie nur die Marken-Hubs und /vergleich/ — also nicht die
  Seite, auf der der Leser steht, wenn die Frage aufkommt.
- Die neuen Seiten waren beim ersten Lauf **vierfach rot** (Sitemap, interner Link,
  zwei Asset-Versionen) — dieselben vier Punkte, die B4 bei seiner neuen Seite gefunden
  hat. Die Gates fangen bei neuem Content genau das, was man vergisst.

## Gelernt

1. **Eine Maßnahme kann richtig sein und ihre Begründung trotzdem verfallen.** Die
   GSC-Nachfrage nach Duellen war eine Momentaufnahme aus Lauf 6: zwei Queries, je eine
   Impression, beide längst bedient. Wer die Maßnahme auf dieser Prämisse umsetzt, baut
   zehn neue Seiten; wer sie nachmisst, macht erst die fünf vorhandenen gut. Zweites Mal
   nach B5 derselbe Fall.

2. **„Mehr davon" ist selten die Antwort auf eine thin Page.** Die Seiten hatten nicht
   zu wenige Geschwister, sondern zu wenig Inhalt: keine Bewertung, keine Verfügbarkeit,
   keine Begründung. Drei von fünf waren kürzer als die Bestenlisten vor B6.

3. **Die Gegenrede trifft den Bau selbst.** In vier von sieben Duellen ist der gewählte
   Sieger der schwächer bewertete — eine Zahl, die vorher auf keiner dieser Seiten
   stand und die jetzt jede trägt. Ein Vergleich ohne Gegenrechnung ist eine Behauptung
   mit Tabelle drumherum.

4. **Beim Schreiben greift man nach dem, was danebensteht.** Ich hätte „230 Gramm" ein
   siebtes Mal in die Welt gesetzt, weil es in der Tabelle stand, die ich gerade
   generierte — acht Stunden nachdem ich selbst protokolliert hatte, dass die Zahl
   unbelegt ist. Eine entfernte Angabe aus dem Datenkern zu löschen reicht nicht; sie
   muss auch aus der Prosa, sonst wandert sie zurück.

5. **Eine Vergleichsseite deckt Widersprüche auf, die vorher niemand sehen konnte.**
   Solange der G8 Plus und der G8 Galileo auf getrennten Seiten standen, konnte die eine
   „Pass-Through ✓" und die andere nichts dazu sagen, ohne dass es auffiel. Sobald beide
   in einer Tabelle stehen, muss man sich entscheiden, und dann stellt sich die Frage,
   woher die Angabe eigentlich kommt. Der Zweitnutzen der Maßnahme war nicht der Traffic,
   sondern dass drei alte Falschaussagen aufgefallen sind.

6. **Wenn zwei eigene Seiten sich widersprechen, ist die Antwort nicht „eine gewinnt".**
   Beim 3,5-mm-Anschluss des G8 Plus war der Reflex, die Mehrheit zählen zu lassen: zwei
   Stellen sagten „kein Anschluss", eine sagte „3,5-mm-Audio". Belegt war keine davon.
   Beides zu löschen fühlt sich nach Verlust an und ist die einzige Fassung, die nichts
   erfindet. „Keine Angabe" ist eine zulässige Antwort auf einer Kaufseite; ein geratenes
   Häkchen ist es nicht.

7. **Einen Widerspruch an einer Stelle zu beheben verschiebt ihn.** Die 230 Gramm standen
   nach dem Fix der Testseite weiter zweimal im Blog. Wer nur die Stelle korrigiert, die
   der Prüfer genannt hat, hat den Prüfer bedient und nicht den Fehler. Deshalb ging bei
   jedem der vier Blocker eine Repo-weite Gegenprobe über dieselbe Aussage.

   **Und dann habe ich genau das in derselben Runde falsch gemacht.** „Switch-Betrieb"
   aus products.json entfernt und an zehn weiteren Stellen stehen gelassen, „40 Stunden"
   an drei. Diese Lehre aufzuschreiben hat nicht gereicht; sie musste in ein Gate. Für
   `✗`-Zellen steht sie jetzt dort. Für freie Prosa gibt es weiter kein Gate, und das
   ist der ehrliche offene Punkt dieses Pakets.

8. **Ein Messfehler in der Gegenprobe ist schlimmer als keine Gegenprobe.** Ich habe
   „der einzige GameSir, der kabellos kann" mit `'BT' in Verb.` geprüft und bestätigt
   bekommen. Beim X2s steht dort `Bluetooth` — die Prüfung konnte den Gegenbeleg
   buchstäblich nicht sehen. Eine Gegenprobe braucht einen Fall, von dem man weiß, dass
   er anschlagen MUSS, sonst misst sie nur das eigene Vorurteil.

9. **Ein „✗" ist keine Meinung, und ein „✓" auch nicht.** Der Generator nahm `merkmale`
   ungeprüft, mit der Begründung „ein Premium-Look ist keine Messung". Das stimmt für
   „Premium-Look" und ist für „✗ Nein" falsch. Nur habe ich daraus erst die halbe Regel
   gebaut: Beleg-Pflicht ab `✗`. Die nächste Runde fand sofort zwei falsche **positive**
   Behauptungen, die ungehindert durchliefen. **Eine Ausnahme für Redaktionelles gehört
   auf Einschätzungen begrenzt, nicht auf ein Zeichen** — und eine Einschätzung darf dann
   kein Häkchen tragen, weil ein Haken einen gemessenen Vorteil behauptet.

10. **Wer eine Prämisse kippt, muss jedes Urteil nachziehen, das darauf stand.** Nachdem
    Pass-Through bei beiden G8 auf „✓ Ja" stand, war es kein Unterscheidungsmerkmal mehr.
    Ich hatte den Absatz umgeschrieben und zwei Urteilsfelder stehen gelassen, die es
    weiter zum Entscheidungsgrund machten. Ein Fix ist nicht fertig, wenn die korrigierte
    Stelle stimmt, sondern wenn nichts mehr auf der alten Annahme steht.

11. **Ein Beleg kann das Gegenteil beweisen, und eine Teilstring-Prüfung merkt es nicht.**
    Ich habe „RGB: ✓ Chroma" mit der Zeile belegt, die auf der eigenen Produktseite unter
    **Schwächen** steht: „✗ Chroma-RGB ist Geschmackssache und für das Spielgefühl ohne
    Nutzen". Der Beleg war echt, die Datei stimmte, der Text stand drin — und er sagte das
    Gegenteil der Zelle. Ein maschineller Beleg beweist Anwesenheit eines Textes, nicht
    Zustimmung. Deshalb prüft das Gate jetzt auch die **Umgebung** des Treffers.

12. **Vorsicht ist nicht automatisch richtig.** Ich habe „2 Rücktasten + 2 Bumper" auf
    „2 Rücktasten" verkürzt, weil ich den Beleg für die Vier nicht gefunden hatte. Er
    stand in zwei FAQ-Stellen der betreffenden Testseite, und 14 Seiten im Repo nannten
    vier. **Eine belegte Zahl zu halbieren ist derselbe Fehler wie eine zu erfinden**, nur
    in die andere Richtung — und er fühlt sich beim Machen wie Sorgfalt an.

13. **Wer einen Widerspruch behebt, erzeugt leicht den nächsten.** Das Urteil, mit dem ich
    in Runde 5 den Pass-Through-Widerspruch beseitigt habe, widersprach in Runde 6 dem Lead
    und dem ersten Absatz derselben Seite. Ein Urteil umzuschreiben, ohne Lead, Tabelle und
    Absätze danebenzulegen, verschiebt das Problem nur um eine Zeile.

14. **Eine Angabe zu entfernen heißt, auch den Head zu lesen.** „40 Stunden" habe ich aus
    Lead und Vorteilsliste derselben Datei entfernt und in `description`, `og:description`
    und `twitter:description` stehen gelassen. Das sind drei Stellen, die kein Leser sieht
    und jede Suchmaschine.

15. **Ein Beleg beweist einen Text, keinen Bezug.** Sechs Runden brauchte diese eine Prüfung, und jede Stufe erzwang ein echter Fehler: keine Prüfung → Pflicht nur bei `✗` → Teilstring statt Kontext → Datei-Herkunft per `in` → Datei-Herkunft exakt → seitengebunden. Der letzte Schritt war der wichtigste: **Die Regel prüfte, aus welcher Datei ein Beleg kommt, nie über welches Produkt darin er etwas sagt** — und products.json mit 42 Produkten war damit ein Freifahrtschein für jede Zeichenfolge. Genau dort sind „Chroma" und „Sensa HD" entstanden. Wer einen Beleg maschinell prüft, muss den **Bezug** prüfen, nicht die Fundstelle.

16. **Eine Regel, die auf Teilstrings arbeitet, hat immer ein Präfix-Loch.** Dreimal in einem Paket: `'38' in '138 g'`, `'razer-kishi-v3' in 'razer-kishi-v3-pro-review'`, und `'Preis' in 'Preis-Leistung'`. Jede dieser Prüfungen sah richtig aus und war in genau dem Fall blind, den sie fangen sollte. **Wo eine Identität gemeint ist, gehört ein Gleichheitszeichen hin**, kein `in`: Ordnernamen exakt vergleichen, Zahlen mit Wortgrenzen, Zuordnungen ausdrücklich deklarieren statt erraten.

17. **Eine Heuristik, die zufällig das Richtige tut, verbirgt so viel wie sie löst.** Als die Unterdrückung doppelter Zeilen von „Begriff im Label" auf eine ausdrückliche Deklaration umgestellt war, kam sofort eine Dopplung zum Vorschein, die sie jahrelang hätte verdecken können. Der Umbau war die Messung.

18. **Ein neuer Seitentyp gehört beim ersten Exemplar generiert, nicht beim fünften.**
   Die fünf Duelle sind durch Kopieren entstanden; danach hatten sie 18 verschiedene
   Zeilen-Labels und auf drei von fünf keine Bewertung. Der Generator kostet beim ersten
   Mal eine Stunde und beim zweiten nichts.
