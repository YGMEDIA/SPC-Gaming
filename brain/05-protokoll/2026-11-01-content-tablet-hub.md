# Tablet-Hub: der zweite dünne Fund, und drei live falsche Aussagen drumherum

**Datum:** 2026-11-01 · **Loop:** content-loop (zweiter Fund aus der Messung zu GSC-Lauf 8)
**Vorlauf:** `05-protokoll/2026-11-01-content-zubehoer-ast.md`

## Was

`/controller/tablet/` von **131 auf 650 Wörter**, mit Überblicks-Sektion, Tabelle, 5 FAQs, ItemList- und FAQPage-Schema. Neu `scripts/gen_tablet_hub.py`.

Zwei Dinge, die größer waren als die Wortzahl:

**Der Hinweiskasten der Seite war falsch.** Er empfahl für Tablets zwei Modelle als „Bluetooth-Standalone". Das zweite ist ein Teleskop-Clip und zugleich die erste Karte derselben Seite, die Seite widersprach sich also. Kasten entfernt, `verify.py` Abschnitt 7 hält den Wortlaut repoweit draußen.

**`blog/controller-fuer-tablet/` widersprach der neuen Seite an vier Stellen, zwei davon im FAQPage-Schema:** „unterhalb des G8 Plus gibt es keine Tablet-Angabe" (der Kishi Ultra kostet 63 €, der G8 Plus 72 €) und „driftfreie Sticks und Tablet-Freigabe verbindet genau ein Modell" (der V3 Pro hat TMR-Sticks, und unser eigener Blog-Artikel sagt „TMR heißt dauerhaft driftfrei"). Alle vier korrigiert, drei VERBOTEN-Einträge dagegen, jeder rot/grün bewiesen.

Dazu `scripts/seitenbau.py` als geteiltes Modul: die Grammatik-Helfer aus P-19, `absatz`, `spanne`, `faq_block`, die beiden Schema-Renderer, das Mass-Gate und `beleg_umgebung()`. Die Extraktion ist AST-geprüft verhaltensneutral.

## Wie

**Zwei Eigenschaften stehen nicht in products.json** und bekamen deshalb Beleg-Paare (Datei, Suchtext) nach dem P-18-Muster: das Laden während des Spielens und die Größengrenze. `check_belege()` prüft bei jedem Lauf Anwesenheit UND Umgebung, sucht in products.json nur im Objekt des Produkts und verlangt für jedes tablet-taugliche Modell einen Eintrag. Sechs Rot-Proben, alle rot.

**Der inhaltliche Befund:** Drei der 28 Controller sind als tablet-tauglich geführt, 63 bis 124 €. Hier steigt die Bewertung mit dem Preis (4,0 → 4,1 → 4,2), anders als bei Kühlern und Triggern, wo jeweils das teuerste Produkt das am schlechtesten bewertete ist. Eins der drei koppelt kabellos. Alle drei nennen eine Größengrenze, aber in verschiedenen Maßen, und die Seite sagt bei jeder, woher sie stammt.

## Warum so

**Warum die Belege nicht in products.json wandern.** Ein neues Spec-Feld schlägt auf alle Karten durch und ändert Dutzende Seiten. Die Beleg-Tabelle hält die Aussage dort, wo sie geprüft wird, und zwingt bei einem neuen Produkt zur Entscheidung statt zum Schweigen.

**Warum die Herkunft im Text steht.** Von drei Größenangaben steht genau eine im Datenkern. Die zweite nur in den Metas einer Testseite, die dritte in einem Amazon-Beleg. Alle drei pauschal „belegt" zu nennen hätte das Wort verwässert, über das dieses Projekt gerade drei Prüfrunden geführt hat.

## Verify

`verify.py` 0 Fehler, 0 Warnungen · 18 Gates ohne Befund · `idempotenzprobe.py` 20 Skripte, 0 Befunde · `gen_vergleich.py --check` nach der Extraktion unverändert 0 Befunde · Rundreise zeichengleich · Drift-Gate 0,65 % Deckungsraum · Beleg-Gate sechsfach rot bewiesen.

**Fünf Prüfrunden, 11 Blocker, alle berechtigt.**

## Gelernt

**1. Ich habe den Prüfer bedient und nicht den Fehler.** Runde 1 beanstandete, dass der Lade-Absatz nur `claim` las und daraus eine Datenlücke behauptete. Ich habe den Lade-Absatz repariert und den **strukturgleichen Größen-Absatz danebenstehen lassen** — ausgerechnet den, der die Datenlage selbst als „am dünnsten" bezeichnete. Dort war die Lücke größer: Für alle drei Modelle ist eine Grenze dokumentiert, die des V3 Pro seit dem 30.09. live auf der Nachbarseite und in deren Schema. **Regel: Nach jedem Befund die Klasse im ganzen Paket suchen, bevor die gemeldete Stelle angefasst wird.** Zum zweiten Mal an einem Tag dieselbe Lehre.

**2. Ich habe Exitcode statt Befundzahl gemeldet, und es hat eine Regression verdeckt.** Mein Beleg zeigte auf eine Datei unter `brain/`; die Idempotenzprobe arbeitet in einer Kopie ohne `brain/`, der Generator brach ab, die Batterie ging von 0 auf 1 Befund. Ich meldete „18 Gates exit 0". Das ist genau die Verwechslung, vor der ich jeden Prüfer in jedem Briefing warne.

**3. Ein Beleg-Gate ohne Richtungsprüfung ist keines.** `"Pass-Through-Charging" in "Kein Pass-Through-Charging"` ist wahr. Die Prüfung existierte seit dem 06.10. in `gen_vergleich.py`; ich habe eine schwächere nachgebaut. Jetzt steht sie in `seitenbau.py` und beide Generatoren rufen sie.

**4. Eine Ellipse ist auch eine Beugung von Hand.** „Millimeter die Gerätebreite" sparte das Verb ein und trug nur, solange der Zoll-Eintrag zuerst stand. Die Reihenfolge kam aus der Preissortierung.

**5. Zum zweiten Mal `mz()` mit einem Substantiv, das das Zahlwort schon enthält** („ein ein Modell", „zwei zwei Modellen", viermal). Am Vortag hatte ich den Docstring dagegen geschrieben.

**6. Dreimal habe ich ein Wort zurückgenommen, statt einen Beleg zu behaupten:** „nennt der Hersteller" → „nennt unser Test" · „ist belegt" → „die Angaben stammen aus" · „in jedem Fall die falsche Bauform" → „je größer das Tablet, desto eher". Das ist die Bewegung, die §A5 verlangt, und sie kostet nichts.

## Offen

- **BRAUCHT YASIN: Der Datenkern widerspricht sich beim abxylute S8.** `claim` nennt iPad, `worksOn` führt kein `tablet`, die Produktseite nennt iPad dreimal inklusive Schema. Entweder Tag nachtragen (dann vier Modelle auf dieser Seite, und der Monotonie-Befund kippt) oder die iPad-Aussagen zurücknehmen. Steht in LOOP-STATE. **Das fehlende Tag allein ist kein Beleg für Untauglichkeit (§A5 (4)).**
- Mass-Gate kennt „ms", nicht „Millisekunden"; „wh", nicht „Wattstunden". Zwei Schlüssel, eigenes Paket.
- Sechs Sätze dieser Seite kann kein Gate prüfen. Sie stehen mit Begründung im Docstring des Generators.
