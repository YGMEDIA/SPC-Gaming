# 2026-10-05 · Content · B10: Die Zahl, die gegen den eigenen Preis spricht

## Was

Maßnahme B10 der Bücher-Synthese (Quelle: Heath, *Made to Stick* — das Unerwartete
bleibt hängen, das Erwartete wird überblättert). Die stillste Annahme beim
Controller-Kauf ist „teurer ist besser", und sie wirkt am stärksten genau dann, wenn der
Leser vor dem teuren Modell steht.

**Gemessen am 05.10.2026 über die 28 Controller mit Preis und Bewertung:** Sechs Produkte
haben ein **günstigeres Geschwister derselben Marke mit besserer Bewertung**:

| teurer | | günstiger und besser | |
|---|---|---|---|
| Razer Kishi V3 Pro | 152 € · 4,2 | Kishi V3 | 88 € · 4,4 |
| GameSir G8 Plus | 76 € · 4,1 | X5 Lite | 45 € · 4,2 |
| Backbone One PlayStation | 76 € · 4,1 | Backbone One (2. Gen) | 63 € · 4,3 |
| GameSir X2s Bluetooth | 53 € · 3,9 | X5 Lite | 45 € · 4,2 |
| 8BitDo Ultimate Mobile | 45 € · 4,3 | Ultimate 2C Wired | 30 € · 4,6 |
| Mars Gaming MGPX | 34 € · 4,1 | MGP-BT2 | 30 € · 4,2 |

**Keine dieser sechs Seiten sagte es.** Vier nannten das günstigere Modell irgendwo im
Text, keine nannte es *besser bewertet*. Die Daten lagen also vor, die Überraschung nicht
— genau die Formulierung, mit der B10 in der Warteschlange stand.

## Wie

`scripts/guenstiger.py` trägt die Regel, `gen_pages.py` rendert sie für die generierten
Seiten, `scripts/sync_guenstiger.py` setzt sie in die handgepflegten Reviews (von den
sechs Fällen liegen vier dort, zwei unter `/produkte/`). Eine Quelle, zwei Wege — wie bei
B1 und B7.

Der Kasten steht **vor** dem Kurz-Urteil, an derselben Stelle wie der
Kompatibilitäts-Block aus B1: Wer erst nach dem Urteil erfährt, dass es ein besseres
Angebot gibt, hat die Entscheidung schon getroffen. Blau statt rot (`.note-info`), weil
das Produkt nicht schlecht ist — es gibt nur ein besseres Angebot.

Dieser Satz stand hier dreimal, bevor er stimmte: Die erste Fassung von `gen_pages.py`
setzte den Block **hinter** Urteil und Absätze, also auf zwei der sechs Seiten genau
andersherum als begründet. Der Prüflauf hat die Dokumentreihenfolge nachgemessen; jetzt
steht der Block auf allen sechs Seiten vor dem Urteil (`KOMPAT < GUENSTIGER < verdict`).

Beide Bewertungen stehen **mit ihrer Anzahl** da (B8): bei 4,4 aus 153 gegen 4,2 aus 151
ist der Abstand knapp, und wer nur die Sterne zeigt, lässt den Leser das nicht einschätzen.

## Warum so

**Nur dieselbe Marke UND dieselbe Kategorie.** Ein markenübergreifender Vergleich („dieser
152-Euro-Razer ist schlechter bewertet als ein 30-Euro-8BitDo") wäre wahr, aber kein
Vergleich: andere Bauform, anderer Zweck. Innerhalb einer Marke und Kategorie steht der
Leser wirklich vor der Wahl zwischen diesen zweien.

Dass „dieselbe Kategorie" nötig ist, hat die erste Fassung bewiesen: Sie filterte nur auf
`type`, und darunter fällt das ganze Zubehör. Sie verglich deshalb einen **RISOKA-Trigger
mit RISOKA-Finger-Sleeves** als „günstiger und besser bewertet" — zwei Produkte, zwischen
denen niemand wählt. Genau der schiefe Vergleich, den der eigene Docstring eine Zeile
weiter oben ausschließt. Die Kategorie kommt jetzt aus derselben Ableitung wie der
Rückweg aus B7 (`hublinks.taxonomie_karte`): gemeinsame Übersichtsseite = vergleichbar.

**Produkte unter der §A6-Schwelle bekommen nichts.** Sie tragen schon den Warnkasten, und
der nennt bereits eine besser bewertete Alternative. Zwei Kästen übereinander sagen nicht
mehr, sie sagen weniger.

Von neun Treffern der ersten Fassung bleiben sechs, und die Reduktion gehört **beiden**
Filtern, nicht nur der Kategorie (hier stand sie zuerst allein beim Kategorie-Absatz).
Nachgerechnet über alle vier Varianten:

| Filter | Treffer |
|---|---|
| nur `type` (erste Fassung) | 9 |
| `type` + §A6-Schwelle | 7 |
| `type` + Kategorie | 8 |
| `type` + Kategorie + §A6 (ausgeliefert) | 6 |

Die Kategorie wirft den RISOKA-Trigger gegen Finger-Sleeves hinaus, die §A6-Schwelle zwei
Ozkak-Trigger (3,7 und 3,6) — die standen mit ihrem Geschwister auf derselben
Übersichtsseite, die Kategorie allein hätte sie behalten.

**Bei Preisgleichheit entscheidet die bessere Bewertung.** `min(kandidaten, key=preis_zahl)`
war von der Reihenfolge in products.json abhängig: Der X2s hat zwei passende Geschwister
zu je 45 € (X5 Lite 4,2 und X3 Pro 4,0). Heute gewann zufällig das besser bewertete; ein
Umsortieren der Datei hätte den schwächeren Hinweis gesetzt, ohne dass ein Gate etwas
merkt. Der Schlüssel ist jetzt `(Preis, -Sterne, Slug)`.

**Der Preis steht so da, wie products.json ihn führt.** Acht der 42 Preise lauten „ca.
34 €" oder „ab 50 €". Die erste Fassung rechnete daraus `preis_zahl()` und schrieb
„kostet 30 €", wo die gepflegte Wahrheit „ca. 30 €" lautet — und eine exakte Differenz
(„kostet 4 € mehr") aus zwei ungefähren Zahlen. Jetzt steht der Preis-String im Text, und
die Differenz heißt „rund 4 € mehr", sobald einer der beiden Preise ungefähr ist.

## Verify

- **Zwölf Gates, jedes exit 0** (neu: `sync_guenstiger.py --check`)
- **Neues Gate §B10** am ausgelieferten Stand, in beide Richtungen nachgemessen:
  Wo die Regel zutrifft, steht der Hinweis; wo sie nicht zutrifft, steht keiner — und das
  zweite gilt für **alle 127 Seiten**, nicht nur für die 42 aus products.json. Der Hinweis
  muss das günstigere Modell im Linktext auf dessen Seite nennen und beide Zahlen mit
  Ziffergrenzen führen.
- **`scripts/links_batterie.py` von 49 auf 59 Fälle** (40 rot, 19 grün), 0 falsch.
  Neun B10-Defektformen rot: Hinweis entfernt · Preis verfälscht · Preis um eine Ziffer
  verlängert · Sternzahl verfälscht · Modell ausgetauscht · END-Marker entfernt · Block in
  einen HTML-Kommentar gehüllt · Hinweis auf einer Produktseite, die keinen haben darf ·
  Hinweis auf einer Blog-Seite. Eine legitime Form grün (zusätzlicher Absatz daneben).
- **Elf Defektformen einzeln nachgemessen** (die neun aus der Batterie plus „END vor
  START" und dieselbe Preis-/Sternverfälschung auf einer generierten Seite): Jede löst
  mindestens eine **eigene §B10-Meldung** aus, nicht nur den Zeichenvergleich der
  Sync-Skripte daneben. Gemessen wurde über die FEHLER-Zeilen mit `§B10` ohne `--check`,
  nicht über den Exit-Code — sonst beweist der Lauf nur, dass irgendetwas rot wurde.
- Browser: Kasten in der Inhaltsspalte — 676 von 1024 px auf den handgepflegten Seiten
  (`1fr 280px`, gap 28), 652 auf den generierten (`1fr 300px`, gap 32); mobil 335 von 375,
  kein Horizontal-Scroll, `--blue-bg` korrekt angewandt
- Idempotent und reihenfolgeunabhängig: `sync_kompat` und `sync_guenstiger` in beiden
  Reihenfolgen, mehrfach, zusammen mit `gen_pages --regen` und `sync_hublinks`, in fünf
  Permutationen — alle fünf zeichengleich (`b5ea2a1c7b5aaa0b` über alle HTML-Dateien),
  verify.py jedes Mal exit 0
- Die vier stehenden Proben gegen den Endstand: `robustheitsprobe.py` 117 Defektformen /
  118 verify-Starts · `idempotenzprobe.py` 15 Schreiber, idempotent **und** baumstabil ·
  `besten_batterie.py` 36 Fälle · `finder_batterie.py` 111 Fälle — zusammen 0 Befunde

## Gelernt

1. **Eine Regel, die „dieselbe Art Produkt" meint, muss die Kategorie kennen.** `type`
   allein reichte nicht — darunter fällt Trigger wie Finger-Sleeve. Die Kategorie stand
   schon im Repo (B7s Taxonomie-Ableitung), ich hatte sie nur nicht benutzt.
2. **Ein Marker-Block um leeren Inhalt ist ein Hinweis, der nicht da sein soll.** Mein
   `block()` umhüllte auch den leeren String und schrieb damit **auf jede generierte
   Produktseite ohne Hinweis** ein leeres Markerpaar — 27 Stück, gemessen durch
   Wiederherstellen der alten Fassung. Nicht auf *jede* Produktseite: `sync_guenstiger.py`
   ruft `block()` bei leerem Inhalt gar nicht auf, die 13 handgepflegten Reviews waren nie
   betroffen. Für den Leser unsichtbar, fürs Gate ein Widerspruch — der erste Lauf des
   B10-Gates wurde mit genau diesen 27 Meldungen rot. Derselbe Fehler steckte seit B7 in
   `hublinks.block()`, dort aber latent (heute hängt jedes Produkt an mindestens einer
   Übersicht, also hat er nie ein leeres Paar erzeugt); beide sind jetzt behoben.
3. **Das Gate hat den Fehler gefunden, nicht ich.** Ich hatte den Block gebaut, die sechs
   Fälle nachgerechnet und im Browser angesehen — und die 27 leeren Markerpaare trotzdem
   nicht bemerkt. Ein Gate, das die Eigenschaft in BEIDE Richtungen prüft („wo sie
   zutrifft" **und** „wo sie nicht zutrifft"), findet, was eine Stichprobe nicht findet.
4. **Ein Gate, das bei kaputtem Markup abbricht, prüft nicht nur diesen Fall nicht.**
   `_h10.index(END)` warf `ValueError`, wenn nur der START-Marker stand. verify.py starb
   mit Traceback, also exit 1 ohne Urteil — und nahm **250 der 301 Prüfstellen** mit, die
   hinter §B10 liegen: Schemas, Links, Sitemap, No-JS-Statik, B7, B8, B9. Genau die Klasse,
   die `produktdaten.py` seit Runde 20 als Gesetz führt, zwei Zeilen später neu gebaut. Der
   Batterie-Lauf unterscheidet ABBRUCH von ROT, deshalb hält der neue Fall sie fest.
5. **Ein Teilstring-Test ist keine Zahlenprüfung.** `wert not in block` ließ „88 €" in
   „188 €" und „4,4" in „14,4" durch, und ein leerer Name machte die ganze Zusicherung
   wirkungslos (`'' in x` ist immer wahr). Zahlen prüfen jetzt mit Ziffergrenzen, der Name
   im Linktext auf die Zielseite — das ist die Aussage, die der Satz macht — und ein leerer
   Name ist selbst der Befund. Rot wurden diese Formen vorher auch, aber nur, weil der
   Zeichenvergleich daneben stand: Eine Zusicherung, die nur durch ihren Nachbarn hält,
   hält nicht.
6. **Eine Schleife über die Datei prüft nicht die Site.** Das Gate lief über
   products.json und sah deshalb nur Produktseiten; ein eingeschmuggelter Hinweis auf
   einer Blog- oder Hub-Seite blieb stumm grün. „Wo nicht, steht keiner" gilt für alle 127
   Seiten — der Gegentest läuft jetzt über `pages`.
7. **Eine Wahl ohne Tiebreak ist eine Wahl, die products.json trifft.** `min(…,
   key=preis_zahl)` hing bei zwei gleich teuren Geschwistern an der Reihenfolge der Datei.
