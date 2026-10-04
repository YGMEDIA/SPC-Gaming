# 2026-10-02 · B5: Problem-Content, abgeleitete Lesezeit, gegatete Mengenaussagen

> Der Runde-für-Runde-Verlauf der neunundzwanzig Prüfläufe steht in
> `2026-09-30-prosa-und-generatorquelle.md` (Abschnitte "Prüflauf zu B5" bis "Neunundzwanzigste
> Prüfung zu B5", Lehren 94 bis 232 (die hoechste Nummer im Gesamtkatalog 1 bis 232; dort sind 229 verschiedene, denn 53, 89 und 90 fehlen — alle drei liegen UNTER 94, in der genannten Spanne ist also keine Luecke)). Diese Datei ist der datierte Eintrag zum Schritt
> selbst, wie CLAUDE.md ihn verlangt. Er entstand erst heute, weil die Arbeit über zwei
> Tage in einer Datei vom 30.09. mitgeschrieben wurde; der achtzehnte Prüfbericht hat das
> als Befund gemeldet, und zu Recht.

## Was

Maßnahme B5 aus der Bücher-Synthese: Problem-Content ausbauen.

- `/blog/controller-verbindet-nicht/` von **803 auf 1232 Wörter**, drei neue Abschnitte
  plus ein Spezialfall. Alle vier tragen `<h2 data-rolle="stoerung">`, damit ihre Anzahl
  ableitbar ist und nicht gezählt werden muss.
- **Lesezeit abgeleitet statt getippt.** Sie stand an 41 Stellen (19 Bylines, 19 Karten
  auf `/blog/`, 3 auf der Startseite) und war auf **17 von 19 Seiten falsch**, nie zu
  niedrig. Eine Regel in `scripts/lesezeit.py`, benutzt von Generator, Sync und Gate.
- **Mengenaussagen gegatet.** "11 der 28 Controller sind kabelgebunden", "6 der 28 laufen
  per Funk und Kabel", "27 der 28 im Finder-Pool", "1 Modell unter der Schwelle": alle aus
  `products.json` nachgerechnet, in beiden Anspruchsrichtungen.
- **§A6 im Controller-Finder.** Vorher lag die 3,8 nur als Ranking-Gewicht in `score()`;
  dass kein schwaches Modell in die Top 3 kam, war ein Ergebnis der Gewichtung. Jetzt
  `const A6_SCHWELLE = 3.8` plus Filter vor der Ausgabe, und verify **führt den Finder
  aus**, statt seinen Quelltext zu lesen.
- **Leseregeln für `products.json`** in `scripts/produktdaten.py`, geteilt mit `kompat.py`.
- Nebenbefunde: `.gitignore` angelegt und eine seit dem 22.09. getrackte `.pyc` aus dem
  Index genommen (sie wurde von GitHub Pages ausgeliefert).

## Wie

Neunundzwanzig Prüfläufe in frischem Kontext, jeder blockierend (Macher ≠ Prüfer). Zwei
Gate-Entwürfe wurden nach dem Beweis ihrer Unlösbarkeit **verworfen**, nicht geflickt: der
breite Erkenner für Mengenaussagen und der breite für Fragenzahl-Zusagen. Beide ersetzt
durch satzexakte Muster auf tagfreiem Text, was messbar **mehr** abdeckt, weil es Text
statt Markup durchsucht.

Jedes Gate hat ein Rot/Grün-Paar: rot auf einem echten Defekt UND grün auf korrektem
Inhalt. "Rot auf falsch" allein beweist nichts, das hat Runde 9 gezeigt, wo ein Gate drei
Runden lang die falsche Zahl erzwungen hat.

## Warum so

Drei Entscheidungen, die anders hätten ausfallen können:

**Erweitern statt drei neue Seiten.** "Verbindet nicht", "wird nicht erkannt" und "trennt
sich" sind fast synonym und hätten sich kannibalisiert (§B1).

**Satzexakt statt breit.** Acht Runden haben versucht, jede Formulierung eines
Mengenanspruchs zu erkennen. Jede Fassung hatte entweder ein Loch oder, schlimmer, einen
Fehlalarm auf wahrem Text (zuletzt 13 von 78 wahren Sätzen rot). Der Preis ist im Code
benannt: ein **neu** formulierter Mengensatz wird nicht geprüft. Der nächste Content-Lauf
muss das wissen.

**Ausführen statt suchen, zweite Stufe.** Der Vertrag zwischen `controller-finder/index.html`
und `finder.js` wurde drei Prüfrunden lang durch Muster über Markup geprüft. Sechzehn
Formen wurden gefangen, und jede Runde lag eine daneben, die den Finder tötete, während die
Seite seine Leistung weiter zusagte. Jetzt wird die Seite geparst
(`scripts/dom_baum.py`), finder.js läuft dagegen (`scripts/finder_probe.js`, Minimal-DOM),
und geprüft werden Zustände: welcher Schritt ist aktiv, welche `data-step`-Werte tragen die
Abschnitte, wie viele Karten erscheinen, wirkt Zurück. Was keinen Zustand erzeugt, bleibt
Quelltext-Prüfung und ist im Code als solche benannt: Ladeordnung des Script-Tags,
CSS-Bindung der umgeschalteten Klasse, fetch-Pfad.

**Ausführen statt lesen.** Der Prüfer hatte das §A6-Gate als prinzipiell nicht schließbar
gemeldet. Es ist schließbar, aber nicht so, wie es naheliegt: Die Ausführung mit den echten
Daten fängt den Defekt NICHT, weil die Rangfolge das schwache Modell ohnehin aus den Top 3
hält. Entscheidend ist die Gegenprobe mit einem Produktsatz, bei dem der Filter alles
aussortieren muss.

## Verify

- `python3 scripts/verify.py` grün (0 Fehler, 0 Warnungen · 127 Seiten · 250 JSON-LD-Blöcke)
- die prüfbaren Gates, jedes mit exit 0: `verify.py`, `audit_prosa.py`,
  `sync_product_values.py --audit`, `sync_footer.py --check`, `sync_lesezeit.py --check`,
  `sync_kompat.py --check`, `css_kaskade.py`, `gen_preisfrage.py --check`,
  `gen_brand_sections.py --check` (neun; `mess_bilder.py --check` braucht Netz und bleibt
  Handarbeit). Hier stand "sechs" -- die Zahl ist gewachsen, ohne mitgezogen zu werden,
  und zwei der Gates sind in diesem Paket entstanden
- Idempotenz mit nachfahrbarer Messvorschrift: `python3 scripts/idempotenzprobe.py` -- 12 Schreiber (`gen_*`, `sync_*`, `bump_asset_version.py`, die beim Lauf Dateien schreiben und keinen Weg nach aussen haben; die Sperre liest Importe per `ast`, kennt `os.system` und Verwandte und verfolgt lokale Hilfsmodule), je dreimal, **idempotent UND baumstabil**: der committete Stand ist schon die Ausgabe der Generatoren. Die Zahl stand hier als "elf" ohne Vorschrift, der Prüfer zählte mit seiner Definition zwölf
- Reinraum-Probe: genau die Dateimenge, die der Commit enthält (**345** Dateien: 334
  getrackt ohne die entfernte `.pyc`, 11 neu), die drei CI-Gates darin exit 0.
  Nachfahrbar: `git ls-files | wc -l` plus
  `git ls-files --others --exclude-standard | wc -l` -- OHNE weiteren Abzug, denn die
  Loeschung der `.pyc` ist gestaged, `git ls-files` zaehlt sie also schon nicht mehr
  (`git ls-files | grep -c pyc` ergibt 0). Die Vorschrift nannte hier einen Abzug zu viel
  und ergab woertlich befolgt 344 statt 345 -- in genau der Passage, die eine Runde vorher
  neu geschrieben wurde, weil sie kaputt war. **Die Zahl stand hier fünfmal falsch** (339, 341, 342, 343, 344), jedes Mal
  gemessen und dann nicht mitgezogen, als eine Datei dazukam. Dass sie trotzdem getippt
  dasteht, ist Absicht: Sie beschreibt EINEN Lauf, nicht eine Invariante.
  Nachtrag: Diese Passage war beim fünften Nachziehen halb überschrieben worden und
  nannte zwei unvereinbare Zahlen gleichzeitig ("345 … 11 neu" und "… 10 neu",
  "fünfmal falsch" und "viermal falsch") samt unpaariger Klammer. Gefunden hat das der
  sechsundzwanzigste Prüfbericht, in der Datei, die Lehre 4 führt.
- ohne `node` im Pfad: exit 0 mit sichtbarer Warnung, nicht rot und nicht stumm
- Robustheit mit nachfahrbarer Messvorschrift: `python3 scripts/robustheitsprobe.py` --
  15 Felder × 7 falsche Typen plus 12 Sonderformen = **117 Defektformen**, jede über alle
  42 Produkte. 0 Abbrüche, 0 Hänger, 0 stumm grün, unveränderter Stand grün
- Proben am Finder: `python3 scripts/finder_batterie.py` -- alle Formen aus den
  Prüfrunden 18 bis 29. Die ANZAHL gibt der Lauf aus, sie steht nicht hier: Sie hat in
  diesem Dokument zweimal veraltet gestanden (33, dann 87), während das Skript daneben die
  richtige ausgibt. Die Zusammensetzung (Defektformen, die rot werden MÜSSEN, und legitime
  Änderungen, die grün bleiben MÜSSEN) steht im Skript. Jeder Fall bekommt eine frische
  Kopie aus dem Repo, und das Skript meldet, wenn eine Mutation nicht gegriffen hat
- Die CSS-Auswertung hat ihre eigene Falltabelle: `python3 scripts/css_kaskade.py` gibt
  Umfang und Ergebnis aus. Jede Form aus den Prüfrunden 21 bis 29 steht darin, in beide
  Richtungen (was treffen MUSS und was nicht treffen darf). Auch hier keine getippte
  Anzahl mehr: Sie stand als "41", dann als "53", und war beide Male schon beim Schreiben
  veraltet
- Em-Dash-Delta in der AUSGELIEFERTEN Copy: **-3** (keine neue). Messvorschrift, weil die Zahl ohne sie nicht nachfahrbar ist: alle gegen HEAD geänderten Dateien, die wirklich ausgeliefert werden -- also `*.html` plus `llms.txt`, nicht `brain/` und nicht `scripts/` (die veröffentlicht der Workflow nicht). Aufgeteilt: `blog/controller-verbindet-nicht/` -1, `blog/index.html` -1, `llms.txt` -1. Nur über die HTML-Dateien gemessen wären es -2; wer die Zahl nachprüft, muss dieselbe Menge nehmen (R30, Lehre 238)

## Gelernt

Die Lehren 94 bis 232 (die hoechste Nummer im Gesamtkatalog 1 bis 232; dort sind 229 verschiedene, denn 53, 89 und 90 fehlen — alle drei liegen UNTER 94, in der genannten Spanne ist also keine Luecke) stehen einzeln in `2026-09-30-prosa-und-generatorquelle.md`. Die
vier, die über dieses Paket hinaus gelten:

1. **Eine Probe an einem Exemplar beweist nichts über eine Stelle hinter einem Filter.**
   Ein Defekt in einem Produkt ließ drei von fünf Abbruchstellen unentdeckt; die breite
   Probe über alle Produkte und alle Felder fand danach elf weitere.
2. **Anwesenheit ist nicht Wirkung, und Wirkung ist nicht am Ergebnis ablesbar.** Ein
   Filter wird bewiesen, indem man ihm einen Eingabesatz gibt, bei dem er alles
   aussortieren muss.
3. **Wenn eine Probe eine Datei verändert, misst man zuerst das Hash-Gate.** Zwei meiner
   Fehlalarme hießen nur "Datei geändert". Eine Probe muss benennen, WELCHE Meldung sie
   erwartet.
4. **Eine Zahl ohne Messvorschrift gehört nicht in die Doku.** "26 Stellen sagen 3 Fragen"
   ließ sich nicht reproduzieren: drei Messungen ergaben 26, 27 und 28. Die Zahl steht
   jetzt nicht mehr da, das Gate schon.

## Zurückgewiesen (mit Beleg)

**"Stand September 2026 in der Byline widerspricht `dateModified: 2026-10-02`."** Tut es
nicht: "Stand" ist der **Datenstand** der Produktdaten, eine repoweite Konstante
(`DATENSTAND_MONAT`, 22 Seiten, von verify gegen die Sitemap gehalten), und die letzte
Preispflege war der 30.09. `dateModified` ist das Textdatum. Auf Oktober zu ziehen hieße,
eine Datenaktualität zu behaupten, für die kein Screenshot existiert (§A5). Offen bleibt
die Frage, ob "Stand" in einer Artikel-Byline für Leser eindeutig ist; das ist eine
Konvention über 22 Seiten und keine Entscheidung dieses Pakets.
