# Zubehör-Ast: die stärkste Seite der Site hatte 163 Wörter

**Datum:** 2026-11-01 · **Loop:** content-loop (Maßnahme aus gsc-loop Lauf 8)
**Vorlauf:** `05-protokoll/2026-11-01-gsc-lauf8-zubehoer-befund.md` · **Rohdaten:** `03-research/raw/gsc/2026-11-01.md`

## Was

| Seite | vorher | nachher | FAQs |
|---|---|---|---|
| /zubehoer/handy-kuehler/ | 163 W | **986 W** | 5 |
| /zubehoer/finger-sleeves/ | 168 W | **881 W** | 4 |
| /zubehoer/trigger/ | 294 W | **1327 W** | 5 |
| /zubehoer/ (Hub) | 41 W | **484 W** | 3 |

Neu: `scripts/gen_zubehoer_sections.py`. Je Seite eine Überblicks-Sektion mit abgeleiteten Zahlen, eine Produkttabelle, FAQs, ItemList- und FAQPage-Schema. Redaktionell bleibt die Textführung; Preise, Bewertungen, Stückzahlen, Maße und Verfügbarkeit kommen aus products.json. Dazu `sitemap.xml` mit vier neuen `lastmod`.

Der inhaltliche Kern ist ein Befund, kein Fülltext: **Zubehör ist der am schwächsten bewertete Teil des Sortiments** (vier der 14 Artikel unter 3,8 Sternen, grau hinterlegt), **in zwei der drei Kategorien ist das teuerste Produkt das am schlechtesten bewertete** (Kühler 70 € / 3,3 · Trigger 33 € / 3,7), und **das meistbewertete Produkt der ganzen Site ist ein 14-Euro-Set Finger Sleeves** mit 3.167 Bewertungen, nicht ein Controller.

## Wie

Sechs Mechanismen nach P-18-Muster, alle rot/grün bewiesen:

1. **Idempotenz per Marker.** Zweiter und dritter Lauf: 0 Dateien.
2. **Rundreise.** Marker-Blöcke entfernt, neu erzeugt, alle vier zeichengleich.
3. **Drift-Gate (§A1).** Jede Zahl muss aus products.json kommen. Deckungsraum **0,80 bis 1,85 Prozent** der Ganzzahlen 1 bis 2000.
4. **Mass-Gate.** Zahl UND Einheit als Paar, Bereiche aufgelöst. 100 von 100 Erfindungen rot über 25 Formen, 19 von 19 echten Angaben grün.
5. **Aussagen-Gate.** Vergleichssätze werden nachgerechnet, nicht nur ihre Zahlen. 14 Proben, 14 wie erwartet.
6. **Schema aus dem Endstand.** ItemList aus der sichtbaren Kartenreihenfolge, FAQPage aus den erzeugten `details`-Blöcken.

Dazu neu in diesem Paket: **P-19, zahlgebundene Prosa.** Zahlwort, Substantiv, Artikel und Verb kommen aus derselben Zahl; alle sechs Helfer brechen bei 0 ab; Mengen-Sätze und ihr `<p>` entfallen zusammen; `rows_of()` verweigert eine Kategorie mit weniger als zwei Produkten.

## Warum so

**Warum Generator.** Der Fließtext trägt auf allen vier Seiten Preise, Bewertungen und Verfügbarkeit. Von Hand gepflegt divergiert er beim nächsten preis-loop (§A1).

**Warum der ganze Ast.** Lauf 7 hat gelehrt, dass ein Thin-Page-Fund selten allein steht. Die Messung über alle 127 Seiten lieferte den Treffer und drei Geschwister, dazu `/controller/tablet/` (131 W) als Fund außerhalb dieses Pakets.

**Meta-Freeze eingehalten.** `/zubehoer/handy-kuehler/` ist seit Lauf 8 Impressions-Träger. Angefasst wurde nur der Body; Title, Description und Social-Metas sind byte-identisch zu HEAD, vom Prüfer zweimal nachgewiesen.

## Verify

`verify.py` grün (129 Seiten, 263 JSON-LD-Blöcke, 42 Produkte, 0 Fehler, 0 Warnungen) · alle 17 Gates exit 0 · `idempotenzprobe.py` 19 Schreiber, 0 Befunde · Rundreise zeichengleich · 0 Em-Dashes, 0 Nullziffern, 0 leere Absätze, 0 Großschreibungen mitten im Satz.

**Sieben Prüfrunden, 15 Blocker, alle berechtigt.** Der Prüfer hat am Ende 43 Datenzustände durchgerechnet (Dickenraum 28 Zustände, Materialraum 0 bis 4 Polyester-Sets, alle vier `stock`-Werte, neun Bewertungsmutationen, Null-Fall, Auslöser-Grenzfall) und dabei einen einzigen Befund gefunden, der kein Fehler ist.

## Gelernt

**1. Ein Zahlen-Gate ohne Einheit ist ein halbes Gate.** Die eigene Probe zeigte „40 Stunden" und „3 Jahre" als Durchläufer: Die Zahl stand als Stückzahl in den Daten, die Einheit nirgends. Dieselbe Form war in diesem Projekt schon einmal live.

**2. Zum vierten Mal eine Abwesenheit behauptet, die die Quelle nicht sagt.** Der erste Entwurf schrieb „keiner der drei Kühler bringt einen eigenen Akku mit". Belegt ist das bei zweien; beim dritten nennt products.json nur ein Netzteil. Gefunden beim Lesen der erzeugten Prosa, nicht durch ein Gate.

**3. Ich behandle die gemeldeten Stellen statt die Klasse.** Runde 4: Der Wurzel-Fix landete auf einer von vier Seiten. Runde 5: drei von sechs Helfern abgesichert, ausgerechnet die drei vergessen, die direkt eine Ziffer liefern. Beide Male hat der Prüfer den Rest gefunden. **Regel: Nach jedem Fix die Klasse messen, nicht die Fundstelle prüfen.**

**4. Dieselbe verworfene Idee ein zweites Mal angefasst.** Die Positivliste der Einheiten wollte ich loswerden. Erster Versuch (jedes Wort hinter einer Zahl ist eine Einheit) meldete „3,3 aus" und „77 Controller". Zweiter Versuch, eine Runde später, erntete die Einheiten aus dem Datenkern und lieferte „bis" aus „Smartphone bis 11mm" und „r" aus „L1R1/L2R2". Beide Fehlversuche stehen jetzt samt Grund im GRENZE-Absatz des Codes. **Eine verworfene Idee gehört dokumentiert, sonst kommt sie wieder.**

**5. Ein Gate kann die eigene Formulierung erzwingen, und das ist in Ordnung.** `audit_prosa.py` machte „Das Set RISOKA kostet 1,40 Euro je Hülse" rot, weil hinter einem Produktlink der echte Preis stehen muss. Die Regel war richtig, mein Satz die Ausnahme. Die neue Fassung („kostet 14 € für 10 Hülsen, also 1,40 Euro je Stück") ist auch für den Leser klarer.

**6. Eine Zahl kann richtig sein und trotzdem die falsche Menge zählen.** „Das ist ein Vergleich von drei gegen eins" beschreibt den Material-Vergleich, rechnete aber aus der Bewertungsschwelle. Heute stimmen beide Mengen zufällig überein. **Prüffrage: Zählt der Satz die Menge, über die er spricht?**

**7. Auch ein Adjektiv ist eine Messung.** „Beim Material zeigt unsere Datenlage ein Gefälle" gilt nur, solange sich die Bewertungsspannen nicht überlappen. Selbst gefunden, nicht vom Prüfer gemeldet.

**8. Die Untergrenze ist eine Entscheidung, keine Beugung.** Sieben Stellen hätten bei einer Einproduktkategorie „ein Sets" geschrieben. Sieben Singular-Zweige hätten sieben grammatisch korrekte, inhaltlich sinnlose Sätze ergeben, weil auf einer vergleichenden Seite mit einem Produkt kein Satz mehr wahr ist.

**9. zsh splittet unquotierte Variablen nicht.** Der erste Gate-Durchlauf meldete 14 von 17 rot; grün waren nur die ohne Argument. Nicht die Gates waren rot, die Messung war kaputt. Dieselbe Klasse wie die Exitcode-Verwechslung vom 06.10.

**10. Das Muster hält: In jeder Runde ein neuer Fehler beim Beheben des vorigen.** Acht in sieben Runden, darunter zweimal ein Syntaxfehler durch ein fehlendes `+`, einmal „ein das Set" durch ein Substantiv mit Artikel an `mz()`, einmal Großschreibung mitten im Satz durch ein `capitalize()` im falschen Helfer. Die letzten vier habe ich selbst gefunden, bevor der Prüfer dran war. **Was sich geändert hat: Diesmal ging keiner davon live.**

## Offen

- **Die Klasse, die kein Gate prüft** (vom Prüfer benannt, als GRENZE in P-19 dokumentiert): Sätze ohne Zahl und ohne Produktverhältnis passieren alle drei Gates. Rund ein Dutzend stehen im Text, überwiegend Regeln fremder Spiele und Technik-Allgemeinplätze. Sie wurden durch Lesen geprüft, zweimal gegen die eigenen Blog-Artikel gekreuzt, und driften unbemerkt, falls sich die Spielregeln ändern.
- **`produkte/ozkak-6finger/index.html`** beschreibt vier Finger und nennt es 6-Finger-Steuerung. Bestandsfehler von vor diesem Paket, in die content-loop-Warteschlange. Meine eigene Definition auf der Trigger-Seite ist deshalb entfallen: Welche Finger das sind, steht in keiner Quelle dieses Projekts.
- **`/controller/tablet/`** mit 131 Wörtern neben Geschwistern von 482 bis 1138, zweiter Thin-Page-Fund aus derselben Messung.
